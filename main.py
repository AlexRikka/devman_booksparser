import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlsplit


def check_for_redirect(response):
    if len(response.history) != 0:
        raise requests.HTTPError


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
    title_tag = soup.find('table').find('h1')
    title_text = title_tag.text.split('::')[0].strip()
    filename_title = sanitize_filename(title_text)
    filename = f'{id}. ' + filename_title
    txt_url = f'https://tululu.org/txt.php?id={id}'
    download_txt(txt_url, filename, folder='books/')
    img_src = soup.find('div', class_='bookimage').find('img')['src']
    img_url = urljoin('https://tululu.org', img_src)
    download_image(img_url)
    comments = []
    soup_comments = soup.find_all('div', class_='texts')
    for comment in soup_comments:
        comments.append(comment.find('span').text)
    genres = []
    soup_genres = soup.find('span', class_='d_book').find_all('a')
    for genre in soup_genres:
        genres.append(genre.text)
    return filename_title, comments, genres


def main():
    os.makedirs('books', exist_ok=True)
    os.makedirs('images', exist_ok=True)
    for i in range(1, 11):
        try:
            title, comments, genres = download_book(i)
            print('Заголовок: ', title)
            print(genres)
            # for comment in comments:
            #     print(comment)
            print('\n')
        except requests.HTTPError:
            pass


if __name__ == '__main__':
    main()
