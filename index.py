from operator import truediv
import xml.etree.ElementTree as et
import file_io
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import sys
import collections
import math

"""
Provides functionality for Parsing the xml files and ranking each pages relevance based on the words inputted into
the query
"""
class Indexer():

    def __init__(self,wiki,titles,docs,words):
        
        #initializing the stop words
        self.STOP_WORDS = set(stopwords.words('english'))
        
        #initializing the stemmer
        self.nltk_test = PorterStemmer()

        #dictionary for words: Dict [str: word,Dict[int: page number,float: relevance number]] 
        self.words : "dict[str, dict[int, float]]" = {}
        
        #dictionary for ids to relevance 
        self.id_to_relevance = {}
        
        #dictionary from ids to pagerank
        self.id_to_pagerank = {}
        
        # dictionary from ids to titles 
        self.ids_to_titles = {}

        #dictionary from titles to ids
        self.titles_to_id = {}
        
        #dictionary from id to links
        self.ids_to_links = collections.defaultdict(set)

        #dictionary from word to frequency
        self.word_to_freq = {}

        #dictionary from id to max count
        self.id_to_max_count = {}
        
        #dictionary from word to relevance value
        self.relevance : "dict[str, dict[int, float]]" = {}

        #dictionary from id to pageweight
        self.page_weight = {}

        #epsilon value for computing weights
        self.epsilon = 0.15

        #delta value for calculating pagerank
        self.delta = 0.001

        #dictionary from the previous page's weight to help determine rank
        self.r = {}

        #dictionary from the current page's weight to help determine rank
        self.r_prime = {}

        self.processWords(wiki)
        self.relevanceFiller()
        self.compute_weights()
        self.page_rank()

        file_io.write_title_file(titles,self.ids_to_titles)
        file_io.write_words_file(words,self.relevance)
        file_io.write_docs_file(docs,self.r_prime)
    
    """
    Goes through the wiki and parses,stems, removes stop words, and fills respective dictionaries that is relevant for relevance and 
    page weight

    Parameters: 
    Wiki

    Returns:
    Nothing, just fills dictionaries 

    Throws:
    """
    def processWords(self,wiki):
        root = et.parse(wiki).getroot()
        ElementTree = root.findall("page")
        
        for page in ElementTree:
            title = page.find("title").text.strip().lower()
            id_number = int(page.find("id").text)
            self.ids_to_titles[id_number] = title
            self.titles_to_id[title] = id_number

        for page in ElementTree:
            title = page.find("title").text.strip().lower()
            id_number = int(page.find("id").text)
            text = page.find("text").text.strip().lower()
            text += " " + title
            n_regex = '''\[\[[^\[]+?\]\]|[a-zA-Z0-9]+'[a-zA-Z0-9]+|[a-zA-Z0-9]+'''
            tokenized_text = re.findall(n_regex,text)
            for word in tokenized_text:
                if self.is_link(word):
                    curr_text, curr_title = self.split_link(word)
                    stemmed_word = [self.trim_word(curr) for curr in curr_text]
                    for next_word in stemmed_word:
                        if next_word != "":
                            self.add_frequency(next_word, id_number)
                    if curr_title in self.titles_to_id:
                        self.ids_to_links[id_number].add(self.titles_to_id[curr_title])
                else:
                    stopped_word = self.trim_word(word)
                    if stopped_word != "" :
                        self.add_frequency(stopped_word, id_number)
                    else:
                        continue

    """
    Takes the page id and word, and for each word it comes across inside that individual page, it will iterate the count of that word 
    and find the max count of words present within the page

    Parameters: 
    A word and page id

    Returns:
    Nothing, just fills dictionaries 

    Throws:
    """
    def add_frequency(self, word : str, page_id : int):
        if word not in self.word_to_freq:
            self.word_to_freq[word] = {}
        if page_id not in self.word_to_freq[word]:
            self.word_to_freq[word][page_id] = 0
        self.word_to_freq[word][page_id] += 1
        if page_id not in self.id_to_max_count:
            self.id_to_max_count[page_id] = 0
        self.id_to_max_count[page_id] = max(self.id_to_max_count[page_id], self.word_to_freq[word][page_id])

    """
    Boolean helper function that identifies if the text is a link or not by using the regex expression if there's brackets
    within the text

    Parameters: 
    word

    Returns:
    True or False

    Throws:
    """
    def is_link(self, word : str):
        return bool(re.match(r"\[\[[^\[]+?\]\]", word))
    
    """
    Takes in a link and uses the regex to seperate the word and title based off of the index of the word (if a pipe is present) or just the 
    word itself as a title and text

    Parameters: 
    word

    Returns:
    title and text(which is a tuple)

    Throws:
    """
    def split_link(self, link : str):
        "you want the first one to be the title and the second one to be the text"
        curr_regex = r"[a-zA-Z0-9]+'[a-zA-Z0-9]+|[a-zA-Z0-9]+"
        reduced_words = link[2:-2]
        title, text = reduced_words, reduced_words
        if "|" in reduced_words:
            link_split = reduced_words.split("|")
            title = link_split[0]
            text = link_split[1]
            return (re.findall(curr_regex, text), title.strip().lower())
        else:
           newTitle = reduced_words.strip()
           newTitle = newTitle.lower()
           newText = reduced_words
           newText = re.findall(curr_regex, newTitle)
           return newText, newTitle
    
    """
    Identifies if the word is a stopword or not and stems it if it isnt

    Parameters: 
    word

    Returns:
    an empty string or the stemmed word 

    Throws:
    """
    def trim_word(self, word : str):
        if word.lower() in self.STOP_WORDS:
            return ""
        else:
            return self.nltk_test.stem(word.lower())

    """
    Iterates through the word to freq dictionary and accesses the number of pages and the number of pages a word appears in the corpus. 
    By doing so the idf values can be calulated by taking the log of the number of pages over the number of pages a word appears 
    in the corpus. Further iterating through each id in the word to dictionary for each word, we can acess the max count for that page by
    accessing the dictionary made previously and the specific count of that word in the word to freq dictionary for that word and that
    page id. We could then finally set the relevance value for that word in that page by multiplying the idf by th ecount for that word 
    over the max count of each page

    Parameters: 
    self

    Returns:
    Nothing, just fills the relevance dictionary  

    Throws:
    """
    def relevanceFiller(self):
        for word in self.word_to_freq:
            self.relevance[word] = {}
            num_of_pages = len(self.ids_to_titles)
            idf = math.log((num_of_pages/len(self.word_to_freq[word])))

            for id in self.word_to_freq[word]:
                max_count_of_each_page = self.id_to_max_count[id]
                count_for_word = self.word_to_freq[word][id]
                self.relevance[word][id] = (count_for_word/max_count_of_each_page) * idf
            

    """
    Iterates through each page of the corpus (by going through the dictionary that maps each id to titles) and similar for the other page
    and checks to see the edge cases for the page weight. Whether it links to itself, no pages at all, whether it links outside of the corpus
    or has multiple links. Depending on that case it would be assign 1 of 3 values. 

    Parameters: 
    self

    Returns:
    Nothing, just fills the page weight dictionary 

    Throws:
    """
    def compute_weights(self):
        num_of_pages = len(self.ids_to_titles)
        for page in self.ids_to_titles:
            for other_page in self.ids_to_titles:
                if page not in self.page_weight:
                    self.page_weight[page] = {}
                if page == other_page:
                    self.page_weight[page][other_page] = self.epsilon/num_of_pages
                elif page not in self.ids_to_links or len(self.ids_to_links[page]) == set():
                    self.page_weight[page][other_page] = self.epsilon/num_of_pages + (1 - self.epsilon) * (1 / (len(self.ids_to_titles) - 1))
                else:
                    if other_page not in self.ids_to_links[page]:
                        self.page_weight[page][other_page] = self.epsilon/num_of_pages
                    else:
                        self.page_weight[page][other_page] = self.epsilon/num_of_pages + (1 - self.epsilon) * (1 / len(self.ids_to_links[page]))

    """
    Two dictionaries that acts as the current and previous page weights and by using the helper function distance for accuracy and 
    efficieny, it can update the page rank of the page based off of its page weight and the number of pages present in the corpus

    Parameters: 
    self

    Returns:
    Nothing, just fills the page rank dictionary (r_prime) 

    Throws:
    """
    def page_rank(self):
        for id in self.ids_to_titles.keys():
            self.r[id] = 0
            self.r_prime[id] = 1 / len(self.ids_to_titles)
        while self.distance(self.r,self.r_prime) > self.delta:
            self.r = self.r_prime.copy()
            for j in self.ids_to_titles.keys():
                self.r_prime[j] = 0
                for k in self.ids_to_titles.keys():
                    self.r_prime[j] = self.r_prime[j] + self.page_weight[k][j] * self.r[k]
    
    """
    Iterates through each id in the previous dictionary and takes the sum of the squared of the difference between the previous and 
    current page ranks

    Parameters: 
    two dictionaries which represent the current and previous page ranks

    Returns:
    The square root of that value 

    Throws:
    """
    def distance(self, r : dict, r_prime : dict):
        sum = 0
        for id in r:
            sum += ((r[id] - r_prime[id]) ** 2)
            return math.sqrt(sum)

if __name__ == "__main__":
    if len(sys.argv) == 5:
        Indexer(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])

    else:
        print("Not enough argmuments")