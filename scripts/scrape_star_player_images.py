"""Script to scrape star player images from bloodbowlbase.ru."""

import os
import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# Base URL
BASE_URL = "https://bloodbowlbase.ru/bb2025/starplayers/"

# Output directory
OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "..",
    "blood-bowl-manager-front",
    "assets",
    "images",
    "star_players",
)

# List of star players from our JSON
STAR_PLAYERS = [
    "Akhorne_The_Squirrel",
    "Anqi_Panqi",
    "Barik_Farblast",
    "Bilerot_Vomitflesh",
    "Boa_Kon'ssstriktr",
    "Bomber_Dribblesnot",
    "Captain_Karina_von_Riesz",
    "Cindy_Piewhistle",
    "Count_Luthor_von_Drakenborg",
    "Deeproot_Strongbranch",
    "Dribl_and_Drull",
    "Eldril_Sidewinder",
    "Estelle_la_Veneaux",
    "Fungus_the_Loon",
    "Glart_Smashrip",
    "Gloriel_Summerbloom",
    "Glotl_Stop",
    "Grak_and_Crumbleberry",
    "Grashnak_Blackhoof",
    "Gretchen_Wächter",
    "Griff_Oberwald",
    "Grim_Ironjaw",
    "Grombrindal",
    "Guffle_Pusmaw",
    "Hakflem_Skuttlespike",
    "Helmut_Wulf",
    "H'thark_the_Unstoppable",
    "Ivan_'the_Animal'_Deathshroud",
    "Ivar_Eriksson",
    "Jeremiah_Kool",
    "Jordell_Freshbreeze",
    "Josef_Bugman",
    "Karla_von_Kill",
    "Kiroth_Krakeneye",
    "Kreek_Rustgouger",
    "Lord_Borak_the_Despoiler",
    "Maple_Highgrove",
    "Max_Spleenripper",
    "Morg_'n'_Thorg",
    "Nobbla_Blackwart",
    "Puggy_Baconbreath",
    "Rashnak_Backstabber",
    "Ripper_Bolgrot",
    "Rodney_Roachbait",
    "Rowana_Forestfoot",
    "Roxanna_Darknail",
    "Rumbelow_Sheepskin",
    "Scrappa_Sorehead",
    "Scyla_Anfingrimm",
    "Skitter_Stab-stab",
    "Skrorg_Snowpelt",
    "Skrull_Halfheight",
    "Swiftvine_Glimmershard",
    "The_Black_Gobbo",
    "The_Mighty_Zug",
    "The_Swift_Twins",
    "Thorsson_Stoutmead",
    "Varag_Ghoul-Chewer",
    "Wilhelm_Chaney",
    "Willow_Rosebark",
    "Withergrasp_Doubledrool",
    "Zolcath_the_Zoat",
    "Zzharg_Madeye",
]

# Headers to mimic browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def normalize_name_for_file(name: str) -> str:
    """Convert star player name to snake_case filename."""
    # Remove special chars and convert to lowercase
    filename = name.lower()
    filename = filename.replace("'", "")
    filename = filename.replace("ä", "a")
    filename = filename.replace(" ", "_")
    filename = re.sub(r"[^a-z0-9_]", "_", filename)
    filename = re.sub(r"_+", "_", filename)
    filename = filename.strip("_")
    return filename


def get_star_player_page_url(name: str) -> str:
    """Build URL for star player page."""
    # URL encode special characters
    from urllib.parse import quote

    encoded_name = quote(name, safe="_")
    return f"{BASE_URL}{encoded_name}/"


def scrape_star_player_image(
    name: str, session: requests.Session
) -> tuple[str, bytes] | None:
    """Scrape image for a single star player."""
    url = get_star_player_page_url(name)
    print(f"Fetching: {url}")

    try:
        response = session.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"  Error fetching page: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Look for images on the page
    # Try different selectors
    img_tags = soup.find_all("img")

    # First priority: images inside <p> tags in main content (actual player portraits)
    for img in img_tags:
        src = img.get("src", "")
        if not src:
            continue

        img_lower = src.lower()

        # Target images in /media/starplayers/ path (site-specific pattern)
        is_media = "/media/" in img_lower or "/starplayers" in img_lower

        # Also accept any image inside a <p> tag (content images vs nav icons)
        inside_paragraph = img.parent and img.parent.name == "p"

        if not (is_media or inside_paragraph):
            continue

        # Skip the badge/logo images
        if "badge" in img_lower or "logo" in img_lower or "assets/" in img_lower:
            continue

        img_url = urljoin(url, src)
        print(f"  Found image: {img_url}")

        try:
            img_response = session.get(img_url, headers=HEADERS, timeout=30)
            img_response.raise_for_status()

            content_type = img_response.headers.get("content-type", "")
            if "png" in content_type:
                ext = ".png"
            elif "webp" in content_type:
                ext = ".webp"
            else:
                ext = ".jpg"

            return ext, img_response.content
        except requests.RequestException as e:
            print(f"  Error downloading image: {e}")

    print(f"  No suitable image found")
    return None


def scrape_all_star_players():
    """Scrape images for all star players."""
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Scraping {len(STAR_PLAYERS)} star players...\n")

    session = requests.Session()

    success_count = 0
    failed = []

    for i, name in enumerate(STAR_PLAYERS, 1):
        print(f"[{i}/{len(STAR_PLAYERS)}] {name}")

        result = scrape_star_player_image(name, session)

        if result:
            ext, img_data = result
            filename = normalize_name_for_file(name) + ext
            filepath = os.path.join(OUTPUT_DIR, filename)

            with open(filepath, "wb") as f:
                f.write(img_data)

            print(f"  Saved: {filename}")
            success_count += 1
        else:
            failed.append(name)

        # Be nice to the server
        time.sleep(0.5)

    print(f"\n{'='*50}")
    print(f"Successfully downloaded: {success_count}/{len(STAR_PLAYERS)}")

    if failed:
        print(f"\nFailed to download:")
        for name in failed:
            print(f"  - {name}")


if __name__ == "__main__":
    scrape_all_star_players()
