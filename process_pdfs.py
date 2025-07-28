import os
import json
import fitz  
from collections import Counter, defaultdict

def merge_lines(lines, y_threshold=5):
    merged = []
    buffer = []
    prev_y = None
    for span in lines:
        y = span["bbox"][1]
        if not buffer or abs(y - prev_y) < y_threshold:
            buffer.append(span)
        else:
            merged.append(buffer)
            buffer = [span]
        prev_y = y
    if buffer:
        merged.append(buffer)
    return merged

def is_potential_heading(span, body_size, heading_sizes):
    size = span['size']
    text = span['text'].strip()
    is_bold = span['flags'] & 16
    if not text or len(text) < 3:
        return False
    if size > body_size or size in heading_sizes:
        return True
    if size == body_size and is_bold:
        return True
    return False

def clean_text(text):
    return ' '.join(text.strip().split())

def extract_outline(pdf_path):
    doc = fitz.open(pdf_path)
    all_spans = []
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        all_spans.append(span)
    font_sizes = [round(span["size"]) for span in all_spans if span["text"].strip()]
    if not font_sizes:
        return {"title": os.path.splitext(os.path.basename(pdf_path))[0], "outline": []}
    body_size = Counter(font_sizes).most_common(1)[0][0]
    heading_sizes = sorted(set(s for s in font_sizes if s > body_size), reverse=True)[:3]
    size_to_level = {size: f"H{idx+1}" for idx, size in enumerate(heading_sizes)}
    headings = []
    repeated_lines = defaultdict(int)
    for page_num, page in enumerate(doc):
        page_lines = []
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = clean_text(span["text"])
                        if text:
                            repeated_lines[text] += 1
                            page_lines.append({**span, "text": text, "page_num": page_num+1})
        candidate_spans = [span for span in page_lines if is_potential_heading(span, body_size, heading_sizes)]
        merged_headings = merge_lines(candidate_spans)
        for group in merged_headings:
            combined_text = clean_text(' '.join([g['text'] for g in group]))
            size = round(group[0]['size'])
            level = size_to_level.get(size, "H3")
            headings.append({"level": level, "text": combined_text, "page": page_num+1})
    n_pages = len(doc)
    filtered_headings = []
    for h in headings:
        if repeated_lines[h['text']] < n_pages * 0.5:
            filtered_headings.append(h)
    title = ""
    first_page = doc[0]
    max_size = 0
    for block in first_page.get_text("dict")["blocks"]:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    s = span["size"]
                    t = clean_text(span["text"])
                    if s > max_size and t:
                        title = t
                        max_size = s
    if not title and filtered_headings:
        title = filtered_headings[0]['text']
    return {"title": title, "outline": filtered_headings}

def process_all_pdfs(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            result = extract_outline(pdf_path)
            output_path = os.path.join(output_dir, filename[:-4] + ".json")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    process_all_pdfs("sample_dataset/pdfs", "sample_dataset/outputs")
