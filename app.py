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

        show_originals = st.checkbox(
            "Show originals",
            value=True,
            help="Display the original PDFs alongside the comparison"
        )

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

                # Show info
                st.info(f"📊 PDF 1: {pages1} page(s) | PDF 2: {pages2} page(s)")

                # Compare PDFs
                results = comparer.compare_pdfs(pdf1_bytes, pdf2_bytes)

                # Calculate overall difference
                avg_diff = sum(r[3] for r in results) / len(results) if results else 0

                # Show overall statistics
                st.markdown("---")
                st.subheader("📈 Overall Statistics")

                metric_cols = st.columns(3)
                with metric_cols[0]:
                    st.metric("Average Deviation", f"{avg_diff:.2f}%")
                with metric_cols[1]:
                    st.metric("Number of Pages", len(results))
                with metric_cols[2]:
                    identical_pages = sum(1 for r in results if r[3] < 1.0)
                    st.metric("Identical Pages", f"{identical_pages}/{len(results)}")

                st.markdown("---")

                # Display results for each page
                for idx, (img1, img2, diff_img, diff_pct) in enumerate(results):
                    st.subheader(f"Page {idx + 1}")

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
