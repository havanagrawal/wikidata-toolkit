"""Add an English label on books which have an English title"""
import click
from pywikibot import Site, ItemPage, WbMonolingualText, Claim

import utils
from sparql.queries import board_games_with_missing_labels
import properties.wikidata_properties as wp


@click.command()
@click.option(
    "--dry",
    is_flag=True,
    default=False,
    help="Only print out the changes, don't run any commands",
)
def main(dry=False):
    dry_str = ""
    if dry:
        print("Running in dry-run mode, will not implement any changes")
        dry_str = "[DRY-RUN MODE] "
    repo = Site().data_repository()
    seen = set()
    for board_game_id, bgg_id in board_games_with_missing_labels():
        if board_game_id in seen:
            continue
        seen.add(board_game_id)
        board_game_name = utils.bgg_title(bgg_id)
        if board_game_name is None:
            print(f"Unable to fetch name for {board_game_id}.")
            continue
        wiki_url = f"https://www.wikidata.org/wiki/{board_game_id}"
        print(f"{dry_str}Setting label='{board_game_name}' for {board_game_id} ( {wiki_url} )")
        if not dry:
            bg_item = ItemPage(repo, board_game_id)
            bg_item.get()
            bg_item.editLabels({"en": board_game_name})


if __name__ == "__main__":
    main()
