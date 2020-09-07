# The main file has a series of libraries for creating a csv file, name it on the
# date it was created, parse links and access to urls. We also need to bring libraries
# for debuggin purposes. 

import argparse
import logging
import csv
import datetime

logging.basicConfig(level=logging.INFO)
import re

from requests.exceptions import HTTPError

from urllib3.exceptions import MaxRetryError

# Finally, we need also to access to our new_page_object file (in order to validate urls,
# titles and bodies) and common (so that we access to our yaml)

import new_page_objects as news
from common import config

# This section is crucial because we use regex to validate urls. 

is_well_formed_url= re.compile(r'^https?://.+/.+$') # i.e. https://www.somesite.com/something
is_root_path = re.compile(r'^/.+$') # i.e. /some-text
logger = logging.getLogger(__name__)


def _news_scraper(news_site_uid):
    
    # This functions accesses to the urls and sends info to our user to inform about
    # the webscraping process. 
    
    host = config()['news_sites'][news_site_uid]['url']

    logging.info('Beginning web scraper {}'.format(host))
    logging.info('Getting links...')

    homepage = news.HomePage(news_site_uid, host)

    articles = []

    for link in homepage.article_links:
        article = _fetch_article(news_site_uid, host, link)

        if article:
            logger.info('Obtained article')
            articles.append(article)

        _save_articles(news_site_uid, articles)


def _fetch_article(news_site_uid, host, link):

    # In this functions, we fetch the urls and inform to which link are we accessing.
    # Likewise, we use a error handling method in case it was not properly parsed
    # in new_page_objects.py

    logger.info('Finding article in  {}'.format(link))

    article = None
    try:
        article = news.ArticlePage(news_site_uid, _build_link(host, link))
    except (HTTPError, MaxRetryError) as e:
        logger.warning('Error while obtaining article', exc_info=False)

    if article and not article.body:
        logger.warning('Invalid article. No article in the structure.')
        return None

    return article


def _build_link(host, link):

    # We use this function to validate urls with regex.

    if is_well_formed_url.match(link):
        return link
    elif is_root_path.match(link):
        return'{}{}'.format(host, link)
    else:
        return'{host}/{url}'.format(host=host, url=link)


def _save_articles(news_site_uid, articles):

    # Having open csvs, we start writing them. The datetime library helps us to name it
    # on the date, after the name of the news site. As well, we use rows functions to add
    # titles and body to the file. 

    now = datetime.datetime.now()
    csv_headers = list(filter(lambda property: not property.startswith('_'), dir(articles[0])))
    out_file_name = '{news_site_uid}_{datetime}_articles.csv'.format(news_site_uid=news_site_uid, datetime=now.strftime('%Y_%m_%d'))

    with open(out_file_name, mode='w+') as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)
        for article in articles:
            row = [str(getattr(article, prop)) for prop in csv_headers]
            writer.writerow(row)

       

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    news_site_choices = list(config()['news_sites'].keys())
    parser.add_argument('news_site',
                        help='The news site that you want to scrape',
                        type=str,
                        choices=news_site_choices)

    args = parser.parse_args()
    _news_scraper(args.news_site)