import click
from properties.wikidata_item import WikidataItemId

class WikidataItemIdType(click.ParamType):
    """Validation class for Wikidata Item IDs such as Q65604139"""
    def convert(self, value, param, ctx):
        item_id = None
        try:
            return str(WikidataItemId(value))
        except ValueError as e:
            self.fail(str(e), param, ctx)

WIKIDATA_ITEM_ID_TYPE = WikidataItemIdType()
