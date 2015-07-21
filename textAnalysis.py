# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 14:29:58 2015

@author: dagrha & ngreeney
"""

from textblob import TextBlob
import pandas as pd
import pylab as plt
import fileinput
import sys

with open (r'lovecraft.txt', 'r') as myfile:
    shunned = myfile.read()

ushunned = unicode(shunned, 'utf-8')

tb = TextBlob(ushunned)

paragraph = tb.sentences[:-120:]

i = -1
for sentence in paragraph:
    i += 1
    sentiment = sentence.sentiment
    if i == 0:
        write_type = 'w'
        with open('shunned.csv', write_type) as text_file:
            header = 'number,' + 'polarity,' + 'subjectivity\n'
            text_file.write(str(header))
    write_type = 'a'
    with open('shunned.csv', write_type) as text_file:
        newline = str(i) + ',' + str(sentiment) + '\n'
        text_file.write(str(newline))

def replace_all(file, search_exp, replace_exp):
    for line in fileinput.input(file, inplace=1):
        if search_exp in line:
            line = line.replace(search_exp,replace_exp)
        sys.stdout.write(line)

replace_all('shunned.csv', 'Sentiment(polarity=', '')
replace_all('shunned.csv', ' subjectivity=', '')
replace_all('shunned.csv', ')', '')

df = pd.DataFrame.from_csv('shunned.csv')

bookTitle = 'HP Lovecraft\'s The Shunned House'
plt.figure()
df.polarity.plot(figsize=(12,5), color='b', title='Sentiment Polarity for\n'+bookTitle)
plt.xlabel('Sentence number')
plt.ylabel('Sentiment polarity')

df['cum_sum'] = df.polarity.cumsum()

plt.figure()
df.cum_sum.plot(figsize=(12,5), color='r', 
                title='Sentiment Polarity cumulative summation for\n'+bookTitle)
plt.xlabel('Sentence number')
plt.ylabel('Sum of Sentiment')

df.head()

df.describe()


for i in df[df.polarity < -0.5].index:
    print i, tb.sentences[i]

