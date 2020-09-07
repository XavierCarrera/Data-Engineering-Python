# This file helps us to parse links, titles and bodies using bs4 libraries, as well as
# using requests to access to the urls. 

import bs4
import requests

from common import config 


class NewsPage:

    # On our constructor function, we define the main arguments in order to access to the
    # websites. 

    def __init__(self, news_site_uid, url):
        self._config = config() ['news_sites'][news_site_uid]
        self._queries = self._config['queries']
        self._html = None
        self._url = url
        self._visit(url)


    def _select(self, query_string):
        
        # In this function we access to the html files
        
        return self._html.select(query_string)

    def _visit(self, url):
        
        # This function helps us to validate a 200 url status.
        
        response = requests.get(url)

        response.raise_for_status()

        self._html = bs4.BeautifulSoup(response.text, 'html.parser')

class HomePage(NewsPage):

    # This class helps us to colect the links in the website. We do this by using the 
    # link_list as the place where we save the urls and add them with the .append method
    # after we validate the with .has_attr

    # It's important to extend to the superclass (News page) to have access to the url
    
    def __init__(self, news_site_uid, url):
       super().__init__(news_site_uid, url)

    @property
    def article_links(self):
        link_list = []
        for link in self._select(self._queries['homepage_article_links']):
            if link and link.has_attr('href'):
                link_list.append(link)

        return set(link['href'] for link in link_list)

class ArticlePage(NewsPage):

    # Once we validated the urls, we access to the titles and bodies. In this case, we
    # return a value only if there's actual content in it. That's why we use the
    # if len(result) else '' function in order to validate this.  

    # It's important to extend to the superclass (News page) to have access to the url

    def __init__(self, news_site_uid, url):
       super().__init__(news_site_uid, url)

    @property
    def body(self):
        result = self._select(self._queries['article_body'])

        return result[0].text if len(result) else ''
    

    @property
    def title(self):
        result = self._select(self._queries['article_title'])
        return result[0].text if len(result) else ''

  
    @property
    def url(self):
        return self._url


