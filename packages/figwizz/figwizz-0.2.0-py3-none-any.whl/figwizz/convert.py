"""
Image format conversion utilities.

This module provides functions for converting images between different formats,
handling various input types (paths, bytes, PIL Images, etc.), and processing
SVG files.

Example:
    ```python
    from figwizz.convert import convert_image
    convert_image('input.png', 'jpg')
    # Returns: 'input.jpg'
    ```
"""

import os, base64
from PIL import Image
from io import BytesIO

from .modify import make_image_opaque
from .utils.images import normalize_image_input, save_image

__all__ = [
    'convert_image', 
    'bytes_to_image',
    'svg_to_image',
    'process_images']

# Input / Image Conversion ----------------------------------------

def convert_image(source_path, target_format, delete_original=False):
    """Convert an image file to another format.
    
    Args:
        source_path: Path to the source image file, or any supported image input type.
        target_format: Target format to convert to (e.g., 'jpg', 'png', 'pdf').
        delete_original: Whether to remove the original file. Defaults to False.
            Only applies if source_path is a file path string.
            
    Returns:
        str: Path to the converted image file.
    """
    # Normalize input to PIL Image
    img = normalize_image_input(source_path)
    
    # Ensure the target format does not start with a dot
    if target_format.startswith('.'):
        target_format = target_format[1:]
    
    # Determine output path
    if isinstance(source_path, str) and not source_path.startswith(('http://', 'https://', 'data:')):
        base = os.path.splitext(source_path)[0]
        target_path = f"{base}.{target_format.lower()}"
    else:
        # For non-path inputs, use a temp name
        target_path = f"converted_image.{target_format.lower()}"
    
    # Use unified save_image function
    result_path = save_image(img, target_path, format=target_format.upper())
    
    # Delete original if requested and it's a file path
    if delete_original and isinstance(source_path, str):
        if os.path.exists(source_path):
            os.remove(source_path)

    return result_path

def bytes_to_image(bytes_input):
    """Convert bytes to a PIL Image object.
    
    Args:
        bytes_input: Bytes input to convert to an image.
    
    Returns:
        PIL Image object.
    """
    # check bytes type (e.g. base64, bytes, etc.)
    if isinstance(bytes_input, str):
        bytes_input = base64.b64decode(bytes_input)
    elif isinstance(bytes_input, bytes):
        pass
    else: # raise error for invalid bytes input
        raise ValueError(f"Invalid bytes input: {type(bytes_input)}")
    
    # convert bytes to image
    return Image.open(BytesIO(bytes_input))

def svg_to_image(svg_content, output_path,
                 width=None, height=None, scale=None):
    """
    Convert SVG content to a raster image.
    
    Args:
        svg_content: Raw SVG file content (bytes)
        output_path: Path to save the output file
           (output type inferred from output_path)
        width: Optional width for output PNG (in pixels)
        height: Optional height for output PNG (in pixels)
        scale: Optional scale factor (e.g., 2.0 for 2x resolution)
    
    Returns:
        True if successful, False otherwise
    """
    
    if output_path.split('.')[-1] not in ['png', 'jpg', 'jpeg', 'pdf']:
        raise ValueError(f"Invalid output path: {output_path}. ",
                         "Output path must end with .png, .jpg, .jpeg, or .pdf.")
        
    output_ext = output_path.split('.')[-1]
    
    try:
        import cairosvg  # type: ignore
    except ImportError:
        print("  Warning: cairosvg not installed, cannot convert SVG to PNG")
        print("  Install with: pip install cairosvg")
        return False
    
    try:
        print('  Converting SVG to {output_ext.upper()}...')
        cairosvg.svg2png(
            bytestring=svg_content,
            write_to=str(output_path),
            output_width=width,
            output_height=height,
            scale=scale
        )
        return True
    except Exception as e:
        print(f"  Error converting SVG to {output_ext.upper()}: {e}")
        return False

# Batch Processing ------------------------------------------------

def _process_image_path(image_path):
    """Process an image path to a PIL Image object.
    
    Args:
        image_path: Path to the image file.
    """
    return Image.open(image_path)

def _process_image_bytes(image_bytes):
    """Process image bytes to a PIL Image object.
    
    Args:
        image_bytes: Bytes of the image.
    """
    return bytes_to_image(image_bytes)

def _process_image_pil(image):
    """Process a PIL Image object.
    
    Args:
        image: PIL Image object.
    """
    return image

def _process_image_list(images):
    """Process a list of images to a list of PIL Image objects.
    
    Args:
        images: List of images.
    """
    return [_process_image_pil(image) for image in images]

def process_images(images, target_format, **kwargs):
    """Process an image to a target format.
    
    Args:
        image: PIL image object, path, bytes, or list thereof.
        target_format: Target format to convert to (e.g., 'jpg', 'png', 'pdf').
        **kwargs: Additional keyword arguments.
    """
    # TODO: Implement this function. Default output format should be a PIL Image object.
    # Check if images is a list or single image
    raise NotImplementedError("process_images is not implemented yet.")