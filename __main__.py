# __main__.py
from colors import print_colored, Colors
from encryption import encryption_mode
from decryption import decryption_mode, decryption_mode_manual

def main():
    print_colored("=== Fractured Keys — Offline Password Manager (stego) ===\n", Colors.INFO, Colors.BOLD)
    if True:
        print_colored("Color Legend:", Colors.INFO, Colors.BOLD)
        print_colored("  Salt - Green", Colors.SALT)
        print_colored("  Nonce - Blue", Colors.NONCE)
        print_colored("  Ciphertext - Red", Colors.CIPHERTEXT)
        print_colored("  Auth Tag - Magenta", Colors.AUTH_TAG)
        print()

    while True:
        print("Choose an option:")
        print("1. Encrypt a password and embed into image")
        print("2. Decrypt from stego image (file picker)")
        print("3. Manual decryption / legacy (.bin or base64)")
        print("4. Exit")
        choice = input("\nEnter your choice (1-4): ").strip()
        if choice == "1":
            encryption_mode()
        elif choice == "2":
            decryption_mode()
        elif choice == "3":
            decryption_mode_manual()
        elif choice == "4":
            print_colored("Goodbye!", Colors.SUCCESS, Colors.BOLD)
            break
        else:
            print_colored("Invalid choice! Enter 1-4.", Colors.ERROR)

        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()

