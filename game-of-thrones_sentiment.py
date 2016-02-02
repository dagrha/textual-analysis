# coding: utf-8
# author: dagrha
# Game of Thrones (Book 1) Sentiment Analysis.
'''This script creates a basic chart and a statistical summary table for a selected
chapter in the novel Game of Thrones (George R.R. Martin)'''

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
#
from blogpost import BlogPost

def soup(bk):
    '''Instantiate BeautifulSoup objects, parse epub xml, and create an ordered dictionary of
    the book, with each entry being a chapter.  Keys to dictionary will be the page number
    of the first page of the chapter'''
    book_dict = collections.OrderedDict()
    for chapter in bk.chapters:
        soup = BeautifulSoup(chapter.content, 'xml')
        try:
            if soup.h1.attrs['class'] == 'chapter0':
                chapter_dict = {}
                string = ""
                for tag in soup('p', class_=['indent', 'nonindent']):
                    string += str(tag.get_text()) + ' '
                chapter_data = []
                chapter_num = soup.h1.attrs['id']
                chapter_data.append(chapter_num)
                chapter_author = soup.h1.get_text()
                chapter_data.append(chapter_author)
                chapter_data.append(string)
                page_num = soup.a.attrs['id']
                chapter_dict[page_num] = chapter_data
                book_dict.update(chapter_dict)
            else:
                pass
    
        except AttributeError:
            #ogging.exception('There has been an exception. Probably tried to load the front-or back-matter, which does not have attr tags.')
            print('ATTRS missing from h1 =',soup.h1)
            pass
    
    '''Book is slightly malformed in that it by default labels two chapters as "c01"
    so here I just re-label the prologue as "c00"'''
    book_dict['page1'][0] = 'c00'
    
    return book_dict
    
def frame(book_dict):
    '''Create a dataframe and populate the fields with information about each chapter'''
    df = pd.DataFrame()
    for page in book_dict:
        #page_no = page
        chapter_no = book_dict[page][0]
        author = book_dict[page][1]
        text = book_dict[page][2]
        tb = TextBlob(text, analyzer=NaiveBayesAnalyzer())
        chap_df = pd.DataFrame(tb.serialized)
        chap_df['chapter'] = chapter_no
        chap_df['author'] = author
        df = pd.concat([df, chap_df])
    
    
    '''Group the dataframe by chapter and run a cumulative summation of the polarity over each chapter.'''
    df['chapter_cumsum'] = df.groupby(['chapter'])['polarity'].cumsum()
    
    
    '''Get user input for the chapter to examine'''
    user_input = 0
    while True:
        try:
            print()
            user_input = int(input("Enter the number of the chapter you'd like to examine: "))
        except ValueError:
            print("Please give an integer instead.")
            print()
            continue
        else:
            print("Ok, thanks. I'll return a dataframe of information for chapter %s." %user_input)
            print()
            break
    
    chapter_code = 'c' + str(user_input).zfill(2)
    return df, chapter_code

def singleChapter(df,chapter_code):
    '''return dataframe of just the chapter chosen'''
    return df[df.chapter == chapter_code]

def chapterInfo(df_chap):
    '''Quick look at the most negative and positive sentences/n
    df_chap is a given chapter dataframe
    '''
    print('The most negative sentences are: ')
    print(df_chap[df_chap.polarity < -0.5][['polarity', 'raw']].values)
    print()
    print('The most positive sentences are: ')
    print(df_chap[df_chap.polarity > 0.5][['polarity', 'raw']].values)
    print()
    
    '''Create a table of summary statistics. Note that any sentence with a polarity
    of 0 has been excluded from the statistics!!'''
    print(df_chap[df_chap.polarity != 0.0].describe().round(2))
    print()
    return
    
def plotHTML(df,chapter_code):
    '''Create a plot of the cumulative sentiment polarity, show it inline in the notebook,
    and save copies as png and html'''
    df_chap = singleChapter(df,chapter_code)
    title = ' '.join(['Chapter',  str(int(chapter_code[1:])), '-', df_chap.author.unique()[0],
                      ':', 'NB senitment polarity'])
    png_name = chapter_code + '_' + df_chap.author.unique()[0] + '.png'
    html_name = chapter_code + '_' + df_chap.author.unique()[0] + '_embed.html'
    
    TOOLS = "pan,wheel_zoom,reset,save"
    p1 = figure(title = title, tools=TOOLS,title_text_font_size='18')
    
    p1.line(df_chap.index, df_chap['chapter_cumsum'])
    p1.line(df_chap.index, df_chap['polarity'])
    
    show(p1)
    save(p1, png_name, title=title, resources=CDN)
    html = file_html(p1, CDN, html_name)
    with open(html_name, 'w') as f:
        f.write(html)
    return

def plotJPG(df,chapter_code):
    '''Create a plot of the cumulative sentiment polarity, show it inline in the notebook,
    and save copies as png and html'''
    df_chap = singleChapter(df,chapter_code)
    title = ''.join(['Chapter ',  str(int(chapter_code[1:])), '-', df_chap.author.unique()[0]])
    filename = chapter_code + '_' + df_chap.author.unique()[0] + '.jpg'
    
    plt.figure()
    plt.plot(df_chap.index, df_chap['chapter_cumsum'],label="Polarity")
    plt.plot(df_chap.index, df_chap['subjectivity'],label="Subjectivity")
    plt.title(title)
    plt.xlim(df_chap.index[0],df_chap.index[-1])
    plt.xlabel("Sentence Number")
    plt.ylabel("Cumulative Sentiment Polarity")
    plt.legend(loc="upper left")
    plt.savefig(filename, bbox='tight',)
    return filename

def postImage(file):
    password = input('Password:')
    wp = BlogPost('python', password)
    wp.uploadJPG(file)
    return


if __name__ == '__main__':
    '''Load the book as an epub book'''
    game_of_thrones = book.Book(r'books/game.epub')
    
    book_dict = soup(game_of_thrones)
    df, chapter = frame(book_dict)
    chapterInfo(singleChapter(df,chapter))
    filename = plotJPG(df,chapter)
    
    user_input = input("Upload Image? (enter yes):")
    if user_input == 'yes':
        postImage(filename)
#    plotHTML(df,chapter)
