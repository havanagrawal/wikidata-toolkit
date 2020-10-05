import constraints
import model.api as api
import properties.wikidata_properties as wp


class BoardGame(api.BaseType):
    @property
    def constraints(self):
        return [
            constraints.general.has_property(prop)
            for prop in [wp.INSTANCE_OF, wp.BOARD_GAME_GEEK_ID]
        ] + [constraints.board_game.has_english_label()]

