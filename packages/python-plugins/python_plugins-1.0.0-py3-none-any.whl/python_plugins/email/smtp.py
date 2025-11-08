import smtplib
from email.message import EmailMessage
import mimetypes


class SmtpSSL:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def send_emsg(self, data):
        emsg = EmailMessage()
        emsg["Subject"] = data["subject"]
        emsg["From"] = data.get("From", self.user)
        emsg["To"] = data["to"]

        if "cc" in data:
            emsg["Cc"] = data["cc"]

        if "bcc" in data:
            emsg["Bcc"] = data["bcc"]

        # Check if HTML content is provided
        if "html_content" in data:
            emsg.add_alternative(data["html_content"], subtype="html")
        else:
            emsg.set_content(data["content"])

        # Add attachments if provided
        if "attachments" in data:
            for file_path in data["attachments"]:
                ctype, encoding = mimetypes.guess_type(file_path)
                if ctype is None or encoding is not None:
                    ctype = "application/octet-stream"
                maintype, subtype = ctype.split("/", 1)

                with open(file_path, "rb") as f:
                    emsg.add_attachment(
                        f.read(),
                        maintype=maintype,
                        subtype=subtype,
                        filename=file_path.split("\\")[-1],
                    )

        with smtplib.SMTP_SSL(self.host, self.port) as smtp:
            # smtp.set_debuglevel(1)
            smtp.login(self.user, self.password)
            senderrs = smtp.send_message(emsg)
        return senderrs
