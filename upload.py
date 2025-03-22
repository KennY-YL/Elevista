import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
from itertools import cycle

# Initialize customtkinter
ctk.set_appearance_mode("white")
ctk.set_default_color_theme("blue")

# Set initial window size
WIDTH, HEIGHT = 1200, 720

# Keep track of all open top-level windows
open_windows = []

active_windows = {}

def close_all_windows(except_window=None):
    """Hide all windows except the specified one."""
    for name, window in active_windows.items():
        if window != except_window and window.winfo_exists():
            window.withdraw()


def insert_circular_image(canvas, image_path):
    # Open and resize the image
    image = Image.open(image_path).resize((300, 300), Image.LANCZOS)
    
    # Create a circular mask
    mask = Image.new("L", (300, 300), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, 300, 300), fill=255)
    
    # Create a transparent image
    circular_image = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
    circular_image.paste(image, (0, 0), mask)

    # Convert to ImageTk for displaying in canvas
    canvas.image = ImageTk.PhotoImage(circular_image)
    canvas.create_image(150, 150, image=canvas.image)

# Function to close all open top-level windows and return to main window
def go_home():
    for window in open_windows:
        if window.winfo_exists():
            window.destroy()
    open_windows.clear()
    tk_root.deiconify()
    tk_root.focus_set()

def create_navigation_bar(parent, parent_window):
    header_frame = ctk.CTkFrame(parent, height=70, fg_color="#0f0f0f")
    header_frame.pack(side="top", fill="x", pady=0)


    logo_label = ctk.CTkLabel(header_frame, text="EleVista", font=("Poppins", 30), fg_color="transparent", text_color="white")
    logo_label.pack(side="left", padx=(30, 30))  # Adjust the first value to move it to the right


    # Navigation Buttons
    nav_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
    nav_frame.pack(side="right", padx=20, pady=15)

    nav_buttons = ["home", "surveys", "manual", "about us"]
    for text in nav_buttons:
        if text == "home":
            btn = ctk.CTkButton(nav_frame, text=text, font=("Poppins", 20), fg_color="transparent", text_color="white",
                            corner_radius=5, hover_color="#09AAA3", width=120, height=40, command=go_home)
        elif text == "about us":
            btn = ctk.CTkButton(nav_frame, text=text, font=("Poppins", 20), fg_color="transparent", text_color="white",
                            corner_radius=5, hover_color="#09AAA3", width=120, height=40, command=about_us_window)
        elif text == "manual":
            btn = ctk.CTkButton(nav_frame, text=text, font=("Poppins", 20), fg_color="transparent", text_color="white",
                            corner_radius=5, hover_color="#09AAA3", width=120, height=40, command=open_instruction_window)
        else:
            btn = ctk.CTkButton(nav_frame, text=text, font=("Poppins", 20), fg_color="transparent", text_color="white",
                            corner_radius=5, hover_color="#09AAA3", width=120, height=40)
        btn.pack(side="left", padx=10)

def about_us_window():   
    if "aboutUs" not in active_windows or not active_windows["aboutUs"].winfo_exists():
        # Create top-level window
        tk_root.withdraw()
        aboutUs = ctk.CTkToplevel(tk_root)
        aboutUs.title("About Us")
        aboutUs.geometry(f"{WIDTH}x{HEIGHT}")
        aboutUs.configure(bg="#e5e5e5")
        center_window(aboutUs, WIDTH, HEIGHT)

        # Create Navigation Bar
        create_navigation_bar(aboutUs, aboutUs)

        # About Section
        about_label = ctk.CTkLabel(aboutUs, text="About EleVista", font=("Poppins", 35, "bold"))
        about_label.pack(anchor="w", pady=(20, 5), padx=(75, 5))

        description = ("EleVista was developed to bridge the gap between traditional surveying and the cutting-edge power of AI, making land elevation measurement smarter, faster, and more accessible than ever before.")
        desc_label = ctk.CTkLabel(aboutUs, text=description, wraplength=900, justify="center", font=("Poppins", 20))
        desc_label.pack(pady=(20, 20))

        # Meet The Team Section
        team_label = ctk.CTkLabel(aboutUs, text="MEET THE TEAM", font=("Poppins", 25, "bold"))
        team_label.pack(pady=(20, 0))
        
        # Team Members Data
        members = [
            ("REGIENA MAE E. CABALLES", "CPE - 4201"),
            ("CHANTEL KYLIE M. MALUNDAS", "CPE - 4201"),
            ("JHON KENNETH M. YLAGAN", "CPE - 4201")
            ]# Create Colorless Parent Frame to Center Members
        container_frame = ctk.CTkFrame(aboutUs, fg_color="transparent")
        container_frame.pack(pady=(20, 40))
        image_paths = ["2.jpg", "1.jpg", "3.jpg"]

        # Create Separate Frames for Each Member
        for (name, title), image_path in zip(members, image_paths):
            member_frame = ctk.CTkFrame(container_frame, width=250, height=300, fg_color="#D9D9D9")
            member_frame.pack(side="left", padx=(20, 20))
            member_frame.pack_propagate(False)

            # Create Circular Canvas
            circle_canvas = ctk.CTkCanvas(member_frame, width=300, height=300, bg="#D9D9D9", highlightthickness=0)
            circle_canvas.create_oval(10, 10, 290, 290, outline="#0C2C44", width=2)
            circle_canvas.pack(pady=20)

            # Insert corresponding image with transparency
            insert_circular_image(circle_canvas, image_path)

            # Display Name and Title
            name_label = ctk.CTkLabel(member_frame, text=name, font=("Poppins", 15, "bold"))
            name_label.pack()

            title_label = ctk.CTkLabel(member_frame, text=title, font=("Poppins", 14))
            title_label.pack()

        active_windows["aboutUs"] = aboutUs

    
    close_all_windows(active_windows["aboutUs"])
    active_windows["aboutUs"].deiconify()



# Function the opens manual
def open_instruction_window():
    # Create top-level window
    if "instructionWindow" not in active_windows or not active_windows["instructionWindow"].winfo_exists():
        tk_root.withdraw()
        instructionWindow = ctk.CTkToplevel(tk_root)
        instructionWindow.title("Manual")
        instructionWindow.geometry(f"{WIDTH}x{HEIGHT}")
        instructionWindow.configure(bg="#e5e5e5")
        instructionWindow.focus_set()
        center_window(instructionWindow, WIDTH, HEIGHT)

        # Create Navigation Bar
        create_navigation_bar(instructionWindow, instructionWindow) 
        # Create a canvas and scrollbar
        canvas = tk.Canvas(instructionWindow)
        scrollbar = ttk.Scrollbar(instructionWindow, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Title Section
        title_label = tk.Label(scrollable_frame, text="Instruction Manual", font=("Arial", 40, "bold"))
        title_label.pack(pady= 1, padx=30, anchor='w')

        # How to Collect Data Section
        collect_label = tk.Label(scrollable_frame, text="How to Collect Data", font=("Arial", 30, "bold"))
        collect_label.pack(anchor="w", pady=1, padx=20)

        tools_label = tk.Label(scrollable_frame, text="Tools You'll Need:", font=("Arial", 22))
        tools_label.pack(anchor="w", padx=40)

        tools = ["Tripod", "Ruler or measuring tape", "Chalk/marker stick", "Printed scale ruler", "Stakes or fixed stick"]
        for tool in tools:
            tk.Label(scrollable_frame, text=f"• {tool}", font=("Arial", 16)).pack(anchor="w", padx=60)

        # Steps for Data Gathering
        steps_label = tk.Label(scrollable_frame, text="Steps for Data Gathering", font=("Arial", 16, "bold"))
        steps_label.pack(anchor="w", padx=20, pady=10)

        steps = [
            "Position the tripod with the mobile phone on the ground, centered in the middle of the inclined land.",
            "Ensure that the bubble level on the tripod is centered.",
            "Measure the height of the phone from the ground and ensure it is 83 cm.",
            "Adjust the tilt feature (camera level) of the phone and ensure that it is leveled at a 90-degree angle.",
            "Measure distances ranging from 2 meters to 12 meters. (Note: The model only recognizes distances up to 12 meters).",
            "Position the tripod or marker stick at the desired distance.",
            "Capture an image of the person holding the tripod or marker stick. Make sure the height of the object is visible in the picture."
        ]

        for i, step in enumerate(steps, 1):
            tk.Label(scrollable_frame, text=f"{i}. {step}").pack(anchor="w", padx=40, pady=2)

        # How to Use the System
        use_label = tk.Label(scrollable_frame, text="How to Use the System", font=("Arial", 16, "bold"))
        use_label.pack(anchor="w", padx=20, pady=10)

        use_steps = [
            "Step 1: Import the Images - Import the images and upload images to the system.",
            "Step 2: Input the Image - Name the file and provide a description. (The description is optional)",
            "Step 3: Import the Images - Wait for the system to process the images. Once completed, the survey information will be displayed."
        ]

        for step in use_steps:
            tk.Label(scrollable_frame, text=step).pack(anchor="w", padx=40, pady=2)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        active_windows["instructionWindow"] = instructionWindow

    close_all_windows(active_windows["instructionWindow"])
    active_windows["instructionWindow"].deiconify()

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

nav_buttons = ["home", "surveys", "manual", "about us"]
for text in nav_buttons:
    if text == "home":
        btn = ctk.CTkButton(nav_frame, text=text, font=("Poppins", 20), fg_color="transparent", text_color="white",
                        corner_radius=5, hover_color="#09AAA3", width=120, height=40, command=go_home)
    elif text == "about us":
        btn = ctk.CTkButton(nav_frame, text=text, font=("Poppins", 20), fg_color="transparent", text_color="white",
                        corner_radius=5, hover_color="#09AAA3", width=120, height=40, command=about_us_window)
    elif text == "manual":
        btn = ctk.CTkButton(nav_frame, text=text, font=("Poppins", 20), fg_color="transparent", text_color="white",
                        corner_radius=5, hover_color="#09AAA3", width=120, height=40, command=open_instruction_window)
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

    create_navigation_bar(loading_window, loading_window) 
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

        create_navigation_bar(survey_window, survey_window) 
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
    if not tk_root.winfo_exists():
        print("Error: tk_root does not exist.")
        return
    
    # Create the survey detail window
    survey_result_window = ctk.CTkToplevel(tk_root)
    survey_result_window.title("EleVista - Survey Detail")
    survey_result_window.geometry(f"{WIDTH}x{HEIGHT}")
    survey_result_window.configure(bg="#e5e5e5")
    center_window(survey_result_window, WIDTH, HEIGHT)

    create_navigation_bar(survey_result_window, survey_result_window)

    # Main Content Frame
    main_frame = ctk.CTkFrame(survey_result_window, fg_color="#e5e5e5")
    main_frame.pack(pady=40, padx=20, fill="both", expand=True)

    # Left - Image Frame
    img_frame = ctk.CTkFrame(main_frame, fg_color="black", width=350, height=350)
    img_frame.pack(side="left", padx=40)

    try:
        placeholder_img = Image.open("checkerboard.png")
        placeholder_img = placeholder_img.resize((350, 350), Image.Resampling.LANCZOS)
        ctk_img = ctk.CTkImage(light_image=placeholder_img, dark_image=placeholder_img, size=(350, 350))
        img_label = ctk.CTkLabel(img_frame, image=ctk_img, text="")
        img_label.pack()
    except FileNotFoundError:
        print("Image not found. Ensure 'checkerboard.png' exists.")

    # Right - Survey Details
    details_frame = ctk.CTkFrame(main_frame, fg_color="#e5e5e5")
    details_frame.pack(side="left", padx=20)

    # Title and Time
    title_label = ctk.CTkLabel(details_frame, text="Survey 1", font=("Arial", 22, "bold"), text_color="#333333")
    title_label.pack(anchor="w")

    date_label = ctk.CTkLabel(details_frame, text="March 8, 2025 | 9:21PM", font=("Arial", 12, "italic"), text_color="#555555")
    date_label.pack(anchor="w")

    # Location
    location_frame = ctk.CTkFrame(details_frame, fg_color="#e5e5e5")
    location_frame.pack(anchor="w", pady=5)

    bullet_label = ctk.CTkLabel(location_frame, text="●", font=("Arial", 12), text_color="#333333")
    bullet_label.pack(side="left")

    location_label = ctk.CTkLabel(location_frame, text="Sorosoro, Batangas City", font=("Arial", 12), text_color="#333333")
    location_label.pack(side="left", padx=5)

    edit_label = ctk.CTkLabel(location_frame, text="edit", font=("Arial", 10, "underline"), text_color="#555555", cursor="hand2")
    edit_label.pack(side="left")

    # Description
    desc_label = ctk.CTkLabel(details_frame, text="Description:", font=("Arial", 12, "bold"), text_color="#333333")
    desc_label.pack(anchor="w", pady=(10, 5))

    desc_textbox = ctk.CTkTextbox(details_frame, width=350, height=100, fg_color="white", border_color="#ccc")
    desc_textbox.pack()

    desc_edit_label = ctk.CTkLabel(details_frame, text="edit", font=("Arial", 10, "underline"), text_color="#555555", cursor="hand2")
    desc_edit_label.pack(anchor="w", pady=5)

    # Survey Metrics
    metrics = [
        ("Horizontal Distance:", "N/A"),
        ("Vertical Angle:", "N/A"),
        ("Slope:", "N/A"),
        ("Elevation:", "N/A")
    ]

    for label_text, value in metrics:
        label = ctk.CTkLabel(details_frame, text=f"{label_text}", font=("Arial", 12, "bold"), text_color="#333333")
        label.pack(anchor="w", pady=2)
        
        value_label = ctk.CTkLabel(details_frame, text=value, font=("Arial", 12), text_color="#333333")
        value_label.pack(anchor="w")

   

# Run Application
tk_root.mainloop()








