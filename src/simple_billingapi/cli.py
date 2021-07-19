import click

from simple_billingapi import setup
from aiohttp import web

from simple_billingapi.web.routes import routes


@click.group()
def cli() -> None:
    setup()


@cli.command()
@click.option('--debug', is_flag=True)
@click.option('--host', type=str, default='127.0.0.1')
@click.option('--port', type=int, default=8000)
def serve(debug: bool, host: str, port: int) -> None:
    app = web.Application(debug=debug)
    app.add_routes(routes)
    web.run_app(app, host=host, port=port)
