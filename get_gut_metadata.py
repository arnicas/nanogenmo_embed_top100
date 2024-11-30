import requests
import rdflib
from pathlib import Path
import gzip
import shutil
import tempfile
import json

CATALOG_URL = "https://gutenberg.org/cache/epub/feeds/rdf-files.tar.bz2"

class GutenbergMetadata:
    
    def __init__(self, cache_dir=None):
        self.cache_dir = cache_dir or Path(tempfile.gettempdir()) / "gutenberg_metadata"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def download_catalog(self):
        """Download and extract the RDF catalog."""
        catalog_path = self.cache_dir / "rdf-files.tar.bz2"
        rdf_cache = self.cache_dir / "cache/epub"
        
        # Skip download if already exists, but don't return early
        if rdf_cache.exists():
            print("Catalog already downloaded and extracted.")
        else:
            print("Downloading Project Gutenberg catalog...")
            response = requests.get(CATALOG_URL, stream=True)
        
            with open(catalog_path, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            
            print("Extracting catalog...")
            shutil.unpack_archive(str(catalog_path), str(self.cache_dir))
        
        # Verify the cache exists
        if not rdf_cache.exists():
            raise RuntimeError("Failed to setup RDF cache directory")
        
    def get_book_metadata(self, book_id):
        """Get metadata for a specific book ID."""
        rdf_path = self.cache_dir / "cache/epub" / str(book_id) / f"pg{book_id}.rdf"
        
        if not rdf_path.exists():
            raise FileNotFoundError(f"RDF file not found for book {book_id}")
            
        g = rdflib.Graph()
        g.parse(rdf_path)
        
        # Define namespaces
        DC = rdflib.Namespace("http://purl.org/dc/elements/1.1/")
        DCTERMS = rdflib.Namespace("http://purl.org/dc/terms/")
        
        # Get book URI
        book_uri = None
        for s in g.subjects(rdflib.RDF.type, rdflib.URIRef("http://www.gutenberg.org/2009/pgterms/ebook")):
            book_uri = s
            break
            
        if not book_uri:
            raise ValueError(f"Could not find book URI for {book_id}")
            
        # Extract metadata
        title = str(g.value(book_uri, DC.title))
        
        authors = []
        for creator in g.objects(book_uri, DC.creator):
            author_name = g.value(creator, rdflib.FOAF.name)
            if author_name:
                authors.append(str(author_name))
                
        return {
            "id": book_id,
            "title": title,
            "author": ', '.join(authors)
        }
        
    def search_books(self, ids):
        """Search for books id list and return their metadata."""
        results = []
        for book_id in ids:
            try:
                metadata = self.get_book_metadata(int(book_id))
                print("found metadata", book_id)
                results.append(metadata)
            except (FileNotFoundError, ValueError) as e:
                print(f"Error fetching metadata for book {book_id}: {e}")
                continue
        return results

def get_id_from_file(filename):
    parts = filename.split("_")
    return parts[0]

def get_id_from_dir(dirname):
    files = [file.name for file in Path(dirname).glob("*.txt")]
    return [get_id_from_file(str(file)) for file in files]

def write_metadata(metadata, filename):
    with open(filename, "w") as f:
        json.dump(metadata, f)
    

def call_gutendex(bookids):
    longdata = []
    shortdata = []
    for book in bookids:
        response = requests.get(f"https://gutendex.com/books/{book}")
        book_data = response.json()

        title = book_data.get('title', 'None')
        authors = [author.get('name', '') for author in book_data.get('authors', [])]
        try:
            author_birthday = book_data.get('authors', [{}])[0].get('birth_year', '')
        except:
            author_birthday = ''
        longdata.append(book_data)
        shortdata.append({    
            "id": book,
            "title": title,
            "author": ', '.join(authors),
            "author_birthday": author_birthday
        })
    return longdata, shortdata

    # Usage example
if __name__ == "__main__":
    print("Starting metadata collection...")

    print("Getting IDs from directory...")
    ids = get_id_from_dir("top100_sents_filtered/")
    print(f"Found {len(ids)} book IDs to process")
    
    print("Fetching metadata for books...")
    long, short = call_gutendex(ids)
    print(f"Successfully retrieved metadata for {len(long)} books")
    
    print("Writing metadata to file...")
    write_metadata(long, "top100_metadata.json")
    write_metadata(short, "top100_metadata_short.json")
    print("Done!")