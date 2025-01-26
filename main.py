import math
import glob
from PIL import Image
import argparse

def calculate_layout(num_images):
    """Find optimal grid layout closest to a 16:9 aspect ratio"""
    best_layout = None
    min_waste = float('inf')

    for cols in range(1, num_images + 1):
        rows = math.ceil(num_images / cols)
        total_cells = cols * rows
        waste = total_cells - num_images
        
        # Prefer layouts closer to 16:9 aspect ratio
        aspect_ratio = cols / rows
        ratio_diff = abs(aspect_ratio - 16/9)
        
        # Score based on waste and aspect ratio match
        score = waste * 0.7 + ratio_diff * 0.3
        
        if score < min_waste:
            min_waste = score
            best_layout = (cols, rows)

    return best_layout

def create_collage(image_paths, max_width, max_height, output_path, quality=95):
    """Smart collage creator with automatic sizing"""
    images = []
    aspect_ratios = []
    
    # First pass: get all image dimensions
    for path in image_paths:
        try:
            with Image.open(path) as img:
                w, h = img.size
                aspect_ratios.append(w / h)
        except Exception as e:
            print(f"Skipping {path}: {e}")
            continue

    if not aspect_ratios:
        print("No valid images found!")
        return

    # Calculate median aspect ratio
    aspect_ratios.sort()
    median_aspect = aspect_ratios[len(aspect_ratios) // 2]

    # Determine thumbnail size based on median aspect
    if median_aspect > 1:  # Landscape
        thumb_width = min(800, max_width)
        thumb_height = int(thumb_width / median_aspect)
    else:  # Portrait
        thumb_height = min(600, max_height)
        thumb_width = int(thumb_height * median_aspect)

    # Second pass: process images
    for path in image_paths:
        try:
            img = Image.open(path)
            img.thumbnail((thumb_width, thumb_height), Image.Resampling.LANCZOS)
            images.append(img)
        except:
            continue

    if not images:
        print("No images to process")
        return

    # Calculate dynamic grid
    cols, rows = calculate_layout(len(images))
    
    # Calculate cell size based on largest image in batch
    max_w = max(img.width for img in images)
    max_h = max(img.height for img in images)
    
    # Create canvas
    collage_width = cols * max_w
    collage_height = rows * max_h
    collage = Image.new('RGB', (collage_width, collage_height), (255, 255, 255))

    # Paste images with smart positioning
    for i, img in enumerate(images):
        row = i // cols
        col = i % cols
        x = col * max_w + (max_w - img.width) // 2
        y = row * max_h + (max_h - img.height) // 2
        collage.paste(img, (x, y))

    collage.save(output_path, quality=quality, subsampling=0)
    print(f"Optimized collage saved to {output_path} ({collage.width}x{collage.height})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Smart Image Collage Maker')
    parser.add_argument('images', nargs='+', help='Input images/wildcards')
    parser.add_argument('--output', default='collage.jpg', help='Output filename')
    parser.add_argument('--width', type=int, default=3840, help='Max collage width')
    parser.add_argument('--height', type=int, default=2160, help='Max collage height')
    parser.add_argument('--quality', type=int, default=95, help='Output quality')
    args = parser.parse_args()

    create_collage(glob.glob(args.images[0]), args.width, args.height, args.output, args.quality)