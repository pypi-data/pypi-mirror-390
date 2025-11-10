"""PyHive CLI entry point"""

import typer

from pyhive.src._generated_versions import SUPPORTED_API_VERSIONS

app = typer.Typer(help="PyHive CLI")


@app.command()
def versions():
    """Show supported Hive versions"""
    print("Supported Hive Versions:")
    for v in SUPPORTED_API_VERSIONS:
        print(v)


@app.command()
def versions2():
    """Show supported API versions"""
    for v in SUPPORTED_API_VERSIONS:
        print(v)


def main():
    """PyHive CLI main entry point"""
    app()


if __name__ == "__main__":
    main()
