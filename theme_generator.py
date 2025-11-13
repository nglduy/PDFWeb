import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

class ThemePreviewTool:
    def __init__(self, root):
        self.root = root
        self.root.title("🎨 PDF Tools Theme Preview & Generator")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Color variables
        self.bg_color = tk.StringVar(value='#667eea')
        self.accent_color = tk.StringVar(value='#007bff')
        self.text_color = tk.StringVar(value='#ffffff')
        self.font_family = tk.StringVar(value='Segoe UI')
        self.font_size = tk.StringVar(value='14')
        
        self.create_interface()
    
    def create_interface(self):
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Left panel - Controls
        control_frame = tk.Frame(main_frame, bg='white', relief='raised', borderwidth=2)
        control_frame.pack(side='left', fill='y', padx=(0, 20))
        
        # Title
        title_label = tk.Label(control_frame, text="🎨 Theme Generator", 
                             font=('Arial', 18, 'bold'), bg='white')
        title_label.pack(pady=20)
        
        # Color controls
        self.create_color_controls(control_frame)
        
        # Font controls  
        self.create_font_controls(control_frame)
        
        # Action buttons
        self.create_action_buttons(control_frame)
        
        # Right panel - Preview
        self.preview_frame = tk.Frame(main_frame, bg='#667eea', relief='sunken', borderwidth=2)
        self.preview_frame.pack(side='right', fill='both', expand=True)
        
        # Create initial preview
        self.update_preview()
    
    def create_color_controls(self, parent):
        color_frame = tk.LabelFrame(parent, text="🌈 Colors", font=('Arial', 12, 'bold'), 
                                  bg='white', padx=10, pady=10)
        color_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Background color
        bg_label = tk.Label(color_frame, text="Background Color:", bg='white')
        bg_label.pack(anchor='w')
        
        bg_frame = tk.Frame(color_frame, bg='white')
        bg_frame.pack(fill='x', pady=(0, 10))
        
        self.bg_entry = tk.Entry(bg_frame, textvariable=self.bg_color, width=10)
        self.bg_entry.pack(side='left')
        self.bg_entry.bind('<KeyRelease>', self.on_color_change)
        
        bg_preview = tk.Frame(bg_frame, bg=self.bg_color.get(), width=30, height=25, relief='solid', borderwidth=1)
        bg_preview.pack(side='left', padx=(10, 0))
        self.bg_preview = bg_preview
        
        # Accent color
        accent_label = tk.Label(color_frame, text="Accent Color (Buttons):", bg='white')
        accent_label.pack(anchor='w')
        
        accent_frame = tk.Frame(color_frame, bg='white')
        accent_frame.pack(fill='x', pady=(0, 10))
        
        self.accent_entry = tk.Entry(accent_frame, textvariable=self.accent_color, width=10)
        self.accent_entry.pack(side='left')
        self.accent_entry.bind('<KeyRelease>', self.on_color_change)
        
        accent_preview = tk.Frame(accent_frame, bg=self.accent_color.get(), width=30, height=25, relief='solid', borderwidth=1)
        accent_preview.pack(side='left', padx=(10, 0))
        self.accent_preview = accent_preview
        
        # Text color
        text_label = tk.Label(color_frame, text="Text Color:", bg='white')
        text_label.pack(anchor='w')
        
        text_frame = tk.Frame(color_frame, bg='white')
        text_frame.pack(fill='x')
        
        self.text_entry = tk.Entry(text_frame, textvariable=self.text_color, width=10)
        self.text_entry.pack(side='left')
        self.text_entry.bind('<KeyRelease>', self.on_color_change)
        
        text_preview = tk.Frame(text_frame, bg=self.text_color.get(), width=30, height=25, relief='solid', borderwidth=1)
        text_preview.pack(side='left', padx=(10, 0))
        self.text_preview = text_preview
    
    def create_font_controls(self, parent):
        font_frame = tk.LabelFrame(parent, text="🔤 Typography", font=('Arial', 12, 'bold'), 
                                 bg='white', padx=10, pady=10)
        font_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Font family
        family_label = tk.Label(font_frame, text="Font Family:", bg='white')
        family_label.pack(anchor='w')
        
        font_combo = ttk.Combobox(font_frame, textvariable=self.font_family, 
                                values=['Segoe UI', 'Arial', 'Helvetica', 'Trebuchet MS', 'Verdana', 'Calibri'])
        font_combo.pack(fill='x', pady=(0, 10))
        font_combo.bind('<<ComboboxSelected>>', self.on_font_change)
        
        # Font size
        size_label = tk.Label(font_frame, text="Font Size:", bg='white')
        size_label.pack(anchor='w')
        
        size_combo = ttk.Combobox(font_frame, textvariable=self.font_size,
                                values=['10', '12', '14', '16', '18', '20', '24', '28', '32', '36'])
        size_combo.pack(fill='x')
        size_combo.bind('<<ComboboxSelected>>', self.on_font_change)
    
    def create_action_buttons(self, parent):
        action_frame = tk.LabelFrame(parent, text="⚡ Actions", font=('Arial', 12, 'bold'), 
                                   bg='white', padx=10, pady=10)
        action_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Preset buttons
        preset_label = tk.Label(action_frame, text="Quick Presets:", bg='white', font=('Arial', 10, 'bold'))
        preset_label.pack(anchor='w', pady=(0, 5))
        
        preset_btns = [
            ("🔵 Original Blue", self.preset_blue),
            ("🟣 Purple Magic", self.preset_purple),
            ("🟢 Nature Green", self.preset_green),
            ("🔴 Warm Red", self.preset_red),
            ("⚫ Dark Mode", self.preset_dark),
        ]
        
        for text, command in preset_btns:
            btn = tk.Button(action_frame, text=text, command=command, 
                          font=('Arial', 9), width=15, bg='#e0e0e0')
            btn.pack(fill='x', pady=1)
        
        # Separator
        separator = tk.Frame(action_frame, bg='gray', height=1)
        separator.pack(fill='x', pady=10)
        
        # Generate code button
        generate_btn = tk.Button(action_frame, text="📝 Generate Code", 
                               command=self.generate_code, font=('Arial', 12, 'bold'),
                               bg='#007bff', fg='white')
        generate_btn.pack(fill='x', pady=5)
        
        # Apply to main app
        apply_btn = tk.Button(action_frame, text="✨ Apply to App", 
                            command=self.apply_to_app, font=('Arial', 12, 'bold'),
                            bg='#28a745', fg='white')
        apply_btn.pack(fill='x', pady=5)
        
        # Help button
        help_btn = tk.Button(action_frame, text="❓ Help", 
                           command=self.show_help, font=('Arial', 12),
                           bg='#ffc107', fg='black')
        help_btn.pack(fill='x', pady=5)
    
    def on_color_change(self, event=None):
        # Update color previews
        try:
            self.bg_preview.config(bg=self.bg_color.get())
        except:
            pass
        try:
            self.accent_preview.config(bg=self.accent_color.get())
        except:
            pass
        try:
            self.text_preview.config(bg=self.text_color.get())
        except:
            pass
        
        # Update main preview
        self.update_preview()
    
    def on_font_change(self, event=None):
        self.update_preview()
    
    def update_preview(self):
        # Clear preview
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        
        # Update preview background
        try:
            self.preview_frame.config(bg=self.bg_color.get())
        except:
            pass
        
        # Create preview content
        preview_content = tk.Frame(self.preview_frame, bg=self.bg_color.get(), padx=30, pady=30)
        preview_content.pack(fill='both', expand=True)
        
        # Title
        try:
            title = tk.Label(preview_content, text="🔄 PDF Tools Preview", 
                           font=(self.font_family.get(), int(self.font_size.get())*2, 'bold'),
                           fg=self.text_color.get(), bg=self.bg_color.get())
            title.pack(pady=(0, 20))
        except:
            pass
        
        # Sample card
        card = tk.Frame(preview_content, bg='white', relief='raised', borderwidth=2, padx=20, pady=20)
        card.pack(fill='x', pady=(0, 20))
        
        card_title = tk.Label(card, text="📄 Sample Section", 
                            font=(self.font_family.get(), int(self.font_size.get())+4, 'bold'),
                            fg='#343a40', bg='white')
        card_title.pack(anchor='w', pady=(0, 15))
        
        # Sample button
        try:
            sample_btn = tk.Button(card, text="🚀 Sample Button", 
                                 font=(self.font_family.get(), int(self.font_size.get()), 'bold'),
                                 bg=self.accent_color.get(), fg='white', 
                                 relief='flat', borderwidth=0, padx=20, pady=10)
            sample_btn.pack(pady=10)
        except:
            pass
        
        # Status examples
        status_frame = tk.Frame(preview_content, bg=self.bg_color.get())
        status_frame.pack(fill='x')
        
        # Success status
        success = tk.Label(status_frame, text="✅ Success: Operation completed!", 
                         bg='#d4edda', fg='#155724', relief='solid', borderwidth=1, padx=15, pady=10)
        success.pack(fill='x', pady=2)
        
        # Error status  
        error = tk.Label(status_frame, text="❌ Error: Something went wrong!", 
                       bg='#f8d7da', fg='#721c24', relief='solid', borderwidth=1, padx=15, pady=10)
        error.pack(fill='x', pady=2)
    
    # Preset functions
    def preset_blue(self):
        self.bg_color.set('#667eea')
        self.accent_color.set('#007bff')
        self.text_color.set('#ffffff')
        self.font_family.set('Segoe UI')
        self.font_size.set('14')
        self.update_entries()
        self.update_preview()
    
    def preset_purple(self):
        self.bg_color.set('#8e44ad')
        self.accent_color.set('#9b59b6')
        self.text_color.set('#ffffff')
        self.font_family.set('Trebuchet MS')
        self.font_size.set('14')
        self.update_entries()
        self.update_preview()
    
    def preset_green(self):
        self.bg_color.set('#27ae60')
        self.accent_color.set('#2ecc71')
        self.text_color.set('#ffffff')
        self.font_family.set('Segoe UI')
        self.font_size.set('14')
        self.update_entries()
        self.update_preview()
    
    def preset_red(self):
        self.bg_color.set('#e74c3c')
        self.accent_color.set('#c0392b')
        self.text_color.set('#ffffff')
        self.font_family.set('Arial')
        self.font_size.set('14')
        self.update_entries()
        self.update_preview()
    
    def preset_dark(self):
        self.bg_color.set('#2c3e50')
        self.accent_color.set('#34495e')
        self.text_color.set('#ecf0f1')
        self.font_family.set('Segoe UI')
        self.font_size.set('14')
        self.update_entries()
        self.update_preview()
    
    def update_entries(self):
        # Update color previews
        self.on_color_change()
    
    def generate_code(self):
        # Generate the code snippet for the current theme
        code = f'''# 🎨 Generated Theme Code - Copy this into your setup_styles() method

# Background color
self.root.configure(bg='{self.bg_color.get()}')

# Title style
self.style.configure('Title.TLabel', 
                   font=('{self.font_family.get()}', {int(self.font_size.get())*2}, 'bold'), 
                   foreground='{self.text_color.get()}', 
                   background='{self.bg_color.get()}')

# Primary button style
self.style.configure('Primary.TButton',
                   font=('{self.font_family.get()}', {self.font_size.get()}, 'bold'),
                   foreground='white',
                   background='{self.accent_color.get()}',
                   borderwidth=0,
                   focuscolor='none')

self.style.map('Primary.TButton',
             background=[('active', '{self.darken_color(self.accent_color.get())}'),
                       ('pressed', '{self.darken_color(self.accent_color.get(), 0.3)}')])

# Card frame style
self.style.configure('Card.TFrame',
                   background='white',
                   relief='flat',
                   borderwidth=0)
'''
        
        # Show code in a new window
        code_window = tk.Toplevel(self.root)
        code_window.title("🎨 Generated Theme Code")
        code_window.geometry("800x600")
        code_window.configure(bg='white')
        
        # Code display
        text_frame = tk.Frame(code_window, bg='white', padx=20, pady=20)
        text_frame.pack(fill='both', expand=True)
        
        tk.Label(text_frame, text="📝 Copy this code into your setup_styles() method:", 
                font=('Arial', 14, 'bold'), bg='white').pack(anchor='w', pady=(0, 10))
        
        code_text = tk.Text(text_frame, font=('Consolas', 11), wrap='word')
        code_text.pack(fill='both', expand=True)
        code_text.insert(1.0, code)
        
        # Copy button
        def copy_code():
            self.root.clipboard_clear()
            self.root.clipboard_append(code)
            messagebox.showinfo("✅ Copied!", "Code copied to clipboard!")
        
        tk.Button(text_frame, text="📋 Copy to Clipboard", command=copy_code,
                font=('Arial', 12, 'bold'), bg='#007bff', fg='white').pack(pady=(10, 0))
    
    def darken_color(self, color, factor=0.2):
        """Darken a hex color by a factor"""
        if color.startswith('#'):
            color = color[1:]
        
        try:
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            
            r = max(0, int(r * (1 - factor)))
            g = max(0, int(g * (1 - factor)))
            b = max(0, int(b * (1 - factor)))
            
            return f'#{r:02x}{g:02x}{b:02x}'
        except:
            return color
    
    def apply_to_app(self):
        messagebox.showinfo("🔄 Apply Theme", 
                          "To apply this theme to your PDF app:\n\n"
                          "1. Click 'Generate Code' to get the theme code\n"
                          "2. Copy the generated code\n"
                          "3. Open your pdf_tool_desktop.py file\n"
                          "4. Replace the colors in setup_styles() method\n"
                          "5. Test with: python pdf_tool_desktop.py\n"
                          "6. Rebuild with: python build_executable.py")
    
    def show_help(self):
        help_text = """🎨 Theme Generator Help

🌈 COLORS:
- Use hex format: #ff0000 (red), #00ff00 (green), #0000ff (blue)
- Try online color pickers for inspiration
- Ensure good contrast between text and background

🔤 FONTS:
- Use system fonts for best compatibility
- Recommended: Segoe UI, Arial, Helvetica
- Larger sizes for titles, smaller for body text

⚡ QUICK START:
1. Try the preset themes first
2. Adjust colors and fonts to your taste
3. Use 'Generate Code' to get the CSS
4. Copy-paste into your app
5. Test before rebuilding

💡 TIPS:
- Dark backgrounds need light text
- Light backgrounds need dark text
- Use accent colors sparingly for buttons/highlights
- Test your theme with the actual app before finalizing
"""
        
        help_window = tk.Toplevel(self.root)
        help_window.title("❓ Theme Generator Help")
        help_window.geometry("600x500")
        help_window.configure(bg='white')
        
        help_frame = tk.Frame(help_window, bg='white', padx=20, pady=20)
        help_frame.pack(fill='both', expand=True)
        
        help_label = tk.Label(help_frame, text=help_text, font=('Arial', 11), 
                            bg='white', justify='left', anchor='nw')
        help_label.pack(fill='both', expand=True)

def main():
    root = tk.Tk()
    app = ThemePreviewTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()