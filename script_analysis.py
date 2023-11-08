from collections import Counter
from nltk.corpus import stopwords

def remove_stopwords(word_list):
    '''
    Removes the NLTK stopwords and my own list of stopwords from the input list
    '''
    my_stop_words = [
    'yeah',
    'uh',
    "i'm",
    'okay',
    'well',
    'oh',
    'right',
    'get',
    "we're",
    'um',
    "let's",
    "him",
    "get",
    "go",
    "let",
    "can",
    'come',
    'here',
    ''
]
    stop_words = list(set(stopwords.words('english'))) + my_stop_words
    filtered_words = [word for word in word_list if word not in stop_words]
    return filtered_words

def persons_of_interest(chars_list):
    chars_dict = { i:[i.lower()] for i in chars_list}
    return chars_dict

def sum_names_in_wordlist(
        persons_of_interest, 
        word_list):
    '''
    Using the persons_of_interest dict to find all variants of each series character's
    name. 
    Word_list should be a list of single words. 
        Can be used on an episode, season, or entire series. THis accepts a 
        list of strings and counts the 'persons_of_interest' occurences in those 
        strings
    '''
    word_counts = Counter(word_list)
    summed_counts = {}
    
    for key, word_list in persons_of_interest.items():
        total_count = sum(word_counts[word] for word in word_list if word in word_counts)
        summed_counts[key] = total_count
    return summed_counts
#################

def select_season_words(
        episodes_dict,
        season_num):
    '''
    episodes_dict should have keys as episode ids and titles, values is the wordlist per episode

    Returns a list of the words used in one particular season.
    Filters by using the season number ( [2] ) index position of each dictionary key
    '''
    list_of_wordlists = [episodes_dict[key] for key in episodes_dict if key[1] == season_num]
    big_wordlist = [i for sublist in list_of_wordlists for i in sublist]
    return big_wordlist

def season_name_count(season_num):
    '''
    Returns a Counter dict like object that counts all the name appearnces of the main characters.
    '''
    season_words = select_season_words(succ_book, season_num)
    word_counts =  Counter(season_words)
    return sum_names_in_wordlist(word_counts)