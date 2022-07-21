from typing import Tuple
import strawberry
from strawberry.types import Info
from prisma import Prisma

from ...models.graphql_model import Movie


@strawberry.type
class MovieQuery:
    @strawberry.field
    async def movies(self, info: Info) -> list[Movie]:
        client: Prisma = info.context.prisma
        res = await client.movie.find_many()
        print(res)
        return res
