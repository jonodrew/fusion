from app import app, db
from app.models import User, Candidate
import click


@app.cli.command()
@click.argument('name')
def print_name(name):
    """Prints a user's name"""
    print('Hello ' + name)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Candidate': Candidate}
