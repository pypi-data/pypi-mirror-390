import requests
from typing import Optional

BASE_URL = "https://animepixels-api.vercel.app/api/media"

# ----------------- IMAGES -----------------

def get_all_images(limit: int = 50, offset: int = 0):
    res = requests.get(f"{BASE_URL}/all-images", params={"limit": limit, "offset": offset})
    res.raise_for_status()
    return res.json()

def random_image(category: Optional[str] = None):
    url = f"{BASE_URL}/random/image"
    if category:
        url += f"/{category}"
    res = requests.get(url)
    res.raise_for_status()
    return res.json()

def get_image_by_id(media_id: int):
    res = requests.get(f"{BASE_URL}/image/id/{media_id}")
    res.raise_for_status()
    return res.json()

def search_images(q: str, limit: int = 50, offset: int = 0):
    res = requests.get(f"{BASE_URL}/search/image", params={"q": q, "limit": limit, "offset": offset})
    res.raise_for_status()
    return res.json()

def get_images_by_category(category: str, limit: int = 50, offset: int = 0):
    res = requests.get(f"{BASE_URL}/image/{category}", params={"limit": limit, "offset": offset})
    res.raise_for_status()
    return res.json()


# ----------------- GIFS -----------------

def get_all_gifs(limit: int = 50, offset: int = 0):
    res = requests.get(f"{BASE_URL}/all-gifs", params={"limit": limit, "offset": offset})
    res.raise_for_status()
    return res.json()

def random_gif(category: Optional[str] = None):
    url = f"{BASE_URL}/random/gif"
    if category:
        url += f"/{category}"
    res = requests.get(url)
    res.raise_for_status()
    return res.json()

def get_gif_by_id(media_id: int):
    res = requests.get(f"{BASE_URL}/gif/id/{media_id}")
    res.raise_for_status()
    return res.json()

def search_gifs(q: str, limit: int = 50, offset: int = 0):
    res = requests.get(f"{BASE_URL}/search/gif", params={"q": q, "limit": limit, "offset": offset})
    res.raise_for_status()
    return res.json()

def get_gifs_by_category(category: str, limit: int = 50, offset: int = 0):
    res = requests.get(f"{BASE_URL}/gif/{category}", params={"limit": limit, "offset": offset})
    res.raise_for_status()
    return res.json()


# ----------------- CATEGORIES -----------------

def get_categories():
    res = requests.get(f"{BASE_URL}/categories")
    res.raise_for_status()
    return res.json().get("categories", [])
