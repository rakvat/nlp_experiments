from bs4 import BeautifulSoup
import requests

html_doc = requests.get("https://player.fm/series/machine-learning-guide-1457335").text
soup = BeautifulSoup(html_doc, 'html.parser')
# print(soup.prettify())

# document.querySelectorAll(".info a[data-remote='true']")
info_divs = soup.find_all(attrs={'class': 'info'})
for info in info_divs:
    podcast_a = info.find('a')
    if podcast_a:
        url = "https://player.fm" + podcast_a['href']
        print(url)
        podcast_html = requests.get(url).text
        soup = BeautifulSoup(podcast_html, 'html.parser')
        links = soup.find(attrs={'class': 'links'})
        if links:
          mp3_link = links.find('a')
          podcast_url = mp3_link['href']
          print(podcast_url)
          response = requests.get(podcast_url, stream=True)
          target_path = podcast_a['href'].split('/')[-1].split('?')[0] + '.mp3'
          print(target_path)
          handle = open(target_path, 'wb')
          for chunk in response.iter_content(chunk_size=512):
              if chunk:  # filter out keep-alive new chunks
                  handle.write(chunk)
          handle.close()
