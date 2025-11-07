from typing import cast

from bs4 import BeautifulSoup, Tag


class HTMLParser:
    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, "html.parser")

    def parse_session_key(self) -> str:
        input_tag = self.soup.find("input", {"name": "sessionDataKey"})
        if not isinstance(input_tag, Tag):
            raise ValueError("sessionDataKey input tag not found in the HTML content")
        value = input_tag.get("value")
        if value is None:
            raise ValueError("sessionDataKey input tag does not have a value attribute")
        return cast(str, value)

    def parse_url(self) -> str:
        for tag in self.soup.find_all(href=True):
            if isinstance(tag, Tag):
                href = tag.get("href")
                if href and "/accountrecoveryendpoint/" in str(href):
                    href_str = cast(str, href)
                    base_url = href_str.split("/accountrecoveryendpoint/")[0]
                    return f"{base_url}/samlsso"
        raise ValueError("URL not found in the HTML content")

    def parse_form_data(self) -> dict[str, str]:
        form = self.soup.find("form")
        if not isinstance(form, Tag):
            raise ValueError("Form tag not found in the HTML content")

        data: dict[str, str] = {}
        for input_tag in form.find_all("input"):
            if not isinstance(input_tag, Tag):
                continue  # Just in case, but should not happen
            name = input_tag.get("name")
            value = input_tag.get("value", "")
            if name is not None:
                data[cast(str, name)] = str(value)
        return data

    def parse_form_url(self) -> str:
        form_tag = self.soup.find("form")
        if not isinstance(form_tag, Tag):
            raise ValueError("Form tag not found in the HTML content")
        action = form_tag.get("action")
        if action is None:
            raise ValueError("Form tag does not have an action attribute")
        return cast(str, action)
