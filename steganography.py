# steganography.py
from PIL import Image
from colors import print_colored, Colors

MAGIC = b"FKSV1"   # 5 bytes
MAGIC_LEN = len(MAGIC)

def _bits_from_bytes(data: bytes):
    for byte in data:
        for i in range(7, -1, -1):
            yield (byte >> i) & 1

def _read_n_bytes_from_bits(bit_iter, n):
    """Read n bytes (n*8 bits) from bit iterator; raise if not enough bits."""
    out = bytearray()
    for _ in range(n):
        b = 0
        for _ in range(8):
            try:
                bit = next(bit_iter)
            except StopIteration:
                raise ValueError("Not enough bits in image while reading payload.")
            b = (b << 1) | bit
        out.append(b)
    return bytes(out)

def embed_data_into_image(image_path: str, data_bytes: bytes, output_path: str = None) -> str:
    """
    Embed data_bytes into the LSB of RGB channels of the image.
    Saves as PNG. Returns output_path.
    """
    try:
        img = Image.open(image_path)
    except Exception as e:
        raise ValueError(f"Cannot open carrier image: {e}")

    img = img.convert('RGB')  # always use 3 channels
    width, height = img.size
    capacity_bits = width * height * 3  # 3 bits per pixel
    payload = MAGIC + len(data_bytes).to_bytes(4, 'big') + data_bytes
    required_bits = len(payload) * 8

    print_colored(f"Carrier image: {image_path} ({width}x{height}, RGB)", Colors.INFO)
    print_colored(f"Payload size: {len(data_bytes)} bytes -> requires {required_bits} bits", Colors.INFO)
    print_colored(f"Image capacity: {capacity_bits} bits ({capacity_bits//8} bytes)", Colors.INFO)

    if required_bits > capacity_bits:
        raise ValueError(
            f"Carrier image too small: need {required_bits} bits ({required_bits//8} bytes). "
            f"Image capacity: {capacity_bits} bits ({capacity_bits//8} bytes)."
        )

    pixels = list(img.getdata())  # list of (R,G,B) tuples
    bit_iter = _bits_from_bytes(payload)

    new_pixels = []
    exhausted = False
    for (r, g, b) in pixels:
        new_rgb = []
        for channel in (r, g, b):
            try:
                bit = next(bit_iter)
                new_rgb.append((channel & ~1) | bit)
            except StopIteration:
                new_rgb.append(channel)
                exhausted = True
        new_pixels.append(tuple(new_rgb))
        if exhausted:
            # copy remaining pixels unchanged
            idx = len(new_pixels)
            new_pixels.extend(pixels[idx:])
            break

    out_img = Image.new('RGB', img.size)
    out_img.putdata(new_pixels)

    if output_path is None:
        # generate default filename
        base, _ = image_path.rsplit('.', 1) if '.' in image_path else (image_path, '')
        output_path = f"{base}_stego.png"

    out_img.save(output_path, format='PNG')
    print_colored(f"Stego image saved: {output_path}", Colors.SUCCESS, Colors.BOLD)
    return output_path

def extract_data_from_image(image_path: str) -> bytes:
    """
    Extract embedded data and return data_bytes (the original binary blob).
    Verifies MAGIC and reads length.
    """
    try:
        img = Image.open(image_path)
    except Exception as e:
        raise ValueError(f"Cannot open image: {e}")

    img = img.convert('RGB')
    pixels = list(img.getdata())
    bit_iter = (channel & 1 for (r, g, b) in pixels for channel in (r, g, b))

    # read magic
    header = _read_n_bytes_from_bits(bit_iter, MAGIC_LEN)
    if header != MAGIC:
        raise ValueError("Magic header mismatch - image does not appear to contain Fractured Keys payload.")

    # read length (4 bytes)
    length_bytes = _read_n_bytes_from_bits(bit_iter, 4)
    length = int.from_bytes(length_bytes, 'big')
    if length < 0:
        raise ValueError("Invalid payload length in header.")

    print_colored(f"Found payload header. Expecting {length} bytes of data.", Colors.INFO)

    data_bytes = _read_n_bytes_from_bits(bit_iter, length)
    print_colored(f"Extracted {len(data_bytes)} bytes from image.", Colors.SUCCESS)
    return data_bytes

