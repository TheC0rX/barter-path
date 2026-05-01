import asyncio
from loguru import logger

from sqlalchemy import delete

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

        name_ru = data["name"]["lines"]["ru"]
        name_en = data["name"]["lines"]["en"]

        return {
            "id": data["id"],
            "name_ru": name_ru,
            "name_en": name_en,
            "category": data.get("category", "unknown"),
        }

    async def update_all_data(self):
        logger.info("Updating items database...")

        paths = await self.api.get_items_tree()
        recipes_data = await self.api.fetch_json("global/barter_recipes.json")

        barterable_ids = set()
        ingredient_ids = set()

        for location in recipes_data:  # type: ignore
            for rec in location.get("recipes", []):
                target_id = rec["item"]
                barterable_ids.add(target_id)

                for offer in rec.get("offers", []):
                    for ing in offer.get("requiredItems", []):
                        ingredient_ids.add(ing["item"])

        all_needed_ids = barterable_ids | ingredient_ids

        path_map = {p.split("/")[-1].replace(".json", ""): p for p in paths}
        tasks_paths = [path_map[i_id] for i_id in all_needed_ids if i_id in path_map]
        logger.info(
            f"Items to download: {len(all_needed_ids)}\nResources: {len(ingredient_ids)} | Items: {len(barterable_ids)}"
        )

        logger.info(f"Start downloading {len(tasks_paths)} items...")

        parsed_items = []
        batch_size = 35
        for i in range(0, len(tasks_paths), batch_size):
            batch = tasks_paths[i : i + batch_size]
            results = await asyncio.gather(
                *[self._fetch_and_parse_item(p) for p in batch]
            )
            parsed_items.extend([r for r in results if r])
            logger.info(f"Loaded: {len(parsed_items)}/{len(tasks_paths)}")

        async with async_session_maker() as session:
            logger.info("Deleting old recipes...")
            await session.execute(delete(Recipe))

            logger.info("Updating data of items...")
            for item_data in parsed_items:
                item_id = item_data["id"]
                is_goal = item_id in barterable_ids
                await session.merge(Item(**item_data, is_barterable=is_goal))

            logger.info("Updating data of recipes...")
            for location in recipes_data:  # type: ignore
                for rec in location.get("recipes", []):
                    target_id = rec["item"]

                    for offer_idx, offer in enumerate(rec.get("offers", [])):
                        for ing in offer.get("requiredItems", []):
                            session.add(
                                Recipe(
                                    item_id=target_id,
                                    ingredient_id=ing["item"],
                                    amount=ing["amount"],
                                    offer_index=offer_idx,
                                )
                            )

            await session.commit()
            logger.success("Database was successfully updated.")


if __name__ == "__main__":
    stalcraftupdater = StalcraftUpdater()
    asyncio.run(stalcraftupdater.update_all_data())
