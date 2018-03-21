import os
import click
from app import db
from app.models import Region

def register(app):
    @app.cli.group()
    def data_generate():
        """Data generation commands"""
        pass

    @data_generate.command()
    def generate_regions():
        """Generate regions data if it doesn't already exist"""
        if Region.query.count() < 4:
            regions = [Region(name='Wales'), Region(name='England'), Region(name='Scotland'), Region(name='London')]
            for r in regions:
                db.session.add(r)
            db.session.commit()