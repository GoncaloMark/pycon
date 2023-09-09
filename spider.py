from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

class Spider:
    def __init__(self, url, max_hops=0):
        self.__url = url
        self.__internal_urls = set()
        self.__external_urls = set()
        self.__hops = int(max_hops)
        isValid = self.__validateURL(url)
        if isValid is False:
            raise ValueError

    def __validateURL(self, url):
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)
    
    async def getLinks(self, session):
        page = await session.request("GET", self.__url)
        page.raise_for_status()
        html = await page.text()
        soup = BeautifulSoup(html, "html.parser")
        domain_name = urlparse(self.__url).netloc

        # print(html)

        for link_tag in soup.find_all("a")[0:self.__hops]:
            href = link_tag.attrs.get("href")
            # print(href)
            if href == "" or href is None:
                continue
            join_href = urljoin(self.__url, href)

            # print(join_href)
            
            if not self.__validateURL(join_href):
                continue

            if domain_name not in join_href:
                self.__external_urls.add(join_href)
                continue
            
            self.__internal_urls.add(join_href)

    def show_links(self):
        return (self.__internal_urls, self.__external_urls)





