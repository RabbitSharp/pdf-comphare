# PDF Comparison Tool

A professional tool for comparing PDF files with advanced features for reducing false positives and focusing on meaningful differences. Optimized for text-based PDF reports.

## Key Features

### Core Functionality
- 📄 **Drag & Drop interface** - Easy PDF upload
- 🔍 **Page-by-page comparison** - Detailed analysis
- 🎨 **Visual difference highlighting** - Red rectangles mark changes
- 📊 **Precise deviation metrics** - Percentage-based analysis optimized for text PDFs
- 🖼️ **Side-by-side view** - Optional original display

### Advanced Filtering
- 📑 **Manual page skip** - Exclude specific pages by number
- 🔤 **Text-based page skip** - Auto-skip pages containing specific text
- 🚫 **Exclusion zones** - Define areas to ignore (headers, footers, timestamps)
- 🎯 **Adjustable sensitivity** - Fine-tune comparison strictness
- 🔬 **Minimum area filter** - Ignore small rendering artifacts

### Professional Features
- 🎨 **Tab-based workflow** - Define zones, then compare
- 💾 **Export/import zones** - Reusable configurations (JSON)
- 📝 **Console logging** - Monitor operations and debug
- ⚙️ **Configurable quality** - Balance speed vs. accuracy

## How to Use

### Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   streamlit run app.py
   ```

3. **Define exclusion zones** (optional, Tab 1):
   - Upload a reference PDF
   - Enter coordinates for areas to exclude (headers, footers, etc.)
   - Export configuration for reuse

4. **Compare PDFs** (Tab 2):
   - Upload two PDFs
   - Configure comparison settings in sidebar
   - View results with color-coded deviations

### Tab 1: Define Exclusion Zones

**Purpose:** Define rectangular areas to exclude from comparison across all pages.

**Workflow:**
1. Upload reference PDF (any PDF with typical layout)
2. Download reference image to find coordinates
3. Enter zone coordinates (x1, y1, x2, y2)
4. Preview zones with visual overlay
5. Export as JSON for reuse (optional)

**Use Cases:**
- Headers with dates/timestamps
- Footers with page numbers
- Dynamic metadata fields
- Watermarks or logos

**Example zones:**
```
0,0,800,100        # Top header (100px tall)
0,2900,800,3000    # Bottom footer (100px tall)
650,20,780,50      # Corner timestamp
```

### Tab 2: Compare PDFs

**Purpose:** Compare two PDFs with all configured exclusions and filters.

**Settings (Sidebar):**
- **Image Quality (Zoom):** 1.0-4.0 (higher = better quality, slower)
- **Sensitivity:** 10-100 (higher = less sensitive, fewer false positives)
- **Minimum Area:** 20-500 pixels (ignore small differences)
- **Show Originals:** Toggle side-by-side view

**Page Skip Options:**
- **Manual:** Enter page numbers (e.g., "1,3,5")
- **Text-Based:** Enter search strings to find pages
- **Both:** Combine both methods

## Page Skip Features

### Manual Page Selection
Skip specific pages by number:
- Format: comma-separated (e.g., "1,3,5")
- Independent for each PDF
- Useful for cover pages, TOC, indices

### Text-Based Skip
Automatically skip pages containing specific text:
- Enter search strings (one per line)
- Case-sensitive or insensitive search
- Matches: "DRAFT", "Generated on", timestamps, etc.
- Skips entire pages, not partial content

**Example patterns:**
```
DRAFT
Generated on
Version
```

### Combined Approach
Use both methods together for maximum control:
- Manual skip of known pages (e.g., cover)
- Text-based skip of dynamic pages (e.g., with timestamps)
- Automatically merged and deduplicated

## Exclusion Zones

**What:** Rectangular areas excluded from comparison on all pages.

**When to use:**
- Headers/footers with dynamic content
- Timestamps or dates in consistent locations
- Page numbers
- User/session information
- More precise than skipping entire pages

**How to define:**
1. **Tab 1:** Upload reference PDF
2. Download reference image (PNG)
3. Open in image editor (Paint, GIMP, etc.)
4. Find pixel coordinates
5. Enter as: x1, y1, x2, y2
6. Preview and adjust

**Benefits:**
- Pixel-perfect accuracy
- Reusable configurations (JSON export/import)
- Apply same zones to multiple comparisons
- Compare rest of page while ignoring known differences

**Tip:** Open the downloaded reference image in an image editor (Paint, GIMP, Photoshop) to find exact pixel coordinates for the areas you want to exclude.

## Deviation Metrics

**Optimized for text-based PDF reports with low deviation.**

### Classification Scale

| Deviation | Badge | Meaning |
|-----------|-------|---------|
| 0.00% | ✅ Green | Identical - perfect match |
| < 0.3% | ℹ️ Blue | Minor differences |
| < 2.0% | ⚠️ Yellow | Moderate differences - noticeable content changes |
| ≥ 2.0% | ❌ Red | Major differences - significant changes |

**Why strict thresholds?**
Text-based reports typically have very low deviation when identical (0.00%) and small deviations only for actual content changes. This scale makes it easy to distinguish rendering artifacts from real differences.

## Accuracy Improvements

### Perceptual Color Difference
- Weighted RGB channels (R: 0.299, G: 0.587, B: 0.114)
- Matches human vision sensitivity
- Reduces false positives from minor color variations

### Noise Filtering
- **Gaussian blur** (sigma=1.5) - Smooths rendering artifacts
- **Morphological opening** - Removes small noise
- **Morphological closing** - Fills small gaps
- Significantly reduces antialiasing false positives

### Smart Region Detection
- Only highlights contiguous regions above minimum area
- Prevents scattered pixel noise from being marked
- Cleaner visualization of actual differences

### Configurable Thresholds

**Sensitivity** (10-100):
- Default: 50
- Higher values = less sensitive (fewer false positives)
- Recommended: 60-80 for text PDFs

**Minimum Area** (20-500 pixels):
- Default: 100
- Higher values = ignore smaller differences
- Recommended: 200-300 for text PDFs

## Installation

### Requirements
- Python 3.8 or higher
- At least 2GB RAM (more for large PDFs)
- Modern browser (Chrome, Firefox, Edge)

### Setup

1. **Clone or download** the repository

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

The app opens automatically at http://localhost:8501

## Best Practices

### For Text-Based Reports

**Recommended Settings:**
- **Sensitivity:** 60-70
- **Min Area:** 200-300
- **Zoom:** 2.0-2.5

**Expected Deviations:**
- Identical: 0.00%
- Rendering diffs: 0.1-0.3%
- Actual changes: 0.3-2.0%
- Major changes: > 2.0%

### Reducing False Positives

1. **Increase sensitivity** to 60-80
2. **Increase minimum area** to 200-300
3. **Use exclusion zones** for headers/footers with dynamic content
4. **Skip pages** with "Generated on", "DRAFT", or timestamps
5. **Use higher zoom** (2.5-3.0) for better rendering accuracy

### Workflow for Monthly Reports

**One-time setup:**
1. Tab 1: Define exclusion zones for headers/footers
2. Export zones as JSON
3. Save for future use

**Monthly comparison:**
1. Tab 1: Import saved zones
2. Tab 2: Upload current and previous reports
3. Configure page skip if needed
4. Review results

### Working with Large PDFs

- **Reduce zoom** (1.5-2.0) for faster processing
- **Disable "Show originals"** for better overview
- **Skip unnecessary pages** (covers, TOC)
- **Process in batches** if memory limited

## Technologies

- **PyMuPDF (fitz)** - High-performance PDF processing
- **Streamlit** - Modern web UI framework
- **Pillow (PIL)** - Image processing and manipulation
- **NumPy** - Numerical computations
- **SciPy** - Scientific computing for difference detection

## License

This project is licensed under the [MIT License](./LICENSE).
