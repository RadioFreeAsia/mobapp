"""classes for simulating content and plone utilities"""
from Products.rfasite.tests.test_browser import DummyCatalog


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
    
class DummySlideshow(DummyContext):
    portal_type = "Slideshow"
    def __init__(self):
        self.contained_objects = [] #typically, these would be images
    
    def __iter__(self):
        return iter(self.contained_objects)
    
    def values(self):
        return self.contained_objects
    
class DummyImage(DummyContext):
    pass
    
    
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