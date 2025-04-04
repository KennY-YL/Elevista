import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
from itertools import cycle
from tkinter import messagebox,simpledialog
import firebase_admin
from firebase_admin import credentials, firestore
import hashlib  # For password hashing
import json
import os
from datetime import datetime
import shutil



# Initialize customtkinter
ctk.set_appearance_mode("white")
ctk.set_default_color_theme("blue")

# Set initial window size
WIDTH, HEIGHT = 1200, 650

# Keep track of all open top-level windows
open_windows = []

active_windows = {}

# Initialize Firebase
cred = credentials.Certificate("elevista-1cae7-firebase-adminsdk-fbsvc-9a5b78dc69.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

SURVEY_DIR = os.path.join(os.path.expanduser("~"), "Documents", "Surveys")
# Loads and displays existing survey folders
if not os.path.exists(SURVEY_DIR):
    os.makedirs(SURVEY_DIR)  # Ensure the directory exists

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
    create_navigation_bar(tk_root)


"""NAV BAR FOR THE TOP LEVEL WINDOWS"""
def create_navigation_bar(parent):
    if hasattr(parent, "header_frame") and parent.header_frame.winfo_exists():
        print(f"Destroying old header_frame in {parent}")
        parent.header_frame.destroy()
    
    # Create a new header frame and pack it at the top
    parent.header_frame = tk.Frame(parent, height=70, bg="#0f0f0f")  # Use 'bg' instead of 'fg_color'
    parent.header_frame.pack(side="top", fill="x", pady=0)

    # Show "EleVista" text for top-level window, else show logo for main window
    try:
        if parent == tk_root:
            logo_image = Image.open("LOGO.png").resize((50, 50), Image.Resampling.LANCZOS)
            logo_photo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(50, 50))
            logo_label = ctk.CTkLabel(parent.header_frame, image=logo_photo, text="", fg_color="transparent")
            parent.logo_photo = logo_photo  # Prevent garbage collection
        else:
            logo_label = ctk.CTkLabel(parent.header_frame, text="EleVista", font=("Poppins", 30), fg_color="transparent", text_color="white")
    except Exception as e:
        print(f"Error loading image: {e}")
        logo_label = ctk.CTkLabel(parent.header_frame, text="Logo Not Found", font=("Poppins", 20), fg_color="transparent", text_color="white")

    logo_label.pack(side="left", padx=(30, 30))

    # Destroy old nav frame if it exists
    if hasattr(parent, "nav_frame") and parent.nav_frame.winfo_exists():
        parent.nav_frame.destroy()

    # Create new Navigation Frame
    parent.nav_frame = ctk.CTkFrame(parent.header_frame, fg_color="transparent")
    parent.nav_frame.pack(side="right", padx=20, pady=15)
    print(f"Created new nav_frame for {parent}")  # Debugging print

    # Show Profile Button if Logged In, else show Login & Sign-Up
    nav_buttons = ["home", "surveys", "manual", "about us", "LOGIN", "SIGN UP"]

    if is_logged_in:  # If logged in, show profile and other buttons
        for text in nav_buttons:
            if text == "home":
                btn = ctk.CTkButton(parent.nav_frame, text=text, font=("Poppins", 20), fg_color="transparent", text_color="white",
                                    corner_radius=5, hover_color="#09AAA3", width=120, height=40, command=go_home)
            elif text == "surveys":
                btn = ctk.CTkButton(parent.nav_frame, text=text, font=("Poppins", 20), fg_color="transparent", text_color="white",
                                    corner_radius=5, hover_color="#09AAA3", width=120, height=40,command=open_survey_folder_window)
            elif text == "manual":
                btn = ctk.CTkButton(parent.nav_frame, text=text, font=("Poppins", 20), fg_color="transparent", text_color="white",
                                    corner_radius=5, hover_color="#09AAA3", width=120, height=40, command=open_instruction_window)
            elif text == "about us":
                btn = ctk.CTkButton(parent.nav_frame, text=text, font=("Poppins", 20), fg_color="transparent", text_color="white",
                                    corner_radius=5, hover_color="#09AAA3", width=120, height=40,command=about_us_window)
            btn.pack(side="left", padx=10)

        # Add profile image button
        profile_img = ctk.CTkImage(Image.open("profile.png"), size=(30, 30))
        profile_btn = ctk.CTkButton(parent.nav_frame, text="", image=profile_img, width=40, height=40,
                                    fg_color="transparent", hover_color="#09AAA3", command=show_logout)
        profile_btn.pack(side="left", padx=(10, 5))
        parent.profile_img = profile_img  # Prevent garbage collection

    else:  # If not logged in, show Login and Sign Up buttons
        for text in nav_buttons:
            if text == "home":
                btn = ctk.CTkButton(parent.nav_frame, text=text, font=("Poppins", 20), fg_color="transparent", text_color="white",
                                    corner_radius=5, hover_color="#09AAA3", width=120, height=40, command=go_home)
            elif text == "surveys":
                btn = ctk.CTkButton(parent.nav_frame, text=text, font=("Poppins", 20), fg_color="transparent", text_color="white",
                                    corner_radius=5, hover_color="#09AAA3", width=120, height=40,command=open_survey_folder_window)
            elif text == "manual":
                btn = ctk.CTkButton(parent.nav_frame, text=text, font=("Poppins", 20), fg_color="transparent", text_color="white",
                                    corner_radius=5, hover_color="#09AAA3", width=120, height=40, command=open_instruction_window)
            elif text == "about us":
                btn = ctk.CTkButton(parent.nav_frame, text=text, font=("Poppins", 20), fg_color="transparent", text_color="white",
                                    corner_radius=5, hover_color="#09AAA3", width=120, height=40,command=about_us_window)
            elif text == "LOGIN":
                btn = ctk.CTkButton(parent.nav_frame, text=text, font=("Poppins", 20), fg_color="#09AAA3", text_color="white",
                                    corner_radius=5, width=120, height=40, command=show_login_window)
            else:
                btn = ctk.CTkButton(parent.nav_frame, text=text, font=("Poppins", 20), fg_color="transparent", text_color="white",
                                    corner_radius=5, hover_color="#09AAA3", border_color="#09AAA3", border_width=2, width=120, height=40,
                                    command=show_signup_window)

            btn.pack(side="left", padx=10)

    parent.header_frame.lift()
    parent.update_idletasks()
    print(f"Created new header_frame in {parent} with children: {[w for w in parent.winfo_children()]}")
"""END HERE"""

"""ABOUT US WINDOW"""
def about_us_window():   
    if "aboutUs" not in active_windows or not active_windows["aboutUs"].winfo_exists():
        # Create top-level window
        tk_root.withdraw()
        aboutUs = ctk.CTkToplevel(tk_root)
        aboutUs.title("About Us")
        aboutUs.geometry(f"{WIDTH}x{HEIGHT}")
        aboutUs.configure(bg="#e5e5e5")
        center_window(aboutUs, WIDTH, HEIGHT)
        aboutUs.resizable(False, False)
        aboutUs.overrideredirect(True)
       
        # Create Navigation Bar
        create_navigation_bar(aboutUs)

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

"""END HERE"""


"""MANUAL WINDOW"""
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
        instructionWindow.resizable(False, False)
        instructionWindow.overrideredirect(True)

        # Create Navigation Bar (implement this function as needed)
        create_navigation_bar(instructionWindow)

        # Create canvas and scrollbar
        canvas = tk.Canvas(instructionWindow, bg="#e5e5e5")
        scrollbar = ttk.Scrollbar(instructionWindow, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#e5e5e5")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Title Section
        title_label = tk.Label(scrollable_frame, text="Instruction Manual", font=("Arial", 35, "bold"), bg="#e5e5e5")
        title_label.pack(pady=(35, 53), padx=25, anchor='w')

        # How to Collect Data Section
        collect_label = tk.Label(scrollable_frame, text="How to Collect Data", font=("Arial", 25, "bold"), bg="#e5e5e5")
        collect_label.pack(anchor="w", pady=(1, 25), padx=25)

        tools_label = tk.Label(scrollable_frame, text="-----------------------------------------------------------------------Tools You'll Need:-----------------------------------------------------------------------------", font=("Arial", 22), bg="#e5e5e5")
        tools_label.pack(anchor="w", padx=40)

        image_files = [
            ("im1.png", "Smartphone"),
            ("im2.png", "Tripod Stand"),
            ("im3.png", "Measuring Tape"),
            ("im4.png", "Colored Chalk"),
            ("im5.png", "Stadia Rod"),
            ("im6.png", "Meter Stick"),
            ("im7.png", "Pampatay sa bampira")
        ]

        # Canvas for image gallery
        img_canvas = tk.Canvas(scrollable_frame, width=1200, height=350, bg="#0C1822", highlightthickness=0, relief="flat")
        img_canvas.pack(pady=20)

        # Frame to hold images
        frame = tk.Frame(img_canvas, bg="#0C1822")
        img_canvas.create_window((0, 0), window=frame, anchor="nw")

        # Function to create rounded corner images
        def add_rounded_corners(image, radius):
            mask = Image.new("L", image.size, 0)
            draw = ImageDraw.Draw(mask)
            
            draw.rounded_rectangle((0, 0, image.width, image.height), radius=radius, fill=255)
            
            rounded = Image.new("RGBA", image.size)
            rounded.paste(image, (0, 0), mask)
            
            return rounded

        # Hover text label
        tooltip = tk.Label(instructionWindow, text="", bg="#333333", fg="white", font=("Helvetica", 12, "bold"), padx=10, pady=5)
        tooltip.place_forget()

        # Hover functions
        def on_hover(event, text):
            tooltip.config(text=text)
            tooltip.place(
                x=event.x_root - instructionWindow.winfo_rootx() + 15,
                y=event.y_root - instructionWindow.winfo_rooty() + 15
            )

        def on_leave(event):
            tooltip.place_forget()

        # Load and display images with hover effect
        images = []
        labels = []

        for i, (file, hover_text) in enumerate(image_files):
            img = Image.open(file)
            img = img.resize((270, 315), Image.LANCZOS)

            img_rounded = add_rounded_corners(img, radius=40)

            img_tk = ImageTk.PhotoImage(img_rounded)
            images.append(img_tk)

            lbl = tk.Label(frame, image=img_tk, bg="#0C1822", relief="flat", bd=0)
            lbl.grid(row=0, column=i, padx=15, pady=10)
            labels.append(lbl)

            lbl.bind("<Enter>", lambda e, text=hover_text: on_hover(e, text))
            lbl.bind("<Leave>", on_leave)

        # Smooth scrolling functionality
        scroll_x = 0
        scroll_step = 60

        def smooth_scroll(direction):
            nonlocal scroll_x
            max_scroll = (len(images) * 285) - img_canvas.winfo_width()

            if direction == "left" and scroll_x < 0:
                scroll_x += scroll_step
            elif direction == "right" and abs(scroll_x) < max_scroll:
                scroll_x -= scroll_step

            img_canvas.xview_moveto(-scroll_x / img_canvas.winfo_width())

        # Navigation buttons
        btn_left = ctk.CTkButton(
            scrollable_frame, text="❮",
            command=lambda: smooth_scroll("left"),
            fg_color="#333333", hover_color="#555555",
            text_color="white",
            width=5, height=250,
            corner_radius=10, font=("Helvetica", 18, "bold")
        )
        btn_left.place(x=170, y=180)
    

        btn_right = ctk.CTkButton(
            scrollable_frame, text="❯",
            command=lambda: smooth_scroll("right"),
            fg_color="#333333", hover_color="#555555",
            text_color="white",
            width=5, height=250,
            corner_radius=10, font=("Helvetica", 18, "bold")
        )
        btn_right.place(x=1001, y=180)

        # Update canvas scroll region
        frame.update_idletasks()
        img_canvas.config(scrollregion=img_canvas.bbox("all"))

        # Steps for Data Gathering
        steps_label = tk.Label(scrollable_frame, text="Steps for Data Gathering", font=("Arial", 25, "bold"), bg="#e5e5e5")
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
            tk.Label(scrollable_frame, text=f"{i}. {step}", bg="#e5e5e5",font=("Arial", 16)).pack(anchor="w", padx=40, pady=2)

        # How to Use the System
        use_label = tk.Label(scrollable_frame, text="How to Use the System", font=("Arial", 16, "bold"), bg="#e5e5e5")
        use_label.pack(anchor="w", padx=20, pady=10)

        use_steps = [
            "Step 1: Import the Images - Upload images to the system.",
            "Step 2: Name the file and provide a description. (Optional)",
            "Step 3: Wait for processing. Once completed, the survey information will be displayed."
        ]

        for step in use_steps:
            tk.Label(scrollable_frame, text=step, bg="#e5e5e5",font=("Arial", 16)).pack(anchor="w", padx=40, pady=2)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        active_windows["instructionWindow"] = instructionWindow


    close_all_windows(active_windows["instructionWindow"])
    active_windows["instructionWindow"].deiconify()

"""LOGOUT"""
popup = None  # Global variable to track the popup window
logged_in_email = ""

def get_logged_in_email():
    """Retrieve the logged-in email from Firestore."""
    global logged_in_email
    return logged_in_email if logged_in_email else "No User Logged In"

def show_logout():
    global popup

    if popup and popup.winfo_exists():
        popup.destroy()
        popup = None
    else:
        popup = ctk.CTkToplevel(tk_root)
        popup.geometry("220x120+1500+169")
        popup.configure(fg_color="white")
        popup.overrideredirect(True)

        # Fetch the logged-in email
        user_email = get_logged_in_email()

        # Email Display
        email_label = ctk.CTkLabel(popup, text=user_email, font=("Arial", 12), text_color="black")
        email_label.pack(pady=(20, 10))

        # Logout Button
        logout_button = ctk.CTkButton(popup, text="Logout", fg_color="black", text_color="white",
                                      hover_color="gray", command=logout)
        logout_button.pack(pady=10)

def logout():
    global is_logged_in, logged_in_email

    is_logged_in = False
    logged_in_email = None

    # Destroy all top-level windows to avoid conflicts
    for window in list(active_windows.values()):
        if window.winfo_exists():
            print(f"Destroying top-level window: {window}")
            window.destroy()

    active_windows.clear()

    # Hide all top-level windows and refresh navbar
    tk_root.deiconify()
    create_navigation_bar(tk_root)
    tk_root.update()

    messagebox.showinfo("Logged Out", "You have been successfully logged out.")

"""END HERE"""


        
"""LOGIN FUNCTIONALITY"""
REMEMBER_ME_FILE = "remember_me.json"


# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
# Function to save credentials
def save_credentials(email):
    with open(REMEMBER_ME_FILE, "w") as f:
        json.dump({"email": email}, f)

# Function to load saved credentials
def load_credentials():
    if os.path.exists(REMEMBER_ME_FILE):
        with open(REMEMBER_ME_FILE, "r") as f:
            data = json.load(f)
            return data.get("email", "")
    return ""
# Function to check credentials
is_logged_in = False  

def login(email_entry, password_entry, remember_var, parent_window):
    global is_logged_in, logged_in_email

    email = email_entry.get()
    password = password_entry.get()

    if not email or not password:
        messagebox.showerror("Error", "Please enter both email and password.")
        return

    hashed_password = hash_password(password)

    try:
        users_ref = db.collection("users").where("email", "==", email).stream()
        for user in users_ref:
            user_data = user.to_dict()
            if user_data["password"] == hashed_password:
                if remember_var.get():
                    save_credentials(email)

                messagebox.showinfo("Success", "Login successful!")

                # Update login state
                is_logged_in = True
                logged_in_email = email

                # Destroy all top-level windows
                for window in list(active_windows.values()):
                    if window.winfo_exists():
                        print(f"Closing window: {window}")
                        window.destroy()

                active_windows.clear()

                # Ensure the main window is visible
                tk_root.deiconify()
                tk_root.lift()
                tk_root.focus_force()

                # Refresh the main window's navbar
                create_navigation_bar(tk_root)
                tk_root.update()

                return

        messagebox.showerror("Error", "Invalid email or password.")

    except Exception as e:
        messagebox.showerror("Error", f"Firestore error: {str(e)}")





def close_window():
    login_window.destroy()

def show_login_window():
    global login_window, email_entry, password_entry, remember_var, toggle_button
    
    # Create the login window
    login_window = ctk.CTkToplevel(tk_root)
    login_window.title("Login")
    login_window.configure(fg_color="white")
    login_window.overrideredirect(True)
    
    # Define login window size
    window_width = 500
    window_height = 500
    
    # Make sure the window opens in the foreground
    login_window.attributes('-topmost', True)

    # Set the position and size
    login_window.geometry(f"{window_width}x{window_height}+{560}+{169}")
    
    # Remove topmost attribute after placement
    login_window.after(100, lambda: login_window.attributes('-topmost', False))
    saved_email = load_credentials()
        # Close Button (X)
    close_button = ctk.CTkButton(
        login_window, text="X", font=("Poppins", 14, "bold"),
        fg_color="white", text_color="#00b3b3", width=30, height=30,
        corner_radius=0, border_width=0, command=login_window.destroy
    )
    close_button.place(x=450, y=10)
    ctk.CTkLabel(login_window, text="LOGIN", font=("Poppins", 30, "bold"), text_color="#09AAA3").pack(pady=(50, 20))

    ctk.CTkLabel(login_window, text="Email", font=("Poppins", 14)).pack(anchor="w", padx=50)
    email_entry = ctk.CTkEntry(login_window, width=350, font=("Poppins", 14))
    email_entry.pack(anchor="w",pady=10,padx=52)
    email_entry.insert(0, saved_email)

    # Ensure Password Label is Visible
    password_label = ctk.CTkLabel(login_window, text="Password", font=("Poppins", 14))
    password_label.pack(anchor="w", padx=50, pady=(10, 0))  # Ensure correct placement

    # Password Entry + Eye Button Frame
    password_frame = ctk.CTkFrame(login_window, fg_color="transparent")
    password_frame.pack(pady=5)

    # Password Entry
    password_entry = ctk.CTkEntry(password_frame, width=350, font=("Poppins", 14), show="*")
    password_entry.pack(side="left", padx=(0, 5))

    # Eye Toggle Button (inside password field)
    toggle_button = ctk.CTkButton(password_frame, text="", width=30, height=30, fg_color="transparent",
                                  image=eye_closed_img, command=toggle_password)
    toggle_button.pack(side="left")

    # Remember Me Checkbox
    remember_var = tk.BooleanVar(value=bool(saved_email))
    remember_me = ctk.CTkCheckBox(login_window, text="Remember Me ?", variable=remember_var, font=("Poppins", 12))
    remember_me.pack(anchor="w", padx=50, pady=10)

    # Login Button
    login_btn = ctk.CTkButton(login_window, text="LOGIN", font=("Poppins", 14, "bold"), fg_color="#00b3b3",
                              text_color="white", width=200, height=40, command=lambda: login(email_entry, password_entry, remember_var,tk_root))
    login_btn.pack(pady=20)

    # Forgot Password Label
    forgot_label = ctk.CTkLabel(
        login_window, text="Forgot Password ?", text_color="gray",
        fg_color="transparent", font=("Poppins", 12), cursor="hand2"
    )
    forgot_label.pack()

    # Divider Line
    ctk.CTkLabel(login_window, text="_________________ or _________________", text_color="gray", 
                fg_color="transparent", font=("Poppins", 12)).pack(pady=7)


    # Signup Link
    signup_label = ctk.CTkLabel(login_window, text="Need an account? SIGN UP", text_color="#00b3b3",
                                font=("Poppins", 12, "bold"), cursor="hand2")
    signup_label.pack(pady=5)
    signup_label.bind("<Button-1>", lambda e: show_signup_window())

    login_window.focus_force()
 # Load eye images
eye_open_img = ctk.CTkImage(Image.open("view.png"), size=(25, 25))
eye_closed_img = ctk.CTkImage(Image.open("hide.png"), size=(25, 25))
def toggle_password():
    """Toggle password visibility and switch eye icon."""
    if password_entry.cget("show") == "*":
        password_entry.configure(show="")  # Show password
        toggle_button.configure(image=eye_open_img)  # Switch to open eye image
    else:
        password_entry.configure(show="*")  # Hide password
        toggle_button.configure(image=eye_closed_img)  # Switch to closed eye image
"""END HERE"""


"""SIGN UP"""
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def show_signup_window():
    
    # Create the sign-up window
    signup_window = ctk.CTkToplevel(tk_root)
    signup_window.title("Sign Up")
    signup_window.configure(fg_color="white")
    signup_window.overrideredirect(True)  # Remove window decorations

     # Define login window size
    window_width = 500
    window_height = 500
    
    # Make sure the window opens in the foreground
    signup_window.attributes('-topmost', True)

    # Set the position and size
    signup_window.geometry(f"{window_width}x{window_height}+{560}+{169}")
    
    # Remove topmost attribute after placement
    signup_window.after(100, lambda: signup_window.attributes('-topmost', False))

    # Close Button (X)
    close_button = ctk.CTkButton(
        signup_window, text="X", font=("Poppins", 14, "bold"),
        fg_color="white", text_color="#00b3b3", width=30, height=30,
        corner_radius=0, border_width=0, command=signup_window.destroy
    )
    close_button.place(x=450, y=10)

    # Sign-Up Label
    signup_label = ctk.CTkLabel(
        signup_window, text="SIGN UP", font=("Poppins", 30, "bold"),
        text_color="#00b3b3", fg_color="transparent"
    )
    signup_label.pack(pady=(50, 20))

    # Email Label & Entry
    ctk.CTkLabel(signup_window, text="Email", fg_color="transparent", font=("Poppins", 14)).pack(anchor="w", padx=50)
    email_entry = ctk.CTkEntry(signup_window, width=400, font=("Poppins", 14))
    email_entry.pack(pady=5)

    # Password Label & Entry
    ctk.CTkLabel(signup_window, text="Password", fg_color="transparent", font=("Poppins", 14)).pack(anchor="w", padx=50)
    password_entry = ctk.CTkEntry(signup_window, width=400, font=("Poppins", 14), show="*")
    password_entry.pack(pady=5)

    # Confirm Password Label & Entry
    ctk.CTkLabel(signup_window, text="Confirm Password", fg_color="transparent", font=("Poppins", 14)).pack(anchor="w", padx=50)
    confirm_password_entry = ctk.CTkEntry(signup_window, width=400, font=("Poppins", 14), show="*")
    confirm_password_entry.pack(pady=5)

    # Sign-Up Button
    signup_btn = ctk.CTkButton(
        signup_window, text="SIGN UP", font=("Poppins", 14, "bold"),
        fg_color="#00b3b3", text_color="white", width=250, height=40,
        command=lambda: sign_up(email_entry, password_entry, confirm_password_entry)  # Pass the entry fields
    )
    signup_btn.pack(pady=20)
    # Divider Line
    ctk.CTkLabel(signup_window, text="_________________ or _________________", text_color="gray",
                 fg_color="transparent", font=("Poppins", 12)).pack(pady=5)

    # Already have an account? LOGIN
    login_label = ctk.CTkLabel(
        signup_window, text="Already a user? LOGIN", text_color="#00b3b3",
        fg_color="transparent", font=("Poppins", 12, "bold"), cursor="hand2"
    )
    login_label.pack(pady=5)
    login_label.bind("<Button-1>", lambda e: show_login_window())

    # Focus on the sign-up window
    signup_window.focus_force()

def sign_up(email_entry, password_entry, confirm_password_entry):
    email = email_entry.get()
    password = password_entry.get()
    confirm_password = confirm_password_entry.get()

    # Validate input
    if not email or not password or not confirm_password:
        messagebox.showerror("Error", "Please fill all fields.")
        return

    if password != confirm_password:
        messagebox.showerror("Error", "Passwords do not match.")
        return

    # Hash the password
    hashed_password = hash_password(password)

    # Store user in Firestore
    try:
        db.collection("users").add({
            "email": email,
            "password": hashed_password  # Store hashed password
        })
        messagebox.showinfo("Success", "Account created successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Firestore error: {str(e)}")
"""END HERE"""


"""FUNCTION FOR CENTERING THE WINDOWS"""
# Function to center any window
def center_window(window, width, height):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")
    window.update()
"""END HERE"""

"""SURVEY FOLDER"""
def custom_input_dialog():
    dialog = ctk.CTkToplevel()
    dialog.title("Survey")
   
    dialog.geometry("300x175+800+300")
    dialog.configure(fg_color="white")
    dialog.resizable(False, False)
    dialog.overrideredirect(True)

    # Close Button (Top Right)
    close_button = ctk.CTkButton(
        dialog, text="✕", font=("Poppins", 14, "bold"),
        fg_color="white", text_color="#00b3b3", width=30, height=30,
        corner_radius=5, border_width=0, command=dialog.destroy
    )
    close_button.place(relx=1.0, x=-10, y=10, anchor="ne")  # Positions at the top-right

    # Label
    ctk.CTkLabel(dialog, text="Enter folder name:", font=("Poppins", 14), text_color="black").pack(pady=(40, 5))

    # Entry Field
    entry = ctk.CTkEntry(dialog, font=("Poppins", 12), width=200, fg_color="white", text_color="black")
    entry.pack(pady=5)

    result = ctk.StringVar()

    def submit():
        result.set(entry.get())
        dialog.destroy()

    # OK Button (Bottom Right)
    submit_button = ctk.CTkButton(
        dialog, text="OK", command=submit, font=("Arial", 14, "bold"),
        fg_color="#00b3b3", text_color="white", corner_radius=5, width=70, height=30
    )
    submit_button.place(relx=1.0, rely=1.0, x=-15, y=-15, anchor="se")  # Bottom right positioning

    dialog.grab_set()  # Make modal
    dialog.wait_window()  # Wait until closed

    return result.get()




def add_survey():
    folder_name = custom_input_dialog()
    if folder_name:
        folder_path = os.path.join(SURVEY_DIR, folder_name)
        try:
            os.makedirs(folder_path, exist_ok=True)
            display_folder(folder_name)  # Display newly created folder
            messagebox.showinfo("Survey", f"Folder '{folder_name}' created successfully!", parent=surveyFolder)
        except Exception as e:
            messagebox.showerror("Error", f"Could not create folder:\n{str(e)}")

def delete_survey(folder_widget, folder_path):
    try:
        shutil.rmtree(folder_path)  # Recursively delete the folder and its contents
        folder_widget.destroy()     # Remove from UI
        messagebox.showinfo("Deleted", "Folder deleted successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Could not delete folder:\n{str(e)}")

def display_folder(folder_name):
    """Displays a folder in the survey window."""
    folder_path = os.path.join(SURVEY_DIR, folder_name)

    # Create Folder Display Frame
    folder_frame = tk.Frame(scrollable_frame, bg="#d3d3d3", padx=10, pady=5, height=200)
    folder_frame.pack(fill="x", pady=5)
    folder_frame.pack_propagate(False)

    # Load Image using Pillow
    image_path = "Folder.png"
    image_pil = Image.open(image_path).resize((150, 150), Image.Resampling.LANCZOS)
    image = ImageTk.PhotoImage(image_pil)

    image_label = ctk.CTkLabel(folder_frame, image=image, text="")
    image_label.image = image
    image_label.pack(side="left", padx=10)

    # Folder Info
    folder_info_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
    folder_info_frame.pack(side="left", padx=10)

    folder_label = ctk.CTkLabel(folder_info_frame, text=folder_name, font=("Poppins", 16, "bold"))
    folder_label.grid(row=0, column=0, sticky="w")

    edit_label = ctk.CTkLabel(folder_info_frame, text="edit", font=("Poppins", 14, "underline"), cursor="hand2")
    edit_label.grid(row=0, column=1, sticky="w")

    file_count_label = ctk.CTkLabel(folder_info_frame, text=f"{len(os.listdir(folder_path))} files", font=("Poppins", 14, "italic"))
    file_count_label.grid(row=1, column=0, sticky="w")

    # Folder creation timestamp
    creation_time = os.path.getctime(folder_path)
    timestamp = datetime.fromtimestamp(creation_time).strftime("%B %d, %Y | %I:%M %p")
    time_label = ctk.CTkLabel(folder_info_frame, text=timestamp, font=("Poppins", 14, "italic"))
    time_label.grid(row=2, column=0, sticky="w")

    # Buttons Frame
    button_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
    button_frame.pack(side="bottom", anchor="se", padx=10, pady=10)

    view_btn = ctk.CTkButton(button_frame, text="View", font=("Poppins", 14, "bold"), fg_color="#18a999", text_color="white", corner_radius=5,command=lambda: view_survey_files(folder_name))
    view_btn.pack(side="left", padx=5)

    delete_btn = ctk.CTkButton(button_frame, text="Delete", font=("Poppins", 14, "bold"), fg_color="#ff5252", text_color="white", corner_radius=5,
                                command=lambda: delete_survey(folder_frame, folder_path))
    delete_btn.pack(side="left", padx=5)

def load_existing_surveys():
    folders = [f for f in os.listdir(SURVEY_DIR) if os.path.isdir(os.path.join(SURVEY_DIR, f))]
    for folder in folders:
        display_folder(folder)  # Display each folder


def parse_survey_file(file_path):
    """Extracts Date, Location, Description, and Metrics from a survey file."""
    details = {
        "Date": "Unknown",
        "Location": "Unknown",
        "Description": "No description available.",
        "Metrics": {
            "Horizontal Distance": "N/A",
            "Vertical Angle": "N/A",
            "Slope": "N/A",
            "Elevation": "N/A"
        }
    }

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

            # Parse each line
            for i, line in enumerate(lines):
                line = line.strip()

                if line.startswith("Date:"):
                    details["Date"] = line.replace("Date:", "").strip()
                elif line.startswith("Location:"):
                    details["Location"] = line.replace("Location:", "").strip()
                elif line.startswith("Description:"):
                    details["Description"] = lines[i+1].strip() if i+1 < len(lines) else "No description available."
                elif line.startswith("- Horizontal Distance:"):
                    details["Metrics"]["Horizontal Distance"] = line.split(":")[1].strip()
                elif line.startswith("- Vertical Angle:"):
                    details["Metrics"]["Vertical Angle"] = line.split(":")[1].strip()
                elif line.startswith("- Slope:"):
                    details["Metrics"]["Slope"] = line.split(":")[1].strip()
                elif line.startswith("- Elevation:"):
                    details["Metrics"]["Elevation"] = line.split(":")[1].strip()

    except Exception as e:
        print(f"Error reading file {file_path}: {e}")

    return details

def view_survey_files(folder_name):
    """Displays all text files in the selected folder dynamically."""
    folder_path = os.path.join(SURVEY_DIR, folder_name)

    # Destroy previous window if it exists to prevent data leakage
    if "view_window" in active_windows and active_windows["view_window"].winfo_exists():
        active_windows["view_window"].destroy()

    tk_root.withdraw()
    view_window = ctk.CTkToplevel(tk_root)
    view_window.title(f"Surveys in {folder_name}")
    view_window.geometry(f"{WIDTH}x{HEIGHT}")
    view_window.configure(bg="#e5e5e5")
    center_window(view_window, WIDTH, HEIGHT)
    view_window.resizable(False, False)

    create_navigation_bar(view_window)

    # Scrollable Frame
    scrollable_frame = ctk.CTkFrame(view_window, fg_color="transparent")
    scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # List all text files in the folder
    files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]

    if not files:
        # If no files, display "No text files found."
        empty_label = ctk.CTkLabel(scrollable_frame, text="No text files found.", font=("Poppins", 16, "italic"))
        empty_label.pack(pady=10)
        active_windows["view_window"] = view_window
        

    for file in files:
        file_path = os.path.join(folder_path, file)
        survey_details = parse_survey_file(file_path)

        # Create a frame for each survey file
        file_frame = ctk.CTkFrame(scrollable_frame, fg_color="white", corner_radius=10)
        file_frame.pack(fill="x", padx=5, pady=5)
        file_frame.pack_propagate(False)

        # Load and display an image (placeholder)
        image_path = "Folder.png"  # Adjust if using another image
        image_pil = Image.open(image_path).resize((80, 80), Image.Resampling.LANCZOS)
        image = ImageTk.PhotoImage(image_pil)

        image_label = ctk.CTkLabel(file_frame, image=image, text="")
        image_label.image = image  # Prevent garbage collection
        image_label.pack(side="left", padx=10, pady=5)

        # Text information frame
        text_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Date
        date_label = ctk.CTkLabel(text_frame, text=f"Date: {survey_details['Date']}", font=("Poppins", 12, "bold"))
        date_label.pack(anchor="w")

        # Location
        location_label = ctk.CTkLabel(text_frame, text=f"Location: {survey_details['Location']}", font=("Poppins", 12))
        location_label.pack(anchor="w")

        # Description
        description_label = ctk.CTkLabel(text_frame, text="Description:", font=("Poppins", 12, "bold"))
        description_label.pack(anchor="w")

        description_text_label = ctk.CTkLabel(
            text_frame,
            text=survey_details["Description"],
            font=("Poppins", 12),
            wraplength=400,
            justify="left"
        )
        description_text_label.pack(anchor="w", padx=10)

        # Survey Metrics
        metrics_label = ctk.CTkLabel(text_frame, text="Survey Metrics:", font=("Poppins", 12, "bold"))
        metrics_label.pack(anchor="w", pady=(5, 0))

        metrics_text = "\n".join(
            [f"- {key}: {value}" for key, value in survey_details["Metrics"].items()]
        )

        metrics_text_label = ctk.CTkLabel(text_frame, text=metrics_text, font=("Poppins", 12), justify="left")
        metrics_text_label.pack(anchor="w", padx=10)

        # Menu Button (Placeholder for actions)
        menu_btn = ctk.CTkButton(file_frame, text="⋮", width=30, fg_color="white", text_color="black", corner_radius=5)
        menu_btn.pack(side="right", padx=10)

    active_windows["view_window"] = view_window  # Store reference to prevent multiple windows

    close_all_windows(active_windows["view_window"])
    active_windows["view_window"].deiconify()


def open_survey_folder_window():
    global scrollable_frame, surveyFolder
    if "surveyFolder" not in active_windows or not active_windows["surveyFolder"].winfo_exists():
        tk_root.withdraw()
        surveyFolder = ctk.CTkToplevel(tk_root)
        surveyFolder.title("Survey Folder")
        surveyFolder.geometry(f"{WIDTH}x{HEIGHT}")
        surveyFolder.configure(bg="#e5e5e5")
        center_window(surveyFolder, WIDTH, HEIGHT)
        surveyFolder.resizable(False, False)

        create_navigation_bar(surveyFolder)
        screen_width = surveyFolder.winfo_screenwidth()

        add_folder_frame = ctk.CTkFrame(surveyFolder, fg_color="#d3d3d3", height=100, corner_radius=0, width=screen_width)
        add_folder_frame.pack(fill="x", pady=10)
        add_folder_frame.pack_propagate(False)

        plus_btn = ctk.CTkButton(
            add_folder_frame, text="+", font=("Poppins", 28, "bold"),
            width=50, height=50, fg_color="white", text_color="black",
            hover_color="#bfbfbf", corner_radius=10,
            command=add_survey
        )
        plus_btn.pack(side="left", padx=20, pady=10)

        add_folder_label = ctk.CTkButton(
            add_folder_frame, text="Add new survey folder", font=("Poppins", 18, "bold"),
            fg_color="#d3d3d3", text_color="black", hover_color="#bfbfbf",
            border_width=0, corner_radius=10, command=add_survey
        )
        add_folder_label.pack(side="left", padx=10)

        surveyFolderFrame = ctk.CTkFrame(surveyFolder, fg_color="#e5e5e5")
        surveyFolderFrame.pack(fill="both", expand=True)

        canvas = tk.Canvas(surveyFolderFrame, bg="#e5e5e5", highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(surveyFolderFrame, orientation="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas, fg_color="#e5e5e5")

        def update_frame_width(event):
            canvas_width = event.width
            scrollable_frame.configure(width=canvas_width)
            canvas.itemconfig(frame_window, width=canvas_width)

        canvas.bind("<Configure>", update_frame_width)
        frame_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        load_existing_surveys()  # Load and display existing surveys

        active_windows["surveyFolder"] = surveyFolder

    close_all_windows(active_windows["surveyFolder"])
    active_windows["surveyFolder"].deiconify()
"""END HERE"""





"""MAIN WINDOW"""
# Create main window
tk_root = ctk.CTk()
tk_root.title("EleVista")
tk_root.geometry(f"{WIDTH}x{HEIGHT}")
tk_root.iconbitmap("LOGO.ico")
tk_root.resizable(False, False)

# Center main window
center_window(tk_root, WIDTH, HEIGHT)
# tk_root.overrideredirect(True)

# Load background image
bg_image = Image.open("HomeBackground.png")
bg_image = bg_image.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
bg_photo = ctk.CTkImage(light_image=bg_image, dark_image=bg_image, size=(WIDTH, HEIGHT))

# Create a background label
bg_label = ctk.CTkLabel(tk_root, image=bg_photo, text="", fg_color="transparent")
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# ✅ Define Global is_logged_in Variable
is_logged_in = False

# ✅ Call Navigation Bar Function
create_navigation_bar(tk_root)
"""ENDS HERE"""

   
"""LOADING SCREEN"""
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
   
    loading_window.resizable(False, False)
    loading_window.overrideredirect(True)
    
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

    create_navigation_bar(loading_window) 
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
"""ENDS HERE"""


"""UPLOAD FILE FUNCTION"""
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
        survey_window.resizable(False, False)
        # survey_window.overrideredirect(True)

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

        create_navigation_bar(survey_window) 
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
"""ENDS HERE"""


"""SURVEY RESULT WINDOW"""
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
    survey_result_window.resizable(False, False)
    survey_result_window.overrideredirect(True)
    create_navigation_bar(survey_result_window)

    # Main Content Frame
    main_frame = ctk.CTkFrame(survey_result_window, fg_color="transparent")
    main_frame.pack(pady=40, padx=20, fill="both", expand=True)

    # Left - Image Frame
    img_frame = ctk.CTkFrame(main_frame, fg_color="transparent", width=350, height=350)
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
    details_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    details_frame.pack(side="left", padx=20)

    # Title and Time
    title_label = ctk.CTkLabel(details_frame, text="Survey 1", font=("Arial", 22, "bold"), text_color="#333333")
    title_label.pack(anchor="w")

    date_label = ctk.CTkLabel(details_frame, text="March 8, 2025 | 9:21PM", font=("Arial", 12, "italic"), text_color="#555555")
    date_label.pack(anchor="w")

    # Location
    location_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
    location_frame.pack(anchor="w", pady=5)

    bullet_label = ctk.CTkLabel(location_frame, text="●", font=("Arial", 12), text_color="#333333")
    bullet_label.pack(side="left")

    location_label = ctk.CTkLabel(location_frame, text="Sorosoro, Batangas City", font=("Arial", 12), text_color="#333333")
    location_label.pack(side="left", padx=5)

    edit_label = ctk.CTkLabel(location_frame, text="edit", font=("Arial", 10, "underline"), text_color="#555555", cursor="hand2")
    edit_label.pack(side="left")

    # Description
    desc_label_frame = ctk.CTkFrame(details_frame, fg_color="transparent", width=350)
    desc_label_frame.pack(anchor="w", pady=3, fill="x", expand=True)

    desc_label = ctk.CTkLabel(desc_label_frame, text="Description:", font=("Arial", 12, "bold"), text_color="#333333")
    desc_label.pack(side="left", pady=(10, 3))
    desc_edit_label = ctk.CTkLabel(desc_label_frame, text="edit", font=("Arial", 10, "underline"), text_color="#555555", cursor="hand2")
    desc_edit_label.pack(side="right", pady=3)

    desc_textbox = ctk.CTkTextbox(details_frame, width=350, height=100, fg_color="white", border_color="#e5e5e5")
    desc_textbox.pack()

    # Survey Metrics
    metrics = [
        ("Horizontal Distance:", "N/A"),
        ("Vertical Angle:", "N/A"),
        ("Slope:", "N/A"),
        ("Elevation:", "N/A")
    ]

    for label_text, value in metrics:
        frame = ctk.CTkFrame(details_frame, fg_color="transparent")
        frame.pack(anchor="w", pady=2, fill="x")
        
        label = ctk.CTkLabel(frame, text=label_text, font=("Arial", 12, "bold"), text_color="#333333")
        label.pack(side="left", padx=(0, 10))  # Adds some space between label and value
        
        value_label = ctk.CTkLabel(frame, text=value, font=("Arial", 12), text_color="#333333")
        value_label.pack(side="left")



    def save_to_new_survey_folder():
    # Ask user to name the new survey folder
        folder_name = custom_input_dialog()

        if folder_name:
            new_folder_path = os.path.join(SURVEY_DIR, folder_name)

            # Check if the folder already exists
            if os.path.exists(new_folder_path):
                messagebox.showerror("Error", "A folder with this name already exists.")
                return

            try:
                os.makedirs(new_folder_path)

                # Once folder is created, save survey just like your existing function
                date = date_label.cget("text").strip()
                location = location_label.cget("text").strip()
                description = desc_textbox.get("1.0", tk.END).strip()

                if not date or not location or not description:
                    messagebox.showwarning("Warning", "Please ensure all fields are filled before saving.")
                    return

                # Survey Metrics (you can make this dynamic later)
                metrics = {
                    "Horizontal Distance": "N/A",
                    "Vertical Angle": "N/A",
                    "Slope": "N/A",
                    "Elevation": "N/A"
                }

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = os.path.join(new_folder_path, f"survey_{timestamp}.txt")

                # Ensure unique file name
                counter = 1
                while os.path.exists(file_path):
                    file_path = os.path.join(new_folder_path, f"survey_{timestamp}_{counter}.txt")
                    counter += 1

                # Save details to the file
                with open(file_path, "w") as file:
                    file.write(f"Date: {date}\n")
                    file.write(f"Location: {location}\n")
                    file.write(f"Description:\n{description}\n\n")
                    file.write("Survey Metrics:\n")
                    for key, value in metrics.items():
                        file.write(f"- {key}: {value}\n")

                # Check if the user is logged in
                if is_logged_in:
                    # Save to Firestore
                    db.collection("surveys").add({
                        "user_email": logged_in_email,
                        "file_path": file_path,
                        "folder_name": os.path.basename(new_folder_path),
                        "date": date,
                        "location": location,
                        "description": description,
                        "metrics": metrics,
                        "timestamp": firestore.SERVER_TIMESTAMP
                    })
                    messagebox.showinfo("Success", f"Survey saved in new folder:\n{new_folder_path} and also in the database.")
                else:
                    messagebox.showinfo("Success", f"Survey saved locally in:\n{new_folder_path}.")

            except Exception as e:
                messagebox.showerror("Error", f"Could not create/save to folder:\n{str(e)}")

        else:
            messagebox.showwarning("Cancelled", "Folder creation cancelled.")




    def save_survey_details():
        folder_selected = filedialog.askdirectory(initialdir=SURVEY_DIR, title="Select an Existing Survey Folder")
        
        if folder_selected:  # Ensure user selected a folder
            # Get values from the UI fields
            date = date_label.cget("text").strip()
            location = location_label.cget("text").strip()
            description = desc_textbox.get("1.0", tk.END).strip()  # Get text from Textbox

            # Survey Metrics (static for now, can be dynamic if needed)
            metrics = {
                "Horizontal Distance": "N/A",
                "Vertical Angle": "N/A",
                "Slope": "N/A",
                "Elevation": "N/A"
            }

            # Ensure required fields are not empty
            if not date or not location or not description:
                messagebox.showwarning("Warning", "Please ensure all fields are filled before saving.")
                return

            try:
                # Generate a unique file name using timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Example: 20250403_121530
                file_path = os.path.join(folder_selected, f"survey_{timestamp}.txt")

                # Ensure no overwriting
                counter = 1
                while os.path.exists(file_path):  # Check if file already exists
                    file_path = os.path.join(folder_selected, f"survey_{timestamp}_{counter}.txt")
                    counter += 1

                # Save survey details to a uniquely named file
                with open(file_path, "w") as file:
                    file.write(f"Date: {date}\n")
                    file.write(f"Location: {location}\n")
                    file.write(f"Description:\n{description}\n\n")
                    file.write("Survey Metrics:\n")
                    for key, value in metrics.items():
                        file.write(f"- {key}: {value}\n")

                # Check if the user is logged in
                if is_logged_in:
                    # Save to Firestore
                    db.collection("surveys").add({
                        "user_email": logged_in_email,
                        "file_path": file_path,
                        "folder_name": os.path.basename(folder_selected),
                        "date": date,
                        "location": location,
                        "description": description,
                        "metrics": metrics,
                        "timestamp": firestore.SERVER_TIMESTAMP
                    })
                    messagebox.showinfo("Success", f"Survey details saved in: {file_path} and also in the database.")
                else:
                    messagebox.showinfo("Success", f"Survey details saved locally in: {file_path}.")

            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{str(e)}")
        else:
            messagebox.showwarning("Warning", "No folder selected. Please select a folder.")

    def popup_save():
        popup = ctk.CTkToplevel(tk_root)
        popup.geometry("200x125+800+500")
        popup.configure(fg_color="white")
        popup.overrideredirect(True)

        # Close Button (Top Right)
        close_button = ctk.CTkButton(
            popup, text="X", font=("Poppins", 14, "bold"),
            fg_color="white", text_color="#00b3b3", width=30, height=30,
            corner_radius=0, border_width=0, command=popup.destroy
        )
        close_button.place(relx=1.0, x=-5, y=5, anchor="ne")  # Positions at the top-right

        def save_new_and_close():
            popup.destroy()
            save_to_new_survey_folder()

        new_button = ctk.CTkButton(
        popup, text="Save to New Folder", fg_color="white", text_color="black",
        hover_color="#1abc9c", command=save_new_and_close
    )
        new_button.pack(pady=(40, 5))

        # Existing Button
        existing_button = ctk.CTkButton(
            popup, text="Save to Existing Folder", fg_color="white", text_color="black",
            hover_color="#1abc9c", command=save_survey_details
        )
        existing_button.pack(pady=5)

    # Create a bottom frame for the button
    button_frame = ctk.CTkFrame(survey_result_window, fg_color="transparent")
    button_frame.pack(side="bottom", fill="x", pady=20, padx=20, anchor="se")

    # Save button
    save_button = ctk.CTkButton(button_frame, text="SAVE", fg_color="#1abc9c", 
                                text_color="white", hover_color="#16a085",command=popup_save)
    save_button.pack(side="right", padx=10)


    def delTemp():
        messagebox.showinfo("Deleted","You have deleted!")
        go_home()

    delete_button = ctk.CTkButton(button_frame, text="DELETE", fg_color="#1abc9c", 
                                text_color="white", hover_color="#16a085",command=delTemp)
    delete_button.pack(side="right", padx=20)
"""ENDS HERE"""
   

# Run Application
tk_root.mainloop()








