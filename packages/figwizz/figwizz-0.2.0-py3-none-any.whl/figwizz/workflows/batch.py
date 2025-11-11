"""
Batch processing utilities for multiple files
"""

from pathlib import Path
from tqdm import tqdm


def batch_convert_images(input_dir, target_format, output_dir=None, **kwargs):
    """
    Convert all images in a directory to a target format.
    
    Args:
        input_dir: Directory containing images
        target_format: Target format (e.g., 'jpg', 'png')
        output_dir: Output directory (uses input_dir if None)
        **kwargs: Additional arguments passed to convert_image
    
    Returns:
        List of converted image paths
    """
    from ..convert import convert_image
    
    input_path = Path(input_dir)
    output_path = Path(output_dir) if output_dir else input_path
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all image files
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp', '*.tiff']
    image_files = []
    for ext in image_extensions:
        image_files.extend(input_path.glob(ext))
    
    converted = []
    for img_path in tqdm(image_files, desc="Converting images"):
        try:
            result = convert_image(str(img_path), target_format, **kwargs)
            converted.append(result)
        except Exception as e:
            print(f"Failed to convert {img_path}: {e}")
    
    return converted


def batch_create_hexicons(input_dir, output_dir, **kwargs):
    """
    Create hexicons for all images in a directory.
    
    Args:
        input_dir: Directory containing images
        output_dir: Output directory for hexicons
        **kwargs: Additional arguments passed to make_hexicon
    
    Returns:
        List of hexicon paths
    """
    from ..workflows.icons import make_hexicon
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all image files
    image_extensions = ['*.png', '*.jpg', '*.jpeg']
    image_files = []
    for ext in image_extensions:
        image_files.extend(input_path.glob(ext))
    
    hexicons = []
    for img_path in tqdm(image_files, desc="Creating hexicons"):
        try:
            hexicon = make_hexicon(str(img_path), **kwargs)
            output_file = output_path / img_path.name
            hexicon.save(output_file)
            hexicons.append(str(output_file))
        except Exception as e:
            print(f"Failed to create hexicon for {img_path}: {e}")
    
    return hexicons


def batch_process_images(input_dir, process_func, output_dir=None, **kwargs):
    """
    Apply a processing function to all images in a directory.
    
    Args:
        input_dir: Directory containing images
        process_func: Function that takes an image and returns processed image
        output_dir: Output directory (uses input_dir if None)
        **kwargs: Additional arguments passed to process_func
    
    Returns:
        List of processed image paths
    """
    from ..utils.images import normalize_image_input, save_image
    
    input_path = Path(input_dir)
    output_path = Path(output_dir) if output_dir else input_path
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all image files
    image_extensions = ['*.png', '*.jpg', '*.jpeg']
    image_files = []
    for ext in image_extensions:
        image_files.extend(input_path.glob(ext))
    
    processed = []
    for img_path in tqdm(image_files, desc="Processing images"):
        try:
            img = normalize_image_input(str(img_path))
            result_img = process_func(img, **kwargs)
            output_file = output_path / img_path.name
            save_image(result_img, str(output_file))
            processed.append(str(output_file))
        except Exception as e:
            print(f"Failed to process {img_path}: {e}")
    
    return processed

