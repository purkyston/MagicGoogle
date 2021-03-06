import requests
import chardet
import random
import os
import sys
import time
from pyquery import PyQuery as pq
from MagicGoogle.config import USER_AGENT, DOMAIN, BLACK_DOMAIN, URL_SEARCH, URL_NUM, LOGGER

if sys.version_info[0] > 2:
    from urllib.parse import quote_plus, urlparse, parse_qs
else:
    from urllib import quote_plus
    from urlparse import urlparse, parse_qs

class MagicGoogle():
    """
    Magic google search.
    """

    def __init__(self, proxies=None):
        self.proxies = random.choice(proxies) if proxies else None

    def search(self, query, language='en', num=None, start=0, pause=2):
        """
        Get the results you want,such as title,description,url
        :param query:
        :param language:
        :param num:
        :param start:
        :return: Generator
        """
        content = self.search_page(query, language, num, start, pause)
        pq_content = self.pq_html(content)
        for item in pq_content('div.g').items():
            result = {}
            result['title'] = item('h3.r>a').eq(0).text()
            href = item('h3.r>a').eq(0).attr('href')
            if href:
                url = self.filter_link(href)
                result['url'] = url
            text = item('span.st').text()
            result['text'] = text
            yield result

    def search_page(self, query, language='en', num=None, start=0, pause=2):
        """
        Google search
        :param query: Keyword
        :param language: Language
        :return: result
        """
        time.sleep(pause)
        #domain = self.get_random_domain()
        domain = 'www.google.com'
        if num is None:
            url = URL_SEARCH
            url = url.format(
                domain=domain, language=language, query=quote_plus(query))
        else:
            url = URL_NUM
            url = url.format(
                domain=domain, language=language, query=quote_plus(query), num=num)
        # Add headers
        headers = {'user-agent': self.get_random_user_agent()}
        headers['X-ProxyMesh-Timeout'] = '100'
        # headers['X-ProxyMesh-Country'] = domain[domain.rfind('.') + 1:].upper()
        headers['X-ProxyMesh-Country'] = 'US'

        try:
            requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
            r = requests.get(url=url,
                             proxies=self.proxies,
                             headers=headers,
                             allow_redirects=False,
                             verify=False,
                             timeout=30)
            LOGGER.info(url)
            charset = chardet.detect(r.content)
            content = r.content.decode(charset['encoding'])
            return content
        except Exception as e:
            LOGGER.exception(e)
            return None

    def search_url(self, query, language='en', num=None, start=0, pause=2):
        """
        :param query:
        :param language:
        :param num:
        :param start:
        :return: Generator
        """
        content = self.search_page(query, language, num, start, pause)
        pq_content = self.pq_html(content)
        for item in pq_content('h3.r').items():
            href = item('a').attr('href')
            if href:
                url = self.filter_link(href)
                if url:
                    yield url

    def filter_link(self, link):
        """
        Returns None if the link doesn't yield a valid result.
        Token from https://github.com/MarioVilas/google
        :return: a valid result
        """
        try:
            # Valid results are absolute URLs not pointing to a Google domain
            # like images.google.com or googleusercontent.com
            o = urlparse(link, 'http')
            if o.netloc:
                return link
            # Decode hidden URLs.
            if link.startswith('/url?'):
                link = parse_qs(o.query)['q'][0]
                # Valid results are absolute URLs not pointing to a Google domain
                # like images.google.com or googleusercontent.com
                o = urlparse(link, 'http')
                if o.netloc:
                    return link
        # Otherwise, or on error, return None.
        except Exception as e:
            LOGGER.exception(e)
            return None

    def pq_html(self, content):
        """
        Parsing HTML by pyquery
        :param content: HTML content
        :return:
        """
        return pq(content)

    def get_url_from_query(self, query, language='en', num=None, start=0):
        """
        Get Url from query
        :param query: Keyword
        :param language: Language
        :return: url
        """
        domain = self.get_random_domain()
        if num is None:
            url = URL_SEARCH
            url = url.format(
                domain=domain, language=language, query=quote_plus(query))
        else:
            url = URL_NUM
            url = url.format(
                domain=domain, language=language, query=quote_plus(query), num=num)
        return url

    def get_random_user_agent(self):
        """
        Get a random user agent string.
        :return: Random user agent string.
        """
        return random.choice(self.get_data('user_agents.txt', USER_AGENT))

    def get_random_domain(self):
        """
        Get a random domain.
        :return: Random user agent string.
        """
        domain = self.get_data('all_domain.txt', DOMAIN)
        domain_filter = self.get_data('domain_filter.txt')
        domain = [ d for d in domain if d[d.rfind('.') + 1 :].upper() in domain_filter]
        domain = random.choice(domain)
        if domain in BLACK_DOMAIN:
            self.get_random_domain()
        else:
            return domain

    def get_data(self, filename, default=''):
        """
        Get data from a file
        :param filename: filename
        :param default: default value
        :return: data
        """
        root_folder = os.path.dirname(__file__)
        user_agents_file = os.path.join(
            os.path.join(root_folder, 'data'), filename)
        try:
            with open(user_agents_file) as fp:
                data = [_.strip() for _ in fp.readlines()]
        except:
            data = [default]
        return data

    def get(self, url, pause=2):
        """
        requests get
        url: 
        :return: result
        """
        time.sleep(pause)
        #domain = self.get_random_domain()
        # Add headers
        headers = {'user-agent': self.get_random_user_agent()}
        headers['X-ProxyMesh-Timeout'] = '100'
        # headers['X-ProxyMesh-Country'] = domain[domain.rfind('.') + 1:].upper()
        headers['X-ProxyMesh-Country'] = 'US'

        try:
            requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
            r = requests.get(url=url,
                             proxies=self.proxies,
                             headers=headers,
                             allow_redirects=False,
                             verify=False,
                             timeout=30)
            LOGGER.info(url)
            charset = chardet.detect(r.content)
            content = r.content.decode(charset['encoding'])
            return content
        except Exception as e:
            LOGGER.exception(e)
            return None
