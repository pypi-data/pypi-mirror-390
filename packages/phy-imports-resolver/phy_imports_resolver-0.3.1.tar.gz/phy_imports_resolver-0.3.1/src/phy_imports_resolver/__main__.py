""" expose module entry as cli """
from phy_imports_resolver.cli import cli_app

if __name__ == '__main__':
    # this is click command; pylint: disable=no-value-for-parameter
    cli_app()
