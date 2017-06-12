import click
import beu


@click.command()
@click.argument('url', nargs=1, default='')
def main(url):
    """Find and download vids related to vid url"""
    url = url or beu.ih.user_input('vid url')
    if not url:
        return

    selected = beu.ih.make_selections(
        beu.ph.youtube_related_to(url),
        wrap=False,
        item_format='{duration} .::. {title} .::. {user}',
    )
    if selected:
        results = [beu.yh.av_from_url(x['link'], playlist=True) for x in selected]
        return results
