import re
import json
from typing import Any, Optional
import requests
from bs4 import BeautifulSoup
from requests.models import Response

from utils.models.error import CrawlingError


class Countries:
    _req: Response
    _soup: BeautifulSoup
    countries: Optional[list[dict[str, str]]] = None

    def __init__(self, url: str) -> None:
        """This will take url (String as argument)"""
        try:
            self._req = requests.get(url)
            self._soup = BeautifulSoup(
                self._req.content, "html.parser")
        except:
            raise CrawlingError("Connection failed!",
                                "Can't not connected with requested server.")
        self.countries = self._get_countries()

    def _to_text(self, selector: Any) -> str:
        """This will converts selector inner element into text, removing unnecessary character"""
        return selector.get_text().strip().lower()

    def _get_countries(self) -> Optional[list[dict[str, str]]]:
        tags = self._soup.select('div[class="aux-content-widget-3"] a')
        if not tags:
            return None

        result = []
        for tag in tags:
            href = tag.get("href")
            text = self._to_text(tag)
            if href and text:
                result.append(
                    {"name": text, "link": f"https://www.imdb.com{href}"})
        return result if result else None


class Upcoming:
    def __init__(self, link, base_url="https://www.imdb.com"):
        self.url = base_url
        self.__req = requests.get(link)
        self.__soup = BeautifulSoup(self.__req.content, "html.parser")

    def __movie(self, m):
        anchor = m.select_one("a")
        if anchor:
            t = m.get_text().strip()
            d = re.findall(r"\(\s*\+?(-?\d+)\s*\)", t)
            return {
                "title": anchor.string.strip(),
                "link": f'{self.url}{anchor["href"]}',
                "year": d[0] if len(d) else ""
            }
        return None

    def movies(self):
        d = [i.string.strip() for i in self.__soup.select("div#main > h4")]
        u_list = self.__soup.select("div#main > h4 + ul")
        all_movies = []
        if len(d) == len(u_list):
            for i, ms in enumerate(u_list):
                movies_in_date = []
                for m in ms.find_all("li"):
                    temp = self.__movie(m)
                    if temp:
                        movies_in_date.append(temp)
                all_movies.append({
                    "date": d[i],
                    "movies": movies_in_date
                })
            return all_movies
        else:
            print("No move is upcoming")
            return all_movies


countries_obj = Countries("https://www.imdb.com/calendar")

result = []
for country in countries_obj.countries:
    up = Upcoming(country["link"])
    result.append({"country": country["name"], "movies": up.movies()})

print(result)
