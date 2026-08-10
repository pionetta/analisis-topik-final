import os
import re

def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = "".join([c*2 for c in hex_str])
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def to_grayscale_hex(hex_str):
    try:
        r, g, b = hex_to_rgb(hex_str)
        # Using luminance formula
        gray = int(0.299*r + 0.587*g + 0.114*b)
        return rgb_to_hex(gray, gray, gray)
    except:
        return hex_str

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all hex colors
    def replacer(match):
        original = match.group(0)
        return to_grayscale_hex(original)

    new_content = re.sub(r'#[0-9a-fA-F]{3,6}\b', replacer, content)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}")

def main():
    src_dir = r"c:\Users\hp\OneDrive\Documents\Arstywn\Aplikasi\Analisis Topik 6\frontend\src"
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.jsx'):
                process_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
