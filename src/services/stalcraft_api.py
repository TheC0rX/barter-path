import httpx

from src.config import config


class StalcraftAPI:
    def __init__(self):
        self.token = config.GITHUB_TOKEN.get_secret_value()

        self.owner = "EXBO-Studio"
        self.repo = "stalcraft-database"

        self.api_url = "https://api.github.com"
        self.raw_url = "https://raw.githubusercontent.com"

        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Barter-Path",
        }

    async def get_latest_commit_sha(self) -> str:
        url = f"{self.api_url}/repos/{self.owner}/{self.repo}/commits/main"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()["sha"]

    async def get_items_tree(self):
        url = (
            f"{self.api_url}/repos/{self.owner}/{self.repo}/git/trees/main?recursive=1"
        )
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()

            tree = response.json().get("tree", [])
            return [
                item["path"]
                for item in tree
                if item["path"].startswith("global/items/")
                and item["path"].endswith(".json")
            ]

    async def fetch_json(self, path: str):
        url = f"{self.raw_url}/{self.owner}/{self.repo}/main/{path.lstrip('/')}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers={"User-Agent": "Barter-Path"})
            if response.status_code == 200:
                return response.json()

            return None
