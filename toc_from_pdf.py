import fitz  # PyMuPDF

def extract_filtered_toc(pdf_path):
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

    # First pass: record all entries and determine initial invalidity
    entries = []
    for entry in toc:
        level, title, page = entry
        # If deeper than max_level, automatically invalid (or we can just note it's beyond scope)
        if level > max_level:
            is_invalid = True
        else:
            title_lower = title.lower().strip()
            is_invalid = any(term in title_lower for term in non_chapter_terms)
        
        entries.append((level, title, page, is_invalid))

    # Second pass: propagate invalidity from invalid top-level entries
    # If a top-level (level=1) entry is invalid, all subsequent entries of greater level
    # until the next top-level entry are also invalid.
    i = 0
    while i < len(entries):
        level, title, page, is_invalid = entries[i]

        # If we hit a top-level entry that is invalid, propagate
        if level == 1 and is_invalid:
            j = i + 1
            while j < len(entries) and entries[j][0] > 1:
                # Mark sub-chapters invalid
                l, t, p, inv = entries[j]
                entries[j] = (l, t, p, True)
                j += 1
        i += 1

    # Now build the partitions from all entries
    partitions = []
    for level, title, page, is_invalid in entries:
        partitions.append({
            "chapter_title": title,
            "chapter_level": level,
            "page_start": page,
            "page_end": None,
            "invalid": is_invalid
        })

    # Determine page_end for each partition
    for i in range(len(partitions)):
        current_level = partitions[i]["chapter_level"]
        current_page = partitions[i]["page_start"]
        end_page = doc.page_count

        for j in range(i+1, len(partitions)):
            next_level = partitions[j]["chapter_level"]
            next_page = partitions[j]["page_start"]
            if next_level <= current_level:
                end_page = next_page - 1
                break

        partitions[i]["page_end"] = end_page

    # Filter out invalid partitions
    final_partitions = [p for p in partitions if not p["invalid"]]

    # Print results for demonstration
    for part in final_partitions:
        indent = "  " * (part["chapter_level"] - 1)
        print(f"{indent}{part['chapter_title']} (Start Page: {part['page_start']}, End Page: {part['page_end']})")

    return final_partitions

# Example usage:
partitions = extract_filtered_toc("Jakki_Mohr.pdf")