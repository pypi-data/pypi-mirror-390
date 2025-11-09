			       MASTO-MAILO-INATOR
			       ==================

1. WTF?

Masto-mailo-inator is a short program which fetches toots and stores them as
emails (Maildir format). They can then be read from the comfort of your email
client.

Official website: https://michal.sapka.pl/project/masto-mailo-inator

2. Installation

You can install masto-mailo-inator directly from PyPI:

```
pip install masto-mailo-inator
```

Or install from source:

```
git clone https://codeberg.org/mms/masto-mailo-inator.git
cd masto-mailo-inator
pip install .
```

3. Usage

After installation, you can use masto-mailo-inator from anywhere:

```
# First-time setup (configure authentication)
masto-mailo-inator setup

# Fetch and store new toots as emails
masto-mailo-inator get
```

You can also add `-V` or `--version` to check the version.

Refer to the official website for more info, including plans.
