import os

from flask import Flask
from flask_migrate import Migrate, stamp, upgrade
from flask_sqlalchemy import SQLAlchemy

DATABASE_NAME = "rent_management.db"

db = SQLAlchemy()
migrate = Migrate()


def initialize_db(app: Flask, db_name_prefix=None):
    db_directory = os.path.dirname(__file__)

    db_file_name = DATABASE_NAME
    if db_name_prefix is not None:
        db_file_name = db_name_prefix + db_file_name

    db.db_path = os.path.join(db_directory, db_file_name)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db.db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Required for Flask-SqlAlchemy to detect models
    from ..models import Property, User

    db.init_app(app)

    migrations_directory = os.path.join(db_directory, "migrations")
    migrate.init_app(app, db, directory=migrations_directory)

    with app.app_context():
        if not os.path.exists(db.db_path):
            # db doesn't exist, creating it...
            db.create_all()
            stamp()
        else:
            # Upgrade the db to the latest schema
            upgrade()

    return db
