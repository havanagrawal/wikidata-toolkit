import click

import commands
from .click_utils import validate_item_id

@click.command()
@click.argument("tvshow_id", callback=validate_item_id)
@click.option("--child_type", type=click.Choice(["episode", "season", "series", "all"]), default="all")
@click.option("--autofix", is_flag=True, default=False, help="Fix constraint violations")
@click.option("--accumulate", is_flag=True, default=False, help="Accumulate all fixes before applying them")
@click.option("--interactive", is_flag=True, default=False, help="Prompt for confirmation before applying any fix")
@click.option("--filter", default="", help="Comma separated property names/tags to filter")
def check_tv_show(tvshow_id=None, child_type="all", autofix=False, accumulate=False, interactive=False, filter=""):
    commands.check_tv_show(tvshow_id, child_type, autofix=autofix, accumulate=accumulate, interactive=interactive, filter=filter)


if __name__ == "__main__":
    check_tv_show()
