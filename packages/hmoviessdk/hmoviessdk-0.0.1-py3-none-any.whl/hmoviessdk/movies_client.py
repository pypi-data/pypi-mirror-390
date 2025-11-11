import httpx
from typing import Optional, List, Literal, Union
from .schemas import MovieSimple, MovieDetailed, RatingSimple, TagSimple, LinkSimple, AnalyticsResponse
from .movies_config import MovieConfig
import pandas as pd


class MovieClient:
    def __init__(self, config: Optional[MovieConfig] = None):
        # Initialize the client with a given configuration or a default one
        self.config = config or MovieConfig()
        self.movie_base_url = self.config.movie_base_url

    def _format_output(self, data, model, output_format: Literal["pydantic", "dict", "pandas"]):
        # Helper method to convert API responses into different formats:
        # - "pydantic": a list of validated model instances
        # - "dict": a list of raw dictionaries
        # - "pandas": a DataFrame for data analysis
        if output_format == "pydantic":
            return [model(**item) for item in data]
        elif output_format == "dict":
            return data
        elif output_format == "pandas":
            return pd.DataFrame(data)
        else:
            raise ValueError("Invalid output_format. Choose from 'pydantic', 'dict', or 'pandas'.")

    def health_check(self) -> dict:
        # Check if the API server is up and responding
        url = f"{self.movie_base_url}/"
        response = httpx.get(url)
        response.raise_for_status()
        return response.json()

    def get_movie(self, movies_Id: int) -> MovieDetailed:
        # Retrieve detailed information for a specific movie by ID
        url = f"{self.movie_base_url}/movies/{movies_Id}"
        response = httpx.get(url)
        response.raise_for_status()
        return MovieDetailed(**response.json())

    def list_movies(
        self,
        skip: int = 0,
        limit: int = 100,
        title: Optional[str] = None,
        genre: Optional[str] = None,
        output_format: Literal["pydantic", "dict", "pandas"] = "pydantic"
    ) -> Union[List[MovieSimple], List[dict], "pd.DataFrame"]:
        # Retrieve a list of movies with optional filters (title, genre) and pagination
        url = f"{self.movie_base_url}/movies"
        params = {"skip": skip, "limit": limit}
        if title:
            params["title"] = title
        if genre:
            params["genre"] = genre
        response = httpx.get(url, params=params)
        response.raise_for_status()
        return self._format_output(response.json(), MovieSimple, output_format)

    def get_rating(self, user_Id: int, movies_Id: int) -> RatingSimple:
        # Retrieve a specific user's rating for a specific movie
        url = f"{self.movie_base_url}/ratings/{user_Id}/{movies_Id}"
        response = httpx.get(url)
        response.raise_for_status()
        return RatingSimple(**response.json())

    def list_ratings(
        self,
        skip: int = 0,
        limit: int = 100,
        movies_Id: Optional[int] = None,
        user_Id: Optional[int] = None,
        min_rating: Optional[float] = None,
        output_format: Literal["pydantic", "dict", "pandas"] = "pydantic"
    ) -> Union[List[RatingSimple], List[dict], "pd.DataFrame"]:
        # Retrieve a list of ratings with optional filters (movies_Id, user_Id, min_rating)
        url = f"{self.movie_base_url}/ratings"
        params = {"skip": skip, "limit": limit}
        if movies_Id:
            params["movies_Id"] = movies_Id
        if user_Id:
            params["user_Id"] = user_Id
        if min_rating:
            params["min_rating"] = min_rating
        response = httpx.get(url, params=params)
        response.raise_for_status()
        return self._format_output(response.json(), RatingSimple, output_format)

    def get_tag(self, user_Id: int, movies_Id: int, tag_text: str) -> TagSimple:
        # Retrieve a specific tag associated with a user and movie
        url = f"{self.movie_base_url}/tags/{user_Id}/{movies_Id}/{tag_text}"
        response = httpx.get(url)
        response.raise_for_status()
        return TagSimple(**response.json())

    def list_tags(
        self,
        skip: int = 0,
        limit: int = 100,
        movies_Id: Optional[int] = None,
        user_Id: Optional[int] = None,
        output_format: Literal["pydantic", "dict", "pandas"] = "pydantic"
    ) -> Union[List[TagSimple], List[dict], "pd.DataFrame"]:
        # Retrieve a list of tags with optional filters (movies_Id, user_Id)
        url = f"{self.movie_base_url}/tags"
        params = {"skip": skip, "limit": limit}
        if movies_Id:
            params["movies_Id"] = movies_Id
        if user_Id:
            params["user_Id"] = user_Id
        response = httpx.get(url, params=params)
        response.raise_for_status()
        return self._format_output(response.json(), TagSimple, output_format)

    def get_link(self, movies_Id: int) -> LinkSimple:
        # Retrieve external link information for a specific movie
        url = f"{self.movie_base_url}/links/{movies_Id}"
        response = httpx.get(url)
        response.raise_for_status()
        return LinkSimple(**response.json())

    def list_links(
        self,
        skip: int = 0,
        limit: int = 100,
        output_format: Literal["pydantic", "dict", "pandas"] = "pydantic"
    ) -> Union[List[LinkSimple], List[dict], "pd.DataFrame"]:
        # Retrieve a list of links for multiple movies with pagination
        url = f"{self.movie_base_url}/links"
        params = {"skip": skip, "limit": limit}
        response = httpx.get(url, params=params)
        response.raise_for_status()
        return self._format_output(response.json(), LinkSimple, output_format)

    def get_analytics(self) -> AnalyticsResponse:
        # Retrieve global analytics or statistical data from the API
        url = f"{self.movie_base_url}/analytics"
        response = httpx.get(url)
        response.raise_for_status()
        return AnalyticsResponse(**response.json())
