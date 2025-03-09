import tkinter as tk
import math
from itertools import cycle

class LoadingScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Loading...")
        self.root.geometry("640x400")
        self.root.configure(bg="black")

        # Create a canvas for the large loading circle
        self.canvas = tk.Canvas(root, width=200, height=200, bg="black", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.38, anchor="center")  # Centered canvas

        # Loading text inside the circle
        self.loading_texts = cycle(["loading.", "loading..", "loading..."])
        self.loading_label = tk.Label(root, text="loading.", font=("Arial", 18, "bold"), fg="white", bg="black")
        self.loading_label.place(relx=0.5, rely=0.38, anchor="center")  # Matches canvas position

        # Status text below the circle
        self.text_label = tk.Label(root, text="EleVista is processing your image.\nPlease wait.", 
                                   font=("Arial", 14, "italic"), fg="white", bg="black")
        self.text_label.place(relx=0.5, rely=0.70, anchor="center")  # Spaced further below

        self.angle = 0  # Initial angle for the rotating arc
        self.running = True  # Control animation loop

        self.animate_loading()
        self.animate_dots()

    def animate_loading(self):
        """ Rotates the large loading arc. """
        if not self.running:
            return  # Stop animation if app is closing

        self.canvas.delete("arc")  # Clear previous arc
        start_angle = self.angle
        extent = 120  # Arc opening size

        # Draw arc (big loading indicator)
        self.canvas.create_arc(10, 10, 190, 190, start=start_angle, extent=extent, 
                               outline="white", width=6, style="arc", tags="arc")

        self.angle = (self.angle + 15) % 360  # Rotate arc smoothly
        self.root.after(100, self.animate_loading)  # Update every 100ms

    def animate_dots(self):
        """ Animates the dots in 'loading...' """
        if not self.running:
            return  # Stop animation if app is closing

        self.loading_label.config(text=next(self.loading_texts))
        self.root.after(500, self.animate_dots)  # Change every 500ms

    def on_closing(self):
        """ Properly stops the animation when closing the app. """
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = LoadingScreen(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)  # Handle closing event
    root.mainloop()


