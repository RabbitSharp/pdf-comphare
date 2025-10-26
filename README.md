# PDF Comparison Tool

A simple yet powerful tool for comparing two PDF files with visual highlighting of differences.

## Features

- 📄 Drag & Drop interface for PDF files
- 🔍 Page-by-page comparison
- 🎨 Visual highlighting of differences in red
- 📊 Percentage deviation analysis
- ⚙️ Adjustable image quality
- 🎯 Configurable sensitivity to reduce false positives
- 🔬 Minimum area threshold to filter noise
- 🖼️ Optional: Display original documents
- 📑 **Skip pages manually** by page number
- 🔤 **Skip pages automatically** by text content

## Page Skip Features

### Manual Page Selection
- Enter specific page numbers to exclude from comparison
- Comma-separated format (e.g., "1,3,5")
- Different pages can be skipped from each PDF

### Text-Based Page Skip (NEW!)
- Automatically skip pages containing specific text patterns
- Enter search strings (one per line)
- Case-sensitive or case-insensitive search
- Perfect for excluding pages with:
  - Timestamps or dates
  - Version numbers
  - "DRAFT" or "CONFIDENTIAL" watermarks
  - Dynamic content
  - Cover pages or table of contents

### Combined Approach
- Use both manual and text-based methods together
- Automatically combines and deduplicates skip lists
- Provides maximum flexibility

### Limitations

- **OCR not supported**: Only works with text-based PDFs (not scanned images)
- **Exact substring**: Must match the text exactly as it appears
- **No regex**: Simple substring matching (no regular expressions)
- **Page-level**: Skips entire pages, not partial content

## Accuracy Improvements

- **Perceptual color difference**: Uses weighted RGB channels matching human vision
- **Gaussian blur filtering**: Reduces minor antialiasing and rendering artifacts
- **Morphological operations**: Removes noise and fills small gaps
- **Configurable thresholds**: Adjust sensitivity and minimum area to suit your needs
- **Smart region detection**: Only highlights significant, contiguous difference areas

#### Perceptual Color Difference
- Uses weighted RGB channels (R: 0.299, G: 0.587, B: 0.114)
- More accurate representation of visible differences
- Reduces false positives from minor color variations

#### Noise Filtering
- Gaussian blur (sigma=1.5) to smooth out minor rendering artifacts
- Morphological opening to remove small noise
- Morphological closing to fill small gaps
- Significantly reduces antialiasing false positives

#### Configurable Thresholds
- **Sensitivity Threshold** (10-100): Control how sensitive the comparison is
    - Default: 50
    - Higher values = less sensitive (fewer false positives)
    - Recommended: 60-80 for most PDFs

- **Minimum Difference Area** (20-500 pixels): Filter out small artifacts
    - Default: 100
    - Higher values = ignore smaller differences
    - Recommended: 200-300 to filter rendering noise

#### 4. Region Detection
- Only highlights contiguous regions above minimum area threshold
- Prevents scattered pixel noise from being marked
- Cleaner visualization of actual differences

### General Recommendations
For best results with similar PDFs that show many false positives:
1. Set sensitivity to 60-80
2. Set minimum area to 200-300
3. Use zoom level 2.5-3.0
4. Check the "Show originals" option to verify real differences

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
   - **Sensitivity Threshold**: Higher values reduce false positives (try 60-80)
   - **Minimum Difference Area**: Filters out small rendering artifacts (try 200-300)
   - **Show originals**: Toggle display of original PDFs
   - **Page Selection**: Choose skip method (Manual, Text-Based, or Both)
     - Manual: Enter page numbers to skip (e.g., "1,3,5")
     - Text-Based: Enter text patterns to find and skip pages
     - Both: Combine both methods

5. Results:
   - Overall statistics with average deviation
   - Page-by-page view with highlighted differences
   - Color-coded deviation levels (green/blue/yellow/red)

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

- **For large PDFs**: Reduce image quality (zoom) for faster processing
- **For many pages**: Disable "Show originals" for better overview
- **To reduce false positives**: 
  - Increase sensitivity threshold to 60-80
  - Increase minimum area to 200-300
  - Use text-based skip for pages with dynamic content (dates, timestamps)
  - Skip cover pages and pages with version numbers
- **For consistent comparisons**: 
  - Skip pages with "Generated on", "Created:", or other timestamps
  - Skip pages containing "DRAFT" or "CONFIDENTIAL" watermarks
  - Use the same skip settings when comparing multiple document versions
  - Increase minimum area to 200-300 pixels
  - Use higher zoom (2.5-3.0) for better rendering accuracy
- **For very similar PDFs**: Lower sensitivity to 30-40 to catch subtle differences
- First run may take longer as Streamlit initializes

## License
This project is licensed under the [MIT License](./LICENSE).
