from strawberry.tools import merge_types

from .movie.query import MovieQuery

RootQuery = merge_types("Query", (MovieQuery,))
