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
    '''python3 syntax:'''
    def read_book(self):
        with open(self.filename, 'r') as t:
            self.reader = t.read()
            return self.reader
    '''python2 syntax:'''
    #def read_book(self):
    #    with open(self.filename, 'r') as t:
    #        self.reader = t.read()
    #        return unicode(self.reader)

    def textblobify(self):
        self.read_book()
        self.tb = TextBlob(self.reader)
        return self.tb

    def sentimentify(self):
        self.textblobify()
        paragraph = self.tb.sentences
        i = -1
        for sentence in paragraph:
            i += 1
            pol = sentence.sentiment.polarity
            if i == 0:
                with open('temp.csv', 'w') as text_file:
                    header = 'number,' + 'polarity,' + '\n'
                    text_file.write(str(header))
            with open('temp.csv', 'a') as text_file:
                newline = str(i) + ',' + str(pol) + '\n'
                text_file.write(str(newline))
        self.df = pd.DataFrame.from_csv('temp.csv')
        return self.df

    def count_words(self, n):
        '''interger n for the nth most common words'''
        words = re.findall(r'\w+', open(self.filename).read().lower())
        common = collections.Counter(words).most_common(n)
        self.df_freq = pd.DataFrame(common, columns=['word', 'freq'])
        self.df_freq.set_index('word').head(n)
        return self.df_freq
