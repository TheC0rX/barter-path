import asyncio
from loguru import logger

from src.services.stalcraft_api import StalcraftAPI
from src.db.models import Item, Recipe
from src.db.base import async_session_maker


class StalcraftUpdater:
    def __init__(self):
        self.api = StalcraftAPI()

    async def _fetch_and_parse_item(self, path: str):
        data = await self.api.fetch_json(path)
        if not data:
            return None

        return {
            "id": data["id"],
            "name_ru": data["name"]["lines"]["ru"],
            "name_en": data["name"]["lines"]["en"],
            "category": data.get("category", "unknown"),
        }

    async def update_all_data(self):
        paths = await self.api.get_items_tree()
        recipes_data = await self.api.fetch_json("global/barter_recipes.json")

        needed_ids = set()
        for loc in recipes_data:  # type: ignore
            for rec in loc.get("recipes", []):
                needed_ids.add(rec["item"])
                for offer in rec.get("offers", []):
                    for ing in offer.get("requiredItems", []):
                        needed_ids.add(ing["item"])

        tasks_paths = [
            p for p in paths if p.split("/")[-1].replace(".json", "") in needed_ids
        ]
        logger.info(f"Start loading {len(tasks_paths)} items...")

        parsed_items = []
        batch_size = 30
        for i in range(0, len(tasks_paths), batch_size):
            batch = tasks_paths[i : i + batch_size]
            results = await asyncio.gather(
                *[self._fetch_and_parse_item(p) for p in batch]
            )
            parsed_items.extend([r for r in results if r])
            logger.info(f"Loaded: {len(parsed_items)}/{len(tasks_paths)}")

        async with async_session_maker() as session:
            for item_data in parsed_items:
                await session.merge(Item(**item_data))

            logger.info("Updating data of recipes...")
            for loc in recipes_data:  # type: ignore
                for rec in loc.get("recipes", []):
                    target_id = rec["item"]
                    for offer in rec.get("offers", []):
                        for ing in offer.get("requiredItems", []):
                            await session.merge(
                                Recipe(
                                    item_id=target_id,
                                    ingredient_id=ing["item"],
                                    amount=ing["amount"],
                                )
                            )

            await session.commit()
            logger.success("Database was successfully updated.")


if __name__ == "__main__":
    stalcraftupdater = StalcraftUpdater()
    asyncio.run(stalcraftupdater.update_all_data())
