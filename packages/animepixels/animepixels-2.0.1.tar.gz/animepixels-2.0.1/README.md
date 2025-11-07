# AnimePixels-API Python SDK

A simple NPM wrapper for the [AnimePixels API].
Fetch anime images & GIFs by category, ID, randomly, or search — in one line.
Works cross-platform (Node.js, React, Next.js, python etc.).

---

## 🚀 Installation

```bash
pip install animepixels



from animepixels import AnimePixels

# Initialize the API client
api = AnimePixels(base_url="https://animepixels-api.vercel.app/api/media")

# -------------------------------
#  Random Image
# -------------------------------
print("🖼️ Random Image:")
random_img = api.images.random()
print(random_img, "\n")

# -------------------------------
#  Random Image by Category
# -------------------------------
print("🎯 Random Naruto Image:")
naruto_img = api.images.random("naruto")
print(naruto_img, "\n")

# -------------------------------
#  Get Image by ID
# -------------------------------
print("🆔 Get Image by ID:")
image_by_id = api.images.by_id("123abc")  # Replace with valid ID
print(image_by_id, "\n")

# -------------------------------
#  Get Images by Category
# -------------------------------
print("📂 Images from 'onepiece' category:")
onepiece_imgs = api.images.by_category("onepiece", limit=3)
for img in onepiece_imgs:
    print(img["url"])
print()

# -------------------------------
#  Search Images
# -------------------------------
print("🔍 Search for 'itachi' images:")
search_results = api.images.search("itachi", limit=3)
for r in search_results:
    print(r["url"])
print()

# -------------------------------
#  Random GIF
# -------------------------------
print("🎞️ Random GIF:")
random_gif = api.gifs.random()
print(random_gif, "\n")

# -------------------------------
#  Random GIF by Category
# -------------------------------
print("🎬 Random 'naruto' GIF:")
naruto_gif = api.gifs.random("naruto")
print(naruto_gif, "\n")

# -------------------------------
#  Get GIF by ID
# -------------------------------
print("🆔 Get GIF by ID:")
gif_by_id = api.gifs.by_id("abc123")  # Replace with valid ID
print(gif_by_id, "\n")

# -------------------------------
#  Get GIFs by Category
# -------------------------------
print("📁 GIFs from 'attack-on-titan' category:")
aot_gifs = api.gifs.by_category("attack-on-titan", limit=3)
for gif in aot_gifs:
    print(gif["url"])
print()

# -------------------------------
#  Search GIFs
# -------------------------------
print("🔍 Search for 'luffy' GIFs:")
search_gifs = api.gifs.search("luffy", limit=3)
for g in search_gifs:
    print(g["url"])
print()

# -------------------------------
# Get All Categories
# -------------------------------
print("📚 Available Categories:")
categories = api.categories.all()
print(categories)
print("\n✅ Done! All features tested successfully.")
