from pathlib import Path
import requests
from langchain_core.tools import tool
from api.myemailer.sender import send_mail
from api.myemailer.inbox_reader import read_inbox


@tool
def send_me_email(subject: str, content: str) -> str:
    """
    Send an email to myself with a subject and content.

    Args:
        - subject: str - Text subject of the email
        - content: str - Text body content of the email
    """

    try:
        send_mail(subject=subject, content=content)
    except:
        return "Not Sent"
    return "Sent email"


@tool
def get_unread_emails(hours: int = 24) -> str:
    """
    Retreive emails that are unread within last N hours

    Args:
        - hours: int = 24 - number of hours ago to retreive from inbox

    Returns:
        - a string of emails separated by line "----"
    """

    try:
        emails = read_inbox(hours_ago=hours)
    except:
        return "Error getting unread emails"

    cleaned = []
    for email in emails:
        print(email)
        data = email.copy()
        if "html_body" in data:
            data.pop('html_body')
        msg = ""
        for k, v in data.items:
            msg += f"{k}:\t{v}"
        cleaned.append(msg)

    return "\n----\n".join(cleaned)


@tool
def search_and_save_images(topic: str, num_images: int = 3) -> str:
    """
    Search Wikimedia Commons for images related to a topic and save them
    to the images folder.

    Args:
        topic: Topic to search for.
        num_images: Number of images to download.

    Returns:
        Paths of the downloaded images.
    """

    try:
        search_url = "https://commons.wikimedia.org/w/api.php"

        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": topic,
            "gsrnamespace": 6,
            "gsrlimit": num_images,
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": 1200,
            "format": "json",
        }

        response = requests.get(
            search_url,
            params=params,
            headers={"User-Agent": "DockerLearn/1.0"},
            timeout=20,
        )
        response.raise_for_status()

        pages = response.json().get("query", {}).get("pages", {})

        if not pages:
            return f"No images found for: {topic}"

        image_dir = Path("/app/images")
        image_dir.mkdir(parents=True, exist_ok=True)

        saved_paths = []

        for i, page in enumerate(pages.values(), start=1):
            image_info = page.get("imageinfo", [])

            if not image_info:
                continue

            image_url = (
                image_info[0].get("thumburl")
                or image_info[0].get("url")
            )

            if not image_url:
                continue

            image_path = image_dir / f"{topic.replace(' ', '_')}_{i}.jpg"

            image_response = requests.get(
                image_url,
                headers={"User-Agent": "DockerLearn/1.0"},
                timeout=30,
            )
            image_response.raise_for_status()

            image_path.write_bytes(image_response.content)

            saved_paths.append(str(image_path))

        if not saved_paths:
            return f"Could not download images for: {topic}"

        return "\n".join(saved_paths)

    except Exception as e:
        return f"Failed to download images: {e}"
