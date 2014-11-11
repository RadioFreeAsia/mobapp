import unittest
from dummies import *

import Products.rfasite.mobapp.browser as browser

class mediaViewTests(unittest.TestCase):
        
    def testInit(self):
        """Just the basics - to construct test framework"""
        view = browser.MobappMediaView(DummyContext(), DummyRequest())
        
    def testItems(self):
        view = browser.MobappMediaView(DummyContext(), DummyRequest())
        items = view.items()
        
        
    def testSlideshow(self):
        view = browser.MobappMediaView(DummyContext(), DummyRequest())
        view.Photos = True
        view.query_photos = lambda: [DummySlideshow()]  #override query_photos method to return a dummy slideshow
        items = view.items()
        
        articles = items['articles']
        self.assertEqual(len(articles), 1, msg="slideshow articles should be list of length 1")
        gallery = articles[0].gallery
        
        iter(gallery) #should be iterable
        
        
    
