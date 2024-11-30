
# for cleaning start and end material only -- use gutenberg_cleaning.py for full special text cleaning
import os
from pathlib import Path
import re

INPUT_FOLDER = "downloaded"
OUTPUT_FOLDER = "top100_clean"

def clean_book_text(text):
    """
    Removes Project Gutenberg header and footer from book text.
    Returns the cleaned text.
    """
    # Find start marker
    start_markers = [
        "*** START OF THE PROJECT GUTENBERG",
        "*** START OF THIS PROJECT GUTENBERG",
        "**** START OF THE PROJECT GUTENBERG",
        "**** START OF THIS PROJECT GUTENBERG"
    ]
    
    start_pos = -1
    for marker in start_markers:
        pos = text.find(marker)
        if pos != -1:
            start_pos = text.find("***", pos + len(marker))
            break
    
    # Find end marker
    end_markers = [
        "*** END OF THE PROJECT GUTENBERG",
        "*** END OF THIS PROJECT GUTENBERG",
        "**** END OF THE PROJECT GUTENBERG",
        "**** END OF THIS PROJECT GUTENBERG"
    ]
    
    end_pos = -1
    for marker in end_markers:
        pos = text.find(marker)
        if pos != -1:
            end_pos = pos
            break
    
    # Extract text between markers
    if start_pos != -1 and end_pos != -1:
        return text[start_pos+3:end_pos].strip()
    elif start_pos != -1:
        return text[start_pos+3:].strip()
    elif end_pos != -1:
        return text[:end_pos].strip()
    else:
        return text.strip()


def get_id_from_filename(filename):
    """
    Extracts the book ID from a filename.
    Returns the first number found in the filename as a string.
    Example filenames:
    - book_1234.txt -> "1234"
    - 1234_raw.txt -> "1234"
    - pg1234.txt -> "1234"
    """
    match = re.search(r'\d+', filename)
    if match:
        return match.group(0)
    raise ValueError(f"No book ID found in filename: {filename}")

def clean_books_in_folder(input_folder, output_folder="cleaned"):
    """
    Cleans all text files in the input folder and saves them to the output folder.
    
    Args:
        input_folder (str): Path to folder containing raw book files
        output_folder (str): Path to folder where cleaned files will be saved
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(exist_ok=True)
    
    # Process each file in the input folder
    processed = 0
    errors = 0
    
    for file_path in input_path.glob("*.txt"):
        try:
            # Read the raw text
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Clean the text
            cleaned_text = clean_book_text(text)
            
            # Create output filename
            book_id = get_id_from_filename(file_path.name)
            output_file = output_path / f"{book_id}_clean.txt"
            
            # Save cleaned text
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)
            
            print(f"Cleaned {file_path.name}")
            processed += 1
            
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
            errors += 1
    
    print(f"\nCleaning complete!")
    print(f"Files processed successfully: {processed}")
    print(f"Files with errors: {errors}")

if __name__ == "__main__":
    # Example usage
    clean_books_in_folder(INPUT_FOLDER, OUTPUT_FOLDER) 