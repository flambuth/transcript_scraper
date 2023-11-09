from bs4 import BeautifulSoup
import requests
import re

from script_analysis import name_counts_by_season, name_count_line_graph

main_url = 'https://transcripts.foreverdreaming.org/'

def parse_forum_id(href):
    '''
    forum == Series 
    Picks out the f= id that is used as a search term in the viewtopic section of the URL
    Each id corresponds to a unique 'topic' web page. An episode of any series has a unique
    topic id
    '''
    pattern = r'f=(\d{1,4})'
    match = re.search(pattern, href)
    if match:
        return match.group(1)
    else:
        print('Could not find topic ID in URL')

def parse_topic_id(url):
    '''
    topic == Episode of Series
    Picks out the f= id that is used as a search term in the viewtopic section of the URL
    Each id corresponds to a unique 'topic' web page. An episode of any series has a unique
    topic id
    '''
    pattern = r't=(\d{1,6})'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        print('Could not find episode ID in URL')

def forum_pages_past_first(forum_url):
    page = requests.get(forum_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    buttons = (soup.find_all('a', class_='button'))
    possible_pagination = [i.attrs['href'] for i in buttons if i.name == 'a' and i.attrs['href'].startswith('./viewforum.php?f=')]
    real_possible = list(set(possible_pagination))
    if real_possible:
        return [main_url + i for i in real_possible]
    else: 
        return None

def all_episode_IDs_on_page(url):
    '''
    Used at least once for TV series. Used for each pagination of episodes if episode count is above 78.
    About 78 ids per page is the max on ForeverDreamingForum
    '''
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    htmls = soup.findAll('a', class_='topictitle')[1:]
    hrefs = [i['href'] for i in htmls]
    episode_ids = list(map(parse_topic_id, hrefs))
    #episode_titles = [i.contents[0] for i in htmls]
    return episode_ids

def all_episode_titles_on_page(url):
    '''
    Used at least once for TV series. Used for each pagination of episodes if episode count is above 78.
    About 78 ids per page is the max on ForeverDreamingForum
    '''
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    htmls = soup.findAll('a', class_='topictitle')[1:]
    episode_titles = [i.contents[0] for i in htmls]
    return episode_titles

def all_episode_ids(main_url):
    possible_extra = forum_pages_past_first(main_url)
    first_page_ep_ids = all_episode_IDs_on_page(main_url)
    if possible_extra:
        outer_list = list(map(all_episode_IDs_on_page, possible_extra))
        ep_ids = [i for sublist in outer_list for i in sublist]
        return first_page_ep_ids + ep_ids
    else:
        return first_page_ep_ids
    
def all_episode_titles(main_url):
    possible_extra = forum_pages_past_first(main_url)
    first_page_ep_titles = all_episode_titles_on_page(main_url)
    if possible_extra:
        outer_list = list(map(all_episode_titles_on_page, possible_extra))
        ep_titles = [i for sublist in outer_list for i in sublist]
        return first_page_ep_titles + ep_titles
    else:
        return first_page_ep_titles
    

def transcript_from_episode_id(episode_id):
    '''
    episode_id matches up with the website's topic_id
    '''
    url_string = f'https://transcripts.foreverdreaming.org/viewtopic.php?t={episode_id}'
    page = requests.get(url_string)
    soup = BeautifulSoup(page.content, 'html.parser')
    test_resultSet = soup.find_all('div', class_='content')
    test_tag = test_resultSet[0]
    test_big_string = test_tag.get_text()
    return test_big_string

def transcript_to_wordlist(episode_id):
    '''
    Uses the topic id to find the web page with the episode transcript, parses it down to
    a list of words used, all words lowered to lower case.
    '''
    test_big_string = transcript_from_episode_id(episode_id)
    word_list = re.findall(r"\b(?:\w+(?:['*]\w+)?)\b", test_big_string)
    lowered_words = list(map(str.lower, word_list))
    return lowered_words

def transcript_to_sentences(episode_id):
    test_big_string = transcript_from_episode_id(episode_id)
    text = re.sub(r'\[.*?\]', '', test_big_string)
    # Split the text into sentences based on line breaks
    sentences = re.split(r'\n', text)
    # Remove empty strings and strip whitespace from the sentences
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    return sentences

class ForeverDreamingForum:
    def __init__(
            self, 
            url, 
            persons_of_interest=None):
        '''
        Accepts the first page URL of a transcripts.ForeverDreaming.org
        Assigns components for transcript analysis to attributes found at
        that URL
        '''
        self.URL = url
        self.persons_of_interest = persons_of_interest
        self.series_code = parse_forum_id(url)
        self.episode_ids = all_episode_ids(url)
        #includes the S0xE0 prefix before the episode name
        self.episode_titles = all_episode_titles(url)

    def get_series_transcripts(self):
        '''
        Adds a list of transcripts to the FDF object
        '''
        pass

    def harvest_TV_corpus_for_words(self):
        big_list = list(map(transcript_to_wordlist, self.episode_ids))
        big_dict = {key: value for key, value in zip(self.episode_titles, big_list)}
        return big_dict

    def harvest_TV_corpus_for_words_by_season(self):
        '''
        Use ForeverDreamingForum.harvest_TV_corpus_for_words() as the input
        '''
        episode_word_corpii = self.harvest_TV_corpus_for_words()
        result_dict = {}  # Initialize the new dictionary

        for key, value in episode_word_corpii.items():
            season = key[:2]  # Extract the season part, e.g., '02X'
            if season not in result_dict:
                result_dict[season] = {}  # Create a new season-based dictionary if it doesn't exist
            result_dict[season][key] = value

        return result_dict
    
    def harvest_TV_season_corpii(self):
        season_words = self.harvest_TV_corpus_for_words_by_season()
        new_dict = {}
        for season_num in season_words.keys():
            new_dict[season_num] = [i for sublist in season_words[season_num].values() for i in sublist]
        return new_dict
    
    def name_counts_by_season(
            self,
            persons_of_interest=None
            ):
        if persons_of_interest==None:
            persons_of_interest = self.persons_of_interest
        season_name_count_book = name_counts_by_season(
            persons_of_interest,
            self.harvest_TV_season_corpii()
        )
        return season_name_count_book
    
    def name_count_line_graph(
        self,
            persons_of_interest=None
            ):
        if persons_of_interest==None:
            persons_of_interest = self.persons_of_interest
        line_fig = name_count_line_graph(
            persons_of_interest,
            self.harvest_TV_season_corpii()
        )
        return line_fig















#############
#deprecated

def extract_start(url):
    # Split the URL by '=' and get the last part, then convert it to an integer
    return int(url.split('=')[-1])

def last_forum_page(url):
    possible_extra = forum_pages_past_first(url)
    url_with_largest_start = max(possible_extra, key=extract_start)
    return url_with_largest_start

def find_last_topic_on_page(url):
    '''
    give it the last_forum_page(url)
    '''
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    htmls = soup.find_all('a', class_='topictitle')[2:]
    first_ep = htmls[-1]
    first_ep_id = parse_topic_id(first_ep.attrs['href'])
    return first_ep_id

def first_topic_id_for_series(main_url):
    possible_extras = forum_pages_past_first(main_url)
    if possible_extras:
        last_page = last_forum_page(main_url)
        first_ep_id = find_last_topic_on_page(last_page)
        return first_ep_id
    else:
        return find_last_topic_on_page(main_url)

def harvest_TV_corpus_for_sentences(FDF_obj):
    big_list = list(map(transcript_to_sentences, FDF_obj.episode_ids))
    return big_list
