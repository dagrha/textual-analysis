# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 10:36:16 2016

@author: ngreeney
"""

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
#from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods import media
from wordpress_xmlrpc.compat import xmlrpc_client

class BlogPost:
    
    def __init__(self,user,password):
        self.wp = Client("http://dataslant.xyz/xmlrpc.php",user,password)
    
    def postDraft(self, title, body):
        '''
        Creates a draft with title and graph
        
        Currently both title and graph are just strings
        '''
        post = WordPressPost()
        post.title = title
        post.content = body
#        post,terms_names = {
#            'post_tag': ['test'],
#            'category': ['testCat']}
        self.wp.call(NewPost(post))

    def uploadJPG(self, filePath):
        data = {
            'name': filePath.split('/')[-1],
            'type': 'image/jpeg',
            }
        
        with open(filePath, 'rb') as img:
            data['bits'] = xmlrpc_client.Binary(img.read())
        response = self.wp.call(media.UploadFile(data))
        return response['id']
        