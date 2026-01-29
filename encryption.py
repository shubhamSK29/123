# encryption.py
import os
import base64
import getpass
from colors import print_colored, Colors
from crypto import encrypt_password_aes_gcm
from file_utils import create_file_chooser, save_binary_file_manual
from steganography import embed_data_into_image
from sss import split_bytes_into_shares
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Share wrapper metadata
SHARE_MAGIC = b"FKSS01"   # 6 bytes
SHARE_VERSION = 1

def _wrap_share_payload(share_bytes: bytes, index: int, total: int, threshold: int,
                        packaged_cipher: bytes) -> bytes:
    """
    Build binary payload for embedding containing:
    SHARE_MAGIC (6) | version (1) | index (1) | total (1) | threshold (1)
      | share_len (4 BE) | packaged_cipher_len (4 BE) | share_bytes | packaged_cipher_bytes
    """
    if not isinstance(share_bytes, (bytes, bytearray)):
        raise TypeError("share_bytes must be bytes")
    if not isinstance(packaged_cipher, (bytes, bytearray)):
        raise TypeError("packaged_cipher must be bytes")

    header = bytearray()
    header += SHARE_MAGIC
    header.append(SHARE_VERSION & 0xFF)
    header.append(index & 0xFF)
    header.append(total & 0xFF)
    header.append(threshold & 0xFF)
    header += len(share_bytes).to_bytes(4, 'big')
    header += len(packaged_cipher).to_bytes(4, 'big')
    return bytes(header) + share_bytes + packaged_cipher

def encryption_mode():
    print_colored("\n--- ENCRYPTION MODE (SSS shares -> images) ---", Colors.INFO, Colors.BOLD)
    password = getpass.getpass("Enter the password to encrypt: ").strip()
    if not password:
        print_colored("Password cannot be empty.", Colors.ERROR)
        return

    master_password = getpass.getpass("Enter master password for encryption: ").strip()
    if not master_password:
        print_colored("Master password cannot be empty.", Colors.ERROR)
        return

    try:
        print_colored("Encrypting (master password) ...", Colors.INFO)
        salt, nonce, ciphertext_with_tag = encrypt_password_aes_gcm(password, master_password)

        # show to user
        ciphertext = ciphertext_with_tag[:-16]
        auth_tag = ciphertext_with_tag[-16:]
        print_colored("\n--- ENCRYPTION RESULTS (master) ---", Colors.INFO, Colors.BOLD)
        print_colored(f"Salt (base64): {base64.b64encode(salt).decode()}", Colors.SALT)
        print_colored(f"Nonce (base64): {base64.b64encode(nonce).decode()}", Colors.NONCE)
        print_colored(f"Ciphertext (base64): {base64.b64encode(ciphertext).decode()}", Colors.CIPHERTEXT)
        print_colored(f"Auth Tag (base64): {base64.b64encode(auth_tag).decode()}", Colors.AUTH_TAG)

        binary_blob = salt + nonce + ciphertext_with_tag  # master-encrypted blob

        # Ask whether to split into shares + embed
        do_shares = input("\nSplit into 3 SSS shares (threshold 2) and embed into 3 images? (Y/n): ").strip().lower()
        if do_shares == 'n':
            # fallback: save raw binary
            filename = input("Enter filename for binary export (default: encrypted_output.bin): ").strip() or "encrypted_output.bin"
            if not filename.lower().endswith(".bin"):
                filename += ".bin"
            save_binary_file_manual(filename, binary_blob)
            return

        # Now: generate a random 16-byte session key K2, encrypt binary_blob with K2,
        # split K2 into SSS shares (three shares, threshold 2), then embed each share along with the packaged_cipher
        print_colored("Generating ephemeral key and encrypting binary blob (packaging)...", Colors.INFO)
        K2 = os.urandom(16)  # 16-byte key (fits PyCryptodome Shamir)
        aes = AESGCM(K2)
        nonce2 = os.urandom(12)
        packaged_ct_and_tag = aes.encrypt(nonce2, binary_blob, None)  # ciphertext + tag
        packaged_cipher = nonce2 + packaged_ct_and_tag  # we'll store this in each image

        # Split K2 into shares
        n_shares = 3
        threshold = 2
        print_colored("Splitting ephemeral key into SSS shares...", Colors.INFO)
        shares = split_bytes_into_shares(K2, n=n_shares, k=threshold)  # list of bytes (index_byte + share_payload)

        # For each share ask user to pick a carrier image, embed, and optionally choose output filename
        for i, share_bytes in enumerate(shares, start=1):
            print_colored(f"\nSelect carrier image for share {i}/{n_shares}", Colors.INFO)
            file_types = [("Images", ("*.png","*.jpg","*.jpeg","*.bmp","*.tiff")), ("All files", "*.*")]
            carrier_path = create_file_chooser(f"Select carrier image for share {i}", file_types, mode="open")
            if not carrier_path:
                print_colored("No carrier selected. Aborting share embedding.", Colors.ERROR)
                return

            # wrap share with metadata (include packaged_cipher duplicated in each share)
            payload = _wrap_share_payload(share_bytes, index=i, total=n_shares, threshold=threshold, packaged_cipher=packaged_cipher)

            # ask output
            choose_output = input(f"Choose output filename for stego image for share {i}? (Y/n): ").strip().lower()
            if choose_output == 'n':
                output_path = None
            else:
                out_types = [("PNG image", "*.png"), ("All files", "*.*")]
                output_path = create_file_chooser(f"Save stego image for share {i} as", out_types, mode="save")
                if not output_path:
                    output_path = None

            try:
                saved_path = embed_data_into_image(carrier_path, payload, output_path=output_path)
                print_colored(f"✓ Share {i} embedded into {saved_path}", Colors.SUCCESS)
            except Exception as e:
                print_colored(f"Steganography embedding failed for share {i}: {e}", Colors.ERROR)
                # Offer to save raw share as a fallback
                fb = input("Save this share as a raw .share file instead? (y/N): ").strip().lower()
                if fb == 'y':
                    fn = input("Enter filename (default: share.bin): ").strip() or f"share_{i}.bin"
                    with open(fn, "wb") as fw:
                        fw.write(payload)
                    print_colored(f"Saved share payload to {fn}", Colors.SUCCESS)

        print_colored("\nAll shares processed. Keep at least two of the stego images safe to reconstruct.", Colors.INFO)

    except Exception as e:
        print_colored(f"Encryption failed: {e}", Colors.ERROR)

