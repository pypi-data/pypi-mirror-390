import os
import io
import time
import requests
from PIL import Image
from deep_translator import GoogleTranslator
from .exceptions import NoInternetError, ImageGenerationError, ModelQuotaError, APIConnectionError, ImageProcessingError


def get_images_dir():
    """Get the images directory path"""
    images_dir = "images"
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
    return images_dir


def check_internet_connection():
    """
    Check if internet connection is available

    Returns:
        bool: True if internet is available, False otherwise
    """
    try:
        response = requests.get("https://www.google.com", timeout=5)
        return response.status_code == 200
    except:
        return False


def translate_prompt(prompt):
    """
    Translate prompt to English if it's not in English

    Args:
        prompt (str): The prompt text

    Returns:
        str: English translated prompt
    """
    if any(ord(char) > 127 for char in prompt):
        try:
            return GoogleTranslator(source='auto', target='en').translate(prompt)
        except:
            return prompt
    return prompt


def make_transparent_background(img):
    """Make white background transparent"""
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    data = img.getdata()
    new_data = []

    for item in data:
        if item[0] > 250 and item[1] > 250 and item[2] > 250:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)

    img.putdata(new_data)
    return img


def crop_transparent_pixels(img):
    """Crop transparent pixels from image edges"""
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    bbox = img.getbbox()
    if bbox:
        return img.crop(bbox)
    return img


def validate_geometry(width, height):
    """
    Validate image dimensions

    Args:
        width (int): Image width
        height (int): Image height

    Raises:
        ValueError: If dimensions are invalid
    """
    if width < 10 or height < 10:
        raise ValueError("Image dimensions must be at least 10x10 pixels")
    if width > 1024 or height > 1024:
        raise ValueError("Image dimensions cannot exceed 1024x1024 pixels")


def generate_image_with_g4f(prompt, user_prompt, filename, width=None, height=None, transparent_bg=False,
                            crop_transparent=False):
    """Generate image using G4F Flux model with retry logic"""
    from g4f.client import Client

    start_time = time.time()

    debug_logging = True
    try:
        from .generator import _debug_logging
        debug_logging = _debug_logging
    except:
        pass

    max_attempts = 5
    attempt = 0

    while attempt < max_attempts:
        attempt += 1

        # Check internet connection only at the beginning of each attempt
        if not check_internet_connection():
            raise NoInternetError(
                "No internet connection available. AI image generation requires an active internet connection.")

        if debug_logging:
            print(f"\n[GENERATION START] Attempt {attempt}/{max_attempts} - Generating image: {filename}")
            print(f"[USER PROMPT] {user_prompt}")
            print(f"[DIMENSIONS] {width}x{height}")
            print(f"[TRANSPARENT BG] {transparent_bg}")
            print(f"[CROP TRANSPARENT] {crop_transparent}")

        try:
            client = Client()

            final_prompt = prompt
            if transparent_bg:
                final_prompt = f"{prompt}, white background, no white elements on character"

            response = client.images.generate(
                model="flux",
                prompt=final_prompt,
                response_format="url"
            )

            if response.data and hasattr(response.data[0], 'url'):
                image_url = response.data[0].url
                if debug_logging:
                    print(f"[IMAGE URL] {image_url}")

                if debug_logging:
                    print("[STATUS] Downloading image...")
                img_response = requests.get(image_url)
                img_response.raise_for_status()

                file_path = os.path.join(get_images_dir(), filename)

                if debug_logging:
                    print("[STATUS] Processing image...")
                img = Image.open(io.BytesIO(img_response.content))

                if transparent_bg:
                    if debug_logging:
                        print("[STATUS] Adding transparent background...")
                    img = make_transparent_background(img)
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                if crop_transparent and transparent_bg:
                    if debug_logging:
                        print("[STATUS] Cropping transparent edges...")
                    img = crop_transparent_pixels(img)

                if width and height:
                    if debug_logging:
                        print(f"[STATUS] Resizing to {width}x{height}...")
                    img = img.resize((width, height), Image.Resampling.LANCZOS)

                if debug_logging:
                    print(f"[STATUS] Saving as: {filename}")
                img.save(file_path)

                generation_time = time.time() - start_time

                if debug_logging:
                    print(f"[SUCCESS] Image generated successfully in {generation_time:.2f} seconds")

                return filename.replace('.png', '')
            else:
                raise APIConnectionError("No image URL received from AI model. The API response was invalid.")

        except Exception as e:
            generation_time = time.time() - start_time
            error_message = str(e)

            if debug_logging:
                print(f"[ATTEMPT {attempt}/{max_attempts} FAILED] after {generation_time:.2f} seconds: {error_message}")

            if "quota" in error_message.lower() or "exceeded" in error_message.lower():
                if attempt < max_attempts:
                    wait_time = 10
                    if debug_logging:
                        print(f"[RETRY] Waiting {wait_time} seconds before next attempt...")
                    time.sleep(wait_time)
                    continue
                else:
                    if debug_logging:
                        print(f"[FINAL FAILURE] All {max_attempts} attempts exhausted")
                    raise ModelQuotaError(
                        f"AI model quota exceeded after {max_attempts} attempts. Please try again later.")
            elif "try again" in error_message.lower():
                if attempt < max_attempts:
                    wait_time = 10
                    if debug_logging:
                        print(f"[RETRY] Waiting {wait_time} seconds before next attempt...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise APIConnectionError(
                        f"API connection issues after {max_attempts} attempts. Please check your connection and try again.")
            else:
                if debug_logging:
                    print(f"[FATAL ERROR] Not retrying due to error type: {error_message}")
                raise ImageGenerationError(f"Failed to generate image with AI: {error_message}")

    raise ImageGenerationError(f"Failed to generate image after {max_attempts} attempts due to unknown reasons")