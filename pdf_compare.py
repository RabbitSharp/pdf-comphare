"""
PDF Comparison Tool
Compares two PDF files and highlights the differences
"""
import io
import fitz  # PyMuPDF
import numpy as np
from PIL import Image, ImageChops, ImageDraw
from typing import Tuple, List, Optional


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

    def compare_images(self, img1: Image.Image, img2: Image.Image) -> Tuple[Image.Image, float]:
        """
        Compare two images and create a difference visualization

        Args:
            img1: First image
            img2: Second image

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

        # Calculate pixel-wise difference
        diff = ImageChops.difference(img1, img2)

        # Convert to numpy for analysis
        diff_np = np.array(diff)

        # Calculate difference percentage
        total_pixels = diff_np.shape[0] * diff_np.shape[1] * diff_np.shape[2]
        diff_pixels = np.count_nonzero(diff_np)
        diff_percentage = (diff_pixels / total_pixels) * 100

        # Create visualization with red highlights
        # Convert difference to grayscale to find changed areas
        diff_gray = diff.convert('L')
        diff_gray_np = np.array(diff_gray)

        # Create a mask for differences (threshold to reduce noise)
        threshold = 30
        mask = diff_gray_np > threshold

        # Create overlay image
        overlay = img2.copy()
        overlay_draw = ImageDraw.Draw(overlay, 'RGBA')

        # Highlight differences in red with transparency
        mask_pil = Image.fromarray((mask * 255).astype(np.uint8))

        # Create red overlay
        red_overlay = Image.new('RGBA', img2.size, (255, 0, 0, 0))
        red_draw = ImageDraw.Draw(red_overlay)

        # Find contiguous regions of differences and draw rectangles
        labeled_mask = self._find_difference_regions(mask)

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

    def compare_pdfs(self, pdf1_bytes: bytes, pdf2_bytes: bytes) -> List[Tuple[Image.Image, Image.Image, Image.Image, float]]:
        """
        Compare two PDFs page by page

        Args:
            pdf1_bytes: First PDF as bytes
            pdf2_bytes: Second PDF as bytes

        Returns:
            List of tuples (img1, img2, diff_img, diff_percentage) for each page
        """
        images1 = self.pdf_to_images(pdf1_bytes)
        images2 = self.pdf_to_images(pdf2_bytes)

        # Compare page by page
        max_pages = max(len(images1), len(images2))
        results = []

        for i in range(max_pages):
            # Handle PDFs with different page counts
            if i >= len(images1):
                img1 = Image.new('RGB', images2[i].size, 'white')
            else:
                img1 = images1[i]

            if i >= len(images2):
                img2 = Image.new('RGB', images1[i].size, 'white')
            else:
                img2 = images2[i]

            diff_img, diff_pct = self.compare_images(img1, img2)
            results.append((img1, img2, diff_img, diff_pct))

        return results
