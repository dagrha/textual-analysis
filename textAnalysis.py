# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 14:29:58 2015

@author: dagrha & ngreeney
"""

from textblob import TextBlob
import pandas as pd
#import pylab as plt
import bokeh.plotting as bk
import collections
import re


def readBook(book_text):
    with open (book_text, 'r') as book:
        reader = book.read()
    return unicode(reader, 'utf-8')

def sentiment(textblob):
    '''
    analyzer used : pattern
    '''
    paragraph = textblob.sentences
    i = -1
    for sentence in paragraph:
        i += 1
        pol = sentence.sentiment.polarity
        if i == 0:
            write_type = 'w'
            with open('shunned.csv', write_type) as text_file:
                header = 'number,' + 'polarity,' + '\n'
                text_file.write(str(header))
        write_type = 'a'
        with open('shunned.csv', write_type) as text_file:
            newline = str(i) + ',' + str(pol) + '\n'
            text_file.write(str(newline))
        df = pd.DataFrame.from_csv('shunned.csv')
    return df

#def graph(pandaFrame):
#    '''
#    hard coded ploting - polarity and sum of polarity plots
#    '''
#    book_title = 'HP Lovecraft\'s The Shunned House'
#    plt.figure()
#    pandaFrame.polarity.plot(figsize=(12,5), color='b', 
#                              title='Sentiment Polarity for\n'+book_title)
#    plt.xlabel('Sentence number')
#    plt.ylabel('Sentiment polarity')
#    
#    pandaFrame['cum_sum'] = pandaFrame.polarity.cumsum()
#    
#    plt.figure()
#    pandaFrame.cum_sum.plot(figsize=(12,5), color='r', 
#                            title='Sentiment Polarity cumulative summation for\n'
#                            +book_title)
#    plt.xlabel('Sentence number')
#    plt.ylabel('Sum of Sentiment')
#    return
    
def sentencePlot(pandaFrame):
    bk.output_file("test.html", title="Sentiment on Bokeh")
    
    p1 = bk.figure(title="Fig Title",
                   x_axis_label="Sentence Number",
                   y_axis_label="Polarity")
    p1.line(range(pandaFrame['polarity'].size),pandaFrame['polarity'])
    return p1

def sumPlot(pandaFrame):
    bk.output_file("test.html", title="Sentiment on Bokeh")
    
    p1 = bk.figure(title="Fig Title",
                   x_axis_label="Sentence Number",
                   y_axis_label="Polarity")
    p1.line(range(df.cumsum()['polarity'].size),df.cumsum()['polarity'])
    return p1

def analyze(df):
#    df.head()
#    df.describe()
    
    for i in df[df.polarity < -0.5].index:
        print i, tb.sentences[i]
    
    words = re.findall(r'\w+', open('lovecraft.txt').read().lower())
    common = collections.Counter(words).most_common(10)
    
    df_freq = pd.DataFrame(common, columns=['word', 'freq'])
    df_freq.set_index('word').head()

    return

if __name__ == '__main__':
    tb = TextBlob(readBook('lovecraft.txt'))
    df = sentiment(tb)
    
#    graph(df)
    analyze(df)
    
    p1 = sentencePlot(df)
    p2 = sumPlot(df)
    bk.show(bk.VBox(p1,p2))
    
    
    