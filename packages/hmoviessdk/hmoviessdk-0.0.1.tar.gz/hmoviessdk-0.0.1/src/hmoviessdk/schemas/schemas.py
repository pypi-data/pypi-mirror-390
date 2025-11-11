from pydantic import BaseModel
from typing import Optional, List

# --- Second Schemas ---

class RatingBase(BaseModel):
    userId: int
    moviesId: int
    rating: float
    timestamp: int
    class Config:
        orm_mode = True
        

class TagBase(BaseModel):
    userId: int
    moviesId: int
    tag: str
    timestamp: int
    class Config:
        orm_mode = True
        
        
class LinkBase(BaseModel):
    imdbId: Optional[str]
    tmdbId: Optional[int]
    class Config:
        orm_mode = True
        
        
# --- Main Schema for Movies ---

class MovieBase(BaseModel):
    moviesId: int
    title: str
    genres: Optional[str] = None
    
    class Config:
        orm_mode = True
        
class MovieDetailed(MovieBase):
    moviesId: int
    ratings: List[RatingBase] = []
    tags: List[TagBase] = []
    links: Optional[LinkBase] = None
    
    class Config:
        orm_mode = True

# --- Schemas of list of movies without details ---

class MovieSimple(MovieBase):
    moviesId: int
    title: str
    genres: Optional[str]
    
    class Config: 
        orm_mode = True
        
#--- Schemas for the endpoints of ratings and tags ---

class RatingSimple(BaseModel):
    userId: int
    moviesId: int
    rating: float
    timestamp: int
    
    class Config:
        orm_mode = True
        
class TagSimple(BaseModel):
    userId: int
    moviesId: int
    tag: str
    timestamp: int
    
    class Config:
        orm_mode = True
        
class LinkSimple(BaseModel):
    moviesId: int
    imdbId: Optional[str]
    tmdbId: Optional[int]
    
    class Config:
        orm_mode = True
        
# --- Schemas for analytics response ---

class AnalyticsResponse(BaseModel):
    movie_count: int
    rating_count: int
    tag_count: int
    link_count: int
    
    class Config:
        orm_mode = True
        
