# # -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 14:29:58 2015

@author: dagrha & ngreeney
"""

from textblob import TextBlob
import pandas as pd
#import pylab as plt
import bokeh.plotting as bk
import bokeh.models as models
from bokeh.models import CustomJS
import collections
import re


def readBook(book_text):
    with open (book_text, 'r') as book:
        reader = book.read()
    return reader

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
    TOOLS = ['save']
    
    p1 = bk.figure(title="Sentence Polarity",
                   x_axis_label="Sentence Number",
                   y_axis_label="Polarity",
                   tools=TOOLS)
    x=range(pandaFrame['polarity'].size)
    y=pandaFrame['polarity']
    p1.line(x,y)
    
    
    # Add a circle, that is visible only when selected
    source = models.ColumnDataSource({'x': x, 'y': y})
    invisible_circle = models.Circle(x='x', y='y', fill_color='white',
                                     fill_alpha=0.05, line_color=None, size=5)
    visible_circle = models.Circle(x='x', y='y', fill_color='firebrick',
                                   fill_alpha=0.5, line_color=None, size=5)
    cr = p1.add_glyph(source, invisible_circle, selection_glyph=visible_circle,
                      nonselection_glyph=invisible_circle)    
    # Add a hover tool, that selects the circle
    code = "source.set('selected', cb_data['index']);"
    custJS = CustomJS(args={'source': source}, code=code)
    p1.add_tools(models.HoverTool(tooltips=None, callback=custJS,
                                  renderers=[cr], mode='hline'))
    return p1

def sumPlot(pandaFrame):
    bk.output_file("test.html", title="Sentiment on Bokeh")
    TOOLS = ['save',models.HoverTool(tooltips=[
                                ("Sentence","$index"),
                                ("Sentiment","$y")])]
    
    p1 = bk.figure(title="Cumulative Polarity",
                   x_axis_label="Sentence Number",
                   y_axis_label="Polarity",
                   tools=TOOLS)
    p1.line(range(df.cumsum()['polarity'].size),df.cumsum()['polarity'])
    return p1

def analyze(df):
#    df.head()
#    df.describe()
    
    for i in df[df.polarity < -0.5].index:
        print (i, tb.sentences[i])
    
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
    bk.show(bk.vplot(p1,p2))
    
    
    