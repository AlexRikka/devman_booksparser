import requests
import os
from bs4 import BeautifulSoup

from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if len(response.history) != 0:
        raise requests.HTTPError


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.

    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.

    Returns:
        str: Путь до файла, куда сохранён текст.
    """

    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    path = os.path.join(folder, filename + '.txt')
    with open(path, 'wb') as f:
        f.write(response.content)
    return path


def download_book(id):
    """Скачивает книги с tululu.org в формате текстовых файлов.

    Args:
        id (int): id  книги для скачивания

    """
    url = f'https://tululu.org/b{id}/'
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('table').find('h1')
    title_text = title_tag.text.split('::')[0].strip()
    filename = sanitize_filename(title_text)
    filename = f'{id}. ' + filename
    txt_url = f'https://tululu.org/txt.php?id={id}'
    download_txt(txt_url, filename, folder='books/')


def main():
    os.makedirs('books', exist_ok=True)
    for i in range(1, 11):
        try:
            download_book(i)
        except requests.HTTPError:
            pass


if __name__ == '__main__':
    main()
