import re
import requests as r
from bs4 import BeautifulSoup as BS


class Upcoming:
    def __init__(self, link, base_url="https://www.imdb.com"):
        self.url = base_url
        self.__req = r.get(link)
        self.__soup = BS(self.__req.content, "html.parser")

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


up = Upcoming("https://www.imdb.com/calendar", "https://www.imdb.com")
print(up.movies())
