import unittest
from Products.rfasite.tests.test_browser import DummyCatalog

import Products.rfasite.mobapp.browser as browser

class mediaViewTests(unittest.TestCase):
        
    def testInit(self):
        view = browser.MobappMediaView(DummyContext(), DummyRequest())
        
     
class DummyContext(object):
    def getId(self):
        return 'dummy'
    
    def getSubsite(self):
        return DummySubsite()
    
    @property
    def portal_catalog(self):
        portal_catalog = DummyCatalog('foo',
                                      '/',
                                      [],
                                      )    
    
    
class DummyRequest(object):
    
    _form = {} #the get request
    
    @property
    def form(self):
        return self._form
    
class DummyReferenceCatalog(object):
    
    def __init__(self, objects={}):
        self.objects = objects
    
    def lookupObject(self, uid):
        return self.objects[uid]    
    
    
class DummySubsite(DummyContext):
    def __init__(self, refCatalog=DummyReferenceCatalog()):
        self.reference_catalog = refCatalog


