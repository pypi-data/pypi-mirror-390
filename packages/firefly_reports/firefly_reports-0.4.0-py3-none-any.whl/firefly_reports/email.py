import smtplib
import ssl
import traceback
from dataclasses import dataclass
from email.message import EmailMessage

import bs4


@dataclass
class Email:
    email_to: str
    email_from: str
    subject: str
    body: str
    smtp_server: str
    smtp_port: int
    smtp_starttls: bool
    smtp_user: str
    smtp_password: str
    smtp_authentication: bool

    def send_email(self):
        msg = EmailMessage()
        msg["Subject"] = self.subject
        msg["From"] = self.email_from
        msg["To"] = tuple(self.email_to)
        msg.set_content(
            bs4.BeautifulSoup(self.body, "html.parser").get_text()
        )  # just html to text
        msg.add_alternative(self.body, subtype="html")

        # Set up the SSL context for SMTP if necessary
        context = ssl.create_default_context()

        with smtplib.SMTP(host=self.smtp_server, port=self.smtp_port) as s:
            if self.smtp_starttls:
                s.ehlo()
                try:
                    s.starttls(context=context)
                except:
                    traceback.print_exc()
                    print("ERROR: could not connect to SMTP server with STARTTLS")
            if self.smtp_authentication:
                try:
                    s.login(user=self.smtp_user, password=self.smtp_password)
                except:
                    traceback.print_exc()
                    print("ERROR: could not authenticate with SMTP server.")
            s.send_message(msg)
