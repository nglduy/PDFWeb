import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import sys
from pathlib import Path
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime

class CustomThemePDFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌟 PDF Tools - Custom Theme Demo")
        self.root.geometry("1000x800")
        
        # 🎨 EXAMPLE: Dark Purple Theme
        self.root.configure(bg='#2d1b69')  # Deep purple background
        
        # Initialize variables
        self.selected_files = []
        self.current_pdf_path = None
        self.current_pdf_pages = 0
        
        self.setup_custom_styles()
        self.create_interface()
    
    def setup_custom_styles(self):
        """🎨 CUSTOM THEME EXAMPLE - Dark Purple with Gold Accents"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # 🌟 CUSTOM COLOR PALETTE
        bg_primary = '#2d1b69'      # Deep purple background
        bg_secondary = '#3d2c8d'     # Lighter purple
        accent_color = '#ffd700'     # Gold accent
        text_primary = '#ffffff'     # White text
        text_secondary = '#e6e6fa'   # Light lavender
        card_bg = '#4a4a7a'         # Dark purple cards
        
        # Main title style - Large and dramatic
        self.style.configure('Title.TLabel', 
                           font=('Trebuchet MS', 42, 'bold'), 
                           foreground=accent_color,     # Gold title
                           background=bg_primary)
        
        # Subtitle style - Elegant
        self.style.configure('Subtitle.TLabel', 
                           font=('Trebuchet MS', 18, 'italic'), 
                           foreground=text_secondary, 
                           background=bg_primary)
        
        # Card frame style - Dark with border
        self.style.configure('CustomCard.TFrame',
                           background=card_bg,
                           relief='raised',
                           borderwidth=2)
        
        # Section heading style - Gold accent
        self.style.configure('SectionTitle.TLabel', 
                           font=('Trebuchet MS', 24, 'bold'), 
                           foreground=accent_color, 
                           background=card_bg)
        
        # Primary button style - Gold with hover effects
        self.style.configure('CustomPrimary.TButton',
                           font=('Trebuchet MS', 16, 'bold'),
                           foreground=bg_primary,       # Dark text on gold
                           background=accent_color,     # Gold background
                           borderwidth=2,
                           relief='raised')
        
        self.style.map('CustomPrimary.TButton',
                     background=[('active', '#ffed4a'),    # Lighter gold on hover
                               ('pressed', '#e6c200')])    # Darker gold on click
        
        # Secondary button style - Purple outline
        self.style.configure('CustomSecondary.TButton',
                           font=('Trebuchet MS', 12, 'bold'),
                           foreground=text_primary,
                           background=bg_secondary,
                           borderwidth=2,
                           relief='raised')
        
        self.style.map('CustomSecondary.TButton',
                     background=[('active', '#5a4fcf'),
                               ('pressed', '#4a3fb8')])
        
        # Success status style - Green with gold border
        self.style.configure('CustomSuccess.TLabel',
                           font=('Trebuchet MS', 14, 'bold'),
                           foreground='#1a5a1a',        # Dark green text
                           background='#90ee90',        # Light green background
                           borderwidth=3,
                           relief='solid',
                           padding=20)
        
        # Error status style - Red with gold border
        self.style.configure('CustomError.TLabel',
                           font=('Trebuchet MS', 14, 'bold'),
                           foreground='#8b0000',        # Dark red text
                           background='#ffb3b3',        # Light red background
                           borderwidth=3,
                           relief='solid',
                           padding=20)
        
        # Loading status style - Blue with gold border
        self.style.configure('CustomLoading.TLabel',
                           font=('Trebuchet MS', 14, 'bold'),
                           foreground='#003d82',        # Dark blue text
                           background='#add8e6',        # Light blue background
                           borderwidth=3,
                           relief='solid',
                           padding=20)
    
    def create_interface(self):
        """Create the custom-themed interface"""
        # Main scrollable canvas
        self.canvas = tk.Canvas(self.root, bg='#2d1b69', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Main content frame
        self.main_frame = tk.Frame(self.canvas, bg='#2d1b69')
        self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        
        # Header section with custom styling
        self.create_custom_header()
        
        # Content with custom cards
        self.create_custom_content()
        
        # Configure scrolling
        def configure_scroll_region(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        self.main_frame.bind('<Configure>', configure_scroll_region)
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def create_custom_header(self):
        """Create custom header with dramatic styling"""
        header_frame = tk.Frame(self.main_frame, bg='#2d1b69', padx=50, pady=50)
        header_frame.pack(fill='x')
        
        # Decorative border
        border_frame = tk.Frame(header_frame, bg='#ffd700', height=4)
        border_frame.pack(fill='x', pady=(0, 20))
        
        # Main title with custom emoji
        title_label = ttk.Label(header_frame, text="🌟 PDF Magic Tools ⭐", style='Title.TLabel')
        title_label.pack(pady=(0, 15))
        
        # Subtitle with flair
        subtitle_label = ttk.Label(header_frame, 
                                 text="✨ Professional PDF Processing with Style ✨", 
                                 style='Subtitle.TLabel')
        subtitle_label.pack()
        
        # Bottom decorative border
        border_frame2 = tk.Frame(header_frame, bg='#ffd700', height=4)
        border_frame2.pack(fill='x', pady=(20, 0))
    
    def create_custom_content(self):
        """Create content with custom card styling"""
        content_frame = tk.Frame(self.main_frame, bg='#2d1b69', padx=50)
        content_frame.pack(fill='both', expand=True)
        
        # Custom merge card
        self.create_custom_merge_card(content_frame)
        
        # Fancy spacer with decorative element
        spacer_frame = tk.Frame(content_frame, bg='#2d1b69', height=60)
        spacer_frame.pack(fill='x')
        
        # Add decorative separator
        sep_frame = tk.Frame(spacer_frame, bg='#ffd700', height=2)
        sep_frame.place(relx=0.2, rely=0.5, relwidth=0.6)
        
        # Custom split card
        self.create_custom_split_card(content_frame)
        
        # Bottom padding
        bottom_spacer = tk.Frame(content_frame, bg='#2d1b69', height=50)
        bottom_spacer.pack(fill='x')
    
    def create_custom_merge_card(self, parent):
        """Create custom-styled merge card"""
        # Card container with enhanced shadow
        card_container = tk.Frame(parent, bg='#2d1b69')
        card_container.pack(fill='x', pady=(0, 30))
        
        # Multiple shadow layers for depth
        for i in range(3):
            shadow_frame = tk.Frame(card_container, bg='#1a1a40', height=2)
            shadow_frame.place(x=5+i, y=5+i, relwidth=1, height=2)
        
        # Main card frame with custom style
        card_frame = ttk.Frame(card_container, style='CustomCard.TFrame', padding=50)
        card_frame.pack(fill='x')
        
        # Section title with icon
        title_label = ttk.Label(card_frame, text="📚 Merge Multiple PDFs", style='SectionTitle.TLabel')
        title_label.pack(anchor='w', pady=(0, 30))
        
        # Custom file selection area
        file_frame = tk.Frame(card_frame, bg='#5a5a8a', relief='groove', borderwidth=3, bd=3)
        file_frame.pack(fill='x', pady=(0, 25))
        
        # Enhanced drop area
        drop_frame = tk.Frame(file_frame, bg='#6a6a9a', relief='flat', padx=40, pady=40)
        drop_frame.pack(fill='x', expand=True)
        
        # Custom styled button
        self.select_files_btn = ttk.Button(drop_frame, text="📁 Select Your PDF Files", 
                                         command=self.select_files, style='CustomPrimary.TButton')
        self.select_files_btn.pack(pady=(0, 20))
        
        # File display with custom styling
        self.files_display = tk.Text(drop_frame, height=6, font=('Trebuchet MS', 12), 
                                   bg='#7a7aaa', fg='white', relief='sunken', borderwidth=2,
                                   state='disabled', wrap='word', insertbackground='white')
        self.files_display.pack(fill='x', pady=(0, 20))
        
        # Button frame with custom layout
        btn_frame = tk.Frame(drop_frame, bg='#6a6a9a')
        btn_frame.pack(fill='x')
        
        self.clear_files_btn = ttk.Button(btn_frame, text="🗑️ Clear All", 
                                        command=self.clear_files, style='CustomSecondary.TButton')
        self.clear_files_btn.pack(side='left', padx=(0, 15))
        
        self.merge_btn = ttk.Button(btn_frame, text="⚡ MERGE MAGIC ⚡", 
                                  command=self.merge_pdfs, style='CustomPrimary.TButton', 
                                  state='disabled')
        self.merge_btn.pack(side='right')
        
        # Status area with custom styling
        self.merge_status_frame = tk.Frame(card_frame, bg='#4a4a7a')
        self.merge_status_frame.pack(fill='x', pady=(15, 0))
        
        self.merge_status = ttk.Label(self.merge_status_frame, text="", background='#4a4a7a')
        self.merge_status.pack()
    
    def create_custom_split_card(self, parent):
        """Create custom-styled split card"""
        # Similar structure to merge card but with different accent
        card_container = tk.Frame(parent, bg='#2d1b69')
        card_container.pack(fill='x')
        
        # Shadow effects
        for i in range(3):
            shadow_frame = tk.Frame(card_container, bg='#1a1a40', height=2)
            shadow_frame.place(x=5+i, y=5+i, relwidth=1, height=2)
        
        card_frame = ttk.Frame(card_container, style='CustomCard.TFrame', padding=50)
        card_frame.pack(fill='x')
        
        # Section title
        title_label = ttk.Label(card_frame, text="✂️ Split PDF Precision", style='SectionTitle.TLabel')
        title_label.pack(anchor='w', pady=(0, 30))
        
        # File selection with enhanced styling
        self.select_pdf_btn = ttk.Button(card_frame, text="📄 Choose PDF to Split", 
                                       command=self.select_pdf_to_split, style='CustomPrimary.TButton')
        self.select_pdf_btn.pack(pady=(0, 25))
        
        # PDF info box (initially hidden) with custom colors
        self.pdf_info_frame = tk.Frame(card_frame, bg='#5a5a8a', relief='raised', borderwidth=2, padx=25, pady=25)
        
        self.pdf_info_text = tk.Text(self.pdf_info_frame, height=3, font=('Trebuchet MS', 13), 
                                   bg='#7a7aaa', fg='white', relief='flat', borderwidth=0, 
                                   state='disabled', wrap='word')
        self.pdf_info_text.pack(fill='x')
        
        # Page input section with enhanced styling
        self.split_options_frame = tk.Frame(card_frame, bg='#4a4a7a')
        
        input_label = tk.Label(self.split_options_frame, text="🎯 Pages to Extract:", 
                             font=('Trebuchet MS', 16, 'bold'), bg='#4a4a7a', fg='#ffd700')
        input_label.pack(anchor='w', pady=(25, 15))
        
        self.pages_entry = tk.Entry(self.split_options_frame, font=('Trebuchet MS', 16), 
                                  bg='#7a7aaa', fg='white', relief='raised', borderwidth=3,
                                  insertbackground='white')
        self.pages_entry.pack(fill='x', pady=(0, 15), ipady=12)
        
        help_text = tk.Label(self.split_options_frame, 
                           text="💡 Examples: '1,3,5' for specific pages | '1-5' for ranges | '1-3,7,10-12' for mixed",
                           font=('Trebuchet MS', 12, 'italic'), bg='#4a4a7a', fg='#e6e6fa', 
                           wraplength=700, justify='left')
        help_text.pack(anchor='w', pady=(0, 25))
        
        self.split_btn = ttk.Button(self.split_options_frame, text="⚡ SPLIT MAGIC ⚡", 
                                  command=self.split_pdf, style='CustomPrimary.TButton')
        self.split_btn.pack(pady=(0, 25))
        
        # Status area
        self.split_status_frame = tk.Frame(card_frame, bg='#4a4a7a')
        self.split_status_frame.pack(fill='x', pady=(15, 0))
        
        self.split_status = ttk.Label(self.split_status_frame, text="", background='#4a4a7a')
        self.split_status.pack()
    
    # 🔄 COPY ALL THE ORIGINAL FUNCTIONALITY METHODS HERE
    # (select_files, update_files_display, merge_pdfs, etc.)
    # I'm keeping them the same but updating the status styling
    
    def select_files(self):
        """Select multiple PDF files for merging"""
        files = filedialog.askopenfilenames(
            title="Select PDF files to merge",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if files:
            self.selected_files = list(files)
            self.update_files_display()
            self.merge_btn.config(state='normal' if len(self.selected_files) > 1 else 'disabled')
    
    def update_files_display(self):
        """Update the display of selected files"""
        self.files_display.config(state='normal')
        self.files_display.delete(1.0, tk.END)
        
        if self.selected_files:
            text = f"✨ Selected {len(self.selected_files)} magical files:\n\n"
            for i, file_path in enumerate(self.selected_files, 1):
                file_name = os.path.basename(file_path)
                text += f"⭐ {i}. {file_name}\n"
            self.files_display.insert(1.0, text)
        else:
            self.files_display.insert(1.0, "🌙 No files selected - Choose your PDFs above!")
        
        self.files_display.config(state='disabled')
    
    def clear_files(self):
        """Clear selected files"""
        self.selected_files = []
        self.update_files_display()
        self.merge_btn.config(state='disabled')
        self.show_custom_status(self.merge_status, "", "")
    
    def show_custom_status(self, label_widget, message, status_type):
        """Show status message with custom styling"""
        label_widget.config(text=message)
        
        if status_type == "success":
            label_widget.config(style='CustomSuccess.TLabel')
        elif status_type == "error":
            label_widget.config(style='CustomError.TLabel')
        elif status_type == "loading":
            label_widget.config(style='CustomLoading.TLabel')
        else:
            label_widget.config(style='TLabel')
    
    # Add all other methods here...
    # For brevity, I'll include just the essential ones
    
    def merge_pdfs(self):
        """Merge selected PDF files with custom status"""
        if len(self.selected_files) < 2:
            messagebox.showwarning("Magical Warning", "Please select at least 2 PDF files to merge.")
            return
        
        output_file = filedialog.asksaveasfilename(
            title="Save your merged magic as",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if not output_file:
            return
        
        self.merge_btn.config(state='disabled')
        self.show_custom_status(self.merge_status, "⚡ Working PDF Magic... ⚡", "loading")
        self.root.update()
        
        def merge_thread():
            try:
                writer = PdfWriter()
                
                for file_path in self.selected_files:
                    with open(file_path, 'rb') as file:
                        reader = PdfReader(file)
                        for page in reader.pages:
                            writer.add_page(page)
                
                with open(output_file, 'wb') as output:
                    writer.write(output)
                
                self.root.after(0, lambda: self.merge_complete(output_file))
                
            except Exception as e:
                self.root.after(0, lambda: self.merge_error(str(e)))
        
        thread = threading.Thread(target=merge_thread)
        thread.daemon = True
        thread.start()
    
    def merge_complete(self, output_file):
        """Handle successful merge with custom styling"""
        self.merge_btn.config(state='normal')
        file_name = os.path.basename(output_file)
        self.show_custom_status(self.merge_status, f"🌟 MAGIC COMPLETE! Saved as: {file_name} ✨", "success")
    
    def merge_error(self, error_msg):
        """Handle merge error with custom styling"""
        self.merge_btn.config(state='normal')
        self.show_custom_status(self.merge_status, f"💥 Magic Failed: {error_msg}", "error")
    
    def select_pdf_to_split(self):
        """Select PDF file to split"""
        file_path = filedialog.askopenfilename(
            title="Select PDF file to split",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.current_pdf_path = file_path
            self.analyze_pdf()
    
    def analyze_pdf(self):
        """Analyze selected PDF and show info with custom styling"""
        try:
            with open(self.current_pdf_path, 'rb') as file:
                reader = PdfReader(file)
                self.current_pdf_pages = len(reader.pages)
            
            file_name = os.path.basename(self.current_pdf_path)
            
            # Show PDF info with custom text
            self.pdf_info_text.config(state='normal')
            self.pdf_info_text.delete(1.0, tk.END)
            info_text = f"📄 Magic File: {file_name}\n📊 Total Pages: {self.current_pdf_pages}\n⚡ Ready for splitting magic!"
            self.pdf_info_text.insert(1.0, info_text)
            self.pdf_info_text.config(state='disabled')
            
            # Show info and options
            self.pdf_info_frame.pack(fill='x', pady=(0, 25))
            self.split_options_frame.pack(fill='x')
            
        except Exception as e:
            messagebox.showerror("Magic Error", f"Failed to analyze PDF: {str(e)}")

def main():
    root = tk.Tk()
    app = CustomThemePDFApp(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n🛑 Custom theme application interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        messagebox.showerror("Error", f"Unexpected error occurred:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()