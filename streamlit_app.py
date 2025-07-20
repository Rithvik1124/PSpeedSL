import streamlit as st
import os
import uuid
import shutil
import asyncio
import subprocess
from pagespeed_insights2 import main as run_scraper
from makedoc import generate_docx_from_advice
from pagespeed_screenshot import capture_all_screenshots

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

st.title("PageSpeed Audit Tool")
url = st.text_input("Enter the URL to audit")

if st.button("Run Audit") and url:
    uid = str(uuid.uuid4())[:8]
    work_dir = os.path.join(OUTPUT_DIR, uid)
    os.makedirs(work_dir, exist_ok=True)

    with st.spinner("Running PageSpeed audit..."):
        try:
            subprocess.run(["playwright", "install"], check=True)
        except Exception as e:
            st.error(f"Could not install Playwright browsers: {e}")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        advice, performance_data = loop.run_until_complete(run_scraper(url))

        docx_path = os.path.join(work_dir, f"{uid}_report.docx")
        generate_docx_from_advice(advice, url, docx_path)

        screenshots = loop.run_until_complete(capture_all_screenshots(url, uid))
        for path in screenshots:
            shutil.move(path, work_dir)

        zip_path = os.path.join(OUTPUT_DIR, f"{uid}_report.zip")
        shutil.make_archive(zip_path.replace('.zip', ''), 'zip', work_dir)

    st.success("Audit completed!")
    with open(zip_path, "rb") as file:
        st.download_button(label="Download Report ZIP", data=file, file_name=f"{uid}_report.zip")
