import re
import json
import requests as rq
from bs4 import BeautifulSoup as BS


class Movie:
    def __init__(self, url):
        self.__req = rq.get(url)
        self.__soup = BS(self.__req.content, "html.parser")


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


def get_photos(sel):
    temp = []
    for p in sel:
        img_tag = p.find("img")
        if img_tag and img_tag.get("srcset"):
            temp.append([e.strip() for e in re.findall(
                r'(.*?)[0-9]+w,?', img_tag.get("srcset"))])
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


def get_release_date(sel):
    text = sel.get_text().strip().lower()
    if text:
        # date format May 28 2011
        result_text = re.findall(
            r"([a-z]{3} [0-9]{2}\, [0-9]{4})", text)
        if len(result_text):
            date = result_text[0].replace(",", "").split(" ")
            if len(date) == 3:
                return {"day": date[1], "month": date[0], "year": date[2]}
    return None


def get_detail(sel):
    data = []
    if len(sel):
        for o in sel:
            text = o.get_text()
            if text:
                data.append(text.strip().lower())

    return data


def get_filming_locations(sel):
    text = sel.get_text()
    if text and "," in text:
        return [l.lower() for l in text.split(", ")]
    return None


def get_production_companies(sel):
    if sel:
        li_tags = sel.find_all("li")
        if len(li_tags):
            a_tags = []
            for t in li_tags:
                a = t.find("a")
                if a:
                    text = a.get_text()
                    link_text = a.get("href")
                    id = re.findall(r".*\/company\/(.*)\?.*", link_text)
                    if text and len(id):
                        a_tags.append(
                            {"id": id[0], "name": text.strip().lower()})
            return a_tags if len(a_tags) else None
    return None


def get_world_gross(sel):
    if sel:
        li_tag = sel.find("li")
        if li_tag:
            span_tag = li_tag.find("span")
            if span_tag:
                text = span_tag.get_text()
                if text:
                    return text.strip().replace(",", "")
    return None


def get_tech_spec(sel):
    a_tags = sel.find_all("a")
    if len(a_tags):
        data = []
        for a in a_tags:
            text = a.get_text()
            if text:
                data.append(text.strip().lower())
        return data if len(data) else None
    return None


movie = dict()

title_selector = soup.find(
    'h1', attrs={'data-testid': "hero-title-block__title"})
img_selector = soup.find(
    'div', attrs={'data-testid': "hero-media__poster"}).find("img")

photos_selector = soup.find_all(
    "div", attrs={'class': "ipc-photo__photo-image"})

runtime = soup.find(
    'li', attrs={'data-testid': 'title-techspec_runtime'}).select("span")
release_year = soup.find(
    "ul", attrs={'data-testid': "hero-title-block__metadata"})
genres = soup.find('div', attrs={'data-testid': 'genres'}).select("span")
credits = soup.find_all(
    'li', attrs={'data-testid': 'title-pc-principal-credit'})
ratings_select = soup.find('div', attrs={
                           'data-testid': "hero-rating-bar__aggregate-rating__score"}).select("span")[0]
votes_select = soup.find(
    'div', attrs={'class': "AggregateRatingButton__TotalRatingAmount-sc-1ll29m0-3"})

directors = credits[0].find_all("a")
writers = credits[1].find_all("a")

cast_selectors = soup.find_all(
    'div', attrs={'data-testid': 'title-cast-item'})
release_date_selectors = soup.find(
    'li', attrs={'data-testid': 'title-details-releasedate'}).find_all("a")[1]
country_of_origin_selectors = soup.find(
    'li', attrs={'data-testid': 'title-details-origin'}).find_all("a")
languages_selectors = soup.find(
    'li', attrs={'data-testid': 'title-details-languages'}).find_all("a")
filming_locations_selectors = soup.find(
    'li', attrs={'data-testid': 'title-details-filminglocations'}).find_all("a")[1]
production_companines_selectors = soup.find(
    'li', attrs={'data-testid': 'title-details-companies'})
gross_world_wide_selectors = soup.find(
    'li', attrs={'data-testid': 'title-boxoffice-cumulativeworldwidegross'})
color_selectors = soup.find(
    'li', attrs={'data-testid': 'title-techspec_color'})
sound_mix_selectors = soup.find(
    'li', attrs={'data-testid': 'title-techspec_soundmix'})

# print(get_tech_spec(sound_mix_selectors))

movie["title"] = title_selector.get_text().strip().lower()
movie["img"] = img_selector.get("src") if img_selector else None
movie["photos"] = get_photos(photos_selector)
movie["ratings"] = {
    "value": ratings_select.get_text().strip(
    ).lower(),
    "votes": votes_select.get_text().strip().lower()
}
if len(runtime) == 2 and runtime[0].get_text().strip().lower() == "runtime":
    movie["runtime"] = runtime[1].get_text().strip()
movie["release_year"] = release_year.find("a").get_text().strip()
movie["genres"] = [i.get_text().strip() for i in genres]
movie["directors"] = get_credits(directors)
movie["writers"] = get_credits(writers)
movie["cast"] = get_casts(cast_selectors)
movie["release_date"] = get_release_date(release_date_selectors)
movie["country_of_origins"] = get_detail(country_of_origin_selectors)
movie["languages"] = get_detail(languages_selectors)
movie["filming_locations"] = get_filming_locations(filming_locations_selectors)
movie["production_companies"] = get_production_companies(
    production_companines_selectors)
movie["gross_world_wide"] = get_world_gross(gross_world_wide_selectors)
movie["tech_spec"] = {"color": get_tech_spec(
    color_selectors), "sound_mix": get_tech_spec(sound_mix_selectors)}
with open("movie.json", "w") as f:
    json.dump(movie, f, indent=2)
