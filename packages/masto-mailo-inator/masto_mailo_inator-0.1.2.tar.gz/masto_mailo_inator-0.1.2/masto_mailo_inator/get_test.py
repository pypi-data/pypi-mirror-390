"""Test module for get.py functionality.

Contains unit tests for the functions in the get module that handle
Mastodon content processing and email generation.
"""

# pylint: disable=missing-function-docstring,missing-class-docstring

# Standard library imports
import unittest

# Third-party imports
from mastodon.return_types import Account, Status, MediaAttachment

# Local imports
from .get import *  # pylint: disable=wildcard-import,unused-wildcard-import

class TestGet(unittest.TestCase):
    """Test case for the get module functionality."""

    def test_get_author(self):
        account = Account(display_name = "He Man", acct="heman@greyskull")
        assert toot_author(account=account) == 'He Man <heman@greyskull>'

    def test_toot_to_html(self):
        html = """<p>fasfafasfafdsaa
</p> fasdfasdlkfjasdjflkasdjfklsadjlkfjasdlkfjlkasdjflk;asjflk;asdj flksadlkfasdlkflkasdjfasfasdfasd"""  # pylint: disable=line-too-long

        assert toot_to_txt(html=html) == """fasfafasfafdsaa  fasdfasdlkfjasdjflkasdjfklsadjlkfjasdlkfjlkasdjflk;asjflk;asdj
flksadlkfasdlkflkasdjfasfasdfasd"""  # pylint: disable=line-too-long

    def test_toot_to_html_with_html_entities(self):
        html = "&nbsp;&amp;"

        assert toot_to_txt(html=html) == '\xa0&'

    def test_toot_to_html_with_long_url(self):
        original = "https://fasfasdf.sad.fsad.ffasdfsad/fasd/af/asdf/asd/fsad/fsad4fasd/fsdafas/fasfasdfasdfasd.fasfasdfas"

        assert toot_to_txt(html=original) == original

    def test_toot_to_html_with_long_url_with_hyphens(self):
        original = "https://fasfasdf.sad.fsad.ffasdfsad/fasd/af/asdf/asd/f-sad/fsad4fasd/fsdafas/fa-sfasdfasdfasd.fasfasdfas"

        assert toot_to_txt(html=original) == original

    def test_file_and_ext_from_url(self):
        assert file_and_ext_from_url("https://michal.sapka.pl/logo.png") == ("logo", "png")

    def test_txt_media_attachment_as_txt(self):
        attachment = MediaAttachment(
            url="http://michal.sapka.pl/logo.png",
            description="A very very very very very very very very very long long long long long long long description"  # pylint: disable=line-too-long
        )
        assert media_attachment_as_txt(media_attachment=attachment) == """logo.png: A very very very very very very very very very long long long long
long long long description"""  # pylint: disable=line-too-long

    def test_txt_media_attachment_as_txt_without_description(self):
        attachment = MediaAttachment(url="http://michal.sapka.pl/logo.png")
        assert media_attachment_as_txt(media_attachment=attachment) == "logo.png: <no alt text>"

    def test_toot_as_txt_email(self):
        attachment1 = MediaAttachment(
                url="http://michal.sapka.pl/logo1.png",
                description="An image")
        attachment2 = MediaAttachment(
                url="http://michal.sapka.pl/logo2.png",
                description="A different image")
        toot = Status(
            content="text",
            url="https://masto",
            visibility="PUBLIC",
            media_attachments=[attachment1, attachment2]
        )

        assert toot_as_txt_email(toot=toot) == """text

-- 
URL: https://masto
VISIBILITY: PUBLIC

ATTACHMENTS:

logo1.png: An image

logo2.png: A different image


"""

    def test_mail_filename(self):
        actor = Account(id=666)
        user = Account(id=44)
        toot = Status(account=user, id=888)

        assert mail_filename(actor=actor, toot=toot) == "toot.666.44.888"

    def test_create_toot_attachments_attaches_to_msg(self):
        msg = MIMEMultipart('Mixed')
        toot = Status(content="<b>a toot</b>")

        title = create_toot_attachments(toot=toot, msg=msg)

        self.assertIn('''Content-Disposition: inline; filename="toot.txt"

a toot''', msg.as_string())

        self.assertIn('''Content-Disposition: attachment; filename="toot.html"

<b>a toot</b>''', msg.as_string())

        self.assertEqual(title, "a toot")

    def test_create_boost_attachments_attaches_to_msg(self):
        msg = MIMEMultipart('Mixed')
        account = Account(display_name="user", acct="user@server")
        toot = Status(
            url="http://url",
            content="<b>a toot</b>",
            account=account,
            created_at="2025-11-03T19:56:50.353Z"
        )

        title = create_boost_attachments(toot=toot, msg=msg)

        print(msg)
        self.assertIn('''Content-Disposition: inline; filename="toot.txt"

---- BOOSTED TOOT ----
From: user <user@server>
Date: Mon, 03 Nov 2025 19:56:50 +0000

a toot''', msg.as_string())

        self.assertIn('''Content-Disposition: attachment; filename="original_toot.html"

<b>a toot</b>''', msg.as_string())

        self.assertEqual(title, "Boost: a toot")
