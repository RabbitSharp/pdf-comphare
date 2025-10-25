# PDF Comparison Tool

A simple yet powerful tool for comparing two PDF files with visual highlighting of differences.

## Features

- 📄 Drag & Drop interface for PDF files
- 🔍 Page-by-page comparison
- 🎨 Visual highlighting of differences in red
- 📊 Percentage deviation analysis
- ⚙️ Adjustable image quality
- 🖼️ Optional: Display original documents

## Technologies

- **PyMuPDF (fitz)**: High-performance PDF processing
- **Streamlit**: Modern web UI
- **Pillow**: Image processing and comparison
- **NumPy**: Numerical computations
- **SciPy**: Scientific computing for difference detection

## Installation

1. Clone the repository or navigate to the project directory

2. Create a virtual environment (optional but recommended):
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Streamlit app:
```bash
streamlit run app.py
```

2. The app will automatically open in your browser (default: http://localhost:8501)

3. Upload two PDF files:
   - Use drag & drop or click on the upload areas
   - Both PDFs must be uploaded to start the comparison

4. Adjust settings (sidebar):
   - **Image Quality**: Higher values for better quality (slower)
   - **Show originals**: Toggle display of original PDFs

5. Results:
   - Overall statistics with average deviation
   - Page-by-page view with highlighted differences
   - Color-coded deviation levels (green/blue/yellow/red)

## Examples

Example PDFs can be found in the `examples/` directory.

## How it works

1. **PDF to Image**: Each PDF page is converted to a high-resolution image
2. **Pixel-wise Comparison**: Images are compared pixel by pixel
3. **Find Differences**: Areas with differences are identified
4. **Visualization**: Differences are highlighted with red rectangles
5. **Statistics**: Calculation of percentage deviation

## Requirements

- Python 3.8 or higher
- At least 2GB RAM (more for large PDFs)
- Modern browser (Chrome, Firefox, Edge)

## Tips

- For large PDFs: Reduce image quality (zoom) for faster processing
- For many pages: Disable "Show originals" for better overview
- First run may take longer as Streamlit initializes

## License

MIT License

## Author

Created for comparing PDF documents
