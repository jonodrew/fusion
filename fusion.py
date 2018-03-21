from app import create_app, db, cli
from app.matching.classes import Match
from app.models import User, Candidate, CohortLeader, SchemeLeader, Role
import click

app = create_app()
cli.register(app)


@app.cli.command()
@click.argument('name')
def print_name(name):
    """Prints a user's name"""
    print('Hello ' + name)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Candidate': Candidate, 'CohortLeader': CohortLeader, 'SchemeLeader': SchemeLeader, 'Role': Role,
            'Match': Match}


