import click
import beu


@click.command()
@click.option(
    '--mp3', '-m', 'mp3', is_flag=True, default=False,
    help='Convert downloaded to MP3 file'
)
@click.argument('url', nargs=1, default='')
def main(url, **kwargs):
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
        av_from_url_kwargs = {'playlist': True}
        if kwargs and kwargs.get('mp3') is True:
            av_from_url_kwargs.update({
                'audio_only': True,
                'mp3': True,
            })
        results = [
            beu.yh.av_from_url(
                x['link'],
                **av_from_url_kwargs
            ) for x in selected
        ]
        return results
