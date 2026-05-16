import httpx

from src.config import config


class StalcraftAPI:
    def __init__(self):
        self.token = config.GITHUB_TOKEN.get_secret_value()

        self.owner = "EXBO-Studio"
        self.repo = "stalcraft-database"

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Barter-Path",
        }

        self.client = httpx.AsyncClient(
            base_url="https://api.github.com",
            headers=self.headers,
            http2=True,
        )
        self.raw_client = httpx.AsyncClient(
            base_url="https://raw.githubusercontent.com",
            headers={"User-Agent": "Barter-Path"},
            http2=True,
        )

    async def get_latest_commit_sha(self) -> str:
        url = f"/repos/{self.owner}/{self.repo}/commits/main"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()["sha"]

    async def get_items_tree(self):
        url = f"/repos/{self.owner}/{self.repo}/git/trees/main?recursive=1"
        response = await self.client.get(url)
        response.raise_for_status()

        tree = response.json().get("tree", [])
        return [
            item["path"]
            for item in tree
            if item["path"].startswith("global/items/")
            and item["path"].endswith(".json")
        ]

    async def fetch_json(self, path: str):
        url = f"/{self.owner}/{self.repo}/main/{path.lstrip('/')}"
        response = await self.raw_client.get(url)
        if response.status_code == 200:
            return response.json()
        return None
