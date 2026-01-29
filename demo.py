#!/usr/bin/env python3
"""
Fractured Keys Demo Script
Demonstrates the complete workflow of encrypting and decrypting passwords
"""

import sys
import os
import tempfile
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from colors import print_colored, Colors
from crypto import encrypt_password_aes_gcm, decrypt_password_aes_gcm
from sss import split_bytes_into_shares, recover_bytes_from_shares
from steganography import embed_data_into_image, extract_data_from_image
from PIL import Image

def create_demo_images():
    """Create demo images for testing"""
    images = []
    
    # Create 3 different colored images
    colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255)]
    
    for i, color in enumerate(colors, 1):
        img = Image.new('RGB', (200, 200), color=color)
        filename = f"demo_image_{i}.png"
        img.save(filename)
        images.append(filename)
        print_colored(f"Created demo image: {filename}", Colors.SUCCESS)
    
    return images

def demo_encryption():
    """Demonstrate encryption process"""
    print_colored("\n" + "="*60, Colors.INFO)
    print_colored("🔒 FRACTURED KEYS DEMO - ENCRYPTION", Colors.INFO, Colors.BOLD)
    print_colored("="*60, Colors.INFO)
    
    # Demo data
    password = "MySecretPassword123!"
    master_password = "MasterKey456"
    
    print_colored(f"Password to encrypt: {password}", Colors.INFO)
    print_colored(f"Master password: {master_password}", Colors.INFO)
    
    # Step 1: Encrypt password
    print_colored("\n📝 Step 1: Encrypting password with master password...", Colors.INFO)
    salt, nonce, ciphertext_with_tag = encrypt_password_aes_gcm(password, master_password)
    print_colored("✅ Password encrypted successfully", Colors.SUCCESS)
    
    # Show encryption components
    import base64
    ciphertext = ciphertext_with_tag[:-16]
    auth_tag = ciphertext_with_tag[-16:]
    
    print_colored("\n🔍 Encryption Components:", Colors.INFO)
    print_colored(f"Salt: {base64.b64encode(salt).decode()}", Colors.SALT)
    print_colored(f"Nonce: {base64.b64encode(nonce).decode()}", Colors.NONCE)
    print_colored(f"Ciphertext: {base64.b64encode(ciphertext).decode()}", Colors.CIPHERTEXT)
    print_colored(f"Auth Tag: {base64.b64encode(auth_tag).decode()}", Colors.AUTH_TAG)
    
    # Step 2: Create binary blob
    binary_blob = salt + nonce + ciphertext_with_tag
    print_colored(f"\n📦 Binary blob size: {len(binary_blob)} bytes", Colors.INFO)
    
    # Step 3: Generate ephemeral key and package
    print_colored("\n🔑 Step 2: Generating ephemeral key and packaging...", Colors.INFO)
    import os
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    
    K2 = os.urandom(16)  # 16-byte ephemeral key
    aes = AESGCM(K2)
    nonce2 = os.urandom(12)
    packaged_ct_and_tag = aes.encrypt(nonce2, binary_blob, None)
    packaged_cipher = nonce2 + packaged_ct_and_tag
    print_colored("✅ Binary blob packaged with ephemeral key", Colors.SUCCESS)
    
    # Step 4: Split ephemeral key into shares
    print_colored("\n📊 Step 3: Splitting ephemeral key into SSS shares...", Colors.INFO)
    n_shares = 3
    threshold = 2
    shares = split_bytes_into_shares(K2, n=n_shares, k=threshold)
    print_colored(f"✅ Created {len(shares)} shares (threshold: {threshold})", Colors.SUCCESS)
    
    # Step 5: Create demo images
    print_colored("\n🖼️ Step 4: Creating demo images...", Colors.INFO)
    demo_images = create_demo_images()
    
    # Step 6: Embed shares into images
    print_colored("\n🔒 Step 5: Embedding shares into images...", Colors.INFO)
    stego_images = []
    
    for i, (share_bytes, image_path) in enumerate(zip(shares, demo_images), 1):
        # Wrap share with metadata
        payload = wrap_share_payload(share_bytes, index=i, total=n_shares, 
                                   threshold=threshold, packaged_cipher=packaged_cipher)
        
        # Embed into image
        stego_path = f"stego_share_{i}.png"
        saved_path = embed_data_into_image(image_path, payload, output_path=stego_path)
        stego_images.append(saved_path)
        print_colored(f"✅ Share {i} embedded into: {saved_path}", Colors.SUCCESS)
    
    print_colored(f"\n🎉 Encryption complete! Created {len(stego_images)} stego images.", Colors.SUCCESS, Colors.BOLD)
    print_colored("💡 You need at least 2 of these images to decrypt your password.", Colors.INFO)
    
    return stego_images, master_password

def wrap_share_payload(share_bytes, index, total, threshold, packaged_cipher):
    """Wrap share payload with metadata"""
    SHARE_MAGIC = b"FKSS01"
    SHARE_VERSION = 1
    
    header = bytearray()
    header += SHARE_MAGIC
    header.append(SHARE_VERSION & 0xFF)
    header.append(index & 0xFF)
    header.append(total & 0xFF)
    header.append(threshold & 0xFF)
    header += len(share_bytes).to_bytes(4, 'big')
    header += len(packaged_cipher).to_bytes(4, 'big')
    return bytes(header) + share_bytes + packaged_cipher

def parse_share_payload(payload):
    """Parse wrapped share payload"""
    SHARE_MAGIC = b"FKSS01"
    SHARE_MAGIC_LEN = len(SHARE_MAGIC)
    
    min_header = SHARE_MAGIC_LEN + 1 + 1 + 1 + 1 + 4 + 4
    if len(payload) < min_header:
        raise ValueError("Share payload too short")
    if payload[:SHARE_MAGIC_LEN] != SHARE_MAGIC:
        raise ValueError("Share magic mismatch")
        
    pos = SHARE_MAGIC_LEN
    version = payload[pos]; pos += 1
    index = payload[pos]; pos += 1
    total = payload[pos]; pos += 1
    threshold = payload[pos]; pos += 1
    share_len = int.from_bytes(payload[pos:pos+4], 'big'); pos += 4
    packaged_cipher_len = int.from_bytes(payload[pos:pos+4], 'big'); pos += 4
    
    if pos + share_len + packaged_cipher_len > len(payload):
        raise ValueError("Declared sizes exceed payload size")
        
    share_bytes = payload[pos:pos+share_len]; pos += share_len
    packaged_cipher = payload[pos:pos+packaged_cipher_len]
    
    return {
        "version": version,
        "index": index,
        "total": total,
        "threshold": threshold,
        "share_len": share_len,
        "packaged_cipher_len": packaged_cipher_len,
        "share_bytes": share_bytes,
        "packaged_cipher": packaged_cipher
    }

def demo_decryption(stego_images, master_password):
    """Demonstrate decryption process"""
    print_colored("\n" + "="*60, Colors.INFO)
    print_colored("🔓 FRACTURED KEYS DEMO - DECRYPTION", Colors.INFO, Colors.BOLD)
    print_colored("="*60, Colors.INFO)
    
    print_colored(f"Using {len(stego_images)} stego images for decryption", Colors.INFO)
    print_colored(f"Master password: {master_password}", Colors.INFO)
    
    # Step 1: Extract share payloads
    print_colored("\n📁 Step 1: Extracting data from stego images...", Colors.INFO)
    parsed_shares = []
    
    for i, image_path in enumerate(stego_images, 1):
        print_colored(f"Extracting from: {image_path}", Colors.INFO)
        payload = extract_data_from_image(image_path)
        meta = parse_share_payload(payload)
        parsed_shares.append(meta)
        print_colored(f"Found share {meta['index']}/{meta['total']} (threshold={meta['threshold']})", Colors.SUCCESS)
    
    # Step 2: Validate shares
    print_colored("\n🔍 Step 2: Validating shares...", Colors.INFO)
    if len(parsed_shares) < 2:
        print_colored("❌ Not enough shares found", Colors.ERROR)
        return
    
    # Check compatibility
    vs = {s['version'] for s in parsed_shares}
    totals = {s['total'] for s in parsed_shares}
    thresholds = {s['threshold'] for s in parsed_shares}
    pkg_hashes = {s['packaged_cipher'] for s in parsed_shares}
    
    if len(vs) != 1 or len(totals) != 1 or len(thresholds) != 1 or len(pkg_hashes) != 1:
        print_colored("❌ Shares are not compatible", Colors.ERROR)
        return
    
    threshold = parsed_shares[0]['threshold']
    if len(parsed_shares) < threshold:
        print_colored(f"❌ Need at least {threshold} shares", Colors.ERROR)
        return
    
    print_colored("✅ All shares are valid and compatible", Colors.SUCCESS)
    
    # Step 3: Recover ephemeral key
    print_colored("\n🔑 Step 3: Recovering ephemeral key from shares...", Colors.INFO)
    share_bytes_list = [s['share_bytes'] for s in parsed_shares[:threshold]]
    packaged_cipher = parsed_shares[0]['packaged_cipher']
    
    recovered_k2 = recover_bytes_from_shares(share_bytes_list)
    if len(recovered_k2) < 16:
        recovered_k2 = (b'\x00' * (16 - len(recovered_k2))) + recovered_k2
    elif len(recovered_k2) > 16:
        recovered_k2 = recovered_k2[-16:]
    
    print_colored("✅ Ephemeral key recovered successfully", Colors.SUCCESS)
    
    # Step 4: Decrypt packaged cipher
    print_colored("\n📦 Step 4: Decrypting packaged data...", Colors.INFO)
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    aes = AESGCM(recovered_k2)
    nonce2 = packaged_cipher[:12]
    ct_and_tag = packaged_cipher[12:]
    binary_blob = aes.decrypt(nonce2, ct_and_tag, None)
    print_colored("✅ Packaged data decrypted successfully", Colors.SUCCESS)
    
    # Step 5: Parse binary blob
    print_colored("\n🔍 Step 5: Parsing binary blob...", Colors.INFO)
    salt = binary_blob[:16]
    nonce = binary_blob[16:28]
    ciphertext_with_tag = binary_blob[28:]
    print_colored("✅ Binary blob parsed successfully", Colors.SUCCESS)
    
    # Step 6: Decrypt with master password
    print_colored("\n🔐 Step 6: Decrypting with master password...", Colors.INFO)
    plaintext = decrypt_password_aes_gcm(salt, nonce, ciphertext_with_tag, master_password)
    
    print_colored("\n🎉 DECRYPTION SUCCESSFUL!", Colors.SUCCESS, Colors.BOLD)
    print_colored(f"🔑 Decrypted password: {plaintext}", Colors.RESULT, Colors.BOLD)
    print_colored(f"📏 Password length: {len(plaintext)} characters", Colors.SUCCESS)

def cleanup_demo_files():
    """Clean up demo files"""
    print_colored("\n🧹 Cleaning up demo files...", Colors.INFO)
    
    files_to_remove = [
        "demo_image_1.png", "demo_image_2.png", "demo_image_3.png",
        "stego_share_1.png", "stego_share_2.png", "stego_share_3.png"
    ]
    
    for filename in files_to_remove:
        if os.path.exists(filename):
            os.remove(filename)
            print_colored(f"Removed: {filename}", Colors.SUCCESS)

def main():
    """Main demo function"""
    print_colored("🔐 FRACTURED KEYS - COMPLETE DEMO", Colors.INFO, Colors.BOLD)
    print_colored("This demo shows the complete encryption and decryption workflow", Colors.INFO)
    
    try:
        # Run encryption demo
        stego_images, master_password = demo_encryption()
        
        # Run decryption demo
        demo_decryption(stego_images, master_password)
        
        print_colored("\n" + "="*60, Colors.SUCCESS)
        print_colored("🎉 DEMO COMPLETED SUCCESSFULLY!", Colors.SUCCESS, Colors.BOLD)
        print_colored("="*60, Colors.SUCCESS)
        
    except Exception as e:
        print_colored(f"\n❌ Demo failed: {e}", Colors.ERROR)
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        cleanup_demo_files()
        print_colored("\n✨ Demo finished. All temporary files cleaned up.", Colors.INFO)

if __name__ == "__main__":
    main()
