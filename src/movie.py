import requests
import re
import json
from datetime import datetime
from typing import Any, Mapping, Optional, Union
from requests.models import Response
from bs4 import BeautifulSoup

from utils.models.error import CrawlingError
from utils.utils import convert_compact_to_number


class Movie:
    """This class will provide all information about a movie according to their site parsing"""
    _req: Response
    _soup: BeautifulSoup
    title: str
    poster: Optional[tuple[str, ...]] = None
    posters: Optional[list[tuple[str, ...]]] = None
    runtime: Optional[str] = None
    release_year: Optional[int] = None
    release_date: Optional[datetime] = None
    genres: Optional[list[str]] = None
    rating: Optional[dict[str, Union[float, int]]] = None
    directors: list[dict[str, str]]
    writers: list[dict[str, str]]
    casts: Optional[list[dict[str, Optional[Union[str, tuple[str, ...]]]]]] = None
    origins: Optional[list[str]] = None
    languages: Optional[list[str]] = None
    filming_locations: Optional[list[str]] = None
    production_companies: Optional[list[dict[str, str]]] = None
    worldwide_gross: Optional[float] = None
    tech_spec: Optional[dict[str, list[str]]]

    def __init__(self, url: str) -> Union[None, CrawlingError]:
        """This will take url (String as argument)"""

        try:
            self._req = requests.get(url)
            self._soup = BeautifulSoup(self._req.content, "html.parser")
        except:
            raise CrawlingError("Connection failed!",
                                "Can't not connected with requested server.")
        # Title for the movie
        title_tag = self._soup.find(
            'h1', attrs={'data-testid': "hero-title-block__title"})
        if not title_tag:
            raise CrawlingError(
                "Title not found!", "Title not found for this movie that's why no movie found.")
        self.title = self._to_text(title_tag)

        # Credits for the movie
        self.directors, self.writers = self._get_credits()
        # Image for the movie
        self.poster = self._get_poster()
        # Images for the movie
        self.posters = self._get_posters()
        # Rating for the movie
        self.rating = self._get_rating()
        # Runtime of the movie
        self.runtime = self._get_runtime()
        # Releasing Year of the movie
        self.release_year = self._get_releasing_year()
        # Genres of the movie
        self.genres = self._get_genres_or_origins_or_languages(
            'div[data-testid="genres"] span')
        # Casts of the movie
        self.casts = self._get_casts()
        # Release of the movie
        self.release_date = self._get_release_date()
        # Origins of the movie
        self.origins = self._get_genres_or_origins_or_languages(
            'li[data-testid="title-details-origin"] a')
        # Languages of the movie
        self.languages = self._get_genres_or_origins_or_languages(
            'li[data-testid="title-details-languages"] a')
        # Filming locations of the movie
        self.filming_locations = self._get_filming_locations()
        # Production companies of the movie
        self.production_companies = self._get_production_companies()
        # Worldwide gross of the movie
        self.worldwide_gross = self._get_worldwide_gross()
        # Technical specifications of the movie
        color = self._get_tech_spec('li[data-testid="title-techspec_color"] a')
        sound_mix = self._get_tech_spec('li[data-testid="title-techspec_soundmix"] a')
        self.tech_spec = {"color": color, "sound_mix": sound_mix}

    def to_json(self) -> Mapping[str, Any]:
        """This function converts the class into map"""
        return json.dumps({
            "title": self.title,
            "poster": self.poster,
            "images": self.posters,
            "directors": self.directors,
            "writers": self.writers,
            "ratings": self.rating,
            "runtime": self.runtime,
            "releasing_year": self.release_year,
            "genres": self.genres,
            "casts": self.casts,
            "release_date": self.release_date,
            "origins": self.origins,
            "languages": self.languages,
            "filming_locations": self.filming_locations,
            "production_companies": self.production_companies,
            "worldwide_gross": self.worldwide_gross,
            "tech_spec": self.tech_spec
        }, indent=2, sort_keys=True)

    def _to_text(self, selector: Any) -> str:
        """This will converts selector inner element into text, removing unnecessary character"""
        return selector.get_text().strip().lower()

    # Split image srcset into list
    def _split_srcset(self, srcset: Any) -> Optional[tuple[str]]:
        "This will split the srcset string into list of src"
        if type(srcset) is not str:
            return None
        re_result = re.findall(
            r'(.*?)[0-9]+w,?', srcset)
        if not re_result:
            return None
        return tuple(item.strip() for item in re_result)

    # Get movie image
    def _get_image(self, tag: Any) -> Optional[tuple[str, ...]]:
        """This will find out img src from img tag"""
        if not tag:
            return None

        srcset = tag.get("srcset")
        if not srcset:
            src = tag.get("src")
            return (src,) if type(src) is str else None
        srcset = self._split_srcset(srcset)
        return srcset

    def _get_credits(self) -> list[
        list[dict[str, str]],
        list[dict[str, str]]
    ]:
        """This function will return the movie credits like directors & writers"""
        selectors = self._soup.find_all(
            "li", attrs={"data-testid": "title-pc-principal-credit"})
        # If selectors not found return empty list
        if not selectors:
            return [[], []]

        # Helper function
        def list_with_Map(results):
            """This will convert results list with map"""
            final_result = []
            if not results:
                return final_result
            for result in results:
                link = result.get("href")
                name = self._to_text(result)
                if link:
                    id = re.findall(r".*?/name\/(.*)\/\?.*", link)
                    if len(id):
                        id = id[0]
                        final_result.append({"id": id, "name": name})
            return final_result

        directors = writers = []
        # For directors
        if selectors[0]:
            directors = list_with_Map(selectors[0].find_all("a"))

        # For writers
        if selectors[1]:
            writers = list_with_Map(selectors[1].find_all("a"))

        return [directors, writers]

    # Get the movie poster
    def _get_poster(self) -> Optional[tuple[str, ...]]:
        """This will find out poster of the movie"""
        tag = self._soup.select_one(
            'div[data-testid="hero-media__poster"] img')
        return self._get_image(tag)
    # Get movie all images

    def _get_posters(self) -> Optional[list[list[str]]]:
        """This will find out all of the images of the movie"""
        tags = self._soup.select(
            'div[class~="ipc-photo__photo-image"] img')

        if not tags:
            return None
        result = []
        for tag in tags:
            srcset = self._get_image(tag)
            if srcset:
                result.append(srcset)
        return result if result else None

    # Get movie rating
    def _get_rating(self) -> Optional[dict[str, Union[float, int]]]:
        """This will find out rating and votes"""
        rating_tag = self._soup.find('span', attrs={
            'class': 'AggregateRatingButton__RatingScore-sc-1ll29m0-1'})
        if not rating_tag:
            return None
        votes_tag = self._soup.find('div', attrs={
            'class': 'AggregateRatingButton__TotalRatingAmount-sc-1ll29m0-3'})

        rating = float(self._to_text(rating_tag))
        votes = convert_compact_to_number(str(self._to_text(votes_tag)))
        return {
            "value": rating,
            "votes": votes
        }

    # Get movie runtime
    def _get_runtime(self) -> Optional[str]:
        """This will find out runtime of the movie"""
        tags = self._soup.select(
            'li[data-testid="title-techspec_runtime"] span')
        if len(tags) != 2:
            return None
        result = self._to_text(tags[1])
        return result

    # Get releasing date of the movie
    def _get_releasing_year(self) -> Optional[int]:
        """This will find out releasing year of the movie"""
        tag = self._soup.select_one(
            'ul[data-testid="hero-title-block__metadata"] a')

        if not tag:
            return None
        result = int(self._to_text(tag))
        return result

    # Get the genres of the movie
    def _get_genres_or_origins_or_languages(self, selector_query: str) -> Optional[tuple[str]]:
        """This will find out the genres of the movie"""
        tags = self._soup.select(selector_query)
        if not tags:
            return None
        result = tuple(self._to_text(tag) for tag in tags)
        return result

    # Get the casts of the movie
    def _get_casts(self) -> Optional[list[dict[str, Optional[Union[str, tuple[str, ...]]]]]]:
        """This will find out the all casts of the movie"""
        tags = self._soup.select(
            'div[data-testid="title-cast-item"]')
        if not tags:
            return None
        result = []
        for tag in tags:
            name_tag = tag.find(
                "a", attrs={'data-testid': 'title-cast-item__actor'})
            if not name_tag:
                continue

            href: list = re.findall(
                r".*\/name\/(.*)\?.*", name_tag.get("href"))
            if not href or not href[0]:
                continue

            images = self._get_image(tag.find("img"))

            cast: dict[str, Optional[Union[str, tuple[str, ...]]]] = {
                "id": href[0],
                "name": self._to_text(name_tag),
                "images": images
            }

            roleTag = tag.find(
                "a", attrs={'data-testid': 'cast-item-characters-link'})
            role = self._to_text(roleTag) if roleTag else None
            cast.update({"role": role})
            result.append(cast)
        return result if result else None

    # Get release date of the movie
    def _get_release_date(self) -> Optional[datetime]:
        """This will find out the release date of the movie"""
        tag = self._soup.select_one(
            'li[data-testid="title-details-releasedate"] a[class~="ipc-metadata-list-item__list-content-item--link"]')
        if not tag:
            return None

        text = self._to_text(tag)
        if not text:
            return None

        # date format May 28 2011
        re_result = re.findall(r"([a-z]{3} [0-9]{2}\, [0-9]{4})", text)
        if not re_result:
            return None

        try:
            date = datetime.strptime(re_result[0], "%B %d, %Y")
            return str(date)
        except:
            return

    # Get filming locations of the movie
    def _get_filming_locations(self) -> Optional[tuple[str]]:
        """This will find out the filming locations of the movie"""
        tags = self._soup.select(
            'li[data-testid="title-details-filminglocations"] a')

        if not tags or len(tags) < 2:
            return None

        locations = self._to_text(tags[1])
        if not locations or not "," in locations:
            return None

        return tuple(location for location in locations.split(", "))

    # Get production companies of the movie
    def _get_production_companies(self) -> Optional[list[str]]:
        """This will find out the production companines of the movie"""
        tags = self._soup.select(
            'li[data-testid="title-details-companies"] a[class~="ipc-metadata-list-item__list-content-item--link"]')
        if not tags:
            None

        result = []
        for tag in tags:
            href = tag.get("href")
            if not href:
                continue

            re_result: list = re.findall(r".*\/company\/(.*)\?.*", href)
            if not re_result:
                continue

            text = self._to_text(tag)
            if not text:
                continue

            result.append({"id": re_result[0], "name": text})
        return result if result else None

    # Get world wide gross of the movie
    def _get_worldwide_gross(self) -> Optional[int]:
        """This will find out the worldwide gross of the movie"""
        tag = self._soup.select_one(
            'li[data-testid="title-boxoffice-cumulativeworldwidegross"] span[class~="ipc-metadata-list-item__list-content-item"]')
        if not tag:
            return None
        text = re.sub(r"\$|,", "", self._to_text(tag))
        return float(text) if text else None

    # Get technical specifications of the movie
    def _get_tech_spec(self, selector) -> Optional[list[str]]:
        """This will find out the technical specifications of the movie"""
        tags = self._soup.select(selector)
        if not tags:
            return None

        result = []
        for tag in tags:
            text = self._to_text(tag)
            if text:
                result.append(text)
        return result if result else None


try:
    movie: Movie = Movie("https://m.imdb.com/title/tt8332922/")
    print(movie.to_json())
except CrawlingError as err:
    print(err.message)
except:
    print("Unknown Error")
