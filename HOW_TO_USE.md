# 🔐 How to Use Fractured Keys GUI

## 🚀 Quick Start

### 1. Start the Application
```bash
python3 start_app.py
```

This will automatically:
- Check all dependencies
- Install missing packages if needed
- Start the GUI application

### 2. Alternative Start Methods
```bash
# Direct GUI launch
python3 run_gui.py

# Or run the improved GUI directly
python3 gui_improved.py
```

## 🎯 Using the GUI Interface

### 🔒 **Encryption Mode** (Default)

1. **Enter Password**: Type the password you want to encrypt
2. **Enter Master Password**: This will be used to encrypt your password
3. **Choose Options**: 
   - ✅ **Split into shares** (recommended): Creates 3 stego images
   - ❌ **Save as .bin file**: Creates a single encrypted file
4. **Click "🔒 Start Encryption"**
5. **Select Images**: Choose 3 different images to embed the shares
6. **Save Stego Images**: Choose where to save each stego image
7. **Done!**: Keep at least 2 of the 3 images safe

### 🔓 **Decryption Mode**

1. **Add Images**: Click "📁 Add Image" to select stego images
2. **Select at least 2 images** from the same encryption session
3. **Enter Master Password**: The same password you used for encryption
4. **Click "🔓 Start Decryption"**
5. **View Results**: Your decrypted password will appear in the output

### 📁 **Manual Decryption Mode**

1. **Browse for .bin file**: Select an encrypted .bin file
2. **Enter Master Password**: The password used for encryption
3. **Click "🔓 Decrypt File"**
4. **View Results**: Your decrypted password will appear

### ℹ️ **About Mode**

- View information about Fractured Keys
- Learn about the security features
- Understand how the system works

## 🖼️ **Image Requirements**

### For Carrier Images (Encryption):
- **Format**: PNG, JPG, JPEG, BMP, TIFF
- **Size**: At least 200x200 pixels (larger is better)
- **Content**: Any image will work
- **Quality**: Higher quality images work better

### For Stego Images (Decryption):
- **Must be unmodified**: Don't edit the stego images
- **Same format**: Usually PNG format
- **From same session**: All images must be from the same encryption

## 🔧 **Troubleshooting**

### GUI Won't Start
```bash
# Check dependencies
python3 test_gui.py

# Install missing packages
pip install -r requirements.txt

# Check tkinter
python3 -c "import tkinter; print('tkinter OK')"
```

### Encryption Fails
- Make sure images are large enough (200x200+ pixels)
- Check that you have write permissions
- Ensure sufficient disk space

### Decryption Fails
- Verify you're using the correct master password
- Ensure all images are from the same encryption session
- Check that images haven't been modified
- Make sure you have at least 2 images

### Import Errors
```bash
# Install all dependencies
pip install cryptography argon2-cffi Pillow colorama

# Or use the requirements file
pip install -r requirements.txt
```

## 📊 **Understanding the Output**

### Encryption Output Shows:
- **Salt**: Random data for key derivation
- **Nonce**: Random data for encryption
- **Ciphertext**: Encrypted password data
- **Auth Tag**: Authentication tag for security
- **Share Status**: Which images were created successfully

### Decryption Output Shows:
- **Extraction Status**: Data extracted from each image
- **Share Information**: Which shares were found
- **Recovery Process**: Steps in the decryption process
- **Final Result**: Your decrypted password

## 🛡️ **Security Best Practices**

1. **Strong Master Password**: Use a long, complex master password
2. **Store Images Separately**: Keep stego images in different locations
3. **Backup Strategy**: Keep at least 2 of the 3 images safe
4. **Don't Edit Images**: Never modify the stego images
5. **Secure Storage**: Store images in secure locations

## 🎨 **GUI Features**

- **Modern Design**: Clean, professional interface
- **Progress Indicators**: Real-time feedback during operations
- **Error Handling**: Clear error messages and troubleshooting
- **File Dialogs**: Easy file selection and saving
- **Status Updates**: Current operation status in the status bar
- **Responsive Layout**: Adapts to different window sizes

## 📱 **Interface Layout**

```
┌─────────────────────────────────────────┐
│ 🔐 Fractured Keys - Header              │
├─────────────────────────────────────────┤
│ [🔒 Encrypt] [🔓 Decrypt] [📁 Manual]   │
├─────────────────────────────────────────┤
│                                         │
│         Main Content Area               │
│                                         │
│  ┌─────────────┐  ┌─────────────────┐  │
│  │   Input     │  │    Output       │  │
│  │   Fields    │  │    Results      │  │
│  │             │  │                 │  │
│  └─────────────┘  └─────────────────┘  │
│                                         │
├─────────────────────────────────────────┤
│ Status: Ready                           │
└─────────────────────────────────────────┘
```

## 🆘 **Getting Help**

1. **Run Tests**: `python3 test_basic.py`
2. **Check GUI**: `python3 test_gui.py`
3. **View Demo**: `python3 demo.py`
4. **Read Documentation**: Check README_GUI.md

## 🎉 **You're Ready!**

The Fractured Keys GUI is now ready to use. Start with the encryption mode to create your first stego images, then try decryption to recover your password. The interface is designed to be intuitive and user-friendly while handling all the complex cryptography behind the scenes.

**Happy encrypting! 🔐**
