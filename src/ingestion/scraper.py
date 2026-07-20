import os
import json
import logging
import datetime
from urllib.parse import urlparse
from curl_cffi import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

URLS = [
    # Groww
    {"url": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth", "method": "playwright", "category": "groww", "scheme_name": "HDFC Large Cap Fund", "document_type": "Scheme Page"},
    {"url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth", "method": "playwright", "category": "groww", "scheme_name": "HDFC Mid-Cap Fund", "document_type": "Scheme Page"},
    {"url": "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth", "method": "playwright", "category": "groww", "scheme_name": "HDFC Small Cap Fund", "document_type": "Scheme Page"},
    {"url": "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth", "method": "playwright", "category": "groww", "scheme_name": "HDFC Gold ETF Fund of Fund", "document_type": "Scheme Page"},
    {"url": "https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth", "method": "playwright", "category": "groww", "scheme_name": "HDFC Silver ETF FoF", "document_type": "Scheme Page"},
    
    # HDFC AMC Official
    {"url": "https://www.hdfcfund.com/explore/mutual-funds/hdfc-large-cap-fund/regular", "method": "requests", "category": "hdfc_amc", "scheme_name": "HDFC Large Cap Fund", "document_type": "Factsheet"},
    {"url": "https://www.hdfcfund.com/explore/mutual-funds/hdfc-mid-cap-fund/regular", "method": "requests", "category": "hdfc_amc", "scheme_name": "HDFC Mid-Cap Fund", "document_type": "Factsheet"},
    {"url": "https://www.hdfcfund.com/explore/mutual-funds/hdfc-small-cap-fund/regular", "method": "requests", "category": "hdfc_amc", "scheme_name": "HDFC Small Cap Fund", "document_type": "Factsheet"},
    {"url": "https://www.hdfcfund.com/explore/mutual-funds/hdfc-gold-etf-fund-fund/regular", "method": "requests", "category": "hdfc_amc", "scheme_name": "HDFC Gold ETF Fund of Fund", "document_type": "Factsheet"},
    {"url": "https://www.hdfcfund.com/explore/mutual-funds/hdfc-silver-etf-fund-fund/regular", "method": "requests", "category": "hdfc_amc", "scheme_name": "HDFC Silver ETF FoF", "document_type": "Factsheet"},
    
    # HDFC AMC SID/KIM/SAI
    {"url": "https://www.hdfcfund.com/statutory-disclosure/scheme-information-documents", "method": "requests", "category": "sid_kim_sai", "scheme_name": "General", "document_type": "SID"},
    {"url": "https://www.hdfcfund.com/statutory-disclosure/key-information-memorandum", "method": "requests", "category": "sid_kim_sai", "scheme_name": "General", "document_type": "KIM"},
    {"url": "https://www.hdfcfund.com/statutory-disclosure/statement-of-additional-information", "method": "requests", "category": "sid_kim_sai", "scheme_name": "General", "document_type": "SAI"},
    
    # HDFC AMC FAQ
    {"url": "https://www.hdfcfund.com/services/faqs", "method": "requests", "category": "hdfc_amc", "scheme_name": "General", "document_type": "FAQ"},
    {"url": "https://www.hdfcfund.com/services/consolidated-account-statement", "method": "requests", "category": "hdfc_amc", "scheme_name": "General", "document_type": "Account Statements"},
    {"url": "https://www.hdfcfund.com/learn/blog/how-get-capital-gain-statement-mutual-fund-schemes-india", "method": "requests", "category": "hdfc_amc", "scheme_name": "General", "document_type": "Capital Gains Statement"},
    
    # AMFI/SEBI
    {"url": "https://www.amfiindia.com/investor-corner/knowledge-center/what-are-mutual-funds.html", "method": "requests", "category": "amfi_sebi", "scheme_name": "General", "document_type": "Educational"},
    {"url": "https://www.amfiindia.com/investor-corner/knowledge-center/riskometer.html", "method": "requests", "category": "amfi_sebi", "scheme_name": "General", "document_type": "Educational"},
    {"url": "https://www.sebi.gov.in/legal/regulations/jul-2023/sebi-mutual-funds-regulations-1996-last-amended-on-july-04-2023-_74404.html", "method": "requests", "category": "amfi_sebi", "scheme_name": "General", "document_type": "Regulation"},
    {"url": "https://www.amfiindia.com/nav-history-download", "method": "requests", "category": "amfi_sebi", "scheme_name": "General", "document_type": "NAV History"}
]

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
METADATA_FILE = "data/metadata.json"

class Scraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        # Ensure directories exist
        for category in ["groww", "hdfc_amc", "sid_kim_sai", "amfi_sebi"]:
            os.makedirs(os.path.join(RAW_DIR, category), exist_ok=True)
        os.makedirs(PROCESSED_DIR, exist_ok=True)

    def fetch_static(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=15, impersonate="chrome120")
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Failed to fetch {url} via requests: {e}")
            return ""

    def fetch_dynamic(self, url):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(user_agent=self.headers["User-Agent"])
                # Groww can be slow to load fully, wait for load instead of networkidle
                page.goto(url, wait_until="load", timeout=30000)
                page.wait_for_timeout(3000)  # Wait 3s for JS to render
                html = page.content()
                browser.close()
                return html
        except Exception as e:
            logger.error(f"Failed to fetch {url} via playwright: {e}")
            return ""

    def clean_text(self, html):
        if not html:
            return ""
        
        soup = BeautifulSoup(html, "html.parser")
        
        # Remove script, style, nav, header, footer, aside elements which usually don't contain core FAQ/content
        for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
            element.extract()
            
        # Get text with newlines
        text = soup.get_text(separator="\n")
        
        # Clean up excessive whitespace and empty lines
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)

    def get_filename_safe(self, url):
        parsed = urlparse(url)
        path = parsed.path.strip("/").replace("/", "_")
        if not path:
            path = "index"
        return f"{parsed.netloc}_{path}"

    def run(self):
        metadata = []
        
        for item in URLS:
            url = item["url"]
            method = item["method"]
            category = item["category"]
            
            logger.info(f"Scraping [{method}]: {url}")
            
            if method == "playwright":
                html = self.fetch_dynamic(url)
            else:
                html = self.fetch_static(url)
                if not html:
                    logger.info(f"Static fetch failed. Falling back to Playwright for {url}")
                    html = self.fetch_dynamic(url)
                
            if not html:
                logger.warning(f"Skipping {url} due to fetch failure.")
                continue
                
            cleaned_text = self.clean_text(html)
            
            safe_name = self.get_filename_safe(url)
            raw_path = os.path.join(RAW_DIR, category, f"{safe_name}.html")
            processed_path = os.path.join(PROCESSED_DIR, f"{safe_name}.txt")
            
            # Save raw HTML
            with open(raw_path, "w", encoding="utf-8") as f:
                f.write(html)
                
            # Save processed text
            with open(processed_path, "w", encoding="utf-8") as f:
                f.write(cleaned_text)
                
            scrape_date = datetime.datetime.now().strftime("%Y-%m-%d")
            
            meta_entry = {
                "source_url": url,
                "scheme_name": item["scheme_name"],
                "document_type": item["document_type"],
                "scrape_date": scrape_date,
                "raw_file": raw_path,
                "processed_file": processed_path
            }
            metadata.append(meta_entry)
            
        # Save metadata
        with open(METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)
            
        logger.info(f"Scraping complete. Successfully processed {len(metadata)} URLs.")

if __name__ == "__main__":
    scraper = Scraper()
    scraper.run()
