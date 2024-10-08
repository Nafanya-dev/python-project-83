from validators.url import url as url_validator
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse
from .models import UrlCheck, Url
from typing import Optional
import requests

MAX_LENGTH_URL: int = 255


def normalize_url(url: str) -> str:
    """
    Нормализует URL, приводя его к нижнему регистру и убирая путь.

    :return:
    Нормализованный URL.
    """
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme
    netloc = parsed_url.netloc
    normalized_url = f"{scheme}://{netloc}".lower()
    return normalized_url


def validate(url: str) -> dict:
    """
    Проверяет валидность URL.

    :return:
    Словарь с сообщениями об ошибках, если они есть.
    """
    errors = {}
    if not url_validator(url):
        errors['message'] = 'Некорректный URL'
    else:
        if len(url) > MAX_LENGTH_URL:
            errors['message'] = 'URL превышает 255 символов'
    return errors


def check_url(url: Url) -> Optional[UrlCheck]:
    """
    Проверяет доступность URL и извлекает информацию о странице.

    :return:
    Объект UrlCheck с информацией о статусе и содержимом
    страницы или None в случае ошибки.
    """
    try:
        with requests.get(url.name) as r:
            r.raise_for_status()

            status_code = r.status_code
            html_content = r.text
            return parse_html(html_content, status_code)
    except requests.exceptions.RequestException:
        return None


def parse_html(html_content: str, status_code: int) -> UrlCheck:
    """
    Извлекает заголовок, H1 и мета-описание из HTML-контента.

    :return:
    Объект UrlCheck с полученной информацией.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    h1 = soup.h1.text if soup.h1 else None
    title = soup.title.text if soup.title else None
    meta_description = soup.find('meta', attrs={'name': 'description'})
    description = meta_description.get('content'
                                       ) if meta_description else None
    current_time = datetime.now().date()
    return UrlCheck(status_code=status_code,
                    h1=h1,
                    title=title,
                    description=description,
                    created_at=current_time
                    )
