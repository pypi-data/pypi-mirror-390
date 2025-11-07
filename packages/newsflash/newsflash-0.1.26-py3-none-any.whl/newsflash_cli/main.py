from pathlib import Path
import importlib
import sys
import secrets
import tomllib
import getpass

import click
from pydantic import BaseModel


class SecuritySettings(BaseModel):
    debug: bool = True
    secret_key: str = secrets.token_hex(32)
    allowed_hosts: list[str] = ["127.0.0.1", "localhost"]


class AppSettings(BaseModel):
    layout_dirs: list[str] = []


class NewsflashSettings(BaseModel):
    security: SecuritySettings = SecuritySettings()
    app: AppSettings = AppSettings()


def setup_django():
    from django.conf import settings
    from django.conf import global_settings
    from .settings import app_settings
    from django import setup

    newsflash_settings_path = Path.cwd() / "settings.toml"
    if newsflash_settings_path.exists():
        newsflash_settings = NewsflashSettings.model_validate(
            tomllib.loads((Path.cwd() / "settings.toml").read_text())
        )
    else:
        newsflash_settings = NewsflashSettings()

    app_settings["TEMPLATES"][0]["DIRS"] = newsflash_settings.app.layout_dirs

    settings.configure(
        default_settings=global_settings,
        **app_settings,
        DEBUG=newsflash_settings.security.debug,
        SECRET_KEY=newsflash_settings.security.secret_key,
        ALLOWED_HOSTS=newsflash_settings.security.allowed_hosts,
    )

    setup()


@click.command()
def add_user():
    setup_django()
    from django.contrib.auth.models import User

    username = input("Username: ")
    password = getpass.getpass()

    new_user = User.objects.create_user(
        username=username,
        password=password,
    )

    new_user.save()


@click.command()
@click.argument("object_reference")
def run(object_reference: str):
    setup_django()
    module_name, object_name = object_reference.split(":")

    if str(Path.cwd()) not in sys.path:
        sys.path.insert(0, str(Path.cwd()))

    module = importlib.import_module(module_name)

    try:
        app_object = getattr(module, object_name)
    except AttributeError:
        raise ImportError(f"object {object_name} not found in module {module_name}")

    app_object.run()


@click.command()
def setup():
    setup_django()
    from django.core.management import execute_from_command_line

    execute_from_command_line(["manage.py", "makemigrations"])
    execute_from_command_line(["manage.py", "migrate"])
    execute_from_command_line(["manage.py", "createcachetable"])


@click.group()
def cli():
    pass


def main():
    cli.add_command(run)
    cli.add_command(setup)
    cli.add_command(add_user)
    cli()
