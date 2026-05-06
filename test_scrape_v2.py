import urllib.request
import bs4 as bs

imdb_id = 'tt1539877' # Oppenheimer
url = 'https://www.imdb.com/title/{}/reviews?ref_=tt_ov_rt'.format(imdb_id)

try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    req = urllib.request.Request(url, headers=headers)
    sauce = urllib.request.urlopen(req).read()
    soup = bs.BeautifulSoup(sauce,'lxml')
    
    # Let's print the title to see if we even got the right page
    print(f"Page Title: {soup.title.string if soup.title else 'No Title'}")
    
    # Try multiple common selectors
    selectors = [
        ("class: text show-more__control", soup.find_all("div",{"class":"text show-more__control"})),
        ("class: content", soup.find_all("div",{"class":"content"})),
        ("data-testid: review-container", soup.find_all("div",{"data-testid":"review-container"})),
        ("class: imdb-user-review", soup.find_all("div",{"class":"imdb-user-review"}))
    ]
    
    for label, result in selectors:
        print(f"Found {len(result)} with {label}")
        if len(result) > 0:
            print(f"Sample: {result[0].get_text()[:100]}...")

except Exception as e:
    print(f"Error: {e}")
