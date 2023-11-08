from bs4 import BeautifulSoup
import requests
import re

def parse_topic_id(href):
    '''
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

def parse_episode_id(href):
    '''
    Picks out the f= id that is used as a search term in the viewtopic section of the URL
    Each id corresponds to a unique 'topic' web page. An episode of any series has a unique
    topic id
    '''
    pattern = r't=(\d{1,5})'
    match = re.search(pattern, href)
    if match:
        return match.group(1)
    else:
        print('Could not find episode ID in URL')

def transcript_from_episode_id(episode_id):
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
    def __init__(self, url):
        '''
        Accepts the first page URL of a transcripts.ForeverDreaming.org
        Assigns components for transcript analysis to attributes found at
        that URL
        '''
        self.URL = url
        self.series_code = parse_topic_id(url)#url.split('f=')[1]
        self.page = requests.get(self.URL)
        self.soup = BeautifulSoup(self.page.content, 'html.parser')
        
        #all but the first 'a href with topictitle point to an episode
        self.htmls = self.soup.findAll('a', class_='topictitle')[2:]
        #list of links pointing to episodes on this trancript page
        self.hrefs = [i['href'] for i in self.htmls]
        self.episode_ids = list(map(parse_episode_id, self.hrefs))
        #includes the S0xE0 prefix before the episode name. I use index position to
        #choose a season
        self.episode_titles = [i.contents[0] for i in self.htmls]
        #just the names, no IDs
        self.episode_names = [i[8:] for i in self.episode_titles]

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


def harvest_TV_corpus_for_sentences(FDF_obj):
    big_list = list(map(transcript_to_sentences, FDF_obj.episode_ids))
    return big_list