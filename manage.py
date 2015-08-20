#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

from flask_script import Manager, Shell, Server
from flask_migrate import MigrateCommand

from gakkgakk.app import create_app
from gakkgakk.models import User
from gakkgakk.settings import DevConfig, ProdConfig
from gakkgakk.database import db

reload(sys)
sys.setdefaultencoding('utf-8')

app = create_app(ProdConfig)

HERE = os.path.abspath(os.path.dirname(__file__))
TEST_PATH = os.path.join(HERE, 'tests')

manager = Manager(app)


def _make_context():
    """Return context dict for a shell session so you can access
    app, db, and the User model by default.
    """
    return {'app': app, 'db': db, 'User': User}


@manager.command
def test():
    """Run the tests."""
    import pytest
    exit_code = pytest.main([TEST_PATH, '--verbose'])
    return exit_code


manager.add_command('server', Server(host='0.0.0.0', threaded=True))
manager.add_command('shell', Shell(make_context=_make_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
