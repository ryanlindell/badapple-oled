import os
from PIL import Image

def compress_frame_rle(image_path):
    img = Image.open(image_path).convert('1') # Convert to 1-bit
    pixels = list(img.getdata()) # Get flat list of 4096 pixels (128x32)
    
    rle_data = []
    if not pixels:
        return rle_data

    current_color = pixels[0]
    count = 0
    
    for pixel in pixels:
        # If color matches and count < 127, keep counting
        if pixel == current_color and count < 127:
            count += 1
        else:
            # Pack color into the highest bit (bit 7) and count into bits 0-6
            # 0xFF becomes 1 (White) or 0 (Black)
            color_bit = 0x80 if current_color > 0 else 0x00
            rle_data.append(color_bit | count)
            
            # Reset for next run
            current_color = pixel
            count = 1
            
    # Catch the last run
    color_bit = 0x80 if current_color > 0 else 0x00
    rle_data.append(color_bit | count)
    
    return rle_data

def main():
    folder = "." # Assumes script is in the frames folder
    files = sorted([f for f in os.listdir(folder) if f.endswith('.png')])
    
    with open("bad_apple_rle.h", "w") as f:
        f.write("#include <pgmspace.h>\n\n")
        f.write("const uint8_t bad_apple_rle[] PROGMEM = {\n")
        
        frame_offsets = []
        total_bytes = 0
        
        for i, filename in enumerate(files):
            frame_data = compress_frame_rle(os.path.join(folder, filename))
            
            # Record where this frame starts so the ESP32 can find it
            frame_offsets.append(total_bytes)
            total_bytes += len(frame_data)
            
            # Write hex data
            hex_strings = [f"0x{b:02x}" for b in frame_data]
            f.write(", ".join(hex_strings) + ",\n")
            
            if i % 500 == 0:
                print(f"Compressed {i} / {len(files)} frames...")

        f.write("};\n\n")
        
        # Write the offset table so we can jump to specific frames
        f.write(f"const uint32_t frame_offsets[{len(frame_offsets)}] PROGMEM = {{\n")
        f.write(", ".join(map(str, frame_offsets)))
        f.write("\n};\n")
        
        print(f"Done! Total size: {total_bytes} bytes.")
        print(f"Original size would have been: {len(files) * 512} bytes.")

if __name__ == "__main__":
    main()