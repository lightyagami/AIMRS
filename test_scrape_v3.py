import requests
import bs4 as bs

imdb_id = 'tt1539877' # Oppenheimer
url = f'https://www.imdb.com/title/{imdb_id}/reviews'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.google.com/'
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    soup = bs.BeautifulSoup(response.text, 'lxml')
    print(f"Page Title: {soup.title.string if soup.title else 'No Title'}")
    
    # Try the old selector
    results = soup.find_all("div", {"class": "text show-more__control"})
    print(f"Found {len(results)} reviews with old selector.")
    
    if len(results) == 0:
        # Inspect a bit of the body to see what we got
        print("Body snippet:")
        print(response.text[:500])
except Exception as e:
    print(f"Error: {e}")
