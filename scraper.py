from bs4 import BeautifulSoup
import asyncio
import aiohttp
import itertools

max_requests = 5
class Scraper:
    def __init__(self, config, spider):
        self.__config = config
        self.__spider = spider
        self.__cache = {}
        self.__links = []

    async def __get_html(self, link, session):
        if link not in self.__cache:
            page = await session.request("GET", link)
            page.raise_for_status()
            html = await page.text()
            soup = BeautifulSoup(html, "html.parser")
            self.__cache[link] = soup
        return self.__cache[link]
    
    def __parse_by_element(self, html):
        if not self.__config.get("tags"):
            return

        for tag in self.__config.get("tags"):
            result = html.find_all(tag)

            for el in result:
                yield el
    
    def __parse_by_selector(self, html):
        if not self.__config.get("selectors"):
            return
        result = []
        for selector in self.__config.get("selectors"):
            if selector == "id":
                for value in self.__config.get("id"):
                    result.append(html.select_one(f"#{value}"))
            result.append(html.select(selector))
            for el in result:
                yield el

    async def __parse(self, link, session):
        html = await self.__get_html(link, session)
        scrape_list = [[r for r in self.__parse_by_element(html)], [r for r in self.__parse_by_selector(html)]]

        return (link, {"ByElement": scrape_list[0],"BySelector": scrape_list[1]})
    
    async def __scrape(self):
        semaphore = asyncio.Semaphore(max_requests)
        async with aiohttp.ClientSession() as session:
            if self.__config.get("hops") != 0:
                await self.__spider.getLinks(session)
                links = self.__spider.show_links()
                
                internal, external = links
                self.__links = [self.__config.get("url"), *internal, *external]
            async def fetch_with_semaphore(link):
                async with semaphore:
                    return await self.__parse(link, session)
            #TODO task group
            tasks = [fetch_with_semaphore(link) for link in self.__links]
            return await asyncio.gather(*tasks)

    def run(self):
        return asyncio.run(self.__scrape())