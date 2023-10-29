import json
from bs4 import BeautifulSoup
import requests
import concurrent.futures
import utils


class UpdateSectorMap:
    """
    A class for updating sector maps from NiftyIndices website.

    This class allows you to fetch sector data and store it in a JSON file.

    Attributes:
        base_url (str): The base URL of the NiftyIndices website.
        headers (dict): Headers to include in HTTP requests.

    Methods:
        _getResponse(url: str) -> str:
            Fetches an HTTP response from a given URL.

        _mapFile(endpoint: str) -> dict:
            Maps sector names to their corresponding URLs.

        _fetch_datafile(sector: str, url: str):
            Fetches data for a specific sector and saves it to the datafile dictionary.

        updateSector():
            Updates the sector map and saves it to a JSON file.
    """

    def __init__(self):
        self.base_url = "https://www.niftyindices.com"
        self.headers = {"User-Agent": "Mozilla/5.0"}

    @utils.retry(max_attempts=5, initial_delay=2, backoff_factor=3)
    def _getResponse(self, url):
        """
        Fetches an HTTP response from a given URL.

        Args:
            url (str): The URL to fetch data from.

        Returns:
            str: The response content as text.
        """
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(e)
            raise e

    def _mapFile(self, endpoint):
        """
        Maps sector names to their corresponding URLs.

        Args:
            endpoint (str): The endpoint of the NiftyIndices website to fetch data from.

        Returns:
            dict: A dictionary mapping sector names to their URLs.
        """
        url = f"{self.base_url}{endpoint}"
        response = self._getResponse(url)

        soup = BeautifulSoup(response, "html.parser")
        links = soup.select(".tabinsaidmenu li a")
        return {
            link.get_text(): f"https://www.niftyindices.com/{link.get('href')}"
            for link in links
        }

    def _fetch_datafile(self, sector, url):
        """
        Fetches data for a specific sector and saves it to the datafile dictionary.

        Args:
            sector (str): The name of the sector.
            url (str): The URL to fetch data from.
        """
        print(f"Fetching data for {sector} from {url}...")
        try:
            response = self._getResponse(url=url)
            soup = BeautifulSoup(response, "html.parser")
            links_with_index_constituent = soup.find_all("a", href=lambda href: href and "/IndexConstituent/" in href)

            for link in links_with_index_constituent:
                href = link.get("href")
                filename = href.split("/")[-1]
                self.datafile[sector.lower()] = filename

        except requests.exceptions.RequestException as e:
            raise e

    def updateSector(self):
        """
        Updates the sector map and saves it to a JSON file.
        """
        self.datafile = {}
        map_link = self._mapFile(endpoint="/indices/equity/")

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(self._fetch_datafile, sector, url): (sector, url) for sector, url in map_link.items()}

            concurrent.futures.wait(futures)

        with open("SectorMap.json", "w") as json_file:
            json.dump(self.datafile, json_file, indent=4)


if __name__ == "__main__":
    import time

    start_time = time.perf_counter()
    UpdateSectorMap().updateSector()
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")
