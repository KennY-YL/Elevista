import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from PIL import Image
from itertools import cycle

# Initialize customtkinter
ctk.set_appearance_mode("white")
ctk.set_default_color_theme("blue")

# Set initial window size
WIDTH, HEIGHT = 1366, 768

# Keep track of all open top-level windows
open_windows = []

# Function to close all open top-level windows and return to main window
def go_home():
    for window in open_windows:
        if window.winfo_exists():
            window.destroy()
    open_windows.clear()
    tk_root.deiconify()
    tk_root.focus_set()

# Function to center any window
def center_window(window, width, height):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")
    window.update()

# Create main window
tk_root = ctk.CTk()
tk_root.title("EleVista")
tk_root.geometry(f"{WIDTH}x{HEIGHT}")
tk_root.iconbitmap("LOGO.ico")

# Center main window
center_window(tk_root, WIDTH, HEIGHT)

# Load background image
bg_image = Image.open("HomeBackground.png")
bg_image = bg_image.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
bg_photo = ctk.CTkImage(light_image=bg_image, dark_image=bg_image, size=(WIDTH, HEIGHT))

# Create a background label
bg_label = ctk.CTkLabel(tk_root, image=bg_photo, text="", fg_color="transparent")
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Header Frame (Navigation Bar)
header_frame = ctk.CTkFrame(tk_root, height=70, fg_color="#0f0f0f")
header_frame.pack(side="top", fill="x", pady=0)

# Load and display the logo
logo_image = Image.open("logo.png")
logo_image = logo_image.resize((50, 50), Image.Resampling.LANCZOS)
logo_photo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(50, 50))

logo_label = ctk.CTkLabel(header_frame, image=logo_photo, text="", fg_color="transparent")
logo_label.pack(side="left", padx=20)

# Navigation Buttons
nav_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
nav_frame.pack(side="right", padx=20, pady=15)

nav_buttons = ["Home", "Surveys", "Manual", "About Us"]
for text in nav_buttons:
    if text == "Home":
        btn = ctk.CTkButton(nav_frame, text=text, font=("Poppins", 20), fg_color="transparent", text_color="white",
                        corner_radius=5, hover_color="#09AAA3", width=120, height=40, command=go_home)
    else:
        btn = ctk.CTkButton(nav_frame, text=text, font=("Poppins", 20), fg_color="transparent", text_color="white",
                        corner_radius=5, hover_color="#09AAA3", width=120, height=40)
    btn.pack(side="left", padx=10)

# Function to open loading screen
# Function to open loading screen
def open_loading_screen(parent_window):
    # Create the loading window using customtkinter instead of tkinter
    loading_window = ctk.CTkToplevel(tk_root)
    # Add to open windows list
    open_windows.append(loading_window)
    
    loading_window.title("Loading...")
    loading_window.geometry(f"{WIDTH}x{HEIGHT}")
    loading_window.configure(fg_color="#000000")  # Black background
    
    # Center the loading window
    center_window(loading_window, WIDTH, HEIGHT)
    
    # Disable survey window while loading is active
    parent_window.withdraw()

    # Create a container frame for the loading animation
    loading_container = ctk.CTkFrame(loading_window, width=200, height=200, fg_color="transparent")
    loading_container.place(relx=0.5, rely=0.45, anchor="center")

    # Create a canvas for the rotating arc
    canvas = tk.Canvas(loading_container, width=200, height=200, bg="black", highlightthickness=0)
    canvas.pack()

    # Initialize the loading text
    loading_texts = cycle(["loading.", "loading..", "loading..."])
    loading_text = next(loading_texts)
    
    # Function to animate the rotating arc and update the text
    angle = 0
    def animate_loading():
        nonlocal angle, loading_text
        canvas.delete("all")  # Clear the canvas
        
        # Draw the arc
        canvas.create_arc(10, 10, 190, 190, start=angle, extent=120, 
                        outline="white", width=6, style="arc")
        
        # Draw the text in the center of the canvas
        canvas.create_text(100, 100, text=loading_text, fill="white", 
                         font=("Arial", 18, "bold"))
        
        angle = (angle + 15) % 360  # Increment the angle for continuous rotation
        loading_window.after(100, animate_loading)
    
    # Function to animate the loading dots
    def animate_dots():
        nonlocal loading_text
        loading_text = next(loading_texts)
        loading_window.after(500, animate_dots)  # Update dots every 500ms

    animate_loading()
    animate_dots()

    # Status text, positioned below the loading animation
    text_label = ctk.CTkLabel(loading_window, text="EleVista is processing your image.\nPlease wait.", 
                            font=("Arial", 14, "italic"), text_color="white", fg_color="transparent")
    text_label.place(relx=0.5, rely=0.58, anchor="center")

    # Add header frame to match other windows
    header_frame_loading = ctk.CTkFrame(loading_window, height=70, fg_color="#0f0f0f")
    header_frame_loading.pack(side="top", fill="x", pady=0)

    logo_label_loading = ctk.CTkLabel(header_frame_loading, image=logo_photo, text="", fg_color="transparent")
    logo_label_loading.pack(side="left", padx=20)

    nav_frame_loading = ctk.CTkFrame(header_frame_loading, fg_color="transparent")
    nav_frame_loading.pack(side="right", padx=20, pady=15)

    for text in nav_buttons:
        if text == "Home":
            btn = ctk.CTkButton(nav_frame_loading, text=text, font=("Poppins", 20), fg_color="transparent",
                           text_color="white", corner_radius=5, hover_color="#09AAA3", width=120, height=40, 
                           command=go_home)
        else:
            btn = ctk.CTkButton(nav_frame_loading, text=text, font=("Poppins", 20), fg_color="transparent",
                           text_color="white", corner_radius=5, hover_color="#09AAA3", width=120, height=40)
        btn.pack(side="left", padx=10)

    # Close the loading screen after 5 seconds and show the survey result window
    def close_loading():
        if loading_window.winfo_exists():
            loading_window.destroy()
            if loading_window in open_windows:
                open_windows.remove(loading_window)
            # Open the survey result window instead of re-enabling the parent window
            surveyResult()

    loading_window.after(5000, close_loading)

    # Disable main window while loading is active
    loading_window.transient(tk_root)
    loading_window.grab_set()

# Function to open survey window and display image
def upload_file():
    file_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    
    if file_path:
        survey_window = ctk.CTkToplevel(tk_root)
        # Add to open windows list
        open_windows.append(survey_window)
        
        survey_window.title("EleVista Survey")
        survey_window.geometry(f"{WIDTH}x{HEIGHT}")   

        # Set the survey window on top and modal
        survey_window.transient(tk_root)  # Link to main window
        survey_window.grab_set()  # Make modal (disables main window)
        survey_window.focus_set()  # Focus on this window

        survey_window.configure(bg="#e5e5e5")  
        center_window(survey_window, WIDTH, HEIGHT)

        # Variables to track inputs
        title_var = tk.StringVar()
        desc_var = tk.StringVar()
        phone_var = tk.StringVar(value="Android")

        # Function to check if all fields are filled
        def validate_fields(*args):
            if title_var.get().strip() and desc_var.get().strip() and phone_var.get():
                submit_button.configure(state="normal")  # Enable button
            else:
                submit_button.configure(state="disabled")  # Disable button

        # Bind validation function to variable changes
        title_var.trace_add("write", validate_fields)
        desc_var.trace_add("write", validate_fields)
        phone_var.trace_add("write", validate_fields)

        # Header Frame (Survey Window)
        header_frame_survey = ctk.CTkFrame(survey_window, height=70, fg_color="#0f0f0f")
        header_frame_survey.pack(side="top", fill="x", pady=0)

        logo_label_survey = ctk.CTkLabel(header_frame_survey, image=logo_photo, text="", fg_color="transparent")
        logo_label_survey.pack(side="left", padx=20)

        nav_frame_survey = ctk.CTkFrame(header_frame_survey, fg_color="transparent")
        nav_frame_survey.pack(side="right", padx=20, pady=15)

        for text in nav_buttons:
            if text == "Home":
                btn = ctk.CTkButton(nav_frame_survey, text=text, font=("Poppins", 20), fg_color="transparent",
                                text_color="white", corner_radius=5, hover_color="#09AAA3", width=120, height=40,
                                command=go_home)
            else:
                btn = ctk.CTkButton(nav_frame_survey, text=text, font=("Poppins", 20), fg_color="transparent",
                                text_color="white", corner_radius=5, hover_color="#09AAA3", width=120, height=40)
            btn.pack(side="left", padx=10)

        # Left Image Frame
        image_frame = ctk.CTkFrame(survey_window, width=500, height=500, fg_color="#ffffff")
        image_frame.pack(side="left", padx=50, pady=50)
        image_frame.pack_propagate(False)

        # Load and display image using CTkImage
        img = Image.open(file_path)
        img = img.resize((500, 500), Image.Resampling.LANCZOS)
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(500, 500))
        img_label = ctk.CTkLabel(image_frame, image=ctk_img, text="")
        img_label.pack(expand=True, fill="both")

        # Right Form Frame
        form_frame = ctk.CTkFrame(survey_window, fg_color="transparent")
        form_frame.pack(side="right", padx=50, pady=50, fill="both", expand=True)

        survey_label = ctk.CTkLabel(form_frame, text="Survey 1", font=("Arial", 20, "bold"), text_color="#000000")
        survey_label.pack(anchor="w", pady=(0, 20))

        # Survey Title
        ctk.CTkLabel(form_frame, text="Survey Title", text_color="#000000").pack(anchor="w")
        title_entry = ctk.CTkEntry(form_frame, width=400, fg_color="#ffffff", text_color="#000000", textvariable=title_var)
        title_entry.pack(pady=(0, 15))

        # Description
        ctk.CTkLabel(form_frame, text="Description", text_color="#000000").pack(anchor="w")
        desc_entry = ctk.CTkEntry(form_frame, width=400, fg_color="#ffffff", text_color="#000000", textvariable=desc_var)
        desc_entry.pack(pady=(0, 15))

        # Phone Selection
        ctk.CTkLabel(form_frame, text="Specify Phone Used", text_color="#000000").pack(anchor="w")
        phone_dropdown = ctk.CTkOptionMenu(
            form_frame, values=["Android", "iPhone", "Other"], width=400,
            variable=phone_var, fg_color="#ffffff", text_color="#000000"
        )
        phone_dropdown.pack(pady=(0, 20))

        # Submit Button (Initially Disabled)
        submit_button = ctk.CTkButton(
            form_frame, text="Submit", fg_color="#09AAA3", hover_color="#07A293",
            text_color="#ffffff", width=200, height=40, corner_radius=5, state="disabled",
            command=lambda: open_loading_screen(survey_window)  # Pass survey_window to close it when loading starts
        )
        submit_button.pack(pady=20)
# Upload Button
upload_btn = ctk.CTkButton(
    tk_root, text="UPLOAD", font=("Poppins", 25, "bold"),
    fg_color="#09AAA3", text_color="white", corner_radius=5, width=200, height=50,
    command=upload_file
)
upload_btn.place(relx=0.5, rely=0.6, anchor="center")

def surveyResult():
    # Create the top-level survey detail window
    survey_window = ctk.CTkToplevel(tk_root)
    open_windows.append(survey_window)
    
    survey_window.title("EleVista - Survey Detail")
    survey_window.geometry(f"{WIDTH}x{HEIGHT}")
    survey_window.configure(bg="#e5e5e5")
    center_window(survey_window, WIDTH, HEIGHT)
    
    # Create the header frame
    header_frame_survey = ctk.CTkFrame(survey_window, height=70, fg_color="#0f0f0f")
    header_frame_survey.pack(side="top", fill="x", pady=0)

    logo_label_survey = ctk.CTkLabel(header_frame_survey, image=logo_photo, text="", fg_color="transparent")
    logo_label_survey.pack(side="left", padx=20)

    nav_frame_survey = ctk.CTkFrame(header_frame_survey, fg_color="transparent")
    nav_frame_survey.pack(side="right", padx=20, pady=15)

    for text in nav_buttons:
        if text == "Home":
            btn = ctk.CTkButton(nav_frame_survey, text=text, font=("Poppins", 20), fg_color="transparent", 
                                text_color="white", corner_radius=5, hover_color="#09AAA3", width=120, height=40,
                                command=go_home)
        else:
            btn = ctk.CTkButton(nav_frame_survey, text=text, font=("Poppins", 20), fg_color="transparent", 
                                text_color="white", corner_radius=5, hover_color="#09AAA3", width=120, height=40)
        btn.pack(side="left", padx=10)
    
    # Survey Content Frame (Ensure grid or pack isn't conflicting)
    content_frame = ctk.CTkFrame(survey_window, bg_color="#e5e5e5", width=900)
    content_frame.place(relx=0.5, rely=0.5, anchor="center")
    
    # Survey Detail Section
    details_frame = ctk.CTkFrame(content_frame, bg="#e5e5e5", width=600)
    details_frame.grid(row=0, column=0, padx=20, pady=20)
    
    title_label = ctk.CTkLabel(details_frame, text="Survey 1", font=("Arial", 18, "bold"), fg="#333333")
    title_label.grid(row=0, column=0, sticky="w", pady=(0, 10))
    
    date_label = ctk.CTkLabel(details_frame, text="March 8, 2025 | 9:21PM", font=("Arial", 10, "italic"), fg="#555555")
    date_label.grid(row=1, column=0, sticky="w", pady=(0, 5))
    
    # Left side - Image frame
    img_frame = ctk.CTkFrame(content_frame, bg="black", width=250, height=250)
    img_frame.grid(row=0, column=1, padx=20)
    
    # Add a placeholder image to the frame
    placeholder_img = Image.open("placeholder.png")
    placeholder_img = placeholder_img.resize((250, 250), Image.Resampling.LANCZOS)
    ctk_img = ctk.CTkImage(light_image=placeholder_img, dark_image=placeholder_img, size=(250, 250))
    img_label = ctk.CTkLabel(img_frame, image=ctk_img, text="")
    img_label.pack()

    # Survey description and metrics
    metrics = [
        ("Horizontal Distance:", ""),
        ("Vertical Angle:", ""),
        ("Slope:", ""),
        ("Elevation:", "")
    ]
    
    row_num = 2
    for label_text, value in metrics:
        label = ctk.CTkLabel(details_frame, text=label_text, font=("Arial", 10, "bold"), fg="#333333")
        label.grid(row=row_num, column=0, sticky="w", pady=(0, 10))
        row_num += 1

# Run Application
tk_root.mainloop()








