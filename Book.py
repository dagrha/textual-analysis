# python3

from textblob import TextBlob
'''
NTLK capabilities also need to be installed:
run `python -m textblob.download_corpora` from the command line
to install.
'''
import pandas as pd
import collections
import re

class Book:

    kind = 'book'

    def __init__(self, filename, **kwargs):
        self.filename = filename
        self.read_book()
    '''python3 syntax:'''
    def read_book(self):
        with open(self.filename, 'r') as t:
            bookString = t.readline()
            self.to_textblob(bookString)
    '''python2 syntax:'''
    #def read_book(self):
    #    with open(self.filename, 'r') as t:
    #        self.reader = t.read()
    #        return unicode(self.reader)

    def to_textblob(self,text):
        self.tb = TextBlob(text)

    def to_pandas(self):
        self.df = pd.DataFrame(self.tb.serialized)
    
    def get_textblob(self):
        return self.tb
    def get_pandas(self):
        return self.df

    def common_words(self, n):
        '''integer n for the nth most common words'''
        words = re.findall(r'\w+', open(self.filename).read().lower())
        common = collections.Counter(words).most_common(n)
        self.df_freq = pd.DataFrame(common, columns=['word', 'freq'])
        self.df_freq.set_index('word').head(n)
        return self.df_freq
