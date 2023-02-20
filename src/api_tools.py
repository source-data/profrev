from typing import List

from tenacity import retry, stop_after_attempt, wait_fixed
import requests


"""A module to use the Early Evidence Base API."""


class API:
    """An abstract class to represent an API."""
    def __init__(self) -> None:
        self.base_url = None

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def _get(self, endpoint: str) -> dict:
        """Send a GET request to the API.
        Args:
            endpoint: The API endpoint to send the request to.
        Returns:
            The response from the API.
        """
        url = self.base_url + endpoint
        response = requests.get(url)
        response.raise_for_status()
        return response.json()


class EEB(API):
    """A class to represent the Early Evidence Base API."""
    def __init__(self) -> None:
        self.base_url = 'https://eeb.embo.org/api/v1'


    def get_referee_reports(self, doi: str) -> List[str]:
        """Get the referee reports for an article from the Early Evidence Base API.
        Args:
            doi: The DOI of the article to get the referee reports for.
        Returns:
            The referee reports.
        """
        endpoint = f'/referee-reports/{doi}'
        response = self._get(endpoint)
        return response


class BioRxiv(API):
    """A class to represent the BioRxiv API."""

    def __init__(self) -> None:
         self.base_url = 'https://api.biorxiv.org'
    
    def get_preprint(self, doi: str) -> str:
        """Get the preprint full text from the BioRxiv API.
        Args:
            doi: The DOI of the article to get.
        Returns:
            The article.
        """
        endpoint = f'/details/biorxiv/{doi}'
        response = self._get(endpoint)
        return response['collection'][0]
