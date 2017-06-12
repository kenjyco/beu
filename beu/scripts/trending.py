import click
import beu


@click.command()
def main():
    """Select trending vids"""
    selected = beu.ih.make_selections(
        beu.ph.youtube_trending(),
        wrap=False,
        item_format='{duration} .::. {title} .::. {user} .::. {uploaded}',
    )
    if selected:
        results = [beu.yh.av_from_url(x['link']) for x in selected]
        return results
