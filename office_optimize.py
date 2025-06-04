import zipfile
import os
import shutil
from PIL import Image

def optimize_office_images(input_path, output_path, quality=75):
    """
    Optimizes images inside .docx, .pptx, or .xlsx files by recompressing images in the media folder.
    Args:
        input_path: Path to the input Office file
        output_path: Path to save the optimized Office file
        quality: JPEG/WebP quality for recompression (default: 75)
    """
    ext_map = {
        '.docx': ('word/media',),
        '.pptx': ('ppt/media',),
        '.xlsx': ('xl/media',)
    }
    ext = os.path.splitext(input_path)[1].lower()
    if ext not in ext_map:
        raise ValueError('Unsupported Office format for optimization')
    temp_dir = f"_office_opt_temp_{os.getpid()}"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    # Extract all
    with zipfile.ZipFile(input_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    # Optimize images in media folder(s)
    optimized = False
    for media_folder in ext_map[ext]:
        media_path = os.path.join(temp_dir, media_folder)
        if os.path.exists(media_path):
            for fname in os.listdir(media_path):
                fpath = os.path.join(media_path, fname)
                try:
                    img = Image.open(fpath)
                    # Convert PNG to JPEG if size drops, else recompress as original
                    if img.format == 'PNG':
                        img = img.convert('RGB')
                        jpeg_path = fpath + '.jpg'
                        img.save(jpeg_path, 'JPEG', quality=quality, optimize=True)
                        if os.path.getsize(jpeg_path) < os.path.getsize(fpath):
                            os.replace(jpeg_path, fpath)
                            optimized = True
                        else:
                            os.remove(jpeg_path)
                    else:
                        img.save(fpath, img.format, quality=quality, optimize=True)
                        optimized = True
                except Exception:
                    continue
    # Repack zip
    shutil.make_archive(temp_dir, 'zip', temp_dir)
    shutil.move(f"{temp_dir}.zip", output_path)
    shutil.rmtree(temp_dir)
    return optimized
