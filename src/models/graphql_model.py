from datetime import datetime
import strawberry

@strawberry.type
class Movie:
    id: strawberry.ID
    title: str
    created_at: datetime
