# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 10:36:16 2016

@author: ngreeney
"""

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo

class BlogPost:
    
    def __init__(self,user,password):
        self.wp = Client("http://dataslant.xyz/xmlrpc.php",user,password)
    
    def postGraph(self, title, graph):
        '''
        Creates a draft with title and graph
        
        Currently both title and graph are just strings
        '''
        post = WordPressPost()
        post.title = title
        post.content = graph
#        post,terms_names = {
#            'post_tag': ['test'],
#            'category': ['testCat']}
        self.wp.call(NewPost(post))

