import click
from pywikibot import Site, ItemPage

from bots import getbot
from click_utils import validate_item_id

@click.command()
@click.argument('item_ids', nargs=-1)
@click.option('--autofix', is_flag=True, default=False)
@click.option("--accumulate", is_flag=True, default=False, help="Accumulate all fixes before applying them")
@click.option("--filter", default="", help="Comma separated property names/tags to filter")
def validate_constraints(item_ids, autofix, accumulate, filter):
    item_ids = (validate_item_id(None, None, item_id) for item_id in item_ids)
    itempages = (ItemPage(Site(), item_id) for item_id in item_ids)
    bot = getbot(itempages, autofix=autofix, accumulate=accumulate, always=False, filter=filter)
    bot.run()

if __name__ == "__main__":
    validate_constraints()
