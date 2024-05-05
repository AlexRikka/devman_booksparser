import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlsplit


def check_for_redirect(response):
    """Проверка на редирект."""
    if len(response.history) != 0:
        raise requests.HTTPError


def parse_book_page(soup):
    """Парсит html-страницу с информацией о книге.

    Args:
        soup (bs4.BeautifulSoup): html-контент страницы

    Returns:
        book_info (dict): информация о книге
    """
    book_info = {}
    title_tag = soup.find('table').find('h1')
    title_text = title_tag.text.split('::')[0].strip()
    book_info['title'] = sanitize_filename(title_text)
    book_info['author'] = soup.find('table').find('h1').find('a').text

    book_info['comments'] = []
    soup_comments = soup.find_all('div', class_='texts')
    for comment in soup_comments:
        book_info['comments'].append(comment.find('span').text)

    book_info['genres'] = []
    soup_genres = soup.find('span', class_='d_book').find_all('a')
    for genre in soup_genres:
        book_info['genres'].append(genre.text)

    return book_info


def download_image(url,  folder='images/'):
    """Скачивает картинки.

    Args:
      url (str): Cсылка на картинку для скачивания.
      folder (str): Папка, куда сохранять.
    """
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    img_path = folder + urlsplit(url).path.split('/')[-1]
    with open(img_path, 'wb') as f:
        f.write(response.content)


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
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    book_info = parse_book_page(soup)
    filename = f'{id}. ' + book_info['title']
    txt_url = f'https://tululu.org/txt.php?id={id}'
    download_txt(txt_url, filename, folder='books/')
    img_src = soup.find('div', class_='bookimage').find('img')['src']
    img_url = urljoin('https://tululu.org', img_src)
    download_image(img_url)
    return book_info


def main():
    os.makedirs('books', exist_ok=True)
    os.makedirs('images', exist_ok=True)
    for i in range(1, 11):
        try:
            book_info = download_book(i)
            print('Заголовок: ', book_info['title'])
            print(book_info['genres'])
            # for comment in book_info['comments']:
            #     print(comment)
            print('\n')
        except requests.HTTPError:
            pass


if __name__ == '__main__':
    main()
