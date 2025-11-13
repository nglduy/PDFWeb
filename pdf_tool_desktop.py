import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime
import io

class PDFToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Tools - Merge & Split PDFs")
        self.root.geometry("800x600")
        self.root.configure(bg='#f8f9fa')
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure colors
        self.style.configure('Title.TLabel', font=('Arial', 24, 'bold'), foreground='#2c3e50', background='#f8f9fa')
        self.style.configure('Heading.TLabel', font=('Arial', 14, 'bold'), foreground='#495057', background='#f8f9fa')
        self.style.configure('Custom.TButton', font=('Arial', 12, 'bold'), padding=10)
        self.style.configure('Success.TLabel', font=('Arial', 10), foreground='#155724', background='#d4edda')
        self.style.configure('Error.TLabel', font=('Arial', 10), foreground='#721c24', background='#f8d7da')
        
        self.create_widgets()
        
        # Variables
        self.selected_files = []
        self.current_pdf_path = None
        self.current_pdf_pages = 0
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, style='Card.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="🔄 PDF Tools", style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="Free offline tool to merge multiple PDFs or split a PDF into individual pages", 
                                 font=('Arial', 11), foreground='#6c757d', background='#f8f9fa')
        subtitle_label.pack(pady=(0, 30))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Merge tab
        self.create_merge_tab()
        
        # Split tab
        self.create_split_tab()
        
    def create_merge_tab(self):
        # Merge frame
        merge_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(merge_frame, text="📄 Merge PDFs")
        
        # Heading
        merge_heading = ttk.Label(merge_frame, text="Merge Multiple PDFs", style='Heading.TLabel')
        merge_heading.pack(anchor='w', pady=(0, 15))
        
        # File selection section
        file_section = ttk.LabelFrame(merge_frame, text="Select PDF Files", padding="15")
        file_section.pack(fill='x', pady=(0, 15))
        
        # Select files button
        select_btn = ttk.Button(file_section, text="📁 Select PDF Files", 
                               command=self.select_files, style='Custom.TButton')
        select_btn.pack(pady=(0, 10))
        
        # Selected files list
        self.files_listbox = tk.Listbox(file_section, height=8, font=('Arial', 10))
        self.files_listbox.pack(fill='x', pady=(0, 10))
        
        # Buttons frame
        buttons_frame = ttk.Frame(file_section)
        buttons_frame.pack(fill='x')
        
        remove_btn = ttk.Button(buttons_frame, text="❌ Remove Selected", command=self.remove_selected_file)
        remove_btn.pack(side='left', padx=(0, 5))
        
        clear_btn = ttk.Button(buttons_frame, text="🗑️ Clear All", command=self.clear_files)
        clear_btn.pack(side='left')
        
        # Merge section
        merge_section = ttk.LabelFrame(merge_frame, text="Merge Options", padding="15")
        merge_section.pack(fill='x', pady=(0, 15))
        
        self.merge_btn = ttk.Button(merge_section, text="🔄 Merge PDFs", 
                                   command=self.merge_pdfs, style='Custom.TButton', state='disabled')
        self.merge_btn.pack(pady=(0, 10))
        
        # Status label for merge
        self.merge_status = ttk.Label(merge_section, text="", background='#f8f9fa')
        self.merge_status.pack()
        
    def create_split_tab(self):
        # Split frame
        split_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(split_frame, text="✂️ Split PDF")
        
        # Heading
        split_heading = ttk.Label(split_frame, text="Split PDF into Pages", style='Heading.TLabel')
        split_heading.pack(anchor='w', pady=(0, 15))
        
        # File selection section
        pdf_section = ttk.LabelFrame(split_frame, text="Select PDF to Split", padding="15")
        pdf_section.pack(fill='x', pady=(0, 15))
        
        select_pdf_btn = ttk.Button(pdf_section, text="📁 Select PDF File", 
                                   command=self.select_pdf_to_split, style='Custom.TButton')
        select_pdf_btn.pack(pady=(0, 10))
        
        # PDF info
        self.pdf_info_label = ttk.Label(pdf_section, text="No PDF selected", 
                                       font=('Arial', 10), foreground='#6c757d', background='#f8f9fa')
        self.pdf_info_label.pack()
        
        # Split options section
        self.split_section = ttk.LabelFrame(split_frame, text="Split Options", padding="15")
        self.split_section.pack(fill='x', pady=(0, 15))
        
        # Page range input
        ttk.Label(self.split_section, text="Pages to extract:", font=('Arial', 11, 'bold'), background='#f8f9fa').pack(anchor='w', pady=(0, 5))
        
        self.pages_entry = ttk.Entry(self.split_section, font=('Arial', 11), width=50)
        self.pages_entry.pack(fill='x', pady=(0, 5))
        
        help_label = ttk.Label(self.split_section, 
                              text="💡 Examples: '1,3,5' for pages 1,3,5 | '1-5' for pages 1 through 5 | '1-3,7,10-12' for mixed ranges",
                              font=('Arial', 9), foreground='#6c757d', background='#f8f9fa', wraplength=600)
        help_label.pack(anchor='w', pady=(0, 15))
        
        # Split button
        self.split_btn = ttk.Button(self.split_section, text="✂️ Split PDF", 
                                   command=self.split_pdf, style='Custom.TButton', state='disabled')
        self.split_btn.pack(pady=(0, 10))
        
        # Status label for split
        self.split_status = ttk.Label(self.split_section, text="", background='#f8f9fa')
        self.split_status.pack()
        
        # Initially hide split options
        self.split_section.pack_forget()
        
    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Select PDF files to merge",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if files:
            # Add new files to the list
            for file in files:
                if file not in self.selected_files:
                    self.selected_files.append(file)
            
            self.update_files_listbox()
            self.update_merge_button_state()
    
    def update_files_listbox(self):
        self.files_listbox.delete(0, tk.END)
        for i, file_path in enumerate(self.selected_files):
            filename = os.path.basename(file_path)
            self.files_listbox.insert(tk.END, f"{i+1}. {filename}")
    
    def remove_selected_file(self):
        selection = self.files_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_files.pop(index)
            self.update_files_listbox()
            self.update_merge_button_state()
    
    def clear_files(self):
        self.selected_files.clear()
        self.update_files_listbox()
        self.update_merge_button_state()
    
    def update_merge_button_state(self):
        if len(self.selected_files) >= 2:
            self.merge_btn.config(state='normal')
            self.merge_status.config(text=f"Ready to merge {len(self.selected_files)} files", foreground='#155724')
        else:
            self.merge_btn.config(state='disabled')
            if len(self.selected_files) == 0:
                self.merge_status.config(text="Please select PDF files to merge", foreground='#6c757d')
            else:
                self.merge_status.config(text="Please select at least 2 PDF files", foreground='#856404')
    
    def merge_pdfs(self):
        if len(self.selected_files) < 2:
            messagebox.showerror("Error", "Please select at least 2 PDF files to merge")
            return
        
        # Ask where to save
        output_file = filedialog.asksaveasfilename(
            title="Save merged PDF as",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialname=f"merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        
        if not output_file:
            return
        
        # Start merge in thread to prevent UI freezing
        self.merge_btn.config(state='disabled')
        self.merge_status.config(text="🔄 Merging PDFs...", foreground='#0c5460')
        self.root.update()
        
        thread = threading.Thread(target=self.perform_merge, args=(output_file,))
        thread.daemon = True
        thread.start()
    
    def perform_merge(self, output_file):
        try:
            pdf_writer = PdfWriter()
            
            for file_path in self.selected_files:
                with open(file_path, 'rb') as pdf_file:
                    pdf_reader = PdfReader(pdf_file)
                    
                    for page in pdf_reader.pages:
                        pdf_writer.add_page(page)
            
            # Write merged PDF
            with open(output_file, 'wb') as output:
                pdf_writer.write(output)
            
            # Update UI in main thread
            self.root.after(0, self.merge_completed, output_file)
            
        except Exception as e:
            self.root.after(0, self.merge_failed, str(e))
    
    def merge_completed(self, output_file):
        self.merge_btn.config(state='normal')
        self.merge_status.config(text=f"✅ Successfully merged! Saved as: {os.path.basename(output_file)}", foreground='#155724')
        messagebox.showinfo("Success", f"PDFs merged successfully!\n\nSaved as: {output_file}")
    
    def merge_failed(self, error_msg):
        self.merge_btn.config(state='normal')
        self.merge_status.config(text=f"❌ Merge failed: {error_msg}", foreground='#721c24')
        messagebox.showerror("Error", f"Failed to merge PDFs:\n{error_msg}")
    
    def select_pdf_to_split(self):
        file_path = filedialog.askopenfilename(
            title="Select PDF to split",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.current_pdf_path = file_path
            self.analyze_pdf(file_path)
    
    def analyze_pdf(self, file_path):
        try:
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                self.current_pdf_pages = len(pdf_reader.pages)
            
            filename = os.path.basename(file_path)
            self.pdf_info_label.config(
                text=f"📄 {filename}\n📊 Total pages: {self.current_pdf_pages}",
                foreground='#155724'
            )
            
            # Show split options
            self.split_section.pack(fill='x', pady=(0, 15))
            self.split_btn.config(state='normal')
            self.split_status.config(text="Enter page numbers to extract", foreground='#6c757d')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze PDF:\n{str(e)}")
            self.pdf_info_label.config(text="❌ Failed to analyze PDF", foreground='#721c24')
    
    def split_pdf(self):
        if not self.current_pdf_path:
            messagebox.showerror("Error", "Please select a PDF file first")
            return
        
        page_input = self.pages_entry.get().strip()
        if not page_input:
            messagebox.showerror("Error", "Please enter page numbers to extract")
            return
        
        try:
            pages = self.parse_pages(page_input)
            if not pages:
                messagebox.showerror("Error", "Invalid page numbers")
                return
            
            # Validate pages
            invalid_pages = [p for p in pages if p < 1 or p > self.current_pdf_pages]
            if invalid_pages:
                messagebox.showerror("Error", f"Invalid page numbers: {invalid_pages}\nPDF has {self.current_pdf_pages} pages")
                return
            
            # Ask where to save
            output_file = filedialog.asksaveasfilename(
                title="Save split PDF as",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialname=f"split_pages_{'_'.join(map(str, sorted(pages)))}.pdf"
            )
            
            if not output_file:
                return
            
            # Start split in thread
            self.split_btn.config(state='disabled')
            self.split_status.config(text="✂️ Splitting PDF...", foreground='#0c5460')
            self.root.update()
            
            thread = threading.Thread(target=self.perform_split, args=(output_file, pages))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse page numbers:\n{str(e)}")
    
    def parse_pages(self, input_str):
        pages = []
        parts = input_str.split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part:
                try:
                    start, end = part.split('-')
                    start, end = int(start.strip()), int(end.strip())
                    for i in range(start, end + 1):
                        pages.append(i)
                except ValueError:
                    continue
            else:
                try:
                    pages.append(int(part))
                except ValueError:
                    continue
        
        return sorted(list(set(pages)))  # Remove duplicates and sort
    
    def perform_split(self, output_file, pages):
        try:
            with open(self.current_pdf_path, 'rb') as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                pdf_writer = PdfWriter()
                
                for page_num in pages:
                    page_index = page_num - 1  # Convert to 0-based index
                    pdf_writer.add_page(pdf_reader.pages[page_index])
                
                # Write split PDF
                with open(output_file, 'wb') as output:
                    pdf_writer.write(output)
            
            # Update UI in main thread
            self.root.after(0, self.split_completed, output_file, pages)
            
        except Exception as e:
            self.root.after(0, self.split_failed, str(e))
    
    def split_completed(self, output_file, pages):
        self.split_btn.config(state='normal')
        self.split_status.config(text=f"✅ Successfully extracted pages {', '.join(map(str, pages))}!", foreground='#155724')
        messagebox.showinfo("Success", f"PDF split successfully!\n\nExtracted pages: {', '.join(map(str, pages))}\nSaved as: {output_file}")
    
    def split_failed(self, error_msg):
        self.split_btn.config(state='normal')
        self.split_status.config(text=f"❌ Split failed: {error_msg}", foreground='#721c24')
        messagebox.showerror("Error", f"Failed to split PDF:\n{error_msg}")


def main():
    root = tk.Tk()
    
    # Set window icon (if you have an icon file)
    try:
        root.iconbitmap('icon.ico')  # Add an icon file if you have one
    except:
        pass
    
    app = PDFToolApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()