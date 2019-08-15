"""Add an English label to TV episodes which have an English title but a missing label"""
import click
from pywikibot import Site, ItemPage

from sparql.queries import episodes_with_titles_and_missing_labels


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
    for episode_id, title, series_label in episodes_with_titles_and_missing_labels():
        print(f"{dry_str}Fixing {series_label}:{title} ({episode_id})")
        if not dry:
            episode_item = ItemPage(repo, episode_id)
            episode_item.get()
            episode_item.editLabels({"en": title})


if __name__ == "__main__":
    main()
