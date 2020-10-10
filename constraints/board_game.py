from typing import Iterable

import properties.wikidata_properties as wp
import constraints.api as api
import model.board_game
from utils import bgg_title


def has_english_label() -> api.Constraint:
    """Check if an item has an English label"""

    def check(item: model.board_game.BoardGame) -> bool:
        return item.label is not None

    def fix(item: model.television.TvBase) -> Iterable[api.LabelFix]:
        item.refresh()
        _src, _src_key = "Title", "en"
        label = item.label
        # Lookup BGG
        if label is None:
            bgg_id = item.first_claim(wp.BOARD_GAME_GEEK_ID.pid)
            label = bgg_title(bgg_id)
            _src, _src_key = "BGG", bgg_id
        if label is not None:
            return [api.LabelFix(label, "en", item.itempage)]
        return []

    return api.Constraint(check, fixer=fix, name="has_english_label()")