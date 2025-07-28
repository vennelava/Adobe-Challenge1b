import os
import re
import json
from datetime import datetime
import fitz  # PyMuPDF
from sklearn.feature_extraction.text import TfidfVectorizer

def load_input_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    persona = data.get("persona", {}).get("role", "") or data.get("persona", "")
    job = data.get("job_to_be_done", {}).get("task", "") or data.get("job_to_be_done", "")
    filenames = [doc["filename"] for doc in data.get("documents", [])]
    return persona, job, filenames

def extract_outline_and_sections(pdf_path):
    doc = fitz.open(pdf_path)
    headings = []
    sections = []
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        size = span["size"]
                        text = span["text"].strip()
                        is_bold = span["flags"] & 16
                        if not text:
                            continue
                        if (size > 12) or (size >= 11 and is_bold):  # heuristic for headings
                            headings.append((page_num, text))
    # Sectionize by heading
    full_text = []
    for page in doc:
        full_text.append(page.get_text())
    doc.close()
    full_text = "\n".join(full_text)
    # Simple split by headings
    heading_matches = [(m.start(), m.group(1), pnum) for pnum, h in headings for m in re.finditer(re.escape(h), full_text)]
    heading_matches.sort()
    for i, (start, title, pnum) in enumerate(heading_matches):
        end = heading_matches[i + 1][0] if i + 1 < len(heading_matches) else len(full_text)
        content = full_text[start:end].strip()
        sections.append({
            "title": title,
            "content": content,
            "page": pnum
        })
    return sections

def score_sections(sections, query_text):
    # Use TF-IDF to rank sections against the query
    corpus = [query_text] + [s['content'] for s in sections]
    vectorizer = TfidfVectorizer().fit(corpus)
    query_vec = vectorizer.transform([query_text])
    section_vecs = vectorizer.transform([s['content'] for s in sections])
    scores = (section_vecs * query_vec.T).toarray().flatten()
    ranked = sorted(zip(scores, sections), key=lambda x: -x[0])
    return ranked

def combine_lines(s):
    return re.sub(r'\s+', ' ', s).strip()

def main():
    # Hardcoded paths for simplicity (adapt as needed)
    input_json_path = "./Collection 1/challenge1b_input.json"
    pdf_folder_path = "./Collection 1/PDFs"
    output_path = "./Collection 1/challenge1b_output.json"
    num_results = 5

    persona, job, pdf_filenames = load_input_config(input_json_path)
    query_text = f"{persona} {job}"

    input_documents = []
    all_sections = []

    for filename in pdf_filenames:
        path = os.path.join(pdf_folder_path, filename)
        if not os.path.exists(path):
            print(f"Missing: {filename}")
            continue
        sections = extract_outline_and_sections(path)
        for section in sections:
            section["document"] = filename
            all_sections.append(section)
        input_documents.append(filename)
        print(f"Processed {filename}: {len(sections)} sections")

    if not all_sections:
        print("No content found.")
        return

    ranked_sections = score_sections(all_sections, query_text)

    extracted_sections = []
    subsection_analysis = []
    for rank, (score, section) in enumerate(ranked_sections[:num_results], 1):
        extracted_sections.append({
            "document": section["document"],
            "section_title": section["title"],
            "importance_rank": rank,
            "page_number": section["page"] + 1
        })
        subsection_analysis.append({
            "document": section["document"],
            "refined_text": section["title"] + " - " + combine_lines(section["content"]),
            "page_number": section["page"] + 1
        })

    output = {
        "metadata": {
            "input_documents": input_documents,
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"Output saved to {output_path}")

if __name__ == "_main_":
    main()