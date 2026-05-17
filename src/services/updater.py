import asyncio
from loguru import logger

from sqlalchemy.ext.asyncio import AsyncSession

from src.services.stalcraft_api import StalcraftAPI
from src.db.models import Recipe
from src.db.base import async_session_maker
from src.db.repo import StalcraftRepo


class StalcraftUpdater:
    def __init__(self):
        self.api = StalcraftAPI()

    async def _fetch_and_parse_item(self, path: str, semaphore: asyncio.Semaphore):
        async with semaphore:
            try:
                data = await self.api.fetch_json(path)
                if not data:
                    return None

                name_data = data.get("name", {}).get("lines", {})
                return {
                    "id": data["id"],
                    "name_ru": name_data.get("ru", "Unknown"),
                    "name_en": name_data.get("en", "Unknown"),
                    "category": data.get("category", "unknown"),
                }
            except Exception as e:
                logger.error(
                    f"[bold magenta][UPDATER][/] Error fetching/parsing item from [red]{path}[/]: {e}"
                )
                return None

    async def update_all_data(self, session: AsyncSession):
        logger.info("[bold magenta][UPDATER][/] Updating items database...")

        paths = await self.api.get_items_tree()
        recipes_data = await self.api.fetch_json("global/barter_recipes.json")

        if not recipes_data:
            logger.error("[bold magenta][UPDATER][/] Failed to fetch barter recipes.")
            return

        barterable_ids = set()
        ingredient_ids = set()

        for location in recipes_data:  # type: ignore
            for rec in location.get("recipes", []):
                target_id = rec.get("item")
                if target_id:
                    barterable_ids.add(target_id)

                for offer in rec.get("offers", []):
                    currency_type = offer.get("currency")
                    if currency_type == "money" and offer.get("cost", 0) > 0:
                        ingredient_ids.add("money")

                    for ing in offer.get("requiredItems", []):
                        if ing.get("item"):
                            ingredient_ids.add(ing["item"])

        all_needed_ids = barterable_ids | ingredient_ids

        path_map = {p.split("/")[-1].replace(".json", ""): p for p in paths}
        tasks_paths = [path_map[i_id] for i_id in all_needed_ids if i_id in path_map]
        logger.success(
            f"[bold magenta][UPDATER][/] {len(ingredient_ids)} Resources and {len(barterable_ids)} Items were found."
        )
        logger.info(
            f"[bold magenta][UPDATER][/] Start downloading {len(tasks_paths)} items..."
        )

        CONCURRENCY_LIMIT = 40
        semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

        tasks = [self._fetch_and_parse_item(p, semaphore) for p in tasks_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        parsed_items: list[dict] = [res for res in results if isinstance(res, dict)]
        logger.success(
            f"[bold magenta][UPDATER][/] Successfully loaded {len(parsed_items)}/{len(tasks_paths)} items."
        )

        if "money" in ingredient_ids:
            parsed_items.append(
                {
                    "id": "money",
                    "name_ru": "Стоимость",
                    "name_en": "Cost",
                    "category": "currency",
                }
            )

        logger.info("[bold magenta][UPDATER][/] Updating data of items...")
        items_to_merge = []
        for item_data in parsed_items:
            item_data["is_barterable"] = item_data["id"] in barterable_ids
            items_to_merge.append(item_data)

        logger.info("[bold magenta][UPDATER][/] Updating data of recipes...")
        recipes_to_add = []
        seen_recipes = set()
        for location in recipes_data:  # type: ignore
            for rec in location.get("recipes", []):
                target_id = rec.get("item")
                if not target_id:
                    continue

                for offer_idx, offer in enumerate(rec.get("offers", [])):
                    currency_type = offer.get("currency")
                    cost_amount = offer.get("cost", 0)

                    if currency_type == "money" and cost_amount > 0:
                        recipe_key = (target_id, currency_type, offer_idx)
                        if recipe_key not in seen_recipes:
                            recipes_to_add.append(
                                Recipe(
                                    item_id=target_id,
                                    ingredient_id=currency_type,
                                    amount=cost_amount,
                                    offer_index=offer_idx,
                                )
                            )
                            seen_recipes.add(recipe_key)

                    for ing in offer.get("requiredItems", []):
                        ing_id = ing.get("item")
                        if not ing_id:
                            continue

                        recipe_key = (target_id, ing_id, offer_idx)
                        if recipe_key not in seen_recipes:
                            recipes_to_add.append(
                                Recipe(
                                    item_id=target_id,
                                    ingredient_id=ing_id,
                                    amount=ing.get("amount", 0),
                                    offer_index=offer_idx,
                                )
                            )
                            seen_recipes.add(recipe_key)

        repo = StalcraftRepo(session)
        await repo.update_items_and_recipes(items_to_merge, recipes_to_add)

    async def check_and_update(self):
        try:
            latest_sha = await self.api.get_latest_commit_sha()

            async with async_session_maker() as session:
                async with session.begin():
                    repo = StalcraftRepo(session)
                    current_sha = await repo.get_current_commit_sha()

                    if current_sha == latest_sha:
                        logger.success(
                            "[bold magenta][UPDATER][/] Database is up to date."
                        )
                        return

                    logger.warning(
                        f"[bold magenta][UPDATER][/] Update required. [bold yellow]{current_sha[:7] if current_sha else "NONE"}[/] -> [bold cyan]{latest_sha[:7]}[/]"
                    )

                    await self.update_all_data(session)
                    await repo.update_commit_sha(sha=latest_sha)

                    logger.success(
                        f"[bold magenta][UPDATER][/] Successfully updated to [bold cyan]{latest_sha[:7]}[/]"
                    )
        except Exception as e:
            logger.error(f"[bold magenta][UPDATER][/] Update failed: {e}")


async def main():
    updater = StalcraftUpdater()
    try:
        await updater.check_and_update()
    finally:
        await updater.api.close()


if __name__ == "__main__":
    asyncio.run(main())
