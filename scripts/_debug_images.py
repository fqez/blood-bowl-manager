import requests
from bs4 import BeautifulSoup

url = "https://bloodbowlbase.ru/bb2025/starplayers/Morg_%27n%27_Thorg/"
r = requests.get(url)
soup = BeautifulSoup(r.text, "html.parser")

print("=== ALL IMAGES ===")
for img in soup.find_all("img"):
    print(f"src={img.get('src')}")
    print(f"  data-src={img.get('data-src')}")
    print(f"  class={img.get('class')}")
    print(f"  alt={img.get('alt')}")
    print()

print("=== HTML SNIPPET around images ===")
# Find the main content area
main = soup.find("main") or soup.find("article") or soup.find("div", class_="content")
if main:
    for img in main.find_all("img"):
        print(img.parent)
        print("---")
