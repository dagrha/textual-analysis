# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 14:29:58 2015

@author: dagrha & ngreeney
"""

from textblob import TextBlob
import pandas as pd
import pylab as plt
import collections
import re

with open (r'lovecraft.txt', 'r') as myfile:
    shunned = myfile.read()

ushunned = unicode(shunned, 'utf-8')

tb = TextBlob(ushunned)

paragraph = tb.sentences[:-120:]

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

book_title = 'HP Lovecraft\'s The Shunned House'
plt.figure()
df.polarity.plot(figsize=(12,5), color='b', title='Sentiment Polarity for\n'+book_title)
plt.xlabel('Sentence number')
plt.ylabel('Sentiment polarity')

df['cum_sum'] = df.polarity.cumsum()

plt.figure()
df.cum_sum.plot(figsize=(12,5), color='r', 
                title='Sentiment Polarity cumulative summation for\n'+book_title)
plt.xlabel('Sentence number')
plt.ylabel('Sum of Sentiment')

df.head()
df.describe()

for i in df[df.polarity < -0.5].index:
    print i, tb.sentences[i]

words = re.findall(r'\w+', open('lovecraft.txt').read().lower())
common = collections.Counter(words).most_common(10)

df_freq = pd.DataFrame(common, columns=['word', 'freq'])
df_freq.set_index('word').head()