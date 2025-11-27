from pydantic import BaseModel, Field


class UrlInput(BaseModel):
    url: str = Field(description="The url to crawl.")
