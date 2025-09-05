import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from PIL import Image, ImageTk
import os

class LicensePlateVerifier:
    def __init__(self, root):
        self.root = root
        self.root.title("License Plate Detection Verifier")
        self.root.geometry("1200x800")
        
        # Data variables
        self.df = None
        self.current_index = 0
        self.image_folder = ""
        self.csv_file = ""
        self.unsaved_changes = False
        
        # GUI variables
        self.yes_columns = ['easyocr_yes', 'cnn_yes', 'hybrid_yes', 'hybrid_region_yes', 'hybrid_letter_yes', 'hybrid_digits_yes']
        self.button_vars = {}
        
        self.setup_gui()
        
    def setup_gui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Setup section
        setup_frame = ttk.LabelFrame(main_frame, text="Setup", padding=10)
        setup_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(setup_frame, text="Load CSV File", command=self.load_csv).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(setup_frame, text="Select Image Folder", command=self.select_folder).pack(side=tk.LEFT, padx=(0, 5))
        
        self.status_label = ttk.Label(setup_frame, text="Please load CSV and select image folder")
        self.status_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Content frame
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Image frame
        image_frame = ttk.LabelFrame(content_frame, text="Image", padding=10)
        image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.image_label = ttk.Label(image_frame, text="No image loaded")
        self.image_label.pack(expand=True)
        
        # Info and controls frame
        control_frame = ttk.Frame(content_frame)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        # File info
        info_frame = ttk.LabelFrame(control_frame, text="File Info", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.filename_label = ttk.Label(info_frame, text="Filename: -", wraplength=250)
        self.filename_label.pack(anchor=tk.W)
        
        self.progress_label = ttk.Label(info_frame, text="Progress: 0/0")
        self.progress_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Detection results
        results_frame = ttk.LabelFrame(control_frame, text="Detection Results", padding=10)
        results_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.easyocr_label = ttk.Label(results_frame, text="EasyOCR: -", wraplength=250)
        self.easyocr_label.pack(anchor=tk.W)
        
        self.cnn_label = ttk.Label(results_frame, text="CNN: -", wraplength=250)
        self.cnn_label.pack(anchor=tk.W, pady=(2, 0))
        
        self.hybrid_label = ttk.Label(results_frame, text="Hybrid: -", wraplength=250)
        self.hybrid_label.pack(anchor=tk.W, pady=(2, 0))
        
        # Verification buttons
        verify_frame = ttk.LabelFrame(control_frame, text="Verification", padding=10)
        verify_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create buttons for each yes column
        for col in self.yes_columns:
            frame = ttk.Frame(verify_frame)
            frame.pack(fill=tk.X, pady=2)
            
            # Label
            label_text = col.replace('_', ' ').title()
            ttk.Label(frame, text=label_text + ":", width=15).pack(side=tk.LEFT)
            
            # Current value display
            var = tk.StringVar()
            self.button_vars[col] = var
            current_label = ttk.Label(frame, textvariable=var, width=3, relief=tk.SUNKEN)
            current_label.pack(side=tk.LEFT, padx=(0, 5))
            
            # Y/N buttons
            ttk.Button(frame, text="Y", width=3, 
                      command=lambda c=col: self.set_verification(c, 'y')).pack(side=tk.LEFT, padx=1)
            ttk.Button(frame, text="N", width=3, 
                      command=lambda c=col: self.set_verification(c, 'n')).pack(side=tk.LEFT, padx=1)
            ttk.Button(frame, text="Clear", width=5, 
                      command=lambda c=col: self.set_verification(c, '')).pack(side=tk.LEFT, padx=(5, 0))
        
        # Navigation
        nav_frame = ttk.LabelFrame(control_frame, text="Navigation", padding=10)
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        nav_buttons_frame = ttk.Frame(nav_frame)
        nav_buttons_frame.pack(fill=tk.X)
        
        ttk.Button(nav_buttons_frame, text="Previous", command=self.previous_image).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(nav_buttons_frame, text="Next", command=self.next_image).pack(side=tk.LEFT)
        
        # Jump to specific index
        jump_frame = ttk.Frame(nav_frame)
        jump_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(jump_frame, text="Go to:").pack(side=tk.LEFT)
        self.jump_entry = ttk.Entry(jump_frame, width=8)
        self.jump_entry.pack(side=tk.LEFT, padx=(5, 5))
        ttk.Button(jump_frame, text="Go", command=self.jump_to_index).pack(side=tk.LEFT)
        
        # Save button
        save_frame = ttk.Frame(control_frame)
        save_frame.pack(fill=tk.X)
        
        ttk.Button(save_frame, text="Save Progress", command=self.save_csv, 
                  style="Accent.TButton").pack(fill=tk.X, pady=5)
        
        # Keyboard bindings
        self.root.bind('<Left>', lambda e: self.previous_image())
        self.root.bind('<Right>', lambda e: self.next_image())
        self.root.bind('<Control-s>', lambda e: self.save_csv())
        self.root.focus_set()  # Allow window to receive key events
        
    def load_csv(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.df = pd.read_csv(file_path)
                self.csv_file = file_path
                
                # Ensure all yes columns exist
                for col in self.yes_columns:
                    if col not in self.df.columns:
                        self.df[col] = ''
                
                self.current_index = 0
                self.update_status()
                messagebox.showinfo("Success", f"Loaded {len(self.df)} records from CSV")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")
    
    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Select image folder")
        if folder_path:
            self.image_folder = folder_path
            self.update_status()
            messagebox.showinfo("Success", f"Selected image folder: {folder_path}")
    
    def update_status(self):
        if self.df is not None and self.image_folder:
            self.status_label.config(text="Ready to verify images")
            self.load_current_image()
        else:
            missing = []
            if self.df is None:
                missing.append("CSV file")
            if not self.image_folder:
                missing.append("image folder")
            self.status_label.config(text=f"Please load: {', '.join(missing)}")
    
    def load_current_image(self):
        if self.df is None or self.current_index >= len(self.df):
            return
        
        # Get current row data
        row = self.df.iloc[self.current_index]
        filename = row['filename']
        
        # Update labels
        self.filename_label.config(text=f"Filename: {filename}")
        self.progress_label.config(text=f"Progress: {self.current_index + 1}/{len(self.df)}")
        
        # Update detection results
        self.easyocr_label.config(text=f"EasyOCR: {row.get('easyocr_result', 'N/A')}")
        self.cnn_label.config(text=f"CNN: {row.get('cnn_result', 'N/A')}")
        self.hybrid_label.config(text=f"Hybrid: {row.get('hybrid_result', 'N/A')}")
        
        # Update verification button states
        for col in self.yes_columns:
            value = str(row.get(col, '')).strip()
            self.button_vars[col].set(value if value else '-')
        
        # Load and display image
        image_path = os.path.join(self.image_folder, filename)
        
        try:
            if os.path.exists(image_path):
                # Load and resize image to fit display
                image = Image.open(image_path)
                
                # Calculate display size (max 600x400)
                display_width, display_height = 600, 400
                img_width, img_height = image.size
                
                # Calculate scale to fit within display bounds
                scale = min(display_width / img_width, display_height / img_height, 1.0)
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                self.image_label.config(image=photo, text="")
                self.image_label.image = photo  # Keep a reference
            else:
                self.image_label.config(image="", text=f"Image not found:\n{filename}")
                self.image_label.image = None
                
        except Exception as e:
            self.image_label.config(image="", text=f"Error loading image:\n{str(e)}")
            self.image_label.image = None
    
    def set_verification(self, column, value):
        if self.df is None or self.current_index >= len(self.df):
            return
        
        self.df.at[self.current_index, column] = value
        self.button_vars[column].set(value if value else '-')
        self.unsaved_changes = True
    
    def next_image(self):
        if self.df is None:
            return
        
        if self.current_index < len(self.df) - 1:
            self.current_index += 1
            self.load_current_image()
    
    def previous_image(self):
        if self.df is None:
            return
        
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current_image()
    
    def jump_to_index(self):
        if self.df is None:
            return
        
        try:
            index = int(self.jump_entry.get()) - 1  # Convert to 0-based index
            if 0 <= index < len(self.df):
                self.current_index = index
                self.load_current_image()
            else:
                messagebox.showerror("Error", f"Index must be between 1 and {len(self.df)}")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
        
        self.jump_entry.delete(0, tk.END)
    
    def save_csv(self):
        if self.df is None or not self.csv_file:
            messagebox.showerror("Error", "No data to save")
            return
        
        try:
            self.df.to_csv(self.csv_file, index=False)
            self.unsaved_changes = False
            messagebox.showinfo("Success", f"Progress saved to {self.csv_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save CSV: {str(e)}")
    
    def on_closing(self):
        if self.unsaved_changes:
            if messagebox.askyesno("Unsaved Changes", 
                                 "You have unsaved changes. Do you want to save before closing?"):
                self.save_csv()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = LicensePlateVerifier(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.mainloop()

if __name__ == "__main__":
    main()