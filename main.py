import re
import csv
from time import sleep
from bs4 import BeautifulSoup
import requests




headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'referer': "https://www.google.com" ,
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36 Edg/85.0.564.44'
}


def get_article(card):
    """ extrae la informacion de la tarjeta de noticias"""

    titular = card.find('h4', 's-title fz-16 lh-20').text
    source = card.find('span', 's-source mr-5 cite-co').text
    timestamp = card.find('span', 'fc-2nd s-time mr-8').text.replace('·', "").strip()
    description = card.find('p', 's-desc').text.strip()
    raw_link = card.find('a').get('href')
    unquoted_link = requests.utils.unquote(raw_link)
    re_pattern = re.compile(r'RU=(.+)\/RK')
    clean_link = re.search(re_pattern, unquoted_link).group(1)

    article = [titular, source, timestamp, description, clean_link]
    return article

def get_the_news(search, max_pages):
    """ Programa principal para extraccion """

    template = 'https://news.search.yahoo.com/search?p={}'
    url = template.format(search)
    articles = []
    links = set()

    while True:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all('div', 'NewsArticle')

        # extrae datos del articulo
        for card in cards:
            article = get_article(card)
            link = article[-1]
            if not link in links:
                links.add(link)
                articles.append(article)
        # proxima pagina
        count = 0
        try:
            url = soup.find('a', 'next').get('href')
            sleep(1)
            count += 1
            if count == max_pages:
                break
        except AttributeError:
            break

    # salvamos a un CSV
    with open('resultados.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(['Titular', 'Fuente', 'Posteado', 'Descripcion', 'Link'])
        for article in articles:
            writer.writerow(article)

    return articles

def main():
    print("Procesando noticias.. ")
    max_pages = 10
    search_word = "oil"
    get_the_news(search_word, max_pages)
    print("CSV - Listo para analizar")

main()
