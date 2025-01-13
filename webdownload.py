import requests
from bs4 import BeautifulSoup

def download_page_without_ads(url):
    """
    Downloads a web page from the given URL and removes ad elements using BeautifulSoup.
    
    Args:
        url: The URL of the web page to download.

    Returns:
        str: The HTML content of the page with ads removed.
    """
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception if the request fails
    soup = BeautifulSoup(response.content, 'html.parser')

    # Identify ad elements based on class names, IDs, or other attributes
    ad_elements = soup.select('.ad-container', 'div[id^="ad-"]')  

    for ad in ad_elements:
        ad.decompose()  # Remove ad elements from the HTML tree

    clean_html = str(soup)
    return clean_html

# Example usage
target_url = "https://www.example.com/article"
target_url = "https://threadreaderapp.com/thread/1878558994622456276.html" 
clean_page = download_page_without_ads(target_url)

# Save the clean HTML to a file
with open("clean_page.html", "w") as f:
    f.write(clean_page)
