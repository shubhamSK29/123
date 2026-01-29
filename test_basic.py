#!/usr/bin/env python3
"""
Basic test script to verify Fractured Keys functionality
"""

import sys
import os
import tempfile
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from colors import print_colored, Colors
        print("✅ colors module imported")
        
        from crypto import encrypt_password_aes_gcm, decrypt_password_aes_gcm
        print("✅ crypto module imported")
        
        from sss import split_bytes_into_shares, recover_bytes_from_shares
        print("✅ sss module imported")
        
        from steganography import embed_data_into_image, extract_data_from_image
        print("✅ steganography module imported")
        
        from file_utils import create_file_chooser
        print("✅ file_utils module imported")
        
        from encryption import encryption_mode
        print("✅ encryption module imported")
        
        from decryption import decryption_mode, decryption_mode_manual
        print("✅ decryption module imported")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_crypto():
    """Test basic crypto functionality"""
    print("\n🔐 Testing crypto functionality...")
    
    try:
        from crypto import encrypt_password_aes_gcm, decrypt_password_aes_gcm
        
        password = "test_password_123"
        master_password = "master_password_456"
        
        # Encrypt
        salt, nonce, ciphertext_with_tag = encrypt_password_aes_gcm(password, master_password)
        print("✅ Encryption successful")
        
        # Decrypt
        decrypted = decrypt_password_aes_gcm(salt, nonce, ciphertext_with_tag, master_password)
        print("✅ Decryption successful")
        
        if decrypted == password:
            print("✅ Password matches original")
            return True
        else:
            print("❌ Password mismatch")
            return False
            
    except Exception as e:
        print(f"❌ Crypto test failed: {e}")
        return False

def test_sss():
    """Test Shamir Secret Sharing"""
    print("\n📊 Testing Shamir Secret Sharing...")
    
    try:
        from sss import split_bytes_into_shares, recover_bytes_from_shares
        
        secret = b"test_secret_16b"  # Exactly 16 bytes
        n_shares = 3
        threshold = 2
        
        # Split into shares
        shares = split_bytes_into_shares(secret, n=n_shares, k=threshold)
        print(f"✅ Created {len(shares)} shares")
        
        # Recover from first 2 shares
        recovered = recover_bytes_from_shares(shares[:2])
        print("✅ Recovery successful")
        
        if recovered == secret:
            print("✅ Secret matches original")
            return True
        else:
            print("❌ Secret mismatch")
            return False
            
    except Exception as e:
        print(f"❌ SSS test failed: {e}")
        return False

def test_steganography():
    """Test steganography with a simple image"""
    print("\n🖼️ Testing steganography...")
    
    try:
        from PIL import Image
        from steganography import embed_data_into_image, extract_data_from_image
        
        # Create a simple test image
        test_data = b"Hello, Fractured Keys!"
        
        # Create a small test image
        img = Image.new('RGB', (100, 100), color='white')
        test_image_path = "test_image.png"
        img.save(test_image_path)
        
        # Embed data
        stego_path = embed_data_into_image(test_image_path, test_data)
        print("✅ Data embedded successfully")
        
        # Extract data
        extracted = extract_data_from_image(stego_path)
        print("✅ Data extracted successfully")
        
        if extracted == test_data:
            print("✅ Extracted data matches original")
            result = True
        else:
            print("❌ Extracted data mismatch")
            result = False
        
        # Cleanup
        os.remove(test_image_path)
        os.remove(stego_path)
        
        return result
        
    except Exception as e:
        print(f"❌ Steganography test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Fractured Keys - Basic Functionality Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_crypto,
        test_sss,
        test_steganography
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Fractured Keys is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
