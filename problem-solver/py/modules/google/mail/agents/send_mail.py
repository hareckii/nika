import logging
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from sc_client.models import ScAddr
from sc_kpm import ScKeynodes, ScResult
from sc_kpm.utils import (
    get_link_content_data,
    search_element_by_role_relation,
)
from sc_kpm.utils.action_utils import (
    finish_action_with_status,
    get_action_arguments,
)

from auth.models import User
from modules.google.mail.agents import MailAgent
from modules.google.mail.models import Mail
from secrets_env import GMAIL_PASS


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(message)s",
    datefmt="[%d-%b-%y %H:%M:%S]",
)


class SendMailAgent(MailAgent):
    def __init__(self):
        super().__init__("action_send_mail")
        self.rrel_contact_name = ScKeynodes.get("rrel_contact_name")
        self.rrel_contact_email = ScKeynodes.get("rrel_contact_email")
        self.rrel_mail = ScKeynodes.get("rrel_mail")

    def on_event(
        self,
        event_element: ScAddr,  # noqa: ARG002
        event_edge: ScAddr,  # noqa: ARG002
        action_element: ScAddr,
    ) -> ScResult:
        try:
            result = self.run(action_element)
            is_successful = result == ScResult.OK
            finish_action_with_status(action_element, is_successful)
            self.logger.info(
                "Finished %s",
                "successfully" if is_successful else "unsuccessfully",
            )
            return result
        except Exception as e:
            self.logger.error("Finished with error: %s", e)

    def run(self, action_node: ScAddr) -> ScResult:
        message_addr, self.author_node = get_action_arguments(
            action_node,
            2,
        )
        mail = self.get_mail(message_addr)
        if mail is None:
            self.logger.error("Did not get mail")
            return ScResult.ERROR
        res = self.send_mail(mail)
        if not res:
            return ScResult.ERROR
        return ScResult.OK

    def send_mail(self, mail: Mail):
        email_sender = mail.sender.email
        email_receiver = mail.receiver.email
        subject = mail.subject
        body = mail.body

        # Создание сообщения
        mail = MIMEMultipart()
        mail["From"] = email_sender
        mail["To"] = email_receiver
        mail["Subject"] = subject
        mail.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(email_sender, GMAIL_PASS)
                text = mail.as_string()
                server.sendmail(email_sender, email_receiver, text)
                self.logger.info("Send message")
            return True
        except Exception:
            self.logger.error("Got error with email sending")
            raise

    def get_mail(self, message_addr: ScAddr) -> Mail:
        contact: User | None = None
        mail_link = search_element_by_role_relation(
            message_addr,
            self.rrel_mail,
        )
        email_link = search_element_by_role_relation(
            message_addr,
            self.rrel_contact_email,
        )
        name_link = search_element_by_role_relation(
            message_addr,
            self.rrel_contact_name,
        )

        if name_link:
            contact = self.get_contact(name_link)

        if email_link:
            contact = User(
                name=" ",
                email=get_link_content_data(email_link),
            )
        if contact is None:
            return None

        return Mail(
            sender=self.get_author(),
            receiver=contact,
            body=get_link_content_data(mail_link),
        )