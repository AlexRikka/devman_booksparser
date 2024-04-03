import requests
import os


def main():
    os.makedirs('books', exist_ok=True)
    for i in range(1, 11):
        url = 'https://tululu.org/txt.php?id=1'
        response = requests.get(url)
        response.raise_for_status()
        with open(f'books/id{i}.txt', 'wb') as f:
            f.write(response.content)


if __name__ == '__main__':
    main()
