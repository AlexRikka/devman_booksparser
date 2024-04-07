import requests
import os


def download_book(id):
    url = f'https://tululu.org/txt.php?id={id}'
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    with open(f'books/id{id}.txt', 'wb') as f:
        f.write(response.content)


def check_for_redirect(response):
    if len(response.history) != 0:
        raise requests.HTTPError


def main():
    os.makedirs('books', exist_ok=True)
    for i in range(1, 11):
        try:
            download_book(i)
        except requests.HTTPError:
            pass


if __name__ == '__main__':
    main()
