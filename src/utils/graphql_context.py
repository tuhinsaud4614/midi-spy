from fastapi import Depends


from strawberry.fastapi import BaseContext
from prisma import Prisma
from .prisma import prisma


class CustomContext(BaseContext):
    def __init__(self, prisma_client: Prisma):
        self.prisma = prisma_client


def custom_context_dependency() -> CustomContext:
    return CustomContext(prisma)


async def get_context(
    custom_context=Depends(custom_context_dependency),
):
    return custom_context
