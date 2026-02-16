import requests
from bs4 import BeautifulSoup


class Parser:
    def __init__(self):
        self.data_tem = {}
        self.url_tem = "https://cyberleninka.ru/article"

    async def parse_tem(self):
        response = requests.get(self.url_tem, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        soup = BeautifulSoup(response.text, 'html.parser')

        items1 = soup.find_all('div', class_='half')
        items2 = soup.find_all('div', class_='half-right')
        items = items1 + items2

        for i in items:
            a = i.find_all('a')
            if len(a) > 2:
                for link in a:
                    # Получаем текст ссылки (название категории)
                    title = link.text.strip()

                    # Получаем href (относительную ссылку)
                    href = link.get('href', '')

                    # Проверяем, что есть и название и ссылка
                    if title and href:
                        # Делаем ссылку абсолютной
                        full_url = f"https://cyberleninka.ru{href}" if href.startswith('/') else href

                        # Добавляем в словарь
                        # Используем title как ключ, full_url как значение
                        self.data_tem[title] = full_url

        return self.data_tem

    async def parse_site(self, category_url):
        list = []
        vr_list = []
        response = requests.get(category_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        soup = BeautifulSoup(response.text, 'html.parser')

        items = soup.find_all('ul', class_='list')

        items = items[0].find_all('li')

        for item in items:
            title = item.find('div', class_='title')
            autor = item.find('span')
            a = item.find('a')
            href = a.get('href', '')
            full_url = f"https://cyberleninka.ru{href}" if href.startswith('/') else href
            vr_list.append(full_url)
            vr_list.append(autor.text)
            vr_list.append(title.text)
            list.append(vr_list)
            vr_list = []

        return list