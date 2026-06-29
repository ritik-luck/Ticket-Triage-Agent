from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "knowledge_base"
import pandas as pd

def load_documents():
    documents = []

    csv_files = list(DATASET_DIR.glob("*.csv"))

    for file_path in csv_files:
        df = pd.read_csv(file_path)

        subject_col = None
        body_col = None
        answer_col = None

        for col in df.columns:
            c = col.lower()

            if "subject" in c:
                subject_col = col
            elif "body" in c or "description" in c:
                body_col = col
            elif "answer" in c or "resolution" in c or "solution" in c:
                answer_col = col

        subject_col = subject_col or df.columns[0]
        body_col = body_col or df.columns[1]
        answer_col = answer_col or df.columns[-1]

        for _, row in df.iterrows():
            subject = str(row.get(subject_col, "")).strip()
            body = str(row.get(body_col, "")).strip()
            answer = str(row.get(answer_col, "")).strip()

            text_parts = []

            if subject:
                text_parts.append(f"Subject: {subject}")

            if body:
                text_parts.append(f"Description: {body}")

            if answer:
                text_parts.append(f"Solution: {answer}")

            combined_text = "\n".join(text_parts).strip()

            if combined_text:
                documents.append(
                    {
                        "source": file_path.name,
                        "content": combined_text
                    }
                )

    return documents


