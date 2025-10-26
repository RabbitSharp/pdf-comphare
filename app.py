"""
Streamlit App for PDF Comparison
"""
import streamlit as st
from pdf_compare import PDFComparer


def main():
    st.set_page_config(
        page_title="PDF Comparison Tool",
        page_icon="📄",
        layout="wide"
    )

    st.title("📄 PDF Comparison Tool")
    st.markdown("""
    Upload two PDF files to compare them. 
    Differences will be highlighted in red.
    """)

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

    # Settings in sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        zoom = st.slider(
            "Image Quality (Zoom)",
            min_value=1.0,
            max_value=3.0,
            value=2.0,
            step=0.5,
            help="Higher values = better quality, but slower"
        )

        st.markdown("#### Comparison Settings")

        sensitivity = st.slider(
            "Sensitivity Threshold",
            min_value=10.0,
            max_value=100.0,
            value=50.0,
            step=5.0,
            help="Higher values = less sensitive (fewer false positives). Try 60-80 to reduce noise."
        )

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

        # Tab-based selection method
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
        st.markdown("### ℹ️ Info")
        st.markdown("""
        **Technologies used:**
        - PyMuPDF for PDF processing
        - Streamlit for the UI
        - Pillow for image processing
        
        **Features:**
        - Page-by-page comparison
        - Differences highlighted in red
        - Percentage deviation
        - Adjustable sensitivity
        - Skip pages manually or by text content
        
        **Tips for reducing false positives:**
        - Increase sensitivity threshold (60-80)
        - Increase minimum area (200-300)
        - Use higher zoom for better rendering
        - Skip cover pages or dynamic content pages
        - Use text-based skip for pages with dates/timestamps
        
        **Text-based skip examples:**
        - "DRAFT" - skip all pages containing "DRAFT"
        - "Generated on" - skip pages with timestamps
        - "Page 1 of" - skip cover/header pages
        """)

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
                st.info(info_text)

                # Compare PDFs
                results = comparer.compare_pdfs(pdf1_bytes, pdf2_bytes, sensitivity, min_area,
                                              skip_pages_pdf1=skip_pages_1, skip_pages_pdf2=skip_pages_2)

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
        st.info("👆 Upload two PDF files to get started.")


if __name__ == "__main__":
    main()
