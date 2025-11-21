"""
Database Schemas for Mechatronics Portfolio

Each Pydantic model represents a MongoDB collection. The collection name is the lowercase
of the class name (e.g., ContactMessage -> "contactmessage").

Only data that requires persistence is stored (e.g., contact messages). Static portfolio
content (projects, experience) is served by the API but not persisted by default.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List


class ContactMessage(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    subject: Optional[str] = Field(None, max_length=200)
    message: str = Field(..., min_length=10, max_length=5000)
    source: Optional[str] = Field(None, description="Where the message came from (web, mobile, etc.)")


class NewsletterSubscriber(BaseModel):
    email: EmailStr
    name: Optional[str] = Field(None, max_length=120)


class PortfolioVisit(BaseModel):
    path: str
    user_agent: Optional[str] = None
    referrer: Optional[str] = None


# Optional schemas if later we decide to persist projects/experience
class Project(BaseModel):
    title: str
    description: str
    tags: List[str] = []
    repo_url: Optional[str] = None
    live_url: Optional[str] = None
    image: Optional[str] = None
    featured: bool = False


class Experience(BaseModel):
    role: str
    organization: str
    start: str
    end: Optional[str] = "Present"
    summary: str
    highlights: List[str] = []
