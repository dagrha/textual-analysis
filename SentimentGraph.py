# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 13:14:19 2015

@author: ngreeney
"""

import bokeh.plotting as bk
import bokeh.models as models
import Book
from bokeh.models.actions import Callback

class SentimentGraph(object):

    def __init__(self):
        bk.output_file("blank.html", title="Sentiment Plot")

        TOOLS = []
        self.sentPlot = bk.figure(title="Sentence Sentiment",
                       x_axis_label="Sentence Number",
                       y_axis_label="Polarity",
                       tools=TOOLS)


        TOOLS = [models.HoverTool(tooltips=[
                                ("Sentence","$index"),
                                ("Sentiment","$y")])]
        self.sumPlot = bk.figure(title="Sentiment Summation",
                       x_axis_label="Sentence Number",
                       y_axis_label="Cumulative Polarity",
                       tools=TOOLS)


    def plotSentence(self,pandaFrames):
        if type(pandaFrames)!=type([]):
            pandaFrames=[pandaFrames]
        for pf in pandaFrames:
            x=list(range(pf['polarity'].size))
            y=pf['polarity']
            self.sentPlot.line(x,y)

        # Add a circle, that is visible only when selected
        source = models.ColumnDataSource({'x': x, 'y': y})
        invisible_circle = models.Circle(x='x', y='y', fill_color='white',
                                         fill_alpha=0.05, line_color=None, size=5)
        visible_circle = models.Circle(x='x', y='y', fill_color='firebrick',
                                       fill_alpha=0.5, line_color=None, size=5)
        cr = self.sentPlot.add_glyph(source, invisible_circle, selection_glyph=visible_circle,
                          nonselection_glyph=invisible_circle)
        # Add a hover tool, that selects the circle
        #code = "source.set('selected', cb_data['index']);"
        #callback = models.Callback(args={'source': source}, code=code)
        self.sentPlot.add_tools(models.HoverTool(tooltips=None,
                                      renderers=[cr], mode='hline'))

    def plotSum(self,pandaFrames):
        if type(pandaFrames)!=type([]):
            pandaFrames=[pandaFrames]
        for pf in pandaFrames:
            self.sumPlot.line(range(pf.cumsum()['polarity'].size),pf.cumsum()['polarity'])
