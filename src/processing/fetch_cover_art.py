"""
Fetch cover art for one flagship album per artist, for multimodal
(CLIP-based) retrieval.
"""

import json
import time
import requests
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / 'data'
CLEANED_PATH = DATA_DIR / 'processed' / 'mb_cleaned_artists.json'  # adjust to your actual filename
OUTPUT_PATH = DATA_DIR / 'processed' / 'album_covers.json'


def get_cover_art_url(release_group_mbid: str) -> str | None:
    """
    Fetch the front cover art URL for a MusicBrainz release-group.
    Returns None if no cover art exists.
    """
    url = f"https://coverartarchive.org/release-group/{release_group_mbid}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        for image in data.get('images', []):
            if image.get('front'):
                return image['image']
    except requests.exceptions.RequestException:
        return None
    return None


def fetch_flagship_covers(cleaned_path: Path, output_path: Path) -> None:
    """
    For each artist, pick their earliest release-group and fetch its
    cover art, if available.
    """
    with open(cleaned_path) as f:
        artists = json.load(f)

    results = []
    for i, artist in enumerate(artists):
        release_groups = artist.get('release_groups', [])
        if not release_groups:
            continue

        # your task: pick the earliest release-group by first-release-date
        # (hint: sorted() with a key, same pattern you've used before)
        dated_groups = [rg for rg in release_groups if rg.get('first-release-date')]
        if not dated_groups:
            continue  # skip this artist entirely if none of their albums have a known date
        sorted_groups = sorted(dated_groups, key=lambda x: x['first-release-date'])
        earliest = sorted_groups[0]
        print(earliest)

        cover_url = get_cover_art_url(earliest['mbid'])
        time.sleep(1.1)

        if cover_url:
            results.append({
                'artist': artist['name'],
                'album': earliest['title'],
                'mbid': earliest['mbid'],
                'cover_url': cover_url
            })

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Found cover art for {len(results)}/{len(artists)} artists")

print(fetch_flagship_covers(CLEANED_PATH, OUTPUT_PATH))