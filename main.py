import requests
import os
import sys
import argparse
from time import sleep
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlsplit


def check_for_redirect(response):
    """Проверка на редирект."""
    if response.history:
        raise requests.TooManyRedirects


def parse_book_page(soup):
    """Парсит html-страницу с информацией о книге.

    Args:
        soup (bs4.BeautifulSoup): html-контент страницы

    Returns:
        book_info (dict): информация о книге
    """
    title_tag = soup.find('table').find('h1')
    title_text = title_tag.text.split('::')[0].strip()
    book = {
        'title': sanitize_filename(title_text),
        'author': soup.find('table').find('h1').find('a').text,
        'img_src': soup.find('div', class_='bookimage').find('img')['src'],
        'genres': [genre.text for genre
                   in soup.find('span', class_='d_book').find_all('a')],
        'comments': [comment.find('span').text for comment
                     in soup.find_all('div', class_='texts')]
    }

    return book


def download_image(url,  folder='images/'):
    """Скачивает картинки.

    Args:
      url (str): Cсылка на картинку для скачивания.
      folder (str): Папка, куда сохранять.
    """
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    img_path = f"{folder}{urlsplit(url).path.split('/')[-1]}"
    with open(img_path, 'wb') as f:
        f.write(response.content)


def download_txt(book_id, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.

    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.

    Returns:
        str: Путь до файла, куда сохранён текст.
    """

    params = {'id': book_id}
    url = 'https://tululu.org/txt.php'
    response = requests.get(url, params=params)
    response.raise_for_status()
    check_for_redirect(response)
    path = os.path.join(folder, f"{filename}.txt")
    with open(path, 'wb') as f:
        f.write(response.content)
    return path


def download_book(book_id):
    """Скачивает книги с tululu.org в формате текстовых файлов.

    Args:
        book_id (int): id книги для скачивания

    """
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    book = parse_book_page(soup)
    filename = f"{book_id}.{book['title']}"
    download_txt(book_id, filename, folder='books/')
    img_src = book['img_src']
    img_url = urljoin(url, img_src)
    download_image(img_url)
    return book


def main():
    parser = argparse.ArgumentParser(
        description='Парсер книг с сайта tululu.org')
    parser.add_argument('start_id',
                        help='Номер первой книги из диапазона для скачивания',
                        nargs='?',
                        type=int,
                        default=1)
    parser.add_argument('end_id',
                        help='Номер последней книги из диапазона для скачивания',
                        nargs='?',
                        type=int,
                        default=11)
    args = parser.parse_args()
    start_id = args.start_id
    end_id = args.end_id+1
    os.makedirs('books', exist_ok=True)
    os.makedirs('images', exist_ok=True)
    book_id = start_id
    while book_id < end_id:
        try:
            book = download_book(book_id)
            print('Заголовок: ', book['title'])
            print('Автор: ', book['author'])
            print('\n')
        except requests.TooManyRedirects:
            print(f"Книга {book_id} отсутствует на сайте.\n")
        except requests.ConnectionError:
            print("Интернет соединение прервано. Ожидание соединения...\n")
            sleep(5)
            book_id -= 1
            continue
        except requests.HTTPError as err:
            print(*err, file=sys.stderr)
            sys.exit
        finally:
            book_id += 1


if __name__ == '__main__':
    main()
