from curl_cffi import requests

def test_curl_cffi():
    url = "https://www.hdfcfund.com/investor-services/capital-gains-statement"
    response = requests.get(url, impersonate="chrome120")
    html = response.text
    if "Access Denied" in html:
        print("FAILED: Access Denied")
    elif "The page you’re looking for may have moved" in html:
        print("FAILED: Soft 404")
    else:
        print(f"SUCCESS! Status: {response.status_code}")
        print(html[:500])

if __name__ == "__main__":
    test_curl_cffi()
