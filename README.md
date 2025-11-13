# 🖥️ PDF Tools - Desktop Application

A beautiful, offline PDF merger and splitter tool for Windows.

## ✨ Features

### 📄 Merge PDFs
- Select multiple PDF files
- Drag and drop interface
- Reorder files before merging
- Save merged PDF anywhere

### ✂️ Split PDFs
- Select specific pages to extract
- Support for page ranges (e.g., "1-5,10,15-20")
- Preview PDF information (total pages)
- Save split PDF with custom name

## 🚀 Quick Start

### Option 1: Run Pre-built Executable (Recommended)
1. Download `PDFTools.exe` from the releases
2. Double-click to run - no installation needed!
3. Works on any Windows PC without Python

### Option 2: Build from Source
1. Install Python 3.7+ from python.org
2. Download this project
3. Run the build script:
```bash
python build_executable.py
```
4. Find `PDFTools.exe` in the `dist` folder

### Option 3: Run with Python
1. Install Python 3.7+
2. Install requirements:
```bash
pip install -r requirements_desktop.txt
```
3. Run the application:
```bash
python pdf_tool_desktop.py
```

## 📸 Screenshots

### Merge PDFs Tab
- Clean interface for selecting multiple files
- Visual feedback for selected files
- One-click merge with save dialog

### Split PDF Tab
- File analyzer shows page count
- Intuitive page range input
- Examples and help text included

## 💡 Usage Examples

### Merging PDFs
1. Click "Select PDF Files" button
2. Choose 2 or more PDF files
3. Reorder if needed (drag and drop)
4. Click "Merge PDFs"
5. Choose save location

### Splitting PDFs
1. Click "Select PDF File" 
2. Enter pages to extract:
   - Single pages: `1,3,5`
   - Page ranges: `1-5`
   - Mixed: `1-3,7,10-12`
3. Click "Split PDF"
4. Choose save location

## 🛠️ Technical Details

- **Framework**: Python + Tkinter (native GUI)
- **PDF Processing**: PyPDF2
- **Packaging**: PyInstaller
- **Size**: ~15MB executable
- **Requirements**: Windows 7+ (no additional dependencies)

## 🎨 Design Features

- **Modern UI**: Clean, intuitive interface
- **Color-coded Status**: Green for success, red for errors
- **Progress Feedback**: Real-time status updates
- **Error Handling**: Helpful error messages
- **Responsive Design**: Works on different screen sizes

## 📁 File Structure

```
PDFTools/
├── pdf_tool_desktop.py     # Main application
├── build_executable.py     # Build script
├── requirements_desktop.txt # Dependencies
├── README_Desktop.md       # This file
└── dist/
    └── PDFTools.exe       # Built executable
```

## 🔧 Building Custom Executable

To customize the build:

1. Edit `pdf_tool_desktop.py` for functionality changes
2. Modify `build_executable.py` for build options
3. Run: `python build_executable.py`

### PyInstaller Options Used:
- `--onefile`: Single executable file
- `--windowed`: No console window
- `--clean`: Clean build cache

## 🎯 Why Desktop App?

### Advantages over Web Version:
✅ **No internet required** - works completely offline  
✅ **No server costs** - no deployment complexity  
✅ **Better performance** - direct file access  
✅ **Privacy focused** - files never leave your computer  
✅ **Easy distribution** - single .exe file  
✅ **No browser dependencies** - works everywhere  

### Perfect for:
- 🏢 Corporate environments with restricted internet
- 🔒 Sensitive documents that can't go online
- 🚀 Users who want instant, reliable PDF processing
- 📱 Situations where web access is limited

## 📞 Support

This desktop application provides the same great functionality as the web version, but with the reliability and privacy of offline processing.

**File processing is 100% local - your PDFs never leave your computer!** 🔒