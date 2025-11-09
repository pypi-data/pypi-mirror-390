import os
import atexit
import inspect


def center(width=None, height=None):
    """
    Center the game window on screen.
    Automatically detects WIDTH and HEIGHT from global variables if not provided.

    Args:
        width (int, optional): Window width. If None, detects from WIDTH global variable.
        height (int, optional): Window height. If None, detects from HEIGHT global variable.
    """
    from screeninfo import get_monitors

    if width is None or height is None:
        try:
            # Ищем в глобальной области видимости вызывающего модуля
            caller_frame = inspect.currentframe().f_back
            caller_globals = caller_frame.f_globals

            if width is None:
                width = caller_globals.get('WIDTH')
                if width is None:
                    raise RuntimeError("WIDTH variable not found. Please specify width or define WIDTH global variable")

            if height is None:
                height = caller_globals.get('HEIGHT')
                if height is None:
                    raise RuntimeError(
                        "HEIGHT variable not found. Please specify height or define HEIGHT global variable")

        except Exception as e:
            raise RuntimeError(f"Failed to detect window size: {e}")

    # Get monitor dimensions for centering
    for monitor in get_monitors():
        x_fullscreen = monitor.width
        y_fullscreen = monitor.height
        break

    x_screen = int((x_fullscreen - width) / 2)
    y_screen = int((y_fullscreen - height) / 2)

    os.environ['SDL_VIDEO_WINDOW_POS'] = f'{x_screen},{y_screen}'


def cleanup():
    """
    Automatically clean up AI-generated temporary files when program exits.

    This function:
    - Removes only AI-generated image files (with 'generated_' prefix)
    - Preserves user-added files in the images directory
    - Removes the images folder only if it's empty after cleanup
    - Provides detailed logging of cleanup operations only when debug logging is enabled

    Safe to use - will never delete user-created content.
    """
    import glob
    from .utils import get_images_dir

    # Check if debug logging is enabled
    debug_logging = True
    try:
        from .generator import _debug_logging
        debug_logging = _debug_logging
    except:
        pass

    images_dir = get_images_dir()
    if os.path.exists(images_dir):
        # Remove only AI-generated files (generated_actor_*.png, generated_background_*.png)
        generated_files = glob.glob(os.path.join(images_dir, "generated_*.png"))
        for file_path in generated_files:
            try:
                os.remove(file_path)
                if debug_logging:
                    print(f"[CLEANUP] Removed temporary file: {os.path.basename(file_path)}")
            except Exception as e:
                if debug_logging:
                    print(f"[CLEANUP WARNING] Failed to remove {file_path}: {e}")

        # Remove images directory only if it's empty after cleaning temporary files
        if not os.listdir(images_dir):
            try:
                os.rmdir(images_dir)
                if debug_logging:
                    print(f"[CLEANUP] Removed empty directory: {images_dir}")
            except Exception as e:
                if debug_logging:
                    print(f"[CLEANUP WARNING] Failed to remove directory {images_dir}: {e}")


# Register automatic cleanup when program exits
atexit.register(cleanup)