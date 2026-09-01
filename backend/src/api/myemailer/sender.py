import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib
from pathlib import Path
from string import Template
from typing import Iterable, Union

EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_HOST = os.environ.get("EMAIL_HOST") or "smtp.gmail.com"
EMAIL_PORT = os.environ.get("EMAIL_PORT") or "587"


def _coerce_attachment_paths(
    attachment_path: Union[str, Path, Iterable[Union[str, Path]], None]
) -> list[Path]:
    if attachment_path is None:
        return []

    if isinstance(attachment_path, (str, os.PathLike)):
        paths = [attachment_path]
    else:
        paths = list(attachment_path)

    return [Path(path) for path in paths if path]


def _build_image_attachment(file_path: Path) -> MIMEImage:
    suffix = file_path.suffix.lower()
    subtypes = {
        ".png": "png",
        ".jpg": "jpeg",
        ".jpeg": "jpeg",
        ".gif": "gif",
        ".webp": "webp",
        ".bmp": "bmp",
    }

    subtype = subtypes.get(suffix, "png")
    image_data = file_path.read_bytes()
    attachment = MIMEImage(image_data, _subtype=subtype)
    attachment.add_header("Content-Disposition", "attachment", filename=file_path.name)
    return attachment


def send_mail(to_email: str = "motwanij63@gmail.com",
              from_email: str = EMAIL_ADDRESS,
              subject: str = "No subject provided",
              content: str = "No Content Provided",
              attachment_path: Union[str, Path, Iterable[Union[str, Path]], None] = None
              ):
    template_path = Path(__file__).parent / "template.html"
    template = Template(template_path.read_text())

    message = MIMEMultipart()
    message["from"] = from_email
    message["to"] = to_email
    message["subject"] = subject

    content_html = content.replace("\n", "<br>\n")
    body = template.safe_substitute({
        "title": subject,
        "content": content_html,
    })

    message.attach(MIMEText(body, "html"))

    for file_path in _coerce_attachment_paths(attachment_path):
        if file_path.exists() and file_path.is_file():
            message.attach(_build_image_attachment(file_path))

    with smtplib.SMTP(host=EMAIL_HOST, port=int(EMAIL_PORT)) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(message)
        print("Sent")
