from django.core.exceptions import ValidationError
from urllib.parse import urlparse
import re


class URLValidator:
    """
    Валидатор для проверки ссылок в описании
    Разрешает только YouTube ссылки
    """

    def __init__(self, field="description"):
        self.field = field

    def __call__(self, attrs):
        description = attrs.get(self.field, "")
        if description:
            urls = re.findall(r"https?://[^\s]+", description)
            for url in urls:
                parsed_url = urlparse(url)
                domain = parsed_url.netloc.lower()

                allowed_domains = [
                    "youtube.com",
                    "www.youtube.com",
                    "youtu.be",
                    "www.youtu.be",
                    "m.youtube.com",
                ]

                if not any(
                    allowed_domain in domain for allowed_domain in allowed_domains
                ):
                    raise ValidationError(
                        f"Запрещены ссылки на сторонние ресурсы. "
                        f"Разрешены только ссылки на YouTube. "
                        f"Найдена запрещенная ссылка: {url}"
                    )


def validate_youtube_links(value):
    """Функция-валидатор для проверки YouTube ссылок"""
    if value:
        urls = re.findall(r"https?://[^\s]+", value)
        for url in urls:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()

            allowed_domains = [
                "youtube.com",
                "www.youtube.com",
                "youtu.be",
                "www.youtu.be",
                "m.youtube.com",
            ]

            if not any(allowed_domain in domain for allowed_domain in allowed_domains):
                raise ValidationError(
                    f"Запрещены ссылки на сторонние ресурсы. "
                    f"Разрешены только ссылки на YouTube. "
                    f"Найдена запрещенная ссылка: {url}"
                )
