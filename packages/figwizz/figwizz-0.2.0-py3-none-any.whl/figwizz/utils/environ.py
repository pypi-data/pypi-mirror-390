"""
Environment variable loading + checking functions
"""

import os

__all__ = [
    'load_env_variables',
    'check_capabilities',
    'auto_load_env',
]

# Environment Variable Checking Functions ----------------------------------------

def search_for_env_file(env_file='auto', max_parents=3, abspath=False):
    env_file_opts = ['.env', '.env.local', '.env.development', '.env.production']
    
    if env_file != 'auto' and env_file is not None:
        env_file_opts = [env_file if env_file.startswith('.') else f'.{env_file}']
    
    env_filepath = None
    
    for i in range(max_parents):
        for file_opt in env_file_opts:
            relative_path = os.path.join(os.getcwd(), *['..']*i, file_opt)
            if os.path.exists(relative_path):
                env_filepath = relative_path
                break
        if env_filepath is not None:
            break
    
    if env_filepath is not None:
        print(f"Found .env file at {env_filepath}")
        if abspath:
            env_filepath = os.path.abspath(env_filepath)
            
    return env_filepath # return the path to the env file
    
def load_env_variables(env_file='auto', update_environ=True, **kwargs):
    if not os.path.exists(env_file):
        env_file = search_for_env_file(env_file, **kwargs)
        if env_file is None:
            raise FileNotFoundError("No .env file found in the current or parent directories.")
    
    if env_file is not None:
       # update the environment variables with the values from the env file
       env_vars = {}
       with open(env_file, 'r') as file:
           for line_num, line in enumerate(file, 1):
               line = line.strip()
               # Skip empty lines and comments
               if not line or line.startswith('#'):
                   continue
               
               # Handle lines with '=' delimiter
               if '=' not in line:
                   print(f"Warning: Skipping malformed line {line_num} in {env_file}: {line}")
                   continue
               
               # Split on first '=' to handle values with '=' in them
               key, _, value = line.partition('=')
               key = key.strip()
               value = value.strip()
               
               # Remove quotes from value if present
               if value and value[0] in ('"', "'") and value[-1] == value[0]:
                   value = value[1:-1]
               
               # Remove inline comments (only if not in quotes)
               if '#' in value:
                   # Simple approach: split on # and take first part
                   # This won't handle # inside quotes perfectly, but is reasonable
                   value = value.split('#')[0].strip()
               
               env_vars[key] = value
               
       if not update_environ:
            return env_vars
       else: # update the global env
            os.environ.update(env_vars)
            return None

# Capability Detection Functions ----------------------------------------

# Define capability mappings
CAPABILITY_MAP = {
    'stock_image_download': {
        'pixabay': ['PIXABAY_API_KEY'],
        'unsplash': ['UNSPLASH_ACCESS_KEY'],
    },
    'genai_image_generation': {
        'openai': ['OPENAI_API_KEY'],
        'google': ['GOOGLE_API_KEY'],
        'openrouter': ['OPENROUTER_API_KEY'],
    },
}

def check_capabilities(verbose=False):
    """
    Check which capabilities are available based on environment variables.
    
    Parameters
    ----------
    verbose : bool
        If True, print detailed capability information
        
    Returns
    -------
    dict
        Dictionary mapping capability categories to available providers
    """
    capabilities = {}
    
    for capability, providers in CAPABILITY_MAP.items():
        available_providers = []
        for provider, required_keys in providers.items():
            # Check if all required keys are present and non-empty
            if all(os.getenv(key) for key in required_keys):
                available_providers.append(provider)
        
        if available_providers:
            capabilities[capability] = available_providers
    
    if verbose:
        _print_capabilities(capabilities)
    
    return capabilities

def _print_capabilities(capabilities):
    """Print formatted capability information."""
    if not capabilities:
        print("No API keys found. Basic functionality available.")
        print("Add API keys to enable additional features:")
        print("  - Stock image download (Pixabay, Unsplash)")
        print("  - AI image generation (OpenAI, Google, OpenRouter)")
        return
    
    print("Available capabilities:")
    for capability, providers in capabilities.items():
        capability_name = capability.replace('_', ' ').title()
        providers_str = ', '.join(providers)
        print(f"  - {capability_name}: {providers_str}")

def auto_load_env(verbose=False, silent_on_missing=True):
    """
    Automatically search for and load environment variables on import.
    
    Parameters
    ----------
    verbose : bool
        If True, print capability information
    silent_on_missing : bool
        If True, don't raise an error if no .env file is found
        
    Returns
    -------
    dict or None
        Dictionary of available capabilities, or None if silent_on_missing=True
    """
    try:
        # Try to find and load .env file
        env_file = search_for_env_file(env_file='auto', max_parents=3)
        if env_file is not None:
            load_env_variables(env_file=env_file, update_environ=True)
    except FileNotFoundError:
        if not silent_on_missing:
            raise
        # Silently continue if no .env file found
    
    # Check and return capabilities
    capabilities = check_capabilities(verbose=verbose)
    return capabilities