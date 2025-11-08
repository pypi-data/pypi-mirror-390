"""Setup module for Masto-Mailo-Inator.

This module handles configuration loading, Mastodon instance setup,
and authentication required for accessing the Mastodon API.
"""

import os
import tomllib
import importlib.resources
from pathlib import Path
from mastodon import Mastodon

CONFIG_DIR = f'{os.path.expanduser("~")}/.config/masto-mailo-inator'
STATE_DIR = f'{os.path.expanduser("~")}/.local/state/masto-mailo-inator'
CONFIG_FILE = f'{CONFIG_DIR}/config.toml'
SECRET_FILE = f'{STATE_DIR}/oauth'
CLIENT_SECRET = f'{STATE_DIR}/client'

def config():
    """Load and return the application configuration.

    Ensures the configuration file exists before loading.

    Returns:
        dict: The application configuration data.
    """
    ensure_config()
    with open(CONFIG_FILE, "rb") as f:
        data = tomllib.load(f)
    return data

def ensure_config():
    """Ensure the config file exists, creating it if necessary.

    Creates the config directory and copies the default configuration
    file if it doesn't exist.
    """
    file = Path(CONFIG_FILE)
    if not file.is_file():
        os.makedirs(CONFIG_DIR, exist_ok=True)
        # Get the default config from the installed package
        package_path = importlib.resources.files('masto_mailo_inator')
        default_config = package_path / 'default_config.toml'
        with open(default_config, 'rb') as src, open(CONFIG_FILE, 'wb') as dst:
            dst.write(src.read())

        print(f"Config file created. Open {CONFIG_FILE} and add details")

def masto_instance():
    """Create and return an authenticated Mastodon API instance.

    Returns:
        Mastodon: An authenticated Mastodon API client.
    """
    return Mastodon(access_token = SECRET_FILE)

def ensure_auth():
    """Ensure authentication to Mastodon is set up.

    Creates application credentials and user authentication tokens
    if they don't exist. Guides the user through the authentication
    process and sends a test toot to verify everything works.
    """
    auth_file = Path(SECRET_FILE)
    if not auth_file.is_file():
        print(f"Your configured instance: {config().get('instance')}")
        print("Press RETURN key to continue or CTRL-C and start over.")
        input()

    client_file = Path(CLIENT_SECRET)
    if not client_file.is_file():
        os.makedirs(STATE_DIR, exist_ok=True)
        Mastodon.create_app(
                'masto-mailo-inator',
                api_base_url = config().get('instance'),
                to_file = CLIENT_SECRET
                )

    if not auth_file.is_file():
        mastodon = Mastodon(client_id = CLIENT_SECRET,)
        print("You need to allow masto-mailo-inator")
        print(mastodon.auth_request_url())
        mastodon.log_in(
            code=input("Enter the OAuth authorization code: "),
            to_file=SECRET_FILE
            )


    print("Everything seems to be set up correctly.")
    print(f"Instance: {config().get('instance')}")
    print(f"Maildir: {config().get('dir')}")
    print(f"Followed tags: {config().get('followed_tags')}\n")

    print("Press RETURN to send test toot, or Ctrl-C to exit")
    input()

    masto_instance().status_post(status="I'm using masto-mailo-inator!\n#masto_mailo_inator")


def setup():
    """Run the full setup process.

    Ensures configuration exists and authentication is set up.
    """
    config()
    ensure_auth()
