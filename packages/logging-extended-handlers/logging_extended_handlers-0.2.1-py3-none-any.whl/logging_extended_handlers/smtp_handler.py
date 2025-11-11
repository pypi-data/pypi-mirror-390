import logging
import logging.handlers
import smtplib
from collections import Counter
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import List, Optional


class BufferingSMTPHandler(logging.handlers.BufferingHandler):
    """Buffering logging handler which sends logs per mail.

    Email is sent when the flushing is triggered:
    through tear down, manually or exceeding of the buffer limit.

    If the flushing is triggered manually, an attachment can be added.

    :param mailhost: smtp host address
    :param fromaddr: sender mail address
    :param toaddrs: recipient mail addresses
    :param subject: mail subject
    :param capacity: number of log records to buffer, exceeding triggers flushing
    """

    def __init__(self, mailhost: str, fromaddr: str, toaddrs: List[str], subject: str, capacity: int = 999):
        logging.handlers.BufferingHandler.__init__(self, capacity=capacity)

        self.mailhost = mailhost
        self.fromaddr = fromaddr
        self.toaddrs = toaddrs
        self.subject = subject

    def flush(self, attachment_path: Optional[Path] = None):
        """Triggers the flushing. Sends all items in the buffer via smtp.

        Allows to attach a file to the email.

        :param attachment_path: (optional) Path to the attachment file
        """

        if len(self.buffer) > 0:
            msg = f"The following records of level {logging.getLevelName(self.level)} and above occured:\n"
            msg += self._compose_summary()

            for record in self.buffer:
                s = self.format(record)
                msg = msg + s + "\r\n"

            self._send_mail(msg, attachment_path)
            self.buffer = []

        elif len(self.buffer) == 0 and attachment_path is not None:
            msg = f"No records of level {logging.getLevelName(self.level)} and above"
            self._send_mail(msg, attachment_path)

    def _send_mail(self, msg_text: str, attachment_path: Optional[Path] = None):
        msg = MIMEMultipart()

        msg["Subject"] = self.subject
        msg["From"] = self.fromaddr
        msg["To"] = ";".join(self.toaddrs)

        if attachment_path:
            part = self._compose_attachment_part(attachment_path=attachment_path)
            msg.attach(part)

        msg.attach(MIMEText(msg_text))

        server = smtplib.SMTP(self.mailhost)
        server.send_message(msg)
        server.quit()

    def _compose_attachment_part(self, attachment_path: Path) -> MIMEBase:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment_path.open("rb").read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f'attachment; filename="{attachment_path.name!s}"',
        )
        return part

    def _compose_summary(self) -> str:
        """Counts the level type of all records in the buffer and composes a summary

        :return: number of captchured record levels like '[1x ERROR, 2x INFO, ...]'
        """

        levels = [record.levelname for record in self.buffer]
        counts = Counter(levels)

        summary_str = "["
        for lvl_type in counts:
            summary_str += f"{counts[lvl_type]}x {lvl_type}, "

        if not summary_str == "[":
            summary_str = summary_str[:-2]
            summary_str += "]\n\n"

        return summary_str
