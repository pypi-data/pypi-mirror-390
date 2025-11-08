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
    """Automatically clean up temporary files when program exits"""
    import shutil
    from .utils import get_images_dir

    images_dir = get_images_dir()
    if os.path.exists(images_dir):
        shutil.rmtree(images_dir)


# Register automatic cleanup when program exits
atexit.register(cleanup)