import os
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://nufflezone.com/en/blood-bowl-teams/"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def get_soup(url):
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    return BeautifulSoup(res.text, "html.parser")


def sanitize_filename(name):
    return "".join(c for c in name if c.isalnum() or c in ("-", "_")).lower()


def download_image(url, filepath):
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    with open(filepath, "wb") as f:
        f.write(res.content)
    print(f"[✓] {filepath}")


def main():
    os.makedirs("logos", exist_ok=True)

    soup = get_soup(BASE_URL)

    # Cada equipo está como título (h3/h4 dependiendo versión)
    teams = soup.select("h3, h4")

    print(f"Equipos detectados: {len(teams)}")

    for team in teams:
        team_name = team.get_text(strip=True)

        # Saltar cosas que no son equipos reales (NAF, etc.)
        if not team_name or team_name.lower() in ["naf", "no oficial"]:
            continue

        print(f"Procesando: {team_name}")

        # Buscar siguiente imagen después del título
        img = team.find_next("img")

        if not img:
            print("  [!] No hay imagen")
            continue

        img_url = img.get("src")
        if not img_url:
            continue

        img_url = urljoin(BASE_URL, img_url)

        # 🔥 FILTRO CLAVE
        if "/wp-content/uploads/" not in img_url or not img_url.endswith(".webp"):
            print("  [!] No es logo válido")
            continue

        filename = sanitize_filename(team_name) + ".webp"
        filepath = os.path.join("logos", filename)

        download_image(img_url, filepath)


if __name__ == "__main__":
    main()
    main()
