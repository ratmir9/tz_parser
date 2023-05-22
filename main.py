import csv
import time
import requests
from bs4 import BeautifulSoup
from loguru import logger
from core import driver


def get_full_url_for_news(url_news):
    base_url = 'https://www.coindesk.com'
    return f'{base_url}{url_news}'


def write_csv(data):
    with open('news.csv', 'a') as f:
        order = ['title', 'link', 'date']
        writer = csv.DictWriter(f, fieldnames=order)
        writer.writerow(data)


def get_last_page(html):
    soup = BeautifulSoup(html, 'lxml')
    container_for_pages = soup.find('div', class_='Box-sc-1hpkeeg-0 iVHTuS')
    if container_for_pages:
        button_pages = container_for_pages.find_all('button',class_='Button__ButtonBase-sc-1sh00b8-0')
        if button_pages:
            last_pages = button_pages[-3].find('h6')
            if last_pages:
                return int(last_pages.text)


def get_data_for_parser(url):
    try:
        driver.get(url)
        time.sleep(0.5)
        html = driver.page_source
        return get_last_page(html)
    except Exception as err:
        raise Exception(str(err))
    finally:
        driver.close()
        driver.quit()


def get_info_for_news(item_news):
    news = {}
    news['title'] = item_news.get('title')
    news['link'] = get_full_url_for_news(item_news.get('link'))
    news['date'] = item_news.get('pubdate')
    return news


def write_news_file(data_news, page):
    items = data_news.get('items')
    if items:
        for item in items:
            news = get_info_for_news(item_news=item)
            try:
                write_csv(news)
                logger.debug(f'Новость {news["title"]}  успешно записано в файл')
            except Exception as err:
                logger.error(f'Проишола ошибка при записи новости {news["title"]} в файл')


def parser(last_page):
    logger.info('начало парсинга')
    base_url = 'https://www.coindesk.com/pf/api/v3/content/fetch/search?query=%7B%22search_query%22%3A%22bitcoin%22%2C%22sort%22%3A0%2C%22page%22%3A{page}%2C%22filter_url%22%3A%22%22%7D'

    for page in range(last_page):
        url = base_url.format(page=page)
        try:
            r = requests.get(url)
            logger.info(f'Запрос по адресу {url} выполнен успешно')
        except Exception as err:
            logger.error(f'Произошла ошибка, {str(err)} при отправке запрса по адресу {url}')
            continue
        data = r.json()
        if data:
            logger.debug(f'Новости с {page} страницы получены')
            write_news_file(data, page)
                

def get_data(url):
    try:
        last_page = get_data_for_parser(url)
        return last_page
    except Exception as err:
        logger.error(f'Произошла ошибка, {str(err)}')
        exit()


def main():
    url = 'https://www.coindesk.com/search?s=bitcoin'
    last_page = get_data_for_parser(url=url)
    parser(last_page)
    logger.info('Парсер завершен')


if __name__ == '__main__':
    main()
