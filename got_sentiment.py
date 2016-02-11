# coding: utf-8
# authors: dagrha, ngreeney
# Game of Thrones (Book 1) Sentiment Analysis.
'''This class creates a basic chart and a statistical summary table for a selected
chapter in the novel Game of Thrones (George R.R. Martin). Can upload to WordPress
site automatically.'''

# collections from the Standard Library
import collections
import logging

# libepub (https://github.com/jharjono/libepub/)
from libepub import book
# pandas dataframe library (http://pandas.pydata.org/)
import pandas as pd
# Beautiful Soup (http://www.crummy.com/software/BeautifulSoup/)
from bs4 import BeautifulSoup
# TextBlob (http://textblob.readthedocs.org/en/dev/)
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
# Bokeh plotting library (http://bokeh.pydata.org/en/latest/)
from bokeh.io import show, save
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html
# Matplotlib for jpg
import matplotlib.pyplot as plt
# needs --> pip install python-wordpress-xmlrpc
from blogpost import BlogPost
# NLTK
from nltk.tokenize import sent_tokenize, word_tokenize

class ChapterAnalysis:

    def __init__(self, epub):
        self.epub = book.Book(epub)

    def make_book(self):
        self.book_dict = collections.OrderedDict()
        for chapter in self.epub.chapters:
            self.soup = BeautifulSoup(chapter.content, 'xml')
            try:
                if self.soup.h1.attrs['class'] == 'chapter0':
                    self.chapter_dict = dict()
                    string = str()
                    for tag in self.soup('p', class_=['indent', 'nonindent']):
                        string += str(tag.get_text()) + ' '
                    self.chapter_data = list()
                    chapter_num = self.soup.h1.attrs['id']
                    self.chapter_data.append(chapter_num)
                    chapter_author = self.soup.h1.get_text()
                    self.chapter_data.append(chapter_author)
                    self.chapter_data.append(string)
                    page_num = self.soup.a.attrs['id']
                    self.chapter_dict[page_num] = self.chapter_data
                    self.book_dict.update(self.chapter_dict)
                else:
                    pass
            except AttributeError:
                print('ATTRS missing from h1 =', self.soup.h1)
                pass

    def renumber_prologue(self):
        '''Book is slightly malformed in that it by default labels two chapters as "c01"
        so here I just re-label the prologue as "c00"'''
        self.book_dict['page1'][0] = 'c00'

    def repackDict(self):
        new_dict = {}
        for item in self.book_dict.values():
            new_dict[item[0]]=item[1:]
        self.book_dict = new_dict
        return
    
    def natural(self):
        self.select_chapter()
        '''tokenize - using chapter selected, pull text from dict and feed to NLTK
            NLTK then breaks into sentences then into words ending with 2-d list of words'''
        self.nat_chapter = [word_tokenize(t) for t in sent_tokenize(self.book_dict[self.chapter_code][1])]
        
        '''test difference to TextBlob Breakdown of sentences'''
        for i in range(len(self.nat_chapter)):
            x = ''.join(self.df_chapter.iat[i,3].split())
            y = ''.join(self.nat_chapter[i])
            if x!=y:
                print("Difference at:")
                print(x)
                print(y)
                break
        
        return

    def to_df(self):
        '''Create a dataframe and populate the fields with information about each chapter'''
        self.df = pd.DataFrame()
        for page in self.book_dict:
            chapter_no = self.book_dict[page][0]
            author = self.book_dict[page][1]
            text = self.book_dict[page][2]
            self.tb = TextBlob(text, analyzer=NaiveBayesAnalyzer())
            chap_df = pd.DataFrame(self.tb.serialized)
            chap_df['chapter'] = chapter_no
            chap_df['author'] = author
            self.df = pd.concat([self.df, chap_df])

        '''Group the dataframe by chapter and run a cumulative summation of the polarity over each chapter.'''
        self.df['chapter_cumsum'] = self.df.groupby(['chapter'])['polarity'].cumsum()

    def select_chapter(self):
        '''Get user input for the chapter to examine'''
        user_input = 0
        while True:
            try:
                try: 
                    if self.chapter_code != None:
                        print("Current active Chapter is {}.".format(self.chapter_code),end='')
                except AttributeError:
                    pass
                user_input = int(input("Enter the number of the chapter you'd like to examine: "))
            except ValueError:
                print("Please give an integer instead.")
                print()
                continue
            else:
                print("Chapter %s will be set as active." %user_input)
                print()
                break
        self.chapter_code = 'c' + str(user_input).zfill(2)

    def single_chapter(self):
        '''Choose and create dataframe of just one chapter'''
        self.select_chapter()
        self.df_chapter = self.df[self.df.chapter == self.chapter_code]

    def chapter_info(self):
        '''Quick look at the most negative and positive sentences/n
        df_chapter is a dataframe for a given chapter
        '''
        self.info = list()
        print('The most negative sentences are: ')
        self.info.append(self.df_chapter[self.df_chapter.polarity < -0.5][['polarity', 'raw']].values)
        print(self.info[-1])
        print()
        print('The most positive sentences are: ')
        self.info.append(self.df_chapter[self.df_chapter.polarity > 0.5][['polarity', 'raw']].values)
        print(self.info[-1])
        print()

        '''Create a table of summary statistics. Note that any sentence with a polarity
        of 0 has been excluded from the statistics!!'''
        self.info.append(self.df_chapter[self.df_chapter.polarity != 0.0].describe().round(2))
        print(self.info[-1])
        print()

    def plot_html(self): #df, chapter_code):
        '''Create a plot of the cumulative sentiment polarity, show it inline in the notebook,
        and save copies as png and html'''
        self.single_chapter()
        self.title = ' '.join(['Chapter',  str(int(self.chapter_code[1:])), '-', self.df_chapter.author.unique()[0],
                          ':', 'NB senitment polarity'])
        png_name = self.chapter_code + '_' + self.df_chapter.author.unique()[0] + '.png'
        html_name = self.chapter_code + '_' + self.df_chapter.author.unique()[0] + '_embed.html'

        TOOLS = "pan,wheel_zoom,reset,save"
        p1 = figure(title=self.title, tools=TOOLS, title_text_font_size='18')

        p1.line(self.df_chapter.index, self.df_chapter['chapter_cumsum'])
        p1.line(self.df_chapter.index, self.df_chapter['polarity'])

        show(p1)
        save(p1, png_name, title=self.title, resources=CDN)
        self.html = file_html(p1, CDN, html_name)
        with open(html_name, 'w') as f:
            f.write(self.html)

    def plot_jpg(self):
        '''Create a plot of the cumulative sentiment polarity and subjectivity and save as JPEG image'''
        self.single_chapter()
        self.title = ' '.join(['Chapter',  str(int(self.chapter_code[1:])), '-', self.df_chapter.author.unique()[0],
                                ':', 'NB senitment polarity'])
        self.filename = self.chapter_code + '_' + self.df_chapter.author.unique()[0] + '.jpg'

        plt.figure()
        plt.plot(self.df_chapter.index, self.df_chapter['chapter_cumsum'], label="Polarity")
        plt.plot(self.df_chapter.index, self.df_chapter['subjectivity'], label="Subjectivity")
        plt.title(self.title)
        plt.xlim(self.df_chapter.index[0], self.df_chapter.index[-1])
        plt.xlabel("Sentence Number")
        plt.ylabel("Cumulative Sentiment Polarity")
        plt.legend(loc="upper left")
        plt.savefig(self.filename, bbox='tight')

    def start_post(self):
        '''Post the positive and negative sentences along with the description table to WordPress'''
        password = input('Password:')
        wp = BlogPost('python', password)
        user_input = input("Upload File? (enter yes):")
        if user_input == 'yes':
            wp.uploadJPG(self.filename)
        self.title =  ' '.join(['Chapter',  str(int(self.chapter_code[1:])), '-', self.df_chapter.author.unique()[0],
                                ':', 'NB senitment polarity'])
        self.neg_sentences = str()
        for i in self.info[0]:
            self.neg_sentences += '\t'.join(['%.2f' %float(str(i[0])), i[1], '\n'])
        self.pos_sentences = str()
        for i in self.info[1]:
            self.pos_sentences += '\t'.join(['%.2f' %float(str(i[0])), i[1], '\n'])
        neg_title = '<strong>The most negative sentences are:</strong>'
        pos_title = '\n<strong>The most positive sentences are:</strong>'
        table_id_string = '\n\n[table id=' + self.chapter_code[1:].zfill(3) + ' /]'
        copy_string = "Copy code below to TablePress Import as HTML\nChange ID to " + self.title + "\n"
        self.body = '\n'.join([neg_title, self.neg_sentences, pos_title, self.pos_sentences, table_id_string,
                        copy_string, self.info[2].to_html()])
        wp.postDraft(self.title, self.body)


if __name__ == '__main__':
    '''Load the book as an epub book'''
    game_of_thrones = ChapterAnalysis(r'books/game.epub')
    game_of_thrones.make_book()
    game_of_thrones.renumber_prologue()
    game_of_thrones.to_df()
    game_of_thrones.single_chapter()
    game_of_thrones.chapter_info()
    
    '''NLTK analysis'''
    game_of_thrones.repackDict()
    game_of_thrones.natural()
    '''Commented out for NLTK testing'''
#    game_of_thrones.plot_html()
#    game_of_thrones.plot_jpg()
#    user_input = input("Start Post? (enter yes):")
#    if user_input == 'yes':
#        game_of_thrones.start_post()
##    game_of_thrones.plot_html()
