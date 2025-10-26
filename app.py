"""
Streamlit App for PDF Comparison
"""
import streamlit as st
import json
from pdf_compare import PDFComparer
from PIL import ImageDraw
import io


def main():
    st.set_page_config(
        page_title="PDF Comparison Tool",
        page_icon="📄",
        layout="wide"
    )

    st.title("📄 PDF Comparison Tool")
    st.markdown("""
    Compare two PDF files with advanced exclusion zone support.
    Differences will be highlighted in red.
    """)

    # Initialize session state
    if 'exclusion_zones' not in st.session_state:
        st.session_state.exclusion_zones = []
    if 'reference_image' not in st.session_state:
        st.session_state.reference_image = None
    if 'zoom_factor' not in st.session_state:
        st.session_state.zoom_factor = 2.0

    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")

        # Zoom factor
        zoom = st.slider(
            "Image Quality (Zoom)",
            min_value=1.0,
            max_value=4.0,
            value=st.session_state.zoom_factor,
            step=0.5,
            help="Higher values = better quality, but slower"
        )
        st.session_state.zoom_factor = zoom

        st.markdown("#### Comparison Settings")

        # Sensitivity
        sensitivity = st.slider(
            "Sensitivity Threshold",
            min_value=10.0,
            max_value=100.0,
            value=50.0,
            step=5.0,
            help="Higher values = less sensitive (fewer false positives). Try 60-80 to reduce noise."
        )

        # Minimum area
        min_area = st.slider(
            "Minimum Difference Area (pixels)",
            min_value=20,
            max_value=500,
            value=100,
            step=20,
            help="Ignore small differences below this size. Helps filter out minor rendering artifacts."
        )

        show_originals = st.checkbox(
            "Show originals",
            value=True,
            help="Display the original PDFs alongside the comparison"
        )

        st.markdown("---")
        st.markdown("### 📄 Page Selection")

        # Skip method
        skip_method = st.radio(
            "Skip method",
            ["Manual Page Numbers", "Text-Based", "Both"],
            help="Choose how to select pages to skip"
        )

        if skip_method in ["Manual Page Numbers", "Both"]:
            st.markdown("**Manual Selection** (comma-separated, e.g., 1,3,5):")
            skip_pages_1_input = st.text_input(
                "Skip pages from PDF 1",
                value="",
                help="Enter page numbers to skip from the first PDF, separated by commas",
                key="skip_pdf1"
            )

            skip_pages_2_input = st.text_input(
                "Skip pages from PDF 2",
                value="",
                help="Enter page numbers to skip from the second PDF, separated by commas",
                key="skip_pdf2"
            )
        else:
            skip_pages_1_input = ""
            skip_pages_2_input = ""

        if skip_method in ["Text-Based", "Both"]:
            st.markdown("**Text-Based Selection:**")

            skip_text_1_input = st.text_area(
                "Skip pages containing (PDF 1)",
                value="",
                height=80,
                help="Enter text strings (one per line). Pages containing any of these strings will be skipped.",
                key="skip_text_pdf1"
            )

            skip_text_2_input = st.text_area(
                "Skip pages containing (PDF 2)",
                value="",
                height=80,
                help="Enter text strings (one per line). Pages containing any of these strings will be skipped.",
                key="skip_text_pdf2"
            )

            case_sensitive = st.checkbox(
                "Case-sensitive search",
                value=False,
                help="Whether the text search should be case-sensitive"
            )
        else:
            skip_text_1_input = ""
            skip_text_2_input = ""
            case_sensitive = False

        st.markdown("---")
        st.markdown("### 📊 Statistics")
        if st.session_state.exclusion_zones:
            st.write(f"Exclusion zones: {len(st.session_state.exclusion_zones)}")
        else:
            st.write("No exclusion zones defined")

        st.markdown("---")
        st.markdown("### ℹ️ Info")
        st.markdown("""
        **Features:**
        - Page-by-page comparison
        - Differences highlighted in red
        - Skip pages manually or by text content
        - Define exclusion zones visually
        - Export/import zone configurations
        
        **Tips for reducing false positives:**
        - Increase sensitivity threshold (60-80)
        - Increase minimum area (200-300)
        - Use higher zoom for better rendering
        - Define exclusion zones for dynamic content
        """)

    # Main content tabs
    tab1, tab2 = st.tabs(["🎯 Define Exclusion Zones", "🔍 Compare PDFs"])

    # Tab 1: Define exclusion zones
    with tab1:
        st.header("Define Exclusion Zones on Reference PDF")
        st.info("📌 Upload a reference PDF and define rectangles over areas to exclude from comparison.")

        reference_pdf = st.file_uploader(
            "Upload Reference PDF",
            type=['pdf'],
            key='reference_pdf'
        )

        if reference_pdf:
            # Convert first page to image
            comparer = PDFComparer(zoom=st.session_state.zoom_factor)
            pdf_bytes = reference_pdf.read()
            images = comparer.pdf_to_images(pdf_bytes)

            if images:
                ref_img = images[0]  # Only first page
                st.session_state.reference_image = ref_img

                st.success(f"✅ PDF loaded - Image size: {ref_img.width} x {ref_img.height} pixels")

                col1, col2 = st.columns([2, 1])

                with col1:
                    st.subheader("Preview with Exclusion Zones")

                    # Draw exclusion zones on image
                    preview_img = ref_img.copy()
                    draw = ImageDraw.Draw(preview_img)

                    for i, zone in enumerate(st.session_state.exclusion_zones):
                        x1, y1, x2, y2 = zone
                        # Draw red rectangle
                        draw.rectangle([x1, y1, x2, y2], outline='red', width=3)
                        # Add label
                        draw.text((x1 + 5, y1 + 5), f"Zone {i+1}", fill='red')

                    st.image(preview_img, use_container_width=True, caption="Reference PDF with Exclusion Zones")

                    # Coordinate system help
                    with st.expander("ℹ️ Help: Coordinate System"):
                        st.write("""
                        **Coordinate System:**
                        - Origin (0,0) is top-left
                        - X-axis: left to right
                        - Y-axis: top to bottom
                        - Format: (x1, y1, x2, y2)
                          - (x1, y1): Top-left corner
                          - (x2, y2): Bottom-right corner
                        
                        **Tip:** Open the image in an image editor to find exact coordinates.
                        """)

                        # Download reference image
                        buf = io.BytesIO()
                        ref_img.save(buf, format='PNG')
                        st.download_button(
                            label="📥 Download Reference Image",
                            data=buf.getvalue(),
                            file_name="reference_page1.png",
                            mime="image/png"
                        )

                with col2:
                    st.subheader("Add Zone")

                    with st.form("add_zone_form"):
                        st.write("**Rectangle Coordinates:**")
                        col_x1, col_y1 = st.columns(2)
                        col_x2, col_y2 = st.columns(2)

                        with col_x1:
                            x1 = st.number_input("X1 (left)", min_value=0, max_value=ref_img.width, value=0, step=10)
                        with col_y1:
                            y1 = st.number_input("Y1 (top)", min_value=0, max_value=ref_img.height, value=0, step=10)
                        with col_x2:
                            x2 = st.number_input("X2 (right)", min_value=0, max_value=ref_img.width, value=100, step=10)
                        with col_y2:
                            y2 = st.number_input("Y2 (bottom)", min_value=0, max_value=ref_img.height, value=100, step=10)

                        submitted = st.form_submit_button("➕ Add Zone")
                        if submitted:
                            if x2 > x1 and y2 > y1:
                                st.session_state.exclusion_zones.append((int(x1), int(y1), int(x2), int(y2)))
                                st.success("Zone added!")
                                st.rerun()
                            else:
                                st.error("X2 must be greater than X1 and Y2 greater than Y1!")

                    st.divider()

                    st.subheader("Defined Zones")
                    if st.session_state.exclusion_zones:
                        for i, zone in enumerate(st.session_state.exclusion_zones):
                            col_info, col_del = st.columns([3, 1])
                            with col_info:
                                st.write(f"**Zone {i+1}:**")
                                st.write(f"X: {zone[0]} → {zone[2]}")
                                st.write(f"Y: {zone[1]} → {zone[3]}")
                            with col_del:
                                if st.button("🗑️", key=f"del_{i}"):
                                    st.session_state.exclusion_zones.pop(i)
                                    st.rerun()
                            st.divider()

                        # Export zones
                        zones_json = json.dumps(st.session_state.exclusion_zones, indent=2)
                        st.download_button(
                            label="📥 Export as JSON",
                            data=zones_json,
                            file_name="exclusion_zones.json",
                            mime="application/json"
                        )
                    else:
                        st.info("No zones defined yet")

                    # Import zones
                    st.subheader("Import Zones")
                    uploaded_zones = st.file_uploader(
                        "Upload JSON file",
                        type=['json'],
                        key='zones_upload'
                    )
                    if uploaded_zones:
                        try:
                            zones_data = json.load(uploaded_zones)
                            st.session_state.exclusion_zones = zones_data
                            st.success(f"{len(zones_data)} zones imported!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error importing: {e}")

                    # Clear zones
                    if st.button("🗑️ Clear All Zones"):
                        st.session_state.exclusion_zones = []
                        st.rerun()

    # Tab 2: Compare PDFs
    with tab2:
        st.header("Compare PDFs")

        # Create two columns for file upload
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("PDF 1")
            pdf1 = st.file_uploader(
                "Upload first PDF file",
                type=['pdf'],
                key='pdf1',
                help="Drag and drop the PDF file here or click to browse"
            )

        with col2:
            st.subheader("PDF 2")
            pdf2 = st.file_uploader(
                "Upload second PDF file",
                type=['pdf'],
                key='pdf2',
                help="Drag and drop the PDF file here or click to browse"
            )

        # Compare PDFs when both are uploaded
        if pdf1 is not None and pdf2 is not None:
            with st.spinner("Comparing PDFs..."):
                try:
                    # Read PDF bytes
                    pdf1_bytes = pdf1.read()
                    pdf2_bytes = pdf2.read()

                    # Create comparer
                    comparer = PDFComparer(zoom=zoom)

                    # Get page counts
                    pages1 = comparer.get_page_count(pdf1_bytes)
                    pages2 = comparer.get_page_count(pdf2_bytes)

                    # Parse skip pages input - Manual page numbers
                    skip_pages_1 = []
                    skip_pages_2 = []

                    if skip_pages_1_input.strip():
                        try:
                            skip_pages_1 = [int(p.strip()) for p in skip_pages_1_input.split(',') if p.strip()]
                            # Validate page numbers
                            invalid_pages = [p for p in skip_pages_1 if p < 1 or p > pages1]
                            if invalid_pages:
                                st.warning(f"⚠️ Invalid page numbers for PDF 1: {invalid_pages}. Valid range: 1-{pages1}")
                                skip_pages_1 = [p for p in skip_pages_1 if 1 <= p <= pages1]
                        except ValueError:
                            st.error("❌ Invalid format for PDF 1 skip pages. Please use comma-separated numbers (e.g., 1,3,5)")
                            skip_pages_1 = []

                    if skip_pages_2_input.strip():
                        try:
                            skip_pages_2 = [int(p.strip()) for p in skip_pages_2_input.split(',') if p.strip()]
                            # Validate page numbers
                            invalid_pages = [p for p in skip_pages_2 if p < 1 or p > pages2]
                            if invalid_pages:
                                st.warning(f"⚠️ Invalid page numbers for PDF 2: {invalid_pages}. Valid range: 1-{pages2}")
                                skip_pages_2 = [p for p in skip_pages_2 if 1 <= p <= pages2]
                        except ValueError:
                            st.error("❌ Invalid format for PDF 2 skip pages. Please use comma-separated numbers (e.g., 1,3,5)")
                            skip_pages_2 = []

                    # Parse text-based skip criteria
                    text_based_skip_1 = []
                    text_based_skip_2 = []

                    if skip_text_1_input.strip():
                        search_strings_1 = [line.strip() for line in skip_text_1_input.split('\n') if line.strip()]
                        if search_strings_1:
                            with st.spinner("Analyzing PDF 1 for text patterns..."):
                                text_based_skip_1 = comparer.find_pages_with_text(pdf1_bytes, search_strings_1, case_sensitive)
                            if text_based_skip_1:
                                st.info(f"📝 Found matching text in PDF 1 on pages: {sorted(text_based_skip_1)}")

                    if skip_text_2_input.strip():
                        search_strings_2 = [line.strip() for line in skip_text_2_input.split('\n') if line.strip()]
                        if search_strings_2:
                            with st.spinner("Analyzing PDF 2 for text patterns..."):
                                text_based_skip_2 = comparer.find_pages_with_text(pdf2_bytes, search_strings_2, case_sensitive)
                            if text_based_skip_2:
                                st.info(f"📝 Found matching text in PDF 2 on pages: {sorted(text_based_skip_2)}")

                    # Combine manual and text-based skip lists (remove duplicates)
                    skip_pages_1 = sorted(set(skip_pages_1 + text_based_skip_1))
                    skip_pages_2 = sorted(set(skip_pages_2 + text_based_skip_2))

                    # Show info
                    info_text = f"📊 PDF 1: {pages1} page(s) | PDF 2: {pages2} page(s)"
                    if skip_pages_1:
                        info_text += f" | Skipping from PDF 1: {skip_pages_1}"
                    if skip_pages_2:
                        info_text += f" | Skipping from PDF 2: {skip_pages_2}"
                    if st.session_state.exclusion_zones:
                        info_text += f" | Exclusion zones: {len(st.session_state.exclusion_zones)}"
                    st.info(info_text)

                    # Compare PDFs
                    results = comparer.compare_pdfs(
                        pdf1_bytes, pdf2_bytes,
                        sensitivity, min_area,
                        skip_pages_pdf1=skip_pages_1,
                        skip_pages_pdf2=skip_pages_2,
                        exclusion_zones=st.session_state.exclusion_zones
                    )

                    # Calculate overall difference
                    avg_diff = sum(r[3] for r in results) / len(results) if results else 0

                    # Show overall statistics
                    st.markdown("---")
                    st.subheader("📈 Overall Statistics")

                    metric_cols = st.columns(3)
                    with metric_cols[0]:
                        st.metric("Average Deviation", f"{avg_diff:.2f}%")
                    with metric_cols[1]:
                        st.metric("Number of Pages Compared", len(results))
                    with metric_cols[2]:
                        identical_pages = sum(1 for r in results if r[3] < 1.0)
                        st.metric("Identical Pages", f"{identical_pages}/{len(results)}")

                    st.markdown("---")

                    # Display results for each page
                    for idx, (img1, img2, diff_img, diff_pct, page_num_pdf1, page_num_pdf2) in enumerate(results):
                        # Create page header based on which pages are being compared
                        if page_num_pdf1 is not None and page_num_pdf2 is not None:
                            page_header = f"Comparison {idx + 1}: PDF 1 Page {page_num_pdf1} ↔ PDF 2 Page {page_num_pdf2}"
                        elif page_num_pdf1 is not None:
                            page_header = f"Comparison {idx + 1}: PDF 1 Page {page_num_pdf1} ↔ PDF 2 (empty)"
                        elif page_num_pdf2 is not None:
                            page_header = f"Comparison {idx + 1}: PDF 1 (empty) ↔ PDF 2 Page {page_num_pdf2}"
                        else:
                            page_header = f"Comparison {idx + 1}"

                        st.subheader(page_header)

                        # Color code based on difference
                        if diff_pct < 1.0:
                            st.success(f"✅ Deviation: {diff_pct:.2f}% (Nearly identical)")
                        elif diff_pct < 5.0:
                            st.info(f"ℹ️ Deviation: {diff_pct:.2f}% (Minor differences)")
                        elif diff_pct < 15.0:
                            st.warning(f"⚠️ Deviation: {diff_pct:.2f}% (Moderate differences)")
                        else:
                            st.error(f"❌ Deviation: {diff_pct:.2f}% (Major differences)")

                        # Display images
                        if show_originals:
                            cols = st.columns(3)
                            with cols[0]:
                                st.markdown("**PDF 1**")
                                st.image(img1, use_container_width=True)
                            with cols[1]:
                                st.markdown("**PDF 2**")
                                st.image(img2, use_container_width=True)
                            with cols[2]:
                                st.markdown("**Differences**")
                                st.image(diff_img, use_container_width=True)
                        else:
                            st.markdown("**Differences highlighted**")
                            st.image(diff_img, use_container_width=True)

                        st.markdown("---")

                    st.success("✅ Comparison completed!")

                except Exception as e:
                    st.error(f"❌ Error comparing PDFs: {str(e)}")
                    st.exception(e)

        elif pdf1 is not None or pdf2 is not None:
            st.warning("⚠️ Please upload both PDF files to compare them.")
        else:
            st.info("👆 Upload two PDF files in the fields above to compare them.")


if __name__ == "__main__":
    main()
