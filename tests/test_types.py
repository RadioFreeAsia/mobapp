import unittest

from dummies import *

from Products.rfasite.mobapp.Types import PhotoGallery

class TestGallery(unittest.TestCase):

    def testInit(self):
        gallery = PhotoGallery()

    def testAddSlideshow(self):
        gallery = PhotoGallery()
        slideshow = DummySlideshow()
        slideshow.contained_objects = [DummyImage(), DummyImage()]
        gallery.addSlideshow(slideshow)
        
        self.assertEqual(gallery.count, 2, "Slideshow should contain 2 images")

