from curl_cffi import requests
import xml.etree.ElementTree as ET

def find_urls():
    url = "https://www.hdfcfund.com/sitemap.xml"
    response = requests.get(url, impersonate="chrome120")
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        import re
        urls = re.findall(r'<loc>(.*?)</loc>', response.text)
        print("Matching URLs:")
        for u in urls:
            if "large-cap" in u.lower() or "mid-cap" in u.lower() or "small-cap" in u.lower() or "gold-etf" in u.lower() or "silver-etf" in u.lower() or "scheme-information" in u.lower() or "key-information" in u.lower() or "statement-of-additional" in u.lower():
                print(u)
    else:
        print("Failed to get sitemap")

if __name__ == "__main__":
    find_urls()
