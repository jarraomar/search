
from ast import operator
from numpy import sort
from parso import parse
import file_io
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import re
import sys
class querier():
    def __init__(self,titles,words,page_rank, documents):
        self.nltk_test = PorterStemmer()
        self.is_pagerank_true = page_rank
        self.user_input = None
        self.ids_to_pageranks = {}
        self.words_to_doc_relevance = {}
        self.ids_to_titles = {}
        self.get_rel_pages= {}
        self.relevance_total = {}
        file_io.read_docs_file(documents,self.ids_to_pageranks)
        file_io.read_words_file(words,self.words_to_doc_relevance)
        file_io.read_title_file(titles,self.ids_to_titles)

    """
    Goes through the word and parses,stems, removes stop words, and fills respective dictionaries that is relevant for relevance and 
    page weight

    Parameters: 
    Wiki

    Returns:
    the stemmed word

    Throws:
    """
    def parse(self,list_of_words):
        n_regex = '''\[\[[^\[]+?\]\]|[a-zA-Z0-9]+'[a-zA-Z0-9]+|[a-zA-Z0-9]+'''
        tokenized_text = re.findall(n_regex,list_of_words)
        for words in tokenized_text:
            self.STOP_WORDS = set(stopwords.words('english'))
            if words.lower() in self.STOP_WORDS:
                return ""
            else:
                return self.nltk_test.stem(words.lower())

    """
    Fills in the relevance dictionary and for each word in the words to doc relevance, and for each id and each rel val (for that word and
    id its iterating). It checks to see if the id is present and if not it sets that relevance value for that id equal to 0. And then it 
    increment that each rels value for that id

    Parameters: 
    inputted word

    Returns:
    Nothing, just fills the relevance total dictionary  

    Throws:
    """
    def populate_relevant_pages(self, words):
        word = self.parse(words)
        self.relevance_total = {}
        if word in self.words_to_doc_relevance:
            for ids,rel in self.words_to_doc_relevance[word].items():
                if ids not in self.relevance_total:
                    self.relevance_total[ids] = 0.0
                self.relevance_total[ids] += rel
    
    """
    Creates a list of relevance total values and sorts that list for the 10 highest (or at least up to it if there isnt enough) and 
    if the page rank is present within the users argument, it would return the relevance totals only; however, if it is present, 
    it would multiply those values by its page rank

    Parameters: 
    self

    Returns:
    the sorted list

    Throws:
    """
    def top_ten(self):
        all_pages = list(self.relevance_total.keys())
        num_pages = min(10,len(self.relevance_total.keys()))
        if self.is_pagerank_true == False:
            return sorted(all_pages,reverse=True, key = lambda x: self.relevance_total[x])[:num_pages]
        else:
            return sorted(all_pages,reverse=True, key = lambda x: (self.relevance_total[x] * self.ids_to_pageranks[x]))[:num_pages]

    """
    for each page within the sorted list, it prints out the list and the counter for each word

    Parameters: 
    self

    Returns:
    a print statement with the list of the page titles for the most relevant page s

    Throws:
    """
    def print_top_ten(self):
        top_ten_list = self.top_ten()
        counter = 1
        for page_ids in top_ten_list:
            print(str(counter)+ ": " + self.ids_to_titles[page_ids])
            counter += 1

    """
    Handles the user input and returns a list of up to 10 pages that are most relevant to that input and if the user input is 
    the word quit, the code terminates 

    Parameters: 
    self

    Returns:
    returns a list of up to 10 pages that are most relevant to that input 

    Throws:
    """
    def repl(self):
        while True:
            inputs = input("Search: ").lower()
            if inputs == "quit":
                break
            else:
                self.populate_relevant_pages(inputs)
                self.print_top_ten()
    
if __name__ == "__main__":
    if len(sys.argv) == 4:
        page_rank = False
        query = querier(sys.argv[1],sys.argv[2],page_rank,sys.argv[3])
        query.repl()
    elif len(sys.argv) == 5:   
        page_rank = True
        if (sys.argv[1] == "--pagerank"):
            query = querier(sys.argv[2],sys.argv[3],page_rank,sys.argv[4])
            query.repl()
    


    

