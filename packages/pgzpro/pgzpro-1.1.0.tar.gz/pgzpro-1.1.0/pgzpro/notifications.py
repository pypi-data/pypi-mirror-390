import tkinter as tk
from tkinter import font as tkFont
import threading
import time


def message(text="Message", text_color="black", bg_color="white", duration=3.0):
    """
    Show a centered notification message without title bar

    Args:
        text (str): Message text to display
        text_color (str): Text color (any valid tkinter color)
        bg_color (str): Background color of the window
        duration (float/int): Auto-close duration in seconds (1.0 to 10.0)
    """
    # Convert to float if it's int, and validate duration
    duration = float(duration)
    duration = max(1.0, min(10.0, duration))

    def create_window():
        # Create root window
        root = tk.Tk()
        root.title("")
        root.configure(bg=bg_color)

        # Remove window decorations (no title bar)
        root.overrideredirect(True)

        # Make window always on top
        root.attributes('-topmost', True)

        # Create custom font
        custom_font = tkFont.Font(family="Arial", size=12, weight="normal")

        # Create label with text
        label = tk.Label(
            root,
            text=text,
            font=custom_font,
            fg=text_color,
            bg=bg_color,
            justify="center",
            padx=20,
            pady=15
        )
        label.pack()

        # Update window to calculate proper size
        root.update_idletasks()

        # Get screen dimensions
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Get window dimensions based on text content
        window_width = root.winfo_width()
        window_height = root.winfo_height()

        # Apply minimum width of 300px
        window_width = max(300, window_width)

        # Calculate position to center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # Set window position and size
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Close window after specified duration
        def close_window():
            time.sleep(duration)
            root.quit()
            root.destroy()

        # Start thread to auto-close
        close_thread = threading.Thread(target=close_window)
        close_thread.daemon = True
        close_thread.start()

        # Handle manual close on click
        def on_click(event):
            root.quit()
            root.destroy()

        label.bind("<Button-1>", on_click)
        root.bind("<Button-1>", on_click)

        # Start the main loop
        root.mainloop()

    # Run in separate thread to avoid blocking Pygame
    thread = threading.Thread(target=create_window)
    thread.daemon = True
    thread.start()