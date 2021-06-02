import requests as rq
from bs4 import BeautifulSoup as BS


req = rq.get(
    'https://m.imdb.com/chart/boxoffice', 'html.parser')

soup = BS(req.content, 'html.parser')

# movie_tags = soup.find_all('a', attrs={'class': 'btn-full'})

# wg = weekend gross
# tg = total gross
# wsg = weeks since release

# movies = []
# for m in movie_tags:
#     mm = {
#         'name': '',
#         'link': '',
#         'wg': '',
#         'tg': '',
#         'wsr': ''
#     }
#     movie = []
#     movie.append(m.find('h4').string.strip())
#     movie.extend(m.find('p').get_text().strip().split('\n\n'))
#     mm['name'] = movie[0]
#     mm['wg'] = movie[1].split(':')[1].strip()
#     mm['tg'] = movie[2].split(':')[1].strip()
#     mm['wsr'] = movie[3].split(':')[1].strip()
#     mm['link'] = f'https://m.imdb.com{m["href"]}'
#     movies.append(mm)

# print(movies)

movie_images = soup.find_all('div', attrs={'class': 'media'})
movies = []
for m in movie_images:
    # x.append(m.find("div > span > a > img")[0].get("src"))
    z = m.select("div > a > span")[0]
    movie = []
    movie.append(z.find('h4').string.strip())
    movie.extend(z.find('p').get_text().strip().split('\n\n'))
    mm = dict()
    mm['name'] = movie[0]
    mm["image"] = m.find("img").get("src")
    mm['wg'] = movie[1].split(':')[1].strip()
    mm['tg'] = movie[2].split(':')[1].strip()
    mm['wsr'] = movie[3].split(':')[1].strip()
    mm['link'] = f'https://m.imdb.com{m.find("a")["href"]}'
    movies.append(mm)
print(f'{movies}')
