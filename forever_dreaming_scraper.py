from bs4 import BeautifulSoup
import requests
import re

def parse_id(href):
    '''
    Picks out the id that is used as a search term in the viewtopic section of the URL
    Each id corresponds to a unique 'topic' web page. An episode of any series has a unique
    topic id
    '''
    start_index = href.find('t=') + 2
    end_index = href.find('&', start_index)
    id_for_link = href[start_index:end_index]
    return id_for_link

def transcript_to_wordlist(episode_id):
    '''
    Uses the topic id to find the web page with the episode transcript, parses it down to
    a list of words used, all words lowered to lower case.
    '''
    url_string = f'https://transcripts.foreverdreaming.org/viewtopic.php?t={episode_id}'
    page = requests.get(url_string)
    soup = BeautifulSoup(page.content, 'html.parser')
    test_resultSet = soup.find_all('div', class_='content')
    test_tag = test_resultSet[0]
    test_big_string = test_tag.get_text()
    word_list = re.findall(r"\b(?:\w+(?:['*]\w+)?)\b", test_big_string)
    lowered_words = list(map(str.lower, word_list))
    return lowered_words

class ForeverDreamingForum:
    def __init__(self, url):
        '''
        Accepts the first page URL of a transcripts.ForeverDreaming.org
        Assigns components for transcript analysis to attributes found at
        that URL
        '''
        self.URL = url
        self.series_code = url.split('f=')[1]
        self.page = requests.get(self.URL)
        self.soup = BeautifulSoup(self.page.content, 'html.parser')
        
        #all but the first 'a href with topictitle point to an episode
        self.htmls = self.soup.findAll('a', class_='topictitle')[1:]
        #list of links pointing to episodes on this trancript page
        self.hrefs = [i['href'] for i in self.htmls]
        self.episode_ids = list(map(parse_id, self.hrefs))
        #includes the S0xE0 prefix before the episode name. I use index position to
        #choose a season
        self.episode_titles = [i.contents[0] for i in self.htmls]
        #just the names, no IDs
        self.episode_names = [i[8:] for i in self.episode_titles]