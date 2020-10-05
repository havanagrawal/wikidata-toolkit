import re
import click

WIKIDATA_ITEM_ID_PATTERN = re.compile(r"[Qq]\d+$")

def validate_item_id(ctx, param, item_id):
    if WIKIDATA_ITEM_ID_PATTERN.match(item_id) is None:
        raise click.BadParameter(f'item_id must be in the format Q###, found {item_id}')
    return item_id.upper()
