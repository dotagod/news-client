"""Pydantic models for API responses."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl

DEFAULT_LIMIT = 20


class NewsArticle(BaseModel):
    """A news article."""

    id: str = Field(..., description='Article ID')
    title: str = Field(..., description='Headline')
    description: str = Field(..., description='Article summary')
    url: HttpUrl = Field(..., description='Link to article')
    author: Optional[str] = Field(None, description='Author name')
    image: Optional[str] = Field(None, description='Image URL')
    language: str = Field(..., description='Language code')
    category: List[str] = Field(
        default_factory=list,
        description='Article topics',
    )
    published: datetime = Field(..., description='Publication date')

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }


class NewsResponse(BaseModel):
    """API response wrapper."""

    status: str = Field(..., description='Response status')
    news: List[NewsArticle] = Field(..., description='Articles list')

    @property
    def total_count(self) -> int:
        """Get article count.

        Returns:
            Number of articles in the response
        """
        return len(self.news)


class ErrorResponse(BaseModel):
    """Error response from API."""

    status: str = Field(..., description='Error status')
    message: str = Field(..., description='Error message')
    code: Optional[int] = Field(None, description='Error code')


class SearchParams(BaseModel):
    """Search request parameters."""

    keywords: str = Field(..., description='Search terms')
    language: str = Field(default='en', description='Language')
    limit: int = Field(default=DEFAULT_LIMIT, ge=1, le=100, description='Max results')
    domain: Optional[str] = Field(None, description='Domain filter')


class LatestNewsParams(BaseModel):
    """Latest news request parameters."""

    language: str = Field(default='en', description='Language')
    limit: int = Field(default=DEFAULT_LIMIT, ge=1, le=100, description='Max results')


class CategoryNewsParams(BaseModel):
    """Category news request parameters."""

    category: str = Field(..., description='News category')
    language: str = Field(default='en', description='Language')
    limit: int = Field(default=DEFAULT_LIMIT, ge=1, le=100, description='Max results')
