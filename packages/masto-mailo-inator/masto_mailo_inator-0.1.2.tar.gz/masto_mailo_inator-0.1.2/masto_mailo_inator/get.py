"""Get module for Masto-Mailo-Inator.

This module handles fetching toots from Mastodon and converting them
to email format for reading in an email client. It manages timelines,
content formatting, and maildir storage.
"""

# Standard library imports
import os
import re
import textwrap
from pathlib import Path
from typing import Tuple
from email import utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import formataddr
from html import unescape
# Third-party imports
import requests
from mastodon.return_types import Account, MediaAttachment, Status

# Local imports
from .setup import STATE_DIR, config, masto_instance


def get_last_id(directory):
    """Get the ID of the last processed toot from the specified directory.

    Args:
        directory: Directory containing the last_id file

    Returns:
        str: The ID of the last toot processed, or None if not found
    """
    file = Path(f"{directory}/last_id")
    if file.is_file():
        with open(file, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def store_last_id(directory, toot_id):
    """Store the ID of the last processed toot in the specified directory.

    Args:
        directory: Directory to store the last_id file in
        toot_id: ID of the last toot to remember
    """
    with open(f"{directory}/last_id", "w", encoding='utf-8') as f:
        f.write(toot_id)

# v 0.1.0 code
LINE_LENGTH=79

def toot_author(account: Account) -> str:
    """Format a Mastodon account as an email author.

    Args:
        account: Mastodon account object

    Returns:
        str: Formatted string with display name and address
    """
    username = account.display_name
    address = account.acct

    return formataddr((username, address))


def toot_to_txt(html) -> str:
    """Convert HTML toot content to plain text with line wrapping.
    Will convert HTML entites to utf-8.

    Args:
        html: HTML content of the toot

    Returns:
        str: Plain text version of the toot with line wrapping
    """
    raw = re.sub(r"<.*?>", "", html)
    return "\n".join(textwrap.wrap(text=unescape(raw),
                                   width=LINE_LENGTH,
                                   break_on_hyphens=False,
                                   break_long_words=False))

def file_and_ext_from_url(url: str) -> Tuple[str, str]:
    """Extract filename and extension from a URL.

    Args:
        url: URL to a file

    Returns:
        Tuple[str, str]: (filename, extension)
    """
    filename = url.split("/")[-1]
    parts = filename.split(".")
    if len(parts) >= 2:
        ext = parts[-1]
        name = ".".join(parts[:-1])
        return (name, ext)
    return (filename, "")

def media_attachment_as_txt(media_attachment: MediaAttachment) -> str:
    """Format a media attachment as text with alt text.

    Args:
        media_attachment: Mastodon media attachment object

    Returns:
        str: Formatted text description of the media with alt text
    """
    file, ext = file_and_ext_from_url(media_attachment.url)
    alt = (media_attachment.description
           if media_attachment.description
           else "<no alt text>")
    description = f"{file}.{ext}: {alt}"
    return "\n".join(textwrap.wrap(description, LINE_LENGTH))


def toot_as_txt_email(toot : Status) -> str:
    """Format a toot as plain text for email.

    Converts the HTML content to plain text and adds metadata
    like URL, visibility, and media attachments.

    Args:
        toot: Mastodon status object

    Returns:
        str: Formatted plain text email content
    """
    txt = toot_to_txt(toot.content)
    attachment_str = ""

    if toot.media_attachments:
        attachment_str = "\nATTACHMENTS:\n\n"
        for attachment in toot.media_attachments:
            attachment_str = (attachment_str +
                             media_attachment_as_txt(media_attachment=attachment) +
                             "\n\n")

    return f"""{txt}

-- 
URL: {toot.url}
VISIBILITY: {toot.visibility}
{attachment_str}
"""

def mail_filename(actor: Account, toot: Status) -> str:
    """Generate a unique filename for the email representation of a toot.

    Args:
        actor: Account viewing the toot
        toot: The toot to generate a filename for

    Returns:
        str: Unique filename for the email file
    """
    return f"toot.{actor.id}.{toot.account.id}.{toot.id}"

def create_toot_attachments(msg, toot):
    """Create plain text and HTML attachments for a toot.

    Adds both plain text and HTML versions of the toot to the email message.

    Args:
        msg: Email message to attach to
        toot: Toot to create attachments from

    Returns:
        str: The email subject derived from the toot content
    """
    html = toot.content
    txt = toot_as_txt_email(toot=toot)

    text_attachment = MIMEText(txt, 'plain')
    text_attachment.add_header('Content-Disposition', 'inline', filename='toot.txt')
    msg.attach(text_attachment)

    text_attachment = MIMEText(html, 'html')
    text_attachment.add_header('Content-Disposition', 'attachment', filename='toot.html')
    msg.attach(text_attachment)

    return txt.partition('\n')[0][:78]

def create_boost_attachments(msg, toot):
    """Create plain text and HTML attachments for a boosted toot.

    Formats the boosted toot with additional metadata like author and date,
    and attaches both plain text and HTML versions to the email message.

    Args:
        msg: Email message to attach to
        toot: Boosted toot to create attachments from

    Returns:
        str: The email subject derived from the boosted toot content
    """
    html = toot.content
    txt = toot_as_txt_email(toot=toot)
    boosted_txt = f'''---- BOOSTED TOOT ----
From: {toot_author(toot.account)}
Date: {utils.format_datetime(toot.created_at)}

{toot_as_txt_email(toot=toot)}
'''

    html_attachment = MIMEText(html, 'html', 'utf-8')
    html_attachment.add_header('Content-Disposition', 'attachment', filename='original_toot.html')
    msg.attach(html_attachment)

    text_attachment = MIMEText(boosted_txt, 'plain', 'utf-8')
    text_attachment.add_header('Content-Disposition', 'inline', filename='toot.txt')
    msg.attach(text_attachment)

    title = txt.partition('\n')[0][:72]
    return f"Boost: {title}"


def create_media_attachments(msg, media_attachments):
    """Download and attach media files to an email message.

    Args:
        msg: Email message to attach media to
        media_attachments: List of Mastodon media attachments to download and attach
    """
    for m in media_attachments:
        url = m.url
        content = requests.get(url, timeout=30).content
        filename = file_and_ext_from_url(url)

        attachment = MIMEImage(content)
        attachment.add_header(
                'Content-Disposition',
                'attachment', 
                filename=f'{filename[0]}.{filename[1]}')
        msg.attach(attachment)

def create_new_message(toot, folder):
    """Create an email message from a toot and save it to a maildir folder.

    Constructs a complete email message with headers, plain text and HTML versions
    of the toot content, and any media attachments. Handles both original and
    boosted toots.

    Args:
        toot: Mastodon status to convert to email
        folder: Directory path to save the email file in
    """
    msg = MIMEMultipart('Mixed')
    msg.preamble = 'You will not see this in a MIME-aware mail reader.\n'

    message_id = f"<{toot.id}>"
    msg.add_header('Message-Id', message_id)
    msg.add_header('From', toot_author(toot.account))
    msg.add_header('To', toot_author(masto_instance().me()))
    msg.add_header('Date', utils.format_datetime(toot.created_at))

    if toot.in_reply_to_id:
        msg.add_header('In-Reply-To', f"<{toot.in_reply_to_id}>")

    txt_msg = MIMEMultipart('Alternative')
    subject = ""
    if toot.reblog:
        subject = create_boost_attachments(msg=txt_msg, toot=toot.reblog)
    else:
        subject = create_toot_attachments(msg=txt_msg, toot=toot)

    msg.attach(txt_msg)

    msg['Subject'] = subject

    if toot.media_attachments:
        create_media_attachments(msg=msg, media_attachments=toot.media_attachments)

    with open(f"{folder}/{mail_filename(masto_instance().me(), toot)}", "w", encoding='utf-8') as f:
        f.write(msg.as_string())


def get_timeline(timeline):
    """Fetch toots from a timeline and save them as emails.

    Creates the necessary maildir structure, fetches toots from the specified
    timeline, converts them to emails, and stores them in the maildir. Tracks
    the last toot ID to avoid duplicates in future fetches.

    Args:
        timeline: Name of the timeline to fetch (home, public, tag/*)
    """
    maildir = config()["dir"]
    new_dir = Path(f"{maildir}/{timeline}/new")
    os.makedirs(new_dir, exist_ok=True)

    cur_dir = Path(f"{maildir}/{timeline}/cur")
    os.makedirs(cur_dir, exist_ok=True)

    timeline_config_dir = Path(f"{STATE_DIR}/{timeline}/")
    os.makedirs(timeline_config_dir, exist_ok=True)

    last_id = get_last_id(timeline_config_dir)
    toots = masto_instance().timeline(timeline=timeline, min_id=last_id, limit=20)

    for toot in toots:
        # TODO - deduplication  # pylint: disable=fixme
        create_new_message(toot=toot, folder=new_dir)
        if not get_last_id(timeline_config_dir) or get_last_id(timeline_config_dir) < toot.id:
            store_last_id(directory=timeline_config_dir, toot_id=toot.id)

    if masto_instance().get_pagination_info(page=toots, pagination_direction="next"):
        get_timeline(timeline)



def get():
    """Fetch toots from all configured timelines.

    Fetches toots from the home timeline and any followed hashtags,
    converting them to emails stored in the maildir.
    """
    get_timeline(timeline="home")
    for timeline in config()["followed_tags"]:
        get_timeline(timeline=f"tag/{timeline}")
