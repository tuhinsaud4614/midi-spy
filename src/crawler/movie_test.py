from unittest import TestCase
from movie import Movie
from utils.models.error import CrawlingError


class MovieTest(TestCase):
    def test_init(self):
        self.assertRaises(CrawlingError, Movie,
                          "https://m.imdbx.com/title/tt8332922/")

    def test_title(self):
        movie = Movie("https://m.imdb.com/title/tt8332922/")
        self.assertEqual(movie.title, "a quiet place part ii")

    def test_credits(self):
        movie = Movie("https://m.imdb.com/title/tt8332922/")

        # Should return a list with two sub-list
        # Credit of the movie 
        self.assertListEqual(movie._get_credits(), [[
            {
                "id": "nm1024677",
                "name": "john krasinski"
            }
        ], [{
            "id": "nm1024677",
            "name": "john krasinski"
        },
            {
            "id": "nm1456816",
            "name": "bryan woods"
        },
            {
            "id": "nm1399714",
            "name": "scott beck"
        }]])

        # Get Directors the directors 
        self.assertListEqual(movie._get_credits()[0], [{
            "id": "nm1024677",
            "name": "john krasinski"
        }])

        self.assertDictEqual(movie._get_credits()[0][0], {
            "id": "nm1024677",
            "name": "john krasinski"
        })
        # self.assertDictEqual(movie._get_credits()[0][0], {
        #     "id": "nm1024677",
        #     "name": "john krasinski",
        #     "age": 30
        # })
