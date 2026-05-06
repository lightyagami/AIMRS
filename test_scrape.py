import urllib.request
import bs4 as bs
import sys

imdb_id = 'tt1539877' # Oppenheimer
url = 'https://www.imdb.com/title/{}/reviews?ref_=tt_ov_rt'.format(imdb_id)
print(f"Fetching: {url}")

try:
    # Adding a User-Agent because IMDb often blocks default python-urllib agents
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    sauce = urllib.request.urlopen(req).read()
    soup = bs.BeautifulSoup(sauce,'lxml')
    soup_result = soup.find_all("div",{"class":"text show-more__control"})
    
    print(f"Found {len(soup_result)} reviews.")
    for i, review in enumerate(soup_result[:3]):
        print(f"\nReview {i+1}:")
        print(review.get_text()[:200] + "...")
except Exception as e:
    print(f"Error: {e}")
