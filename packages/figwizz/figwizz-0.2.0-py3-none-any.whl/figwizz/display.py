"""
Image display and grid layout utilities.

This module provides functions for displaying images in matplotlib-based
grid layouts with customizable configurations.

Example:
    ```python
    from figwizz.display import make_image_grid
    images = ['img1.png', 'img2.png', 'img3.png']
    fig, axes = make_image_grid(images, titles=['A', 'B', 'C'])
    plt.show()
    ```
"""

import matplotlib.pyplot as plt
import numpy as np
from math import ceil
from .utils.images import normalize_image_input

def make_image_grid(images, titles=None, max_cols=None, show_index=False, 
                    figsize=None, title_fontsize=10, show_axes=False):
    """
    Plot a list of images in a grid layout.
    
    Args:
        images: List of images in any supported format (paths, PIL Images, bytes, etc.)
        titles: Optional list of titles for each image
        max_cols: Maximum number of columns (auto-calculated if None)
        show_index: Whether to show the index of each image
        figsize: Figure size as (width, height). Auto-calculated if None
        title_fontsize: Font size for image titles
        show_axes: Whether to show axes around images
    
    Returns:
        fig, axes: Matplotlib figure and axes objects
    """
    if not images:
        print("No images to display")
        return None, None
    
    # Normalize all images to PIL format
    images = [normalize_image_input(img) for img in images]
    
    n_images = len(images)
    
    # Calculate grid dimensions
    if max_cols is None:
        n_cols = min(4, n_images)  # Default to 4 columns max
    else:
        n_cols = min(max_cols, n_images)
    
    n_rows = ceil(n_images / n_cols)
    
    # Auto-calculate figure size if not provided
    if figsize is None:
        figsize = (n_cols * 3, n_rows * 3)
    
    # Create figure and axes
    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
    
    # Handle case of single subplot
    if n_images == 1:
        axes = np.array([axes])
    
    # Flatten axes array for easy iteration
    axes_flat = axes.flatten() if n_images > 1 else axes
    
    # Plot each image
    for idx, (ax, img) in enumerate(zip(axes_flat, images)):
        ax.imshow(img)
        
        if show_index:
            ax.text(0.02, 0.02, f'Image {idx + 1}', fontsize=8, color='black', 
                    backgroundcolor='whitesmoke', ha='center', va='top', alpha=1.0)

        if not show_axes:
            ax.axis('off')
        
        # Add title if provided
        if titles and idx < len(titles):
            ax.set_title(titles[idx], fontsize=title_fontsize)
    
    # Hide any unused subplots
    for idx in range(n_images, len(axes_flat)):
        axes_flat[idx].axis('off')
    
    plt.tight_layout()
    return fig, axes