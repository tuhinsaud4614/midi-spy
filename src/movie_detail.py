import re
import json
import requests as rq
from bs4 import BeautifulSoup as BS


req = rq.get(
    'https://m.imdb.com/title/tt8332922/', 'html.parser')
soup = BS(req.content, 'html.parser')


def get_credits(sel):
    temp = []
    for c in sel:
        link = c.get("href")
        name = c.get_text().strip()
        if link:
            id = re.findall(r".*?/name\/(.*)\/\?.*", link)
            if len(id):
                id = id[0]
                temp.append({"id": id, "name": name})
    return temp


def get_casts(sel):
    temp = []
    if len(sel):
        for el in sel:
            imgTag = el.find("img")
            roleTag = el.find(
                "a", attrs={'data-testid': 'cast-item-characters-link'})
            nameTag = el.find(
                "a", attrs={'data-testid': 'title-cast-item__actor'})

            if roleTag and nameTag:
                id = re.findall(
                    r".*\/name\/(.*)\?.*", nameTag.get("href"))[0]
                name = nameTag.get_text().strip()
                role = roleTag.get_text().strip()

                cast = {
                    "id": id,
                    "name": name,
                    "role": role,
                    "img": imgTag.get("src") if imgTag else None
                }
            temp.append(cast)
    return temp


movie = dict()

title_selector = soup.find(
    'h1', attrs={'data-testid': "hero-title-block__title"})
img_selector = soup.find(
    'div', attrs={'data-testid': "hero-media__poster"}).find("img")
runtime = soup.find(
    'li', attrs={'data-testid': 'title-techspec_runtime'}).select("span")
release_year = soup.find(
    "ul", attrs={'data-testid': "hero-title-block__metadata"})
genres = soup.find('div', attrs={'data-testid': 'genres'}).select("span")
credits = soup.find_all(
    'li', attrs={'data-testid': 'title-pc-principal-credit'})

directors = credits[0].find_all("a")
writers = credits[1].find_all("a")

cast_selectors = soup.find_all(
    'div', attrs={'data-testid': 'title-cast-item'})
# print(img_selector)

movie["title"] = title_selector.get_text().strip().lower()
movie["img"] = img_selector.get("src") if img_selector else None
if len(runtime) == 2 and runtime[0].get_text().strip().lower() == "runtime":
    movie["runtime"] = runtime[1].get_text().strip()
movie["release_year"] = release_year.find("a").get_text().strip()
movie["genres"] = [i.get_text().strip() for i in genres]
movie["directors"] = get_credits(directors)
movie["writers"] = get_credits(writers)
movie["cast"] = get_casts(cast_selectors)
# print(movie)
with open("movie.json", "w") as f:
    json.dump(movie, f, indent=2)
