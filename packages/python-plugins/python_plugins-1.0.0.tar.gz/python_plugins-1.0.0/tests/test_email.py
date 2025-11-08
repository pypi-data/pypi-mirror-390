import os.path as op
import pytest
from python_plugins.email import SmtpSSL

@pytest.mark.skip(reason="test ok")
def test_send_content():
    host = "smtp.qiye.aliyun.com"
    port = "465"
    user = "test@ojso.com"
    password = "gTk94GEeNvujr4zm"

    to = "test@ojso.com"
    data = {
        "to": to,
        "subject": "test send content",
        "content": "This is a plain text email.",
    }

    s = SmtpSSL(host, port, user, password)
    r = s.send_emsg(data)

    assert not r

@pytest.mark.skip(reason="test ok")
def test_send_html():
    host = "smtp.qiye.aliyun.com"
    port = "465"
    user = "test@ojso.com"
    password = "gTk94GEeNvujr4zm"

    to = "test@ojso.com"
    html_content = """
<html>
  <body>
    <h1>This is a HTML email.</h1>
    <p>You can use <strong>HTML</strong> format!</p>
    <p><a href="https://www.example.com">Click here to access the sample website</a></p>
  </body>
</html>
"""

    data = {
        "to": to,
        "subject": "test send html",
        "html_content": html_content,
    }

    s = SmtpSSL(host, port, user, password)
    r = s.send_emsg(data)

    assert not r

@pytest.mark.skip(reason="test ok")
def test_send_attach():
    host = "smtp.qiye.aliyun.com"
    port = "465"
    user = "test@ojso.com"
    password = "gTk94GEeNvujr4zm"

    to = "test@ojso.com"
    html_content = """
<html>
  <body>
    <h1>This a HTML email with attach</h1>
    <p>have a look at attach</p>
  </body>
</html>
"""
    parent_dir = op.realpath(op.dirname(__file__))
    attach_path_1 = op.join(parent_dir, "tmp","a.txt")
    attach_path_2 = op.join(parent_dir, "tmp","a.png")
    
    data = {
        "to": to,
        "subject": "test send attach",
        "html_content": html_content,
        "attachments": [attach_path_1, attach_path_2],
    }

    s = SmtpSSL(host, port, user, password)
    r = s.send_emsg(data)

    assert not r