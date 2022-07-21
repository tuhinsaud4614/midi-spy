import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from src.utils.prisma import prisma
from src.utils.graphql_context import get_context
from src.resolvers.root import RootQuery

# App
app = FastAPI()

@app.on_event("startup")
async def startup():
    await prisma.connect()


@app.on_event("shutdown")
async def shutdown():
    await prisma.disconnect()


schema = strawberry.Schema(RootQuery)
graphql_app = GraphQLRouter(schema, context_getter=get_context,)

app.include_router(graphql_app, prefix="/graphql")
