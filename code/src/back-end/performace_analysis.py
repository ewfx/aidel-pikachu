import re
import fitz  # PyMuPDF

def extract_second_occurrence_page(pdf_path, search_phrase="Our Performance"):
    """
    Extracts the full page of the second occurrence of a given search phrase in a PDF.

    Args:
        pdf_path (str): Path to the PDF file.
        search_phrase (str): Phrase to search for in the PDF.

    Returns:
        str: Extracted text from the full page where the second occurrence is found.
    """
    # Load PDF
    doc = fitz.open(pdf_path)

    # Find all occurrences
    occurrences = []
    for page_num in range(len(doc)):  # Loop through all pages
        text_blocks = doc[page_num].get_text("blocks")  # Extract text blocks (preserves structure)
        
        for block in text_blocks:
            block_text = block[4]  # The actual text content
            matches = [m.start() for m in re.finditer(re.escape(search_phrase), block_text)]
            
            if matches:
                occurrences.append((page_num, matches))  # Store page number and positions

    # Check if there are at least two occurrences
    if len(occurrences) >= 2:
        second_hit_page = occurrences[1][0]  # Get the page number of the second occurrence
        extracted_blocks = doc[second_hit_page].get_text("blocks")  # Extract blocks from full page

        # Sort blocks based on their y-coordinates to maintain reading order
        extracted_blocks.sort(key=lambda block: block[1])  
        
        extracted_text = "\n".join(block[4] for block in extracted_blocks)
        
        # print(f"\n🔹 **Extracted Full Page (Page {second_hit_page + 1}):**\n")
        # print(extracted_text)
        
        return extracted_text
    else:
        print("\n⚠️ Less than two occurrences of the search phrase found in the document.\n")
        return None

# Example usage:
pdf_path = "2021-annual-report.pdf"  # Update with actual file path
extracted_text = extract_second_occurrence_page(pdf_path)
# print(extracted_text)
