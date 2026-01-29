# decryption.py
import getpass
from colors import print_colored, Colors
from crypto import decrypt_password_aes_gcm
from file_utils import create_file_chooser, read_binary_file
from steganography import extract_data_from_image
from sss import recover_bytes_from_shares
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Share wrapper metadata (must match encryption)
SHARE_MAGIC = b"FKSS01"
SHARE_MAGIC_LEN = len(SHARE_MAGIC)

def _parse_share_payload(payload: bytes):
    """
    Parse wrapped share payload:
    SHARE_MAGIC (6) | version (1) | index (1) | total (1) | threshold (1)
      | share_len (4) | packaged_cipher_len (4) | share_bytes | packaged_cipher_bytes
    Returns dict with fields.
    """
    min_header = SHARE_MAGIC_LEN + 1 + 1 + 1 + 1 + 4 + 4
    if len(payload) < min_header:
        raise ValueError("Share payload too short / malformed")
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


def decryption_mode():
    print_colored("\n--- DECRYPTION MODE (SSS shares from images) ---", Colors.INFO, Colors.BOLD)
    print_colored("You must provide at least 2 stego images (shares).", Colors.INFO)

    # Gather at least 2 stego image paths from user
    selected = []
    min_required = 2
    while True:
        file_types = [("Images", ("*.png","*.jpg","*.jpeg","*.bmp","*.tiff")), ("All files", "*.*")]
        path = create_file_chooser("Select a stego image (or Cancel to finish selection)", file_types, mode="open")
        if not path:
            # if user cancels
            if len(selected) >= min_required:
                break
            else:
                print_colored("You need to select at least two stego images to continue.", Colors.WARNING)
                continue
        selected.append(path)
        print_colored(f"Selected: {path}", Colors.INFO)
        # Ask if they want to pick more or finish
        more = input("Select another share? (Y/n): ").strip().lower()
        if more == 'n':
            if len(selected) >= min_required:
                break
            else:
                print_colored("Need at least two. Continue selecting.", Colors.WARNING)

    # Extract share payloads
    parsed_shares = []
    for p in selected:
        try:
            payload = extract_data_from_image(p)
            meta = _parse_share_payload(payload)
            parsed_shares.append(meta)
            print_colored(f"Found share index {meta['index']}/{meta['total']} (threshold={meta['threshold']}) in {p}", Colors.INFO)
        except Exception as e:
            print_colored(f"Failed to parse share from {p}: {e}", Colors.ERROR)

    if len(parsed_shares) < 2:
        print_colored("Not enough valid shares found to reconstruct secret.", Colors.ERROR)
        return

    # Validate: ensure shares are compatible (same version/total/threshold and packaged_cipher)
    vs = {s['version'] for s in parsed_shares}
    totals = {s['total'] for s in parsed_shares}
    thresholds = {s['threshold'] for s in parsed_shares}
    pkg_lens = {s['packaged_cipher_len'] for s in parsed_shares}
    pkg_hashes = {s['packaged_cipher'] for s in parsed_shares}
    if len(vs) != 1 or len(totals) != 1 or len(thresholds) != 1 or len(pkg_lens) != 1 or len(pkg_hashes) != 1:
        print_colored("Selected shares do not match (version/total/threshold/packaged_cipher mismatch). Aborting.", Colors.ERROR)
        return

    threshold = parsed_shares[0]['threshold']
    if len(parsed_shares) < threshold:
        print_colored(f"Need at least {threshold} shares to reconstruct; you provided {len(parsed_shares)}.", Colors.ERROR)
        return

    # Build share list for recovery (raw share bytes as produced by sss.split)
    share_bytes_list = [s['share_bytes'] for s in parsed_shares[:threshold]]
    packaged_cipher = parsed_shares[0]['packaged_cipher']

    try:
        # recover ephemeral key K2
        recovered_k2 = recover_bytes_from_shares(share_bytes_list)
        # ensure K2 is 16 bytes (pad left if needed)
        if len(recovered_k2) < 16:
            recovered_k2 = (b'\x00' * (16 - len(recovered_k2))) + recovered_k2
        elif len(recovered_k2) > 16:
            # trim if business; ideally shouldn't happen
            recovered_k2 = recovered_k2[-16:]

        print_colored("Recovered ephemeral key from shares.", Colors.SUCCESS)

        # decrypt packaged_cipher with recovered_k2 to get binary_blob
        aes = AESGCM(recovered_k2)
        if len(packaged_cipher) < 12 + 16:
            print_colored("Packaged cipher too small to be valid.", Colors.ERROR)
            return
        nonce2 = packaged_cipher[:12]
        ct_and_tag = packaged_cipher[12:]
        binary_blob = aes.decrypt(nonce2, ct_and_tag, None)

        # Now parse binary blob -> salt(16) + nonce(12) + ciphertext_with_tag
        if len(binary_blob) < 28:
            print_colored("Reconstructed binary blob too small to be valid (need >=28 bytes).", Colors.ERROR)
            return
        salt = binary_blob[:16]
        nonce = binary_blob[16:28]
        ciphertext_with_tag = binary_blob[28:]

        master_password = getpass.getpass("Enter master password to decrypt reconstructed blob: ").strip()
        if not master_password:
            print_colored("Master password cannot be empty.", Colors.ERROR)
            return

        plaintext = decrypt_password_aes_gcm(salt, nonce, ciphertext_with_tag, master_password)
        print_colored("\n--- DECRYPTION RESULTS ---", Colors.SUCCESS, Colors.BOLD)
        print_colored(f"Decrypted password: {plaintext}", Colors.RESULT, Colors.BOLD)
        print_colored(f"Password length: {len(plaintext)} characters", Colors.SUCCESS)

    except Exception as e:
        print_colored(f"Reconstruction or decryption failed: {e}", Colors.ERROR)

def decryption_mode_manual():
    """Manual decryption for .bin files."""
    print_colored("\n--- MANUAL DECRYPTION MODE (.bin files) ---", Colors.INFO, Colors.BOLD)
    
    # Ask for .bin file path
    file_types = [("Binary files", "*.bin"), ("All files", "*.*")]
    file_path = create_file_chooser("Select .bin file for decryption", file_types, mode="open")
    if not file_path:
        print_colored("No file selected. Aborting.", Colors.WARNING)
        return
    
    try:
        # Read binary file
        with open(file_path, "rb") as f:
            binary_blob = f.read()
        
        if len(binary_blob) < 28:
            print_colored("File too small to be valid (need >=28 bytes).", Colors.ERROR)
            return
        
        # Parse binary blob: salt(16) + nonce(12) + ciphertext_with_tag
        salt = binary_blob[:16]
        nonce = binary_blob[16:28]
        ciphertext_with_tag = binary_blob[28:]
        
        master_password = getpass.getpass("Enter master password to decrypt: ").strip()
        if not master_password:
            print_colored("Master password cannot be empty.", Colors.ERROR)
            return
        
        plaintext = decrypt_password_aes_gcm(salt, nonce, ciphertext_with_tag, master_password)
        print_colored("\n--- MANUAL DECRYPTION RESULTS ---", Colors.SUCCESS, Colors.BOLD)
        print_colored(f"Decrypted password: {plaintext}", Colors.RESULT, Colors.BOLD)
        print_colored(f"Password length: {len(plaintext)} characters", Colors.SUCCESS)
        
    except Exception as e:
        print_colored(f"Manual decryption failed: {e}", Colors.ERROR)

