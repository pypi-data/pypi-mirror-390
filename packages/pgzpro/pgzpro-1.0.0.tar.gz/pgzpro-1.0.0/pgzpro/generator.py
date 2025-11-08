from .utils import validate_geometry, translate_prompt, generate_image_with_g4f, check_internet_connection
from .exceptions import NoInternetError
import time

# Global variable for logging control
_debug_logging = True


def no_logging(enable):
    """
    Enable or disable debug logging

    Args:
        enable (bool): True to disable logging, False to enable logging
    """
    global _debug_logging
    _debug_logging = not enable
    print(f"[LOGGING] Debug logging {'disabled' if enable else 'enabled'}")


def actor_generate(prompt, geometry):
    """
    Generate an actor image with AI and return image filename

    Args:
        prompt (str): Prompt for image generation
        geometry (str): Geometry in format "WIDTHxHEIGHT"

    Returns:
        str: Generated image filename (without extension)

    Raises:
        ValueError: If parameters are missing or invalid
        NoInternetError: If no internet connection available
    """
    if not prompt:
        raise ValueError("Prompt parameter is required")
    if not geometry:
        raise ValueError("Geometry parameter is required in format 'WIDTHxHEIGHT'")

    try:
        width, height = map(int, geometry.split('x'))
    except ValueError:
        raise ValueError("Geometry must be in format 'WIDTHxHEIGHT' (e.g., '100x150')")

    validate_geometry(width, height)

    # Check internet connection
    if not check_internet_connection():
        raise NoInternetError("No internet connection available. AI image generation requires an active internet connection.")

    # Translate prompt to English if needed
    english_prompt = translate_prompt(prompt)

    # prompt
    final_prompt = f"{english_prompt}, CHARACTER MUST BE STRICTLY ON WHITE BACKGROUND! Character should not have any white elements or white colors"

    # filename
    timestamp = int(time.time() * 1000)
    filename = f"generated_actor_{timestamp}.png"

    # Generate image and return filename
    image_name = generate_image_with_g4f(
        prompt=final_prompt,
        user_prompt=prompt,
        filename=filename,
        width=width,
        height=height,
        transparent_bg=True,
        crop_transparent=True
    )

    return image_name


def bg_generate(prompt, geometry=None):
    """
    Generate a background image with AI

    Args:
        prompt (str): Prompt for image generation
        geometry (str): Geometry in format "WIDTHxHEIGHT" (if None, tries to detect from global WIDTH and HEIGHT)

    Returns:
        str: Background image filename (without extension)

    Raises:
        ValueError: If prompt is missing
        NoInternetError: If no internet connection available
    """
    if not prompt:
        raise ValueError("Prompt parameter is required")

    if geometry is None:
        import inspect
        try:
            caller_frame = inspect.currentframe().f_back
            caller_globals = caller_frame.f_globals

            width = caller_globals.get('WIDTH', 800)
            height = caller_globals.get('HEIGHT', 600)

        except:
            width = 800
            height = 600
    else:
        try:
            width, height = map(int, geometry.split('x'))
        except ValueError:
            raise ValueError("Geometry must be in format 'WIDTHxHEIGHT' (e.g., '800x600')")

    validate_geometry(width, height)

    # Check internet connection
    if not check_internet_connection():
        raise NoInternetError("No internet connection available. AI image generation requires an active internet connection.")

    # Translate prompt to English if needed
    english_prompt = translate_prompt(prompt)

    # filename
    timestamp = int(time.time() * 1000)
    filename = f"generated_background_{timestamp}.png"

    # Generate image and return filename
    image_name = generate_image_with_g4f(
        prompt=english_prompt,
        user_prompt=prompt,
        filename=filename,
        width=width,
        height=height,
        transparent_bg=False,
        crop_transparent=False
    )

    return image_name