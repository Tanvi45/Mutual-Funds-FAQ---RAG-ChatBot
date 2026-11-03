import os
import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# URLs to scrape as specified
SOURCES = [
    {
        "id": "hdfc_amc",
        "name": "HDFC Mutual Fund AMC Overview",
        "url": "https://groww.in/mutual-funds/amc/hdfc-mutual-funds"
    },
    {
        "id": "hdfc_large_cap",
        "name": "HDFC Large Cap Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth"
    },
    {
        "id": "hdfc_flexi_cap",
        "name": "HDFC Flexi Cap Direct Plan Growth",
        "url": "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth"
    },
    {
        "id": "hdfc_elss",
        "name": "HDFC ELSS Tax Saver Fund Direct Plan Growth",
        "url": "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth"
    },
    {
        "id": "hdfc_mid_cap",
        "name": "HDFC Mid Cap Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
    },
    {
        "id": "amfi_elss_lockin",
        "name": "AMFI - Categorization of Mutual Fund Schemes",
        "url": "https://www.amfiindia.com/investor/knowledge-center-info?zoneName=CategorizationOfMutualFundSchemes"
    }
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_documents():
    """Scrape only the specified Groww pages - no internal links."""
    raw_dir = "data/raw"
    os.makedirs(raw_dir, exist_ok=True)
    
    metadata = []
    
    for source in SOURCES:
        print(f"Scraping {source['name']}...")
        try:
            response = requests.get(source['url'], headers=HEADERS, timeout=30)
            response.raise_for_status()
            
            # Save raw HTML
            html_path = os.path.join(raw_dir, f"{source['id']}.html")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # Parse and extract main content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['nav', 'header', 'footer', 'script', 'style', 'aside', 'iframe']):
                element.decompose()
            
            # Extract text
            text = soup.get_text()
            
            # Clean whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Save cleaned text
            txt_path = os.path.join(raw_dir, f"{source['id']}.txt")
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            metadata.append({
                "source_id": source['id'],
                "name": source['name'],
                "url": source['url'],
                "fetched_at": datetime.now().isoformat(),
                "html_path": html_path,
                "txt_path": txt_path,
                "content_length": len(text)
            })
            
            print(f"[OK] Saved {source['id']}.txt ({len(text)} chars)")
            
        except Exception as e:
            print(f"[ERR] Error scraping {source['id']}: {e}")
    
    # Save metadata
    metadata_path = os.path.join(raw_dir, "metadata.json")
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nScraping complete. {len(metadata)} documents saved.")
    return metadata

if __name__ == "__main__":
    scrape_documents()
