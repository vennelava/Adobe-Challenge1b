
# Intelligent Document Analyst — Persona-Based Summarization

## Overview

This project is a solution to **Adobe Challenge 1B: “Connect What Matters — For the User Who Matters.”**  
The goal is to create a system that extracts and ranks the most relevant sections from a collection of PDFs based on a given **persona** and their **job-to-be-done**.  
The extracted data is saved in a structured JSON format with metadata, ranked section headers, and refined sub-sections.

The solution supports a variety of personas (researchers, analysts, students, etc.) and document types (academic papers, reports, textbooks), and is designed to generalize across use cases.

---

## Key Features

- Accepts multiple PDFs and a persona/job definition in JSON format  
- Extracts document outlines and partitions full text by headings  
- Scores sections using TF-IDF based on the persona and job description  
- Ranks extracted sections by importance  
- Summarizes and refines relevant content  
- Outputs structured JSON in the required format  
- Fully offline, CPU-only processing  

---

## Input

### `challenge1b_input.json` containing:
- List of input PDF filenames  
- Persona definition (`role`)  
- Job-to-be-done (`task`)  

PDF files should be placed inside the `PDFs/` subfolder within each collection.

---

## Output

A structured JSON file saved as `challenge1b_output.json`, for example:

```json
{
  "metadata": {
    "input_documents": ["doc1.pdf", "doc2.pdf"],
    "persona": "PhD Researcher in Computational Biology",
    "job_to_be_done": "Literature review on GNNs for drug discovery",
    "processing_timestamp": "2025-07-28T18:00:00Z"
  },
  "extracted_sections": [
    {
      "document": "doc1.pdf",
      "page_number": 3,
      "section_title": "Graph-based Feature Learning",
      "importance_rank": 1
    }
  ],
  "subsection_analysis": [
    {
      "document": "doc1.pdf",
      "page_number": 3,
      "refined_text": "Graph-based Feature Learning - GNNs have been successfully used in molecule property prediction..."
    }
  ]
}
```

---

## Methodology

- **Heading Extraction**: Detect large or bold text as section titles using PyMuPDF  
- **Section Partitioning**: Use regex-based logic to split full text by headings  
- **Ranking**: Apply TF-IDF vectorization to compare section content with persona/job text  
- **Refinement**: Clean and merge top-ranked sections for summarization  
- **Output Formatting**: Export all data into a structured JSON matching the challenge schema  

---

## Project Structure

```
.
├── Collection 1/
│   ├── PDFs/                        # Input PDFs for Test Case 1
│   ├── challenge1b_input.json       # Input config for persona + job
│   └── challenge1b_output.json      # Output file generated
├── Collection 2/
│   ├── PDFs/                        # Input PDFs for Test Case 2
│   ├── challenge1b_input.json
│   └── challenge1b_output.json
├── Collection 3/
│   ├── PDFs/                        # Input PDFs for Test Case 3
│   ├── challenge1b_input.json
│   └── challenge1b_output.json
├── Dockerfile                       # Docker config for CPU-only container
├── main.py                          # Main script: processes input and generates output
├── process_pdfs.py                  # Reusable outline extraction utility (optional)
├── requirements.txt                 # Python dependencies
└── README.md                        # Project documentation
```

---

## How to Run

### With Docker

Build the image:

```bash
docker build --platform linux/amd64 -t doc-analyzer-1b:latest .
```

Run the solution:

```bash
docker run --rm \
  -v $(pwd)/Collection\ 1:/app/Collection\ 1 \
  --network none \
  doc-analyzer-1b:latest
```

> Make sure `challenge1b_input.json` and the PDF files are inside the appropriate `Collection` folder before running.

---

### Without Docker (for local testing)

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the script:

```bash
python main.py
```

---

## Constraints Addressed

- Execution within **60 seconds** for 3–5 PDFs  
- Model size **≤1GB** (no external models used)  
- **CPU-only**, fully offline (no GPU or internet access)  
- Output **strictly matches** the required schema  

---
