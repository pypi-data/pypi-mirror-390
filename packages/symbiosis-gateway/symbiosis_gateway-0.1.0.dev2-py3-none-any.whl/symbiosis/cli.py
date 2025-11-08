"""Symbiosis CLI module."""

from typing import Annotated
from typer import Typer, Option
import uvicorn

app = Typer(help="Symbiosis Gateway")


@app.command()
def serve(
    port: Annotated[int, Option(help="The port to bind the server to")] = 4321, 
    address: Annotated[str, Option(help="The address to bind the server to")] = "127.0.0.1",  # noqa: E501
) -> None:
    """Start the Symbiosis Gateway server.

    Parameters
    ----------
    port : int
        The port to bind the server to.
    address : str
        The address to bind the server to.
    """
    uvicorn.run("symbiosis.server:app", host=address, port=port, reload=True)


if __name__ == "__main__":
    app()
