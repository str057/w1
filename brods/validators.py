from django.core.exceptions import ValidationError
from urllib.parse import urlparse
import re


def validate_allowed_urls(value):

    if not value:
        return

    # Регулярное выражение для поиска URL в тексте
    url_pattern = r"https?://[^\s]+"
    urls = re.findall(url_pattern, value)

    for url in urls:
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()

            # Разрешаем только youtube.com и youtu.be (короткие ссылки YouTube)
            allowed_domains = [
                "youtube.com",
                "www.youtube.com",
                "youtu.be",
                "www.youtu.be",
            ]

            if not any(allowed_domain in domain for allowed_domain in allowed_domains):
                raise ValidationError(
                    f"Ссылки на домен {domain} запрещены. "
                    f"Разрешены только ссылки на YouTube."
                )

        except Exception:
            raise ValidationError("Некорректная ссылка в материалах урока.")


class URLValidator:

    def __init__(self, field="description"):
        self.field = field

    def __call__(self, attrs):
        value = attrs.get(self.field, "")
        validate_allowed_urls(value)
