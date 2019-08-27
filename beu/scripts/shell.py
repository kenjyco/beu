import click


@click.command()
@click.option(
    '--no-vi', 'no_vi', is_flag=True, default=False,
    help='Do not use vi editing mode'
)
@click.option(
    '--no-colors', 'no_colors', is_flag=True, default=False,
    help='Do not use colors / syntax highlighting'
)
def main(**kwargs):
    """Start ipython with `beu` and `pprint` imported"""
    import beu
    from pprint import pprint
    beu.ih.start_ipython(
        colors=not kwargs['no_colors'],
        vi=not kwargs['no_vi'],
        beu=beu,
        pprint=pprint
    )


if __name__ == '__main__':
    main()
