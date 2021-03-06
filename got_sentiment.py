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
from libepub.book import Book
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
import nltk.tokenize.punkt as punkt
from nltk.tokenize import sent_tokenize, word_tokenize
import nltk.data as nldata
# Numpy - handy arrays
import numpy as np

class BookAnalysis:

    def __init__(self, epub):
        '''
        Pulls all the chapter info from an epub file.
        '''
        ebook = Book(epub)
        self.make_book(ebook)

    def make_book(self,ebook):
        '''
        Breaks epub book into chapters and creates a dictionary called book_dict\n\n
        
        Takes in ebook which is a libepub Book type
        '''
        self.book_dict = collections.OrderedDict()
        for chapter in ebook.chapters:
            soup = BeautifulSoup(chapter.content, 'xml')
            try:
                if soup.h1.attrs['class'] == 'chapter0':
                    chapter_dict = dict()
                    string = str()
                    for tag in soup('p', class_=['indent', 'nonindent']):
                        string += str(tag.get_text()) + ' '
                    string = string.replace('“','"')
                    string = string.replace('”','"')
                    chapter_data = list()
                    chapter_num = soup.h1.attrs['id']
                    chapter_data.append(chapter_num)
                    chapter_author = soup.h1.get_text()
                    chapter_data.append(chapter_author)
                    chapter_data.append(string)
                    page_num = soup.a.attrs['id']
                    chapter_dict[page_num] = chapter_data
                    self.book_dict.update(chapter_dict)
                else:
                    pass
            except AttributeError:
                print('No h1 in {} --- Skipping'.format(soup.div.attrs))
                pass
        self.renumber_prologue()
        self.repack_dict()
        self.dict_to_frame()

    def renumber_prologue(self):
        '''Book is slightly malformed in that it by default labels two chapters as "c01"
        so here I just re-label the prologue as "c00"'''
        self.book_dict['page1'][0] = 'c00'

    def repack_dict(self):
        new_dict = collections.OrderedDict()
        for item in self.book_dict.values():
            new_dict[item[0]]=item[1:]
        self.book_dict = new_dict
        return
    
    def dict_to_frame(self):
        self.pf = pd.DataFrame.from_dict(self.book_dict,orient="index")
        self.pf.columns = ["Character","Text"]
        return
    
    def text_for_character(self,character):
        try:
            temp = self.pf[self.pf.Character == character.upper()]
        except:
            self.dictToFrame()
            temp = self.pf[self.pf.Character == character.upper()]

        text = ''
        chapters = np.array(temp.index)
        chapters.sort()
        for chap in chapters:
            text += temp.loc[chap]['Text'] + '\n\n'
        
        return text
    
    def tokenize(self,text):
        '''
        breaks the dataframe from rows of chapters down to rows of sentences
        '''
        
        trainer = punkt.PunktTrainer()
        trainer.ABBREV = 1.0
        for i in self.pf.Text:
            trainer.train(i,verbose=True,finalize=False)
        param = trainer.get_params()
        
        tok = punkt.PunktSentenceTokenizer(param,True)
        
        return tok.tokenize(text)
    
    def natural(self):
        self.select_chapter()
        '''tokenize - using chapter selected, pull text from dict and feed to NLTK
            NLTK then breaks into sentences then into words ending with 2-d list of words'''
        text = self.book_dict[self.chapter_code][1]
        text = text.replace('?”','? ”').replace('!”', '! ”').replace('.”', '. ”')
        self.nat_analysis = [word_tokenize(t) for t in sent_tokenize(text)]
        
        '''test difference to TextBlob Breakdown of sentences'''
        temp_df = self.single_chapter()
        for i in range(len(self.nat_analysis)):
            x = ''.join(temp_df.iat[i,3].split())
            y = ''.join(self.nat_analysis[i])
            if x!=y:
                print("Difference at:")
                print(x)
                print(y)
                break
        
        return
    
    def blobWholeBook(self):
        '''Create a dataframe and populate the fields with information about each chapter'''
        self.df = pd.DataFrame()
        for chapter in self.book_dict:
            chapter_no = chapter
            author = self.book_dict[chapter][0]
            text = self.book_dict[chapter][1]
            tb = TextBlob(text, analyzer=NaiveBayesAnalyzer())
            chap_df = pd.DataFrame(tb.serialized)
            chap_df['chapter'] = chapter_no
            chap_df['author'] = author
            self.df = pd.concat([self.df, chap_df])

        '''Group the dataframe by chapter, author; run a cumulative summation of the polarity over each group.'''
        self.df.reset_index(drop=True, inplace=True)
        self.df['sent_index'] = self.df.index
        self.df['chap_cumsum'] = self.df.groupby(['chapter'])['polarity'].cumsum()
        self.df['char_cumsum'] = self.df.groupby(['author'])['polarity'].cumsum()
        self.df['book_cumsum'] = self.df['polarity'].cumsum()

    def blobChapter(self):
        '''Create a dataframe and populate the fields with information about the active chapter\n
        Asks for a chapter if there is currently not an active chapter'''
        self.df = pd.DataFrame()
        try:
            chapter = self.chapter_code
        except:
            self.select_chapter()
            chapter = self.chapter_code
        
        chapter_no = chapter
        author = self.book_dict[chapter][0]
        text = self.book_dict[chapter][1]
        tb = TextBlob(text, analyzer=NaiveBayesAnalyzer())
        chap_df = pd.DataFrame(tb.serialized)
        chap_df['chapter'] = chapter_no
        chap_df['author'] = author
        self.df = pd.concat([self.df, chap_df])

        '''Group the dataframe by chapter and run a cumulative summation of the polarity over each chapter.'''
        self.df['chap_cumsum'] = self.df.groupby(['chapter'])['polarity'].cumsum()

    def blobText(self,grouping,text):
        '''Create a dataframe and populate the fields with information passed to method\n\n
        
        grouping = string explaining what the text is, ie. 'Bran', 'Chapters 1-10', etc.\n
        text = raw text to pass to text blob
        '''
        self.df = pd.DataFrame()
        
        chapter_no = '999'
        author = grouping
        tb = TextBlob(text, analyzer=NaiveBayesAnalyzer())
        chap_df = pd.DataFrame(tb.serialized)
        chap_df['chapter'] = chapter_no
        chap_df['author'] = author
        self.df = pd.concat([self.df, chap_df])

        '''Group the dataframe by chapter and run a cumulative summation of the polarity over each chapter.'''
        self.df['chap_cumsum'] = self.df.groupby(['chapter'])['polarity'].cumsum()

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
            self.set_chapter(user_input)

    def event_locator(self, sub_df, text):
        '''Takes the _text_ argument and returns the index of that
        sentence in the given dataframe (_sub_df_ argument) that is 
        closest to the index of the wholeBook dataframe. _sub_df_, 
        for example, could just be the df of a single character, or 
        it could be the entire book. Returns a tuple of the index 
        and the event summary (_event_ argument)'''
        text_filter = self.df.raw.str.contains(text)
        sent_idx = int(self.df[text_filter].sent_index.values)
        sub_sent_idx = int(sub_df.iloc[(sub_df.sent_index - sent_idx).abs().argsort()[:1]].index.values)
        return sub_sent_idx
        
    def set_chapter(self,chap_num):
        self.chapter_code = 'c' + str(user_input).zfill(2)

    def single_chapter(self):
        '''Returns subset of dataframe matching active chapter'''
        return self.df[self.df.chapter == self.chapter_code]
    def get_chardf(self,character):
        char_df = self.df[self.df['author']==character.upper()]
        char_df.reset_index(inplace=True, drop=True)
        return char_df

    def chapter_info(self):
        '''Quick look at the most negative and positive sentences/n
        temp_df is a dataframe for the current active chapter
        '''
        temp_df = self.single_chapter()
        self.info = list()
        print('The most negative sentences are: ')
        self.info.append(temp_df[temp_df.polarity < -0.5][['polarity', 'raw']].values)
        print(self.info[-1])
        print()
        print('The most positive sentences are: ')
        self.info.append(temp_df[temp_df.polarity > 0.5][['polarity', 'raw']].values)
        print(self.info[-1])
        print()

        '''Create a table of summary statistics. Note that any sentence with a polarity
        of 0 has been excluded from the statistics!!'''
        self.info.append(temp_df[temp_df.polarity != 0.0].describe().round(2))
        print(self.info[-1])
        print()

    def plot_html(self): #df, chapter_code):
        '''Create a plot of the cumulative sentiment polarity, show it inline in the notebook,
        and save copies as png and html'''
        temp_df = self.single_chapter()
        self.title = ' '.join(['Chapter',  str(int(self.chapter_code[1:])), '-', temp_df.author.unique()[0],
                          ':', 'NB senitment polarity'])
        png_name = self.chapter_code + '_' + temp_df.author.unique()[0] + '.png'
        html_name = self.chapter_code + '_' + temp_df.author.unique()[0] + '_embed.html'

        TOOLS = "pan,wheel_zoom,reset,save"
        p1 = figure(title=self.title, tools=TOOLS, title_text_font_size='18')

        p1.line(temp_df.index, temp_df['chap_cumsum'])
        p1.line(temp_df.index, temp_df['polarity'])

        show(p1)
        save(p1, png_name, title=self.title, resources=CDN)
        self.html = file_html(p1, CDN, html_name)
        with open(html_name, 'w') as f:
            f.write(self.html)

    def plot_singleChap(self):
        '''Create a plot of the cumulative sentiment polarity and subjectivity and save as JPEG image'''
        temp_df = self.single_chapter()
        try:
            self.title = ' '.join(['Chapter',  str(int(self.chapter_code[1:])), '-', temp_df.author.unique()[0],
                                ':', 'NB senitment polarity'])
            self.filename = self.chapter_code + '_' + temp_df.author.unique()[0] + '.jpg'
        except:
            self.title = "Test"
            self.filename = "test.jpg"

        plt.figure()
        plt.plot(temp_df.index, temp_df['chap_cumsum'], label="Polarity")
        plt.plot(temp_df.index, temp_df['subjectivity'], label="Subjectivity")
        plt.title(self.title)
        plt.xlim(temp_df.index[0], temp_df.index[-1])
        plt.xlabel("Sentence Number")
        plt.ylabel("Cumulative Sentiment Polarity")
        plt.legend(loc="upper left")
        plt.savefig(self.filename, bbox='tight')
        return
        
    def plot_singleChar(self,character):
        '''Plot just the chapters written from a single characters POV/n/n
        
        character = name of chapter example='bran'
        '''
        char_df = self.get_chardf(character)
        
        plt.figure()
        plt.plot(char_df.char_cumsum)
        plt.title('Sentiment Polarity across all {} chapters'.format(character.upper()))
        plt.xlabel('Sentence Number')
        plt.ylabel('Cumulative Sentiment Polarity')
        return
    
    def plot_wholeBook(self):
        '''Plot whole book'''
        plt.figure()
        plt.plot(self.df.book_cumsum.tolist())
        plt.title('Sentiment Polarity across Game of Thrones')
        plt.xlabel('Sentence Number')
        plt.ylabel('Cumulative Sentiment Polarity')
        return

    def add_chapterlines(self,df):
        '''Adds vertical lines at the start of each chapter
        '''
        df['sent_num'] = df.index
        idx = df.groupby('chapter')['start_index'].idxmin()
        chap_bounds = df.loc[idx, ['sent_num','char_cumsum', 'chapter']]
        chap_bound_list = chap_bounds[['sent_num','char_cumsum', 'chapter']].values.tolist()
        
        ylim=plt.ylim()
        for item in chap_bound_list:
            plt.vlines(item[0],ylim[0],ylim[1],'k','dotted')
            plt.text(item[0]+5, ylim[1]*0.97, item[2], fontsize=14)
        return
        
    def add_annot(self, sub_df, event, text, text_height=0.9):
        '''Adds a annotation of _event_ text at the given sentence containing _text_ 
        '''
        event_ix = self.event_locator(sub_df, text)
        event_y=sub_df.loc[event_ix,'char_cumsum']
        ylim = plt.ylim()
        text_y=(ylim[1]-ylim[0])*text_height+ylim[0]
        
        print(text_y)
        plt.annotate(event,(event_ix,event_y),(event_ix,text_y),
                     arrowprops=dict(width=1,headwidth=3))
        return
    
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
        body = '\n'.join([neg_title, self.neg_sentences, pos_title, self.pos_sentences, table_id_string,
                        copy_string, self.info[2].to_html()])
        wp.postDraft(self.title, body)


if __name__ == '__main__':
    '''Load the book as an epub book'''
    got = BookAnalysis(r'books/game.epub')
    
    user_input = input("What to analyze?\nChapter Number, Character Name, else Whole Book:  ")
    try:
        chap_num = int(user_input)
        got.set_chapter(chap_num)
        got.blobChapter()
        got.chapter_info()
#    game_of_thrones.single_chapter() #selected in blobChapter now
    except:
        if user_input.upper() in got.pf['Character'].unique():
            print(user_input+' in Book')
            got.blobWholeBook()
            got.plot_singleChar(user_input)
            got.add_chapterlines(got.get_chardf(user_input))
            
        else:
            print("Blob-ing the whole book")
            got.blobWholeBook()
            got.plot_wholeBook()
            got.add_chapterlines(got.df)
    
    '''NLTK analysis'''
#    game_of_thrones.natural()
    '''Commented out for NLTK testing'''
#    game_of_thrones.plot_html()
#    game_of_thrones.plot_jpg()
#    user_input = input("Start Post? (enter yes):")
#    if user_input == 'yes':
#        game_of_thrones.start_post()
##    game_of_thrones.plot_html()
