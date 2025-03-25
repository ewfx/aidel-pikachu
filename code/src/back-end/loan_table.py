import re
import fitz  # PyMuPDF

def extract_table_content(pdf_path, regex_pattern, stop_phrase):
    """
    Extracts a table's content from a PDF based on a regex pattern and stops at a given phrase.
    
    Parameters:
    - pdf_path: Path to the PDF file.
    - regex_pattern: Regular expression to identify the table heading.
    - stop_phrase: Text where extraction should stop.
    
    Returns:
    - Extracted table text.
    """
    doc = fitz.open(pdf_path)
    extracted_table = []
    table_found = False

    for page_num in range(len(doc)):  # Loop through all pages
        text_blocks = doc[page_num].get_text("blocks")  # Extract text blocks
        text_blocks.sort(key=lambda block: block[1])  # Sort blocks by y-coordinate for proper reading order

        for block in text_blocks:
            block_text = block[4]  # Extract text content
            
            if table_found:
                # Stop extraction when the stop phrase appears
                if re.search(re.escape(stop_phrase), block_text, re.IGNORECASE):
                    print(f"🛑 Stop phrase found on page {page_num + 1}")
                    return "\n".join(extracted_table)
                
                extracted_table.append(block_text)

            # Check if the block matches the table regex pattern
            if re.search(regex_pattern, block_text, re.IGNORECASE):
                print(f"✅ Found table on page {page_num + 1}")
                table_found = True  # Start capturing the following content
                extracted_table.append(block_text)  # Include table title

    return "❌ Table not found in the document or stop phrase not encountered."


# Example Usage
pdf_path = "2021-annual-report.pdf"

