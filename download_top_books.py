import requests
import time
import os
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
import argparse

def get_top_books(num_books=100):
    """
    Fetches the top book IDs from Project Gutenberg.
    Saves the list to a JSON file with timestamp and returns the book IDs.
    Returns a list of book IDs.
    """
    TOP_BOOKS_URL = "https://www.gutenberg.org/browse/scores/top"
    
    try:
        response = requests.get(TOP_BOOKS_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        book_links = []
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if '/ebooks/' in href:
                book_id = re.search(r'/ebooks/(\d+)', href)
                if book_id:
                    book_links.append(book_id.group(1))
        
        # Trim to requested number of books
        book_links = book_links[:num_books]
        
        # Create JSON data with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_data = {
            "timestamp": timestamp,
            "num_books": len(book_links),
            "book_ids": book_links
        }
        
        # Save to JSON file
        filename = f"top_books_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(json_data, f, indent=4)
            
        print(f"Saved book list to {filename}")
        
        return book_links
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching book list: {e}")
        return []

def download_book(book_id, output_dir):
    """
    Downloads a single book from Project Gutenberg by its ID.
    Returns True if successful, False otherwise.
    """
    BASE_URL = "https://www.gutenberg.org/files"
    ALT_URL = "https://www.gutenberg.org/cache/epub"
    
    try:
        # Try UTF-8 text version first
        text_url = f"{BASE_URL}/{book_id}/{book_id}.txt"
        response = requests.get(text_url)
        
        if response.status_code == 404:
            # Try alternate URL pattern
            text_url = f"{BASE_URL}/{book_id}/txt"
            response = requests.get(text_url)

            if response.status_code == 404:
                # Try alternate URL pattern
                text_url = f"{ALT_URL}/{book_id}/pg{book_id}.txt"
                response = requests.get(text_url)
        
        response.raise_for_status()
        
        # Save the book
        output_file = os.path.join(output_dir, f"book_{book_id}.txt")
        with open(output_file, 'wb') as f:
            f.write(response.content)
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading book {book_id}: {e}")
        return False

def download_gutenberg_books(output_dir="gutenberg_books", num_books=100, download=False):
    """
    Downloads top Project Gutenberg books as text files.
    Includes rate limiting and error handling.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Rate limiting parameters
    REQUEST_DELAY = 2  # seconds between requests
    
    print(f"Fetching top {num_books} books list...")
    book_ids = get_top_books(num_books)
    
    if not book_ids:
        print("Failed to fetch book list")
        return
    
    # Download books
    if download:
        for i, book_id in enumerate(book_ids, 1):
            print(f"Downloading book {i}/{num_books} (ID: {book_id})...")
            
            if download_book(book_id, output_dir):
                print(f"Successfully downloaded book {book_id}")
            
            # Rate limiting
            time.sleep(REQUEST_DELAY)
            
            print("\nDownload complete!")
            print(f"Books saved in: {os.path.abspath(output_dir)}")
    else:
        print(f"Book IDs saved to {os.path.abspath('top_books.json')}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download Project Gutenberg books')
    parser.add_argument('--ids', nargs='+', type=str, help='List of book IDs to download')
    parser.add_argument('--output-dir', default='gutenberg_books', help='Output directory for downloaded books')
    parser.add_argument('--num-books', type=int, default=100, help='Number of top books to fetch if no IDs provided')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    if args.ids:
        # Download specific books
        print(f"Downloading {len(args.ids)} specified books...")
        for i, book_id in enumerate(args.ids, 1):
            print(f"Downloading book {i}/{len(args.ids)} (ID: {book_id})...")
            if download_book(book_id, args.output_dir):
                print(f"Successfully downloaded book {book_id}")
            time.sleep(2)  # Rate limiting
    else:
        # Download top books
        download_gutenberg_books(args.output_dir, args.num_books)
