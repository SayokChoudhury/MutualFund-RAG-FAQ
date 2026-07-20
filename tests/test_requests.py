import requests

def test_requests():
    url = "https://www.hdfcfund.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    }
    response = requests.get(url, headers=headers)
    html = response.text
    if "Access Denied" in html:
        print("FAILED: Access Denied")
    else:
        print(f"SUCCESS! Status: {response.status_code}")
        print(html[:500])

if __name__ == "__main__":
    test_requests()
