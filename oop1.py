import requests
import webbrowser
from bs4 import BeautifulSoup


class WikipediaSearcher:
    def __init__(self, query):
        self.query = query
        self.search_url = f"https://ru.wikipedia.org/w/index.php?search={query}&ns0=1"
        self.results = []

    def fetch_results(self):
        try:
            response = requests.get(self.search_url)
            response.raise_for_status()  # Проверяем успешность запроса
        except requests.RequestException as e:
            print(f"Ошибка при подключении к Википедии: {e}")
            return None

        if "Мы не нашли страниц, совпадающих с запросом" in response.text:
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.find_all('li', class_='mw-search-result')

    def parse_results(self, search_results):
        links = []
        for result in search_results[:10]:  # Ограничиваем до 10 результатов
            title_tag = result.find('a')
            if title_tag:
                title = title_tag.text
                link = f"https://ru.wikipedia.org{title_tag['href']}"
                links.append((title, link))
        self.results = links
        return links


class WikipediaOpener:
    def __init__(self, searcher):
        self.searcher = searcher

    def display_results(self):
        if not self.searcher.results:
            print("По вашему запросу ничего не найдено.")
            return

        print("\nРезультаты поиска:")
        for i, (title, link) in enumerate(self.searcher.results, start=1):
            print(f"{i}. {title}")

    def choose_article(self):
        print("\nВведите номер статьи, которую хотите открыть (или 0 для выхода):")
        try:
            choice = int(input().strip())
            if choice == 0:
                print("Выход из программы.")
                return None
            elif 1 <= choice <= len(self.searcher.results):
                return self.searcher.results[choice - 1][1]  # Возвращаем ссылку
            else:
                print("Некорректный номер. Попробуйте снова.")
        except ValueError:
            print("Вы ввели некорректное значение. Попробуйте снова.")
        return None

    def open_article(self, url):
        if url:
            webbrowser.open(url)
            print("Статья открыта в браузере.")


def search_wikipedia():
    print("Введите поисковый запрос:")
    query = input().strip()

    if not query:
        print("Вы не ввели запрос. Попробуйте еще раз.")
        return

    searcher = WikipediaSearcher(query)
    search_results = searcher.fetch_results()

    if search_results is None:
        return  # Прерываем, если произошла ошибка при запросе

    links = searcher.parse_results(search_results)

    # Проверим, если результаты поиска пустые, возможно, статья существует
    if not links:
        article_url = f"https://ru.wikipedia.org/wiki/{query}"
        print(f"\nСтатья с таким названием существует, открываю её: {article_url}")
        webbrowser.open(article_url)
    else:
        opener = WikipediaOpener(searcher)
        opener.display_results()
        url = opener.choose_article()
        opener.open_article(url)


if __name__ == "__main__":
    search_wikipedia()
