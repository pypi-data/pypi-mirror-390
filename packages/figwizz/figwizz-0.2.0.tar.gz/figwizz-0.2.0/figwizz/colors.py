"""Color processing utilities for FigWizard."""

from PIL import ImageColor
import colorsys


__all__ = ['parse_color', 'extract_dominant_color', 'get_contrasting_color']


def parse_color(color_input):
    """
    Parse color input to RGB tuple.
    
    Args:
        color_input: Hex code ('#RRGGBB'), RGB tuple (R, G, B), or color name ('red', 'blue', etc.)
    
    Returns:
        RGB tuple (R, G, B)
    
    Examples:
        ```python
        parse_color('#FF5733')
        # Returns: (255, 87, 51)
        
        parse_color((255, 87, 51))
        # Returns: (255, 87, 51)
        
        parse_color('red')
        # Returns: (255, 0, 0)
        ```
    """
    if isinstance(color_input, str):
        # Try to parse as hex or named color
        try:
            return ImageColor.getrgb(color_input)
        except ValueError:
            raise ValueError(f"Invalid color: {color_input}")
    elif isinstance(color_input, (tuple, list)) and len(color_input) == 3:
        return tuple(color_input)
    else:
        raise ValueError(f"Invalid color format: {color_input}")


def extract_dominant_color(img, num_colors=5):
    """
    Extract the dominant color from an image using color quantization.
    
    Args:
        img: PIL Image object
        num_colors: Number of colors to quantize to
    
    Returns:
        RGB tuple of the dominant color
    """
    # Resize image for faster processing
    img_small = img.copy()
    img_small.thumbnail((100, 100))
    
    # Convert to RGB if necessary
    if img_small.mode != 'RGB':
        img_small = img_small.convert('RGB')
    
    # Quantize colors
    img_quant = img_small.quantize(colors=num_colors)
    
    # Get palette and convert to RGB
    palette = img_quant.getpalette()
    
    # Count color frequency
    histogram = img_quant.histogram()
    
    # Find most frequent color (excluding first if it's white/background)
    sorted_colors = sorted(enumerate(histogram), key=lambda x: x[1], reverse=True)
    
    for idx, count in sorted_colors:
        if count > 0:
            # Get RGB values from palette
            r = palette[idx * 3]
            g = palette[idx * 3 + 1]
            b = palette[idx * 3 + 2]
            
            # Skip very light colors (likely background)
            if r + g + b < 700:  # Not pure white-ish
                return (r, g, b)
    
    # Fallback to first color
    return (palette[0], palette[1], palette[2])


def get_contrasting_color(rgb, prefer_dark=True):
    """
    Generate a contrasting color for the given RGB color.
    
    Args:
        rgb: RGB tuple (R, G, B)
        prefer_dark: If True, prefer dark contrasting colors
    
    Returns:
        RGB tuple of contrasting color
    """
    r, g, b = rgb
    
    # Calculate relative luminance
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    
    if prefer_dark:
        # If image is light, use dark border; if dark, use darker shade
        if luminance > 0.5:
            # Image is light, return dark color
            return (40, 40, 40)
        else:
            # Image is dark, return slightly darker version
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            v = max(0, v - 0.3)  # Darken
            s = min(1, s + 0.2)  # Increase saturation slightly
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            return (int(r * 255), int(g * 255), int(b * 255))
    else:
        # Return contrasting black or white
        if luminance > 0.5:
            return (0, 0, 0)
        else:
            return (255, 255, 255)

