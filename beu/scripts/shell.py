import click


@click.command()
@click.option(
    '--no-vi', 'no_vi', is_flag=True, default=False,
    help='Do not use vi editing mode in ipython'
)
@click.option(
    '--no-colors', 'no_colors', is_flag=True, default=False,
    help='Do not use colors / syntax highlighting in ipython'
)
@click.option(
    '--confirm-exit', 'confirm_exit', is_flag=True, default=False,
    help='Prompt "Do you really want to exit ([y]/n)?" when exiting ipython'
)
def main(**kwargs):
    """Start ipython with `beu` and `pprint` imported"""
    import beu
    from pprint import pprint
    beu.ih.start_ipython(
        colors=not kwargs['no_colors'],
        vi=not kwargs['no_vi'],
        confirm_exit=kwargs['confirm_exit'],
        beu=beu,
        pprint=pprint
    )


if __name__ == '__main__':
    main()
