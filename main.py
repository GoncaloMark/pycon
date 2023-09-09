from spider import Spider
from scraper import Scraper

if __name__ == '__main__':
    config = {
        "url": "https://xeno-canto.org",
        "tags": ["h1"],
        "hops": 0,
    }

    spider = Spider(config.get("url"), config.get("hops"))
    scraper = Scraper(config, spider)
    results = scraper.run()
    print(results)


