"""
PDF Comparison Tool
Compares two PDF files and highlights the differences
"""
import io
import fitz  # PyMuPDF
import numpy as np
from PIL import Image, ImageDraw
from typing import Tuple, List


class PDFComparer:
    """Class to compare two PDF documents and visualize differences"""

    def __init__(self, zoom: float = 2.0):
        """
        Initialize PDF Comparer

        Args:
            zoom: Zoom factor for rendering PDFs (higher = better quality, slower)
        """
        self.zoom = zoom
        self.matrix = fitz.Matrix(zoom, zoom)

    def pdf_to_images(self, pdf_bytes: bytes) -> List[Image.Image]:
        """
        Convert PDF pages to PIL Images

        Args:
            pdf_bytes: PDF file as bytes

        Returns:
            List of PIL Images, one per page
        """
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        images = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            pix = page.get_pixmap(matrix=self.matrix)
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            images.append(img)

        doc.close()
        return images

    def get_page_count(self, pdf_bytes: bytes) -> int:
        """Get number of pages in PDF"""
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        count = len(doc)
        doc.close()
        return count

    def extract_text_from_page(self, pdf_bytes: bytes, page_num: int) -> str:
        """
        Extract text from a specific page

        Args:
            pdf_bytes: PDF file as bytes
            page_num: Page number (0-based)

        Returns:
            Extracted text from the page
        """
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        if page_num < 0 or page_num >= len(doc):
            doc.close()
            return ""

        page = doc[page_num]
        text = page.get_text()
        doc.close()
        return text

    def find_pages_with_text(self, pdf_bytes: bytes, search_strings: List[str],
                            case_sensitive: bool = False) -> List[int]:
        """
        Find all pages containing any of the specified search strings

        Args:
            pdf_bytes: PDF file as bytes
            search_strings: List of strings to search for
            case_sensitive: Whether the search should be case-sensitive

        Returns:
            List of page numbers (1-based) that contain any of the search strings
        """
        if not search_strings:
            return []

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        matching_pages = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()

            if not case_sensitive:
                text = text.lower()
                search_list = [s.lower() for s in search_strings]
            else:
                search_list = search_strings

            # Check if any search string is in the page text
            if any(search_str in text for search_str in search_list):
                matching_pages.append(page_num + 1)  # Convert to 1-based

        doc.close()
        return matching_pages

    def compare_images(self, img1: Image.Image, img2: Image.Image,
                      sensitivity: float = 50.0, min_area: int = 100) -> Tuple[Image.Image, float]:
        """
        Compare two images and create a difference visualization with improved false positive reduction

        Args:
            img1: First image
            img2: Second image
            sensitivity: Threshold for detecting differences (0-255, higher = less sensitive)
            min_area: Minimum area in pixels for a difference region to be considered significant

        Returns:
            Tuple of (difference image with highlights, difference percentage)
        """
        # Ensure both images have the same size
        if img1.size != img2.size:
            # Resize to the larger dimensions
            width = max(img1.width, img2.width)
            height = max(img1.height, img2.height)

            # Create new images with white background
            new_img1 = Image.new('RGB', (width, height), 'white')
            new_img2 = Image.new('RGB', (width, height), 'white')

            new_img1.paste(img1, (0, 0))
            new_img2.paste(img2, (0, 0))

            img1 = new_img1
            img2 = new_img2

        # Convert to RGB if necessary
        if img1.mode != 'RGB':
            img1 = img1.convert('RGB')
        if img2.mode != 'RGB':
            img2 = img2.convert('RGB')

        # Convert to numpy arrays for advanced processing
        img1_np = np.array(img1, dtype=np.float32)
        img2_np = np.array(img2, dtype=np.float32)

        # Calculate perceptual difference using weighted RGB channels
        # Human eye is more sensitive to green, then red, then blue
        diff_r = np.abs(img1_np[:, :, 0] - img2_np[:, :, 0]) * 0.299
        diff_g = np.abs(img1_np[:, :, 1] - img2_np[:, :, 1]) * 0.587
        diff_b = np.abs(img1_np[:, :, 2] - img2_np[:, :, 2]) * 0.114

        # Combine into perceptual difference
        diff_gray_np = diff_r + diff_g + diff_b

        # Apply Gaussian blur to reduce noise and minor antialiasing differences
        from scipy.ndimage import gaussian_filter
        diff_gray_np = gaussian_filter(diff_gray_np, sigma=1.5)

        # Create a mask for significant differences
        mask = diff_gray_np > sensitivity

        # Apply morphological operations to reduce noise
        from scipy.ndimage import binary_opening, binary_closing
        # Remove small noise
        mask = binary_opening(mask, structure=np.ones((3, 3)))
        # Fill small holes
        mask = binary_closing(mask, structure=np.ones((5, 5)))

        # Calculate difference percentage based on significant differences only
        significant_diff_pixels = np.sum(mask)
        total_pixels = mask.shape[0] * mask.shape[1]
        diff_percentage = (significant_diff_pixels / total_pixels) * 100

        # Find contiguous regions and filter by minimum area
        labeled_mask = self._find_difference_regions(mask, min_size=min_area)

        # Create overlay image
        overlay = img2.copy()

        # Only draw if there are significant differences
        if labeled_mask:
            # Create red overlay
            red_overlay = Image.new('RGBA', img2.size, (255, 0, 0, 0))
            red_draw = ImageDraw.Draw(red_overlay)

            for region in labeled_mask:
                x1, y1, x2, y2 = region
                red_draw.rectangle([x1, y1, x2, y2], fill=(255, 0, 0, 80), outline=(255, 0, 0, 200), width=2)

            # Composite the overlay
            overlay = overlay.convert('RGBA')
            overlay = Image.alpha_composite(overlay, red_overlay)
            overlay = overlay.convert('RGB')

        return overlay, diff_percentage

    def _find_difference_regions(self, mask: np.ndarray, min_size: int = 10) -> List[Tuple[int, int, int, int]]:
        """
        Find rectangular regions containing differences

        Args:
            mask: Boolean mask of differences
            min_size: Minimum size of region to detect

        Returns:
            List of (x1, y1, x2, y2) tuples for difference regions
        """
        from scipy import ndimage

        # Label connected components
        try:
            labeled, num_features = ndimage.label(mask)
        except ImportError:
            # Fallback if scipy is not available - create one big box
            if np.any(mask):
                coords = np.argwhere(mask)
                y1, x1 = coords.min(axis=0)
                y2, x2 = coords.max(axis=0)
                return [(int(x1), int(y1), int(x2), int(y2))]
            return []

        regions = []
        for i in range(1, num_features + 1):
            component = labeled == i
            coords = np.argwhere(component)

            if len(coords) < min_size:
                continue

            y1, x1 = coords.min(axis=0)
            y2, x2 = coords.max(axis=0)

            # Add some padding
            padding = 5
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(mask.shape[1] - 1, x2 + padding)
            y2 = min(mask.shape[0] - 1, y2 + padding)

            regions.append((int(x1), int(y1), int(x2), int(y2)))

        return regions

    def compare_pdfs(self, pdf1_bytes: bytes, pdf2_bytes: bytes,
                    sensitivity: float = 50.0, min_area: int = 100,
                    skip_pages_pdf1: List[int] = None, skip_pages_pdf2: List[int] = None) -> List[Tuple[Image.Image, Image.Image, Image.Image, float, int, int]]:
        """
        Compare two PDFs page by page

        Args:
            pdf1_bytes: First PDF as bytes
            pdf2_bytes: Second PDF as bytes
            sensitivity: Threshold for detecting differences (0-255, higher = less sensitive)
            min_area: Minimum area in pixels for a difference region
            skip_pages_pdf1: List of page numbers (1-based) to skip from PDF 1
            skip_pages_pdf2: List of page numbers (1-based) to skip from PDF 2

        Returns:
            List of tuples (img1, img2, diff_img, diff_percentage, page_num_pdf1, page_num_pdf2) for each page
        """
        if skip_pages_pdf1 is None:
            skip_pages_pdf1 = []
        if skip_pages_pdf2 is None:
            skip_pages_pdf2 = []

        # Convert to 0-based indexing for internal use
        skip_pages_pdf1_zero = set(p - 1 for p in skip_pages_pdf1)
        skip_pages_pdf2_zero = set(p - 1 for p in skip_pages_pdf2)

        images1 = self.pdf_to_images(pdf1_bytes)
        images2 = self.pdf_to_images(pdf2_bytes)

        # Filter out skipped pages
        filtered_images1 = [(i, img) for i, img in enumerate(images1) if i not in skip_pages_pdf1_zero]
        filtered_images2 = [(i, img) for i, img in enumerate(images2) if i not in skip_pages_pdf2_zero]

        # Compare page by page
        max_pages = max(len(filtered_images1), len(filtered_images2))
        results = []

        for i in range(max_pages):
            # Handle PDFs with different page counts
            if i >= len(filtered_images1):
                page_num_pdf1 = None
                img1 = Image.new('RGB', filtered_images2[i][1].size, 'white')
            else:
                page_num_pdf1 = filtered_images1[i][0] + 1  # Convert back to 1-based
                img1 = filtered_images1[i][1]

            if i >= len(filtered_images2):
                page_num_pdf2 = None
                img2 = Image.new('RGB', filtered_images1[i][1].size, 'white')
            else:
                page_num_pdf2 = filtered_images2[i][0] + 1  # Convert back to 1-based
                img2 = filtered_images2[i][1]

            diff_img, diff_pct = self.compare_images(img1, img2, sensitivity, min_area)
            results.append((img1, img2, diff_img, diff_pct, page_num_pdf1, page_num_pdf2))

        return results
