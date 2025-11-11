# __name__ = "figwizz"

import os

from . import modify
from . import convert
from . import scrape
from . import stitchkit
from . import webkit

from .convert import (
    convert_image,
    bytes_to_image,
)

from .modify import (
    make_image_opaque,
)

from .display import (
    make_image_grid,
)

from .generate import (
    generate_images,
)

from .stitchkit import (
    slides_to_images,
    convert_to_pdf,
    convert_images_to_pdf,
    mogrify_images_to_pdf,
)

from .scrape import (
    download_pdf_from_url,
    download_stock_images,
    extract_images_from_pdf,
    extract_images_from_url,
)

from .webkit import (
    convert_response_to_dict,
)

from .workflows import (
    make_hexicon,
)

from .utils.environ import (
    auto_load_env,
    check_capabilities,
)

# Automatically load environment variables on import
# Check FIGWIZZ_VERBOSE env var to control verbosity
_verbose = os.getenv('FIGWIZZ_VERBOSE', '').lower() in ('1', 'true', 'yes')
_capabilities = auto_load_env(verbose=_verbose, silent_on_missing=True)

__all__ = [
    # submodules
    "modify",
    "convert",
    "scrape",
    "stitchkit",
    "webkit",
    
    # image conversion
    "convert_image",
    "bytes_to_image",
    
    # image modification
    "make_image_opaque",
    
    # image generation
    "generate_images",
    
    # image stitching
    "make_image_grid",
    "slides_to_images",
    "convert_to_pdf",
    "convert_images_to_pdf",
    "mogrify_images_to_pdf",
    
    # handle requests
    "convert_response_to_dict",
    
    # scrape images from the web
    "download_pdf_from_url",
    "download_stock_images",
    "extract_images_from_pdf",
    "extract_images_from_url",
    
    # figwizz workflows
    "make_hexicon",
    
    # environment utilities
    "auto_load_env",
    "check_capabilities",
]

def package_info():
    """
    Return the import path and first line of the docstring for each submodule.
    """
    info = []
    for submodule in __all__:
        if submodule.startswith('__'):
            continue
        module = __import__(submodule, fromlist=[None])
        docstring = module.__doc__.split('\n')[0]
        info.append(f"{submodule}: {docstring}")
    return info