import os
import subprocess
import uuid
import logging
import settings

logging.basicConfig(level=settings.LOG_LEVEL)


TEMP_HTML_DIR = "temp/html"
TEMP_MD_DIR = "temp/md"



def extract_text_as_semantic_md(raw_html: str) -> str | None:
    # try extract semantic md
    abs_path_workdir = os.path.dirname(os.path.abspath(__file__))
    temp_file_name = str(uuid.uuid4())
    temp_html_file_path = os.path.join(abs_path_workdir, TEMP_HTML_DIR, temp_file_name + ".html")
    with open(temp_html_file_path, "w", encoding="utf-8") as html_f:
        html_f.write(raw_html)
    
    
    temp_md_file_path = os.path.join(abs_path_workdir, TEMP_MD_DIR, temp_file_name + ".md")
    try:
        command = ["npx", "d2m@latest", "-e", "-i", temp_html_file_path, "-o", temp_md_file_path]
        d2m_run = subprocess.run(command, capture_output=True, text=True, timeout=15, cwd=abs_path_workdir) # timeout is in seconds
        if d2m_run.returncode != 0:
            raise Exception(f"Cannot extract semantic md. Exit code: {d2m_run.returncode}\n Error: {d2m_run.stderr}")
        with open(temp_md_file_path, "r", encoding="utf-8") as md_f:
            md_content = md_f.read()
        return md_content
    except Exception:
        # TODO: log this bitch and return None or some shit
        logging.exception("Could not extract content with d2m.")
        return None
    finally:
        # cleanup temp files
        if os.path.exists(temp_html_file_path):
            os.remove(temp_html_file_path)
        if os.path.exists(temp_md_file_path):
            os.remove(temp_md_file_path)
    