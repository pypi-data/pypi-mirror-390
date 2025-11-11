import os
from dotenv import load_dotenv

load_dotenv()

class MovieConfig:
    """
    Class for configuration that includes the SDK client parameters.
    
    Include the configuration base and progressively fallback URL. 
    """

    movie_base_url: str
    movie_backoff: bool
    movie_backoff_max_time: int

    def __init__(
        self,
        movie_base_url: str = None,
        backoff: bool = True,
        backoff_max_time: int = 30,
    ):
        """Building for the class configuration.

        Include initial values to override default settings.

        Args:
        movie_base_url (optional):
            The base URL to use for all API calls. Transmit it and set it up as an environment variable.
            
        movie_backoff:
            A boolean that determines if the SDK should attempt to call using a backoff when an error occurs.
            
        movie_backoff_max_time:
            The maximum number of seconds during which the SDK should continue attempting an API call before giving up.
        """

        self.movie_base_url = movie_base_url or os.getenv("MOVIE_API_BASE_URL")
        print(f"MOVIE_API_BASE_URL in MovieConfig init: {self.movie_base_url}")  

        if not self.movie_base_url:
            raise ValueError("The base URL is required. Set the environment variable MOVIE_API_BASE_URL.")

        self.movie_backoff = backoff
        self.movie_backoff_max_time = backoff_max_time

    def __str__(self):
        """ 
        Stringify function to return the content of the configuration object for logging"""
        return f"{self.movie_base_url} {self.movie_backoff} {self.movie_backoff_max_time}"