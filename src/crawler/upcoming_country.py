import requests as r
from bs4 import BeautifulSoup as BS

url = "https://www.imdb.com"
country_li = []


def soup_value(link):
    return BS(r.get(link).content, "html.parser")


req = r.get("https://www.imdb.com/calendar/?ref_=nv_mv_cal")
soup = BS(req.content, "html.parser")
items = soup.select("div#sidebar ul > li > a")

for i in items:
    country_li.append({
        "name": i.string.strip(),
        "link": f"{url}{i['href']}"
    })

req = r.get(country_li[0]["link"])
soup = BS(req.content, "html.parser")
print(soup.select("div#main > ul"))
