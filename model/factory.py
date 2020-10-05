"""Factory class for generating high-level types from ItemPage instances"""

from pywikibot import ItemPage, Site

import model.api as api
from properties.wikidata_properties import (
    INSTANCE_OF,
    TELEVISION_SERIES,
    TELEVISION_SERIES_EPISODE,
    TELEVISION_SERIES_SEASON,
    ANIMATED_SERIES,
    BOARD_GAME
)

from .television import Episode, Season, Series
from .board_game import BoardGame

class Factory:
    """Factory for creating instances of the wrapper classes exposed by model"""

    def __init__(self, repo=None):
        if repo is None:
            repo = Site().data_repository()
        self.repo = repo

    def get_typed_item(self, item_id: str) -> api.BaseType:
        item_page = ItemPage(self.repo, item_id)
        item_page.get()
        if INSTANCE_OF.pid not in item_page.claims:
            raise ValueError(f"{item_id} has no 'instance of' property")

        claims = item_page.claims[INSTANCE_OF.pid]
        instance_ids = {claim.getTarget().id for claim in claims}
        if TELEVISION_SERIES_EPISODE in instance_ids:
            return Episode(item_page, self.repo)
        if TELEVISION_SERIES_SEASON in instance_ids:
            return Season(item_page, self.repo)
        if TELEVISION_SERIES in instance_ids or ANIMATED_SERIES in instance_ids:
            return Series(item_page, self.repo)
        if BOARD_GAME in instance_ids:
            return BoardGame(item_page, self.repo)

        raise ValueError(f"Unsupported item with instance QIDs {instance_ids}")
