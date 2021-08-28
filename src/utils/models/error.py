from typing import Optional


class CrawlingError(Exception):
    message: str
    detail: Optional[str] = None

    def __init__(self, message: str, detail: Optional[str]) -> None:
        self.message = message
        self.detail = detail
        super().__init__(self.message)
