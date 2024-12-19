import fitz  # PyMuPDF

def extract_filtered_toc(pdf_path):
    ignore = False
    max_level = 2
    # Non-chapter keywords to filter out (all lower case)
    non_chapter_terms = {
        "appendix", "abstract", "preface", "index",
        "cover", "title page", "acknowledgments",
        "about the author", "about the authors", "foreword", 
        "prologue", "summary", "glossary", "contents", "copyrights",
    }
    
    doc = fitz.open(pdf_path)
    toc = doc.get_toc()

    # We'll print the filtered TOC
    for entry in toc:
        level, title, page = entry
        if ignore == True and level > 1:
            continue
        else:
            ignore = False
        if level > max_level:
            continue
        # Convert title to lowercase for matching
        title_lower = title.lower().strip()

        if any(term in title_lower for term in non_chapter_terms):
            if level == 1:
                ignore = True 
            continue

        indent = "  " * (level - 1)
        print(f"{indent}{title} (Page {page})")

extract_filtered_toc("Jakki_Mohr.pdf")