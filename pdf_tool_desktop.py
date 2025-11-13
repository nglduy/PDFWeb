"""
🔄 PDF Tools Desktop - Purple Theme (Matching the UI Image)
Beautiful desktop application for merging and splitting PDFs with a modern purple interface
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import PyPDF2
import os
import threading


class ModernPDFToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔄 PDF Tools - Desktop")
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")
        self.root.configure(bg='#2E2446')  
        
        # Initialize variables
        self.selected_files = []
        self.current_pdf_path = None
        self.current_pdf_pages = 0
        
        self.setup_styles()
        self.create_interface()
    
    def setup_styles(self):
        """🎨 Setup beautiful purple theme styles matching the image"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # 💜 PURPLE THEME COLOR PALETTE (matching the image)
        bg_primary = "#2E2446"        
        bg_secondary = "#DCD7E5"      
        card_bg = '#FFFFFF'           
        text_primary = '#1F2937'      
        text_secondary = '#6B7280'    
        text_purple = '#1F2937'       
        button_primary = '#1F2937'    
        button_secondary = '#E5E7EB'  
        
        # Configure notebook (tabs) style
        self.style.configure('Custom.TNotebook', 
                           background=bg_primary,
                           borderwidth=0)
        
        self.style.configure('Custom.TNotebook.Tab',
                           background='rgba(255,255,255,0.2)',
                           foreground='white',
                           font=('Segoe UI', 14, 'bold'),
                           padding=[20, 12],
                           borderwidth=0)
        
        self.style.map('Custom.TNotebook.Tab',
                     background=[('selected', 'white'),
                               ('active', 'rgba(255,255,255,0.3)')],
                     foreground=[('selected', text_purple),
                               ('active', 'white')])
        
        # Card frame style - White like in image
        self.style.configure('Card.TFrame',
                           background=card_bg,
                           relief='flat',
                           borderwidth=0)
        
        # Main title style - White on purple
        self.style.configure('Title.TLabel', 
                           font=('Segoe UI', 24, 'normal'), 
                           foreground='white', 
                           background=bg_primary)
        
        # Section heading style - Purple on white cards
        self.style.configure('SectionTitle.TLabel', 
                           font=('Segoe UI', 24, 'bold'), 
                           foreground=text_primary, 
                           background=card_bg)
        
        # Subtitle style - Gray on white
        self.style.configure('Subtitle.TLabel', 
                           font=('Segoe UI', 14, 'normal'), 
                           foreground=text_secondary, 
                           background=card_bg)
        
        # Primary button style - Purple like in image
        self.style.configure('Primary.TButton',
                           font=('Segoe UI', 13, 'bold'),
                           foreground='white',
                           background=button_primary,
                           borderwidth=0,
                           focuscolor='none',
                           padding=[20, 12])
        
        self.style.map('Primary.TButton',
                     background=[('active', '#2E2446'),
                               ('pressed', '#2E2446'),
                               ('disabled', '#D1D5DB')],  # Light gray for disabled
                     foreground=[('disabled', '#9CA3AF')])  # Gray text for disabled
        
        # Secondary button style - Light like in image
        self.style.configure('Secondary.TButton',
                           font=('Segoe UI', 12),
                           foreground=text_secondary,
                           background=button_secondary,
                           borderwidth=1,
                           padding=[15, 8])
        
        self.style.map('Secondary.TButton',
                     background=[('active', '#F3F4F6'),
                               ('pressed', '#E5E7EB'),
                               ('disabled', '#F9FAFB')],  # Very light gray for disabled
                     foreground=[('disabled', '#D1D5DB')])  # Light gray text for disabled
        
        # Status styles - Clean and minimal
        self.style.configure('Success.TLabel',
                           font=('Segoe UI', 12, 'bold'),
                           foreground='#059669',
                           background=card_bg,
                           padding=10)
        
        self.style.configure('Error.TLabel',
                           font=('Segoe UI', 12, 'bold'),
                           foreground='#DC2626',
                           background=card_bg,
                           padding=10)
        
        self.style.configure('Loading.TLabel',
                           font=('Segoe UI', 12, 'bold'),
                           foreground=text_purple,
                           background=card_bg,
                           padding=10)

    def create_interface(self):
        """🎨 Create beautiful purple interface matching the design"""
        
        # Main title at top - white on purple
        title_label = ttk.Label(self.root, 
                               text="Merge multiple PDFs or split a single PDF into pages", 
                               style='Title.TLabel')
        title_label.pack(pady=(30, 40), padx=20)
        
        # Create main container with proper spacing
        main_container = tk.Frame(self.root, bg='#8B5CF6')
        main_container.pack(fill='both', expand=True, padx=40, pady=(0, 40))
        
        # Create notebook for tabs (like in the image)
        self.notebook = ttk.Notebook(main_container, style='Custom.TNotebook')
        self.notebook.pack(fill='both', expand=True)
        
        # Create merge tab
        self.merge_frame = self.create_merge_tab()
        self.notebook.add(self.merge_frame, text='🔀 Merge PDFs')
        
        # Create split tab
        self.split_frame = self.create_split_tab()
        self.notebook.add(self.split_frame, text='📄 Split PDF')
    
    def create_merge_tab(self):
        """🔀 Create merge PDFs tab with white card design"""
        # Main frame with white card background
        frame = ttk.Frame(style='Card.TFrame')
        
        # Card container with padding
        card_container = tk.Frame(frame, bg='white')
        card_container.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Section title
        title = ttk.Label(card_container, 
                         text="Merge Multiple PDFs", 
                         style='SectionTitle.TLabel')
        title.pack(pady=(20, 10))
        
        # Subtitle description
        subtitle = ttk.Label(card_container, 
                           text="Select multiple PDF files to combine them into one document. Files will be merged in the order selected.", 
                           style='Subtitle.TLabel')
        subtitle.pack(pady=(0, 30))
        
        # Create drag and drop area (like in the image)
        self.create_drop_area(card_container, 'merge')
        
        # Files list area
        self.files_frame = tk.Frame(card_container, bg='white')
        self.files_frame.pack(fill='x', pady=20)
        
        # Show "No files selected" initially
        self.files_status = tk.Label(self.files_frame, text="No files selected", 
                                    font=('Segoe UI', 12), 
                                    fg='#6B7280', bg='white')
        self.files_status.pack()
        
        # Action buttons container
        buttons_frame = tk.Frame(card_container, bg='white')
        buttons_frame.pack(pady=(20, 30))
        
        # Merge button (purple like in image)
        self.merge_btn = ttk.Button(buttons_frame, 
                                   text="🔀 Merge PDFs", 
                                   style='Primary.TButton',
                                   command=self.merge_pdfs,
                                   state='disabled')
        self.merge_btn.pack(side='left', padx=(0, 15))
        
        # Clear button (light gray like in image)
        clear_btn = ttk.Button(buttons_frame,
                              text="Clear Files",
                              style='Secondary.TButton', 
                              command=self.clear_files)
        clear_btn.pack(side='left')
        
        # Status area
        self.merge_status = ttk.Label(card_container, text="")
        self.merge_status.pack(pady=10)
        
        return frame
    
    def create_split_tab(self):
        """📄 Create split PDF tab with white card design"""
        # Main frame with white card background
        frame = ttk.Frame(style='Card.TFrame')
        
        # Card container with padding
        card_container = tk.Frame(frame, bg='white')
        card_container.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Section title
        title = ttk.Label(card_container, 
                         text="Split PDF into Pages", 
                         style='SectionTitle.TLabel')
        title.pack(pady=(20, 10))
        
        # Subtitle description
        subtitle = ttk.Label(card_container, 
                           text="Select a PDF file to split it into individual pages.", 
                           style='Subtitle.TLabel')
        subtitle.pack(pady=(0, 30))
        
        # Create drag and drop area for single file
        self.create_drop_area(card_container, 'split')
        
        # PDF info display
        self.pdf_info_frame = tk.Frame(card_container, bg='white')
        self.pdf_info_frame.pack(fill='x', pady=20)
        
        # Action buttons container
        buttons_frame = tk.Frame(card_container, bg='white')
        buttons_frame.pack(pady=(20, 30))
        
        # Select PDF button
        select_btn = ttk.Button(buttons_frame,
                               text="📂 Select PDF File",
                               style='Secondary.TButton',
                               command=self.select_pdf_to_split)
        select_btn.pack(side='left', padx=(0, 15))
        
        # Split button (purple like in image)
        self.split_btn = ttk.Button(buttons_frame,
                                   text="📄 Split PDF", 
                                   style='Primary.TButton',
                                   command=self.split_pdf,
                                   state='disabled')
        self.split_btn.pack(side='left')
        
        # Status area
        self.split_status = ttk.Label(card_container, text="")
        self.split_status.pack(pady=10)
        
        return frame
    
    def create_drop_area(self, parent, mode):
        """☁️ Create drag and drop area like in the image"""
        # Dashed border container (like in the image)
        drop_frame = tk.Frame(parent, bg='white', highlightthickness=2, 
                             highlightcolor='#E5E7EB', highlightbackground='#E5E7EB',
                             relief='solid', bd=1)
        drop_frame.pack(fill='x', pady=20, ipady=40)
        
        # Cloud icon and text (like in the image)
        icon_label = tk.Label(drop_frame, text="☁️", font=('Segoe UI', 48), 
                             fg='#9CA3AF', bg='white')
        icon_label.pack(pady=(20, 10))
        
        if mode == 'merge':
            main_text = "Click to select PDF files or drag them here"
            sub_text = "You can select multiple files at once"
        else:
            main_text = "Click to select a PDF file or drag it here"
            sub_text = "Select a single PDF file to split"
        
        # Main drop text (like in the image)
        main_label = tk.Label(drop_frame, text=main_text, 
                             font=('Segoe UI', 14, 'bold'),
                             fg='#374151', bg='white')
        main_label.pack(pady=(0, 5))
        
        # Sub text (like in the image)
        sub_label = tk.Label(drop_frame, text=sub_text, 
                            font=('Segoe UI', 12),
                            fg='#6B7280', bg='white')
        sub_label.pack(pady=(0, 20))
        
        # Make the entire drop area clickable
        if mode == 'merge':
            drop_frame.bind("<Button-1>", lambda e: self.select_files())
            icon_label.bind("<Button-1>", lambda e: self.select_files())
            main_label.bind("<Button-1>", lambda e: self.select_files())
            sub_label.bind("<Button-1>", lambda e: self.select_files())
        else:
            drop_frame.bind("<Button-1>", lambda e: self.select_pdf_to_split())
            icon_label.bind("<Button-1>", lambda e: self.select_pdf_to_split())
            main_label.bind("<Button-1>", lambda e: self.select_pdf_to_split())
            sub_label.bind("<Button-1>", lambda e: self.select_pdf_to_split())
        
        # Store reference for status updates
        if mode == 'merge':
            self.merge_drop_area = drop_frame
            self.merge_status_text = main_label
        else:
            self.split_drop_area = drop_frame
            self.split_status_text = main_label

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
        # Clear existing display
        for widget in self.files_frame.winfo_children():
            widget.destroy()
        
        if self.selected_files:
            # Show file count
            count_text = f"{len(self.selected_files)} files selected:"
            count_label = tk.Label(self.files_frame, text=count_text, 
                                  font=('Segoe UI', 12, 'bold'), 
                                  fg='#374151', bg='white')
            count_label.pack(anchor='w', pady=(0, 10))
            
            # Show files in a scrollable list
            files_container = tk.Frame(self.files_frame, bg='white')
            files_container.pack(fill='both', expand=True)
            
            for i, file_path in enumerate(self.selected_files, 1):
                file_name = os.path.basename(file_path)
                file_label = tk.Label(files_container, 
                                     text=f"{i}. {file_name}", 
                                     font=('Segoe UI', 10),
                                     fg='#6B7280', bg='white',
                                     anchor='w')
                file_label.pack(fill='x', pady=2, padx=20)
        else:
            # Show "No files selected"
            self.files_status = tk.Label(self.files_frame, text="No files selected", 
                                        font=('Segoe UI', 12), 
                                        fg='#6B7280', bg='white')
            self.files_status.pack()

    def clear_files(self):
        """Clear all selected files"""
        self.selected_files = []
        self.merge_btn.config(state='disabled')
        self.update_files_display()
        self.show_status(self.merge_status, "Files cleared", "success")

    def select_pdf_to_split(self):
        """Select a single PDF file for splitting"""
        file_path = filedialog.askopenfilename(
            title="Select PDF file to split",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    self.current_pdf_pages = len(pdf_reader.pages)
                    self.current_pdf_path = file_path
                
                # Update display
                self.update_pdf_info_display()
                self.split_btn.config(state='normal')
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read PDF: {str(e)}")

    def update_pdf_info_display(self):
        """Update the PDF info display"""
        # Clear existing display
        for widget in self.pdf_info_frame.winfo_children():
            widget.destroy()
        
        if self.current_pdf_path:
            file_name = os.path.basename(self.current_pdf_path)
            
            # File info
            info_text = f"📄 {file_name}"
            info_label = tk.Label(self.pdf_info_frame, text=info_text, 
                                 font=('Segoe UI', 12, 'bold'), 
                                 fg='#374151', bg='white')
            info_label.pack(anchor='w', pady=(0, 5))
            
            # Pages info
            pages_text = f"📋 {self.current_pdf_pages} pages • Will be split into {self.current_pdf_pages} separate files"
            pages_label = tk.Label(self.pdf_info_frame, text=pages_text, 
                                  font=('Segoe UI', 10),
                                  fg='#6B7280', bg='white')
            pages_label.pack(anchor='w')

    def merge_pdfs(self):
        """Merge selected PDF files"""
        if len(self.selected_files) < 2:
            messagebox.showerror("Error", "Please select at least 2 PDF files to merge.")
            return
        
        output_path = filedialog.asksaveasfilename(
            title="Save merged PDF as",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if not output_path:
            return
        
        def merge_thread():
            try:
                self.show_status(self.merge_status, "Merging PDFs...", "loading")
                
                pdf_merger = PyPDF2.PdfMerger()
                
                for file_path in self.selected_files:
                    pdf_merger.append(file_path)
                
                with open(output_path, 'wb') as output_file:
                    pdf_merger.write(output_file)
                
                pdf_merger.close()
                
                self.show_status(self.merge_status, 
                               f"✅ Successfully merged {len(self.selected_files)} PDFs into {os.path.basename(output_path)}", 
                               "success")
                
            except Exception as e:
                self.show_status(self.merge_status, f"❌ Error merging PDFs: {str(e)}", "error")
        
        threading.Thread(target=merge_thread, daemon=True).start()

    def split_pdf(self):
        """Split the selected PDF into individual pages"""
        if not self.current_pdf_path:
            messagebox.showerror("Error", "Please select a PDF file to split.")
            return
        
        output_dir = filedialog.askdirectory(title="Choose directory to save split pages")
        
        if not output_dir:
            return
        
        def split_thread():
            try:
                self.show_status(self.split_status, "Splitting PDF...", "loading")
                
                with open(self.current_pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    base_name = os.path.splitext(os.path.basename(self.current_pdf_path))[0]
                    
                    for page_num, page in enumerate(pdf_reader.pages, 1):
                        pdf_writer = PyPDF2.PdfWriter()
                        pdf_writer.add_page(page)
                        
                        output_path = os.path.join(output_dir, f"{base_name}_page_{page_num}.pdf")
                        
                        with open(output_path, 'wb') as output_file:
                            pdf_writer.write(output_file)
                
                self.show_status(self.split_status, 
                               f"✅ Successfully split PDF into {self.current_pdf_pages} files in {os.path.basename(output_dir)}", 
                               "success")
                
            except Exception as e:
                self.show_status(self.split_status, f"❌ Error splitting PDF: {str(e)}", "error")
        
        threading.Thread(target=split_thread, daemon=True).start()

    def show_status(self, label, message, status_type):
        """Show status message with appropriate styling"""
        if status_type == "success":
            label.config(text=message, style='Success.TLabel')
        elif status_type == "error":
            label.config(text=message, style='Error.TLabel')
        elif status_type == "loading":
            label.config(text=message, style='Loading.TLabel')


def main():
    """🚀 Launch the PDF Tools application"""
    root = tk.Tk()
    app = ModernPDFToolApp(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()