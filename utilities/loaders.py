import pandas as pd
from docx import Document
import streamlit as st


@st.cache_data
def load_jobs_from_docx(file_path="data/uploads/jobs.docx"):
    try:
        doc = Document(file_path)
        jobs = []

        for table in doc.tables:
            if len(table.rows) < 2:
                continue

            for row in table.rows[1:]:
                cells = [c.text.strip() for c in row.cells]

                job = {
                    "company": cells[0] if len(cells) > 0 else "",
                    "role": cells[1] if len(cells) > 1 else "",
                    "skills": [x.strip() for x in (cells[2] if len(cells) > 2 else "").split(",") if x.strip()],
                    "culture": [x.strip() for x in (cells[3] if len(cells) > 3 else "").split(",") if x.strip()],
                    "personality": [x.strip() for x in (cells[4] if len(cells) > 4 else "").split(",") if x.strip()],
                    "character": [x.strip() for x in (cells[5] if len(cells) > 5 else "").split(",") if x.strip()],
                }

                if job["company"] and job["role"]:
                    jobs.append(job)

        return pd.DataFrame(jobs)

    except Exception:
        return pd.DataFrame()
