import os
import argparse
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def load_text(script_name):
    md_file = f"{script_name}_md.md"
    if os.path.exists(md_file):
        with open(md_file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            if lines:
                return lines
    return ["नमस्ते"]  # fallback text

def get_font(script_name, size=48):
    if script_name.lower() == "devanagari":
        font_path = "Nirmala.ttc"
    elif script_name.lower() == "modi":
        font_path = "NotoSansModi-Regular.ttf"
    elif script_name.lower() == "sharada":
        font_path = "NotoSansSharada-Regular.ttf"
    else:
        raise ValueError("Unknown script name")

    try:
        return ImageFont.truetype(font_path, size)
    except Exception as e:
        print(f"⚠️ Could not load {font_path}, using default font. Error: {e}")
        return ImageFont.load_default()

def get_background():
    textures = [
        "backgrounds/palm_leaf.jpg",
        "backgrounds/aged_paper.jpg",
        "backgrounds/parchment.jpg"
    ]
    bg_path = random.choice(textures)
    bg = Image.open(bg_path).convert("RGB")
    return bg.resize((2500, 800))

def generate_images(script_name, num_images=100, lines_per_image=5):
    text_lines = load_text(script_name)
    font = get_font(script_name)

    base_dir = os.path.join("data", script_name.lower())
    train_dir = os.path.join(base_dir, "train")
    val_dir = os.path.join(base_dir, "val")
    test_dir = os.path.join(base_dir, "test")

    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(val_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)

    total_lines = len(text_lines)
    chunk_size = max(1, total_lines // num_images)

    for i in range(num_images):
        img = get_background()
        draw = ImageDraw.Draw(img)

        start = i * chunk_size
        end = min(start + lines_per_image, total_lines)
        chosen_lines = text_lines[start:end] or ["नमस्ते"]

        y = 50
        ink_colors = [(0,0,0), (50,30,20), (80,80,80)]  # black, brown, faded
        for line in chosen_lines:
            draw.text(
                (50+random.randint(-10,10), y+random.randint(-5,5)),
                line,
                font=font,
                fill=random.choice(ink_colors)
            )
            y += 80

        # ✅ Add artifacts
        if random.random() < 0.3:
            img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5,1.5)))
        if random.random() < 0.2:
            img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150))

        # ✅ Split: 85 train, 10 val, 5 test
        if i < 85:
            folder = train_dir
        elif i < 95:
            folder = val_dir
        else:
            folder = test_dir

        img.save(os.path.join(folder, f"image_{i+1}.png"))
        with open(os.path.join(folder, f"image_{i+1}.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(chosen_lines))

        print(f"Generated image {i+1}/{num_images} → saved in {folder}")

    print(f"✅ Finished generating {num_images} images for {script_name} with train/val/test split")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synthetic Manuscript Generator")
    parser.add_argument("--script", type=str, required=True,
                        help="Script name: devanagari, modi, sharada")
    args = parser.parse_args()

    generate_images(args.script)
