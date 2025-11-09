"""Test module for get.py functionality.

Contains unit tests for the functions in the get module that handle
Mastodon content processing and email generation.
"""

# pylint: disable=missing-function-docstring,missing-class-docstring,too-many-public-methods,line-too-long

# Standard library imports
import unittest

# Third-party imports
from mastodon.return_types import Account, Status, MediaAttachment, StatusMention

# Local imports
from .get import *  # pylint: disable=wildcard-import,unused-wildcard-import

class TestGet(unittest.TestCase):
    """Test case for the get module functionality."""

    def test_get_author(self):
        account = Account(display_name = "He Man", acct="heman@greyskull")
        assert toot_author(account=account) == 'He Man <heman@greyskull>'

    def test_mention_to_email_address(self):
        mention = StatusMention(url="http://duck.com",
                          username="JonDoe",
                          acct="johndoe@duck.com",
                          id=12321321)

        assert mention_to_email_address(mention=mention) == "JonDoe <johndoe@duck.com>"

    def test_calculate_to_for_public_post(self):
        toot = Status(visibility=PUBLIC_VISIBILITY)
        assert calculate_to(toot=toot) == UNDISCLOSED_RECIPIENTS

    def test_calculate_to_for_unlisted_post(self):
        toot = Status(visibility=UNLISTED_VISIBILITY)
        assert calculate_to(toot=toot) == UNDISCLOSED_RECIPIENTS

    def test_calculate_to_for_private_post(self):
        toot = Status(visibility=PRIVATE_VISIBILITY)
        assert calculate_to(toot=toot) == UNDISCLOSED_RECIPIENTS

    def test_calculate_to_for_direct_post(self):
        mention1 = StatusMention(url="http://duck.com",
                          username="JonDoe",
                          acct="johndoe@duck.com",
                          id=12321321)

        mention2 = StatusMention(url="http://duck.com",
                          username="JaneDoe",
                          acct="janedoe@duck.com",
                          id=12321321)
        toot = Status(visibility=DIRECT_VISIBILITY, mentions=[mention1, mention2])
        assert calculate_to(toot=toot) == "JonDoe <johndoe@duck.com>, JaneDoe <janedoe@duck.com>"


    def test_calculate_cc_for_public_post(self):
        mention1 = StatusMention(url="http://duck.com",
                          username="JonDoe",
                          acct="johndoe@duck.com",
                          id=12321321)

        mention2 = StatusMention(url="http://duck.com",
                          username="JaneDoe",
                          acct="janedoe@duck.com",
                          id=12321321)
        toot = Status(visibility=PUBLIC_VISIBILITY, mentions=[mention1, mention2])
        assert calculate_cc(toot=toot) == "JonDoe <johndoe@duck.com>, JaneDoe <janedoe@duck.com>"

    def test_calculate_cc_for_unlisted_post(self):
        mention1 = StatusMention(url="http://duck.com",
                          username="JonDoe",
                          acct="johndoe@duck.com",
                          id=12321321)

        mention2 = StatusMention(url="http://duck.com",
                          username="JaneDoe",
                          acct="janedoe@duck.com",
                          id=12321321)
        toot = Status(visibility=UNLISTED_VISIBILITY, mentions=[mention1, mention2])
        assert calculate_cc(toot=toot) == "JonDoe <johndoe@duck.com>, JaneDoe <janedoe@duck.com>"
    def test_calculate_cc_for_private_post(self):
        mention1 = StatusMention(url="http://duck.com",
                          username="JonDoe",
                          acct="johndoe@duck.com",
                          id=12321321)

        mention2 = StatusMention(url="http://duck.com",
                          username="JaneDoe",
                          acct="janedoe@duck.com",
                          id=12321321)
        toot = Status(visibility=PUBLIC_VISIBILITY, mentions=[mention1, mention2])
        assert calculate_cc(toot=toot) == "JonDoe <johndoe@duck.com>, JaneDoe <janedoe@duck.com>"

    def test_calculate_cc_for_direct_post(self):
        mention1 = StatusMention(url="http://duck.com",
                          username="JonDoe",
                          acct="johndoe@duck.com",
                          id=12321321)

        mention2 = StatusMention(url="http://duck.com",
                          username="JaneDoe",
                          acct="janedoe@duck.com",
                          id=12321321)
        toot = Status(visibility=DIRECT_VISIBILITY, mentions=[mention1, mention2])
        assert calculate_cc(toot=toot) is None

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
        assert title == "Boost: a toot"

        html_msg = msg.get_payload(0)
        html_content = html_msg.get_payload(decode=True)
        assert html_content == b'<b>a toot</b>'

        txt_msg = msg.get_payload(1)
        txt_content = txt_msg.get_payload(decode=True)
        assert txt_content == b'''---- BOOSTED TOOT ----
From: user <user@server>
Date: Mon, 03 Nov 2025 19:56:50 +0000

a toot

-- 
URL: http://url
VISIBILITY: None


'''
