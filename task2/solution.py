import logging
import re
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from typing import Optional


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S')
logger = logging.getLogger('WikiBeastsParser')


def get_html(url: str) -> Optional[str]:
    """
    Функция, принимающая на вход URL на страницу Википедии с категориями и возвращающая результат get-запроса в виде
    строки, если соединение удалось установить (в противном случае None)

    Ключевые аргументы:
    :param url: адрес страницы в Википедии (str)
    """
    if not re.fullmatch(r'^https?:\/\/ru\.wikipedia\.org\/.*', url):
        logger.error(
            f'Скрипт не может быть выполнен. Переданный url ({url}) не соответствует странице Википедии'
        )
        raise ValueError(f'URL {url} не является адресом страницы Википедии')

    max_retries = 3
    current_try = 0
    response = None

    while current_try < max_retries:
        current_try += 1
        req = requests.get(url)
        if req.status_code != 200:
            logger.error(
                f'Произошла ошибка при попытке доступа к странице. Код состояния: {req.status_code}. '
                f'Повторная попытка ({current_try}/{max_retries}).'
            )
            time.sleep(current_try)
        else:
            response = req.text
            break
    return response


def get_next_page_url(response: str) -> Optional[str]:
    """
    Функция, возвращающая ссылку на следующую страницу, если она есть (если нет, то None).

    Ключевые аргументы:
    :param response: результат get-запроса к странице (str)
    """
    soup = BeautifulSoup(response, 'lxml')
    try:
        # Ищем тег 'a' с текстом = 'Следующая страница'
        next_page = soup.find('a', string='Следующая страница')
        # Если тег 'a' имеет атрибут 'href'
        if next_page.attrs['href'] is not None:
            # Возвращаем ссылку на следующую страницу
            return 'https://ru.wikipedia.org' + next_page.attrs['href']
    except AttributeError:
        return None


def get_letters_dict(response: str) -> Optional[dict[str, int]]:
    """
    Функция, возвращающая словарь с ключами, соответствующими букве каталога и значениями, соответствующими кол-ву
    слов, начинающихся на данную букву (или None)

    Ключевые аргументы:
    :param response: результат get-запроса к странице (str)
    """
    # Инициализируем пустой словарь, в который будем записывать кол-во ссылок для каждой буквы
    animals_dict = {}

    soup = BeautifulSoup(response, 'lxml')

    try:
        # Ищем 'div' с буквой (класс 'mw-category-group'), вложенный в 'div' класса 'mw-category mw-category-columns'
        letters_block = soup.find(
            'div', class_='mw-category mw-category-columns'
        ).find_all(
            'div', class_='mw-category-group'
        )
    except AttributeError:
        logger.info(
            f'На текущей странице отсутствует раздел с категориями'
        )
        raise

    # Инициализируем переменную, которая будет хранить текущую букву, на случай, если на одной странице будет несколько
    current_letter = None
    # Инициализируем переменную, которая будет хранить уникальные ссылки для данной буквы
    current_letter_unique_links = None

    # Обходим divы с буками (минимум 1)
    for block in letters_block:
        # Забираем из него заголовок с самой буквой
        letter = block.find('h3').text
        # Если буква отлична от той, чтоб была ранее
        if letter != current_letter:
            # Добавляем в словарь ключ (буквы) со значением 0
            animals_dict[letter] = 0
            # Обновляем переменную с текущей буквой
            current_letter = letter
            # Обновляем переменную с уникальными ссылками для данной буквы
            current_letter_unique_links = set()
        for link in block.find_all('a'):
            href = link.attrs['href']
            if href not in current_letter_unique_links:
                current_letter_unique_links.add(href)
                animals_dict[letter] += 1
    return animals_dict


def main(url: str = 'https://ru.wikipedia.org/wiki/Категория:Животные_по_алфавиту',
         file_name: str = 'beasts.csv') -> dict[str, int]:
    """
    ФНеобходимо, которая будет получать с русскоязычной википедии список всех животных и записывать в файл в формате
    'beasts.csv' количество животных на каждую букву алфавита

    Ключевые аргументы:
    :param url: адрес страницы в Википедии (str)
    :param file_name: имя файла с расширением .csv, в который будет произведено сохранение данных
    """
    a = ord('А')
    russian_upper_list = ''.join(
        [chr(i) for i in range(a, a + 6)] +
        [chr(1025)] +
        [chr(i) for i in range(a + 6, a + 32)]
    )

    result = {}

    if not re.fullmatch(r'.*(\.csv)$', file_name):
        logger.error(
            f'Скрипт не может быть выполнен. Имя файла не соответствует формату <имя_файла.csv>'
        )
        raise ValueError(f'Имя файла {file_name} не соответствует формату <имя_файла.csv>')

    page_html = get_html(url)

    while True:
        if page_html is None:
            logger.error(
                f'Завершение скрипта по причине невозможности получения доступа к странице.'
            )
            break
        next_page_url = get_next_page_url(page_html)
        current_page_letters_dict = get_letters_dict(page_html)
        if list(current_page_letters_dict.keys())[0] not in russian_upper_list:
            break
        page_html = get_html(next_page_url)
        for key, value in current_page_letters_dict.items():
            if key not in russian_upper_list:
                logger.info(
                    f'Сбор информации с русскоязычной википедии о количестве животных на каждую букву алфавита завершен'
                    f'. Собрано {sum(result.values())} уникальных животных'
                )
                break
            try:
                result[key] += value
            except KeyError:
                result[key] = value
                logger.info(
                    f'Сбор животных на букву {key}'
                )

    if result:
        df = pd.DataFrame([[key, val] for key, val in result.items()])

        df.to_csv(file_name, mode='w', encoding='utf-8', index=False, header=False)
        logger.info(
            f'Сформирован файл {file_name} с результатами сбора данных.'
        )

    return result


if __name__ == '__main__':
    URL = 'https://ru.wikipedia.org/wiki/Категорfия:Животные_по_алфавиту'
    FILE_NAME = 'beasts.csv'
    main(URL, FILE_NAME)
