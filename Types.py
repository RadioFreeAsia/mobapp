""" Glue together Plone schema with mobapp / pangea types.
    This maps, for example, an RFA 'story' to a BBG "Article"
"""

import datetime
from pytz import timezone, utc

import urlparse
from os.path import basename

from zope.component import getMultiAdapter

from Acquisition import aq_inner,aq_parent
from Products.CMFCore.utils import getToolByName
from AccessControl import allow_class

from Products.rfasite.interfaces import IAllowed
from Products.rfasite.interfaces import IImage, ISlideshow

import utils

def format_date(date):

    #Totally fake the time zone.  strftime %Z seems broken, or I'm just confusing DateTime's with datetime's

    #Time Zone support here is really, totally broken.  Yes, I know.

    #Are we a datetime or a DateTime?
    if hasattr(date, 'utcdatetime'): #we are a Zope DateTime!
        utcdate = date.utcdatetime()

    else: #we are a python datetime!
        utcdate = date

    utcdatestr = date.strftime("%a, %d %b %Y %H:%M:%S")
    utcdatestr += " UTC"

    return utcdatestr

class Placeholder_Article(object):
    """A representation of a "Null" Article"""
    default_id = "_placeholder_id"

    def __init__(self):
        pass
    def id(self):
        return self.default_id
    def zone(self):
        return 0
    def pubDate(self):
        return format_date(datetime.datetime(1900,1,1,0,0))
    def url(self):
        return None
    def twitter(self):
        return None
    def title(self):
        return "placeholder article"
    def content(self):
        return "placeholder article"
    def audio(self):
        return None
    def video(self):
        return None
    def image(self):
        return None
    def authors(self):
        return []


class Placeholder_Author(object):
    """A representation of a "Null" Author"""
    #This should really never happen, but it's used when Plone returns "None" for a lookup on an author id.

    def getUser(self):
        class fakeuser(object):
            def getId(self):
                return "None"

        return fakeuser()

    def getProperty(self, prop):
        return ""


class AudioClip(object):
    def __init__(self, ploneObj=None, streamerSegment=None):
        if not any([ploneObj, streamerSegment]):
            raise ValueError, "must provide either ploneObj or streamerSegment to AudioClip init"

        self.obj = ploneObj
        self.segment = streamerSegment

    def __filename(self):
        if self.obj:
            return self.obj.id
        else:
            parsed = urlparse.urlparse(self.segment['url'])
            return basename(parsed.path)

    def id(self):
        if self.obj:
            return self.obj.UID()
        else:
            return self.__filename()

    def duration(self):
        #TODO: Figure out a way to get the 'duration' of an audio clip.
        return 0

    def url(self):
        if self.obj:
            return self.obj.absolute_url()
        else:
            return self.segment['streaming_url']

    def date(self):
        if self.obj:
            if self.obj.effective().year() > 2000:
                date = self.obj.effective()
            else:
                date = self.obj.created()

        else:
            date = datetime.datetime(int(self.segment['year']), int(self.segment['month']), int(self.segment['day']),
                                     int(self.segment['hour']), int(self.segment['minute']))

        return format_date(date)

    def datelocal(self):
        return None

    def title(self):
        if self.obj:
            return self.obj.Title()
        else:
            return ('%(year)s/%(month)s/%(day)s - '
                    '%(hour)s:%(minute)s %(lang)s' % self.segment)

    def description(self):
        if self.obj:
            return self.obj.Description()
        else:
            return self.title()

    def audioType(self):
        #type of audio (c-clip, f-feature or b-broadcastProgram)
        if self.segment:
            return 'b'
        else:
            return 'c'

    def mime(self):
        mt_tool = getToolByName(self.obj.getSubsite(), "mimetypes_registry")
        return mt_tool.lookupExtension(self.__filename())

class Image(object):

    def __init__(self, imgObj, order=0):
        self.obj = imgObj
        self.order = None
        self._parent = None

    def id(self):
        return self.obj.UID()

    def type(self):
        return self.obj.get_content_type()

    def url(self):
        return self.obj.absolute_url()

    def title(self):
        title = self.obj.getCaption()
        if not title:
            title = self.obj.Description() #aka 'alt text'
        if not title:
            return None
        else:
            return title

    def width(self):
        return self.obj.width

    def height(self):
        return self.obj.height

    def description(self):
        return self.obj.CaptionOrTitle()

    def _article_parent(self):
        """Returns None if image has no parent that's a Story
           Otherwise, return the story this image is contained within
        """
        if self._parent is not None:
            return self._parent

        #There MUST be a better way to do this...
        obj = self.obj
        while obj is not None \
                  and getattr(obj, 'portal_type', None) is not None \
                  and obj.portal_type != "Story":

            obj = aq_parent(aq_inner(obj))

        if  getattr(obj, 'portal_type', None) is None:
            return Placeholder_Article()
        else:
            return _Article(obj)

    def _article_parent_id(self):
        return self._article_parent().id()

class PhotoGallery(object):
    def __init__(self, obj=[], g_id="NaN", title=""):
        self.count = 0
        self._images = list()
        if ISlideshow.providedBy(obj):
            if g_id=="NaN":
                g_id = obj.UID()
            if title=="":
                title = obj.Title()
            self.addSlideshow(obj)
        elif IImage.providedBy(obj):
            self.addImage(obj)

        else:
            for image in obj:
                if IImage.providedBy(image):
                    self.addImage(image)

        self.id = g_id
        self.title=title
        self.obj = obj

    def __getitem__(self, index):
        return self._images[index]

    def __len__(self):
        return len(self._images)

    #def __iter__(self):
    #   pass

    def photos(self):
        return self._images

    def addImage(self, image):
        image.order=self.count
        self._images.append(image)
        self.count += 1

    def addSlideshow(self, slideshow):
        for image in slideshow.values():
            self.addImage(image)

    def setId(self, g_id):
        self.id = g_id

    def _article_parent(self):
        """Returns None if PhotoGallery has no parent that's a Story
           Otherwise, return the story this slideshow is contained within
        """
        if self._parent is not None:
            return self._parent

        #There MUST be a better way to do this...
        obj = self.obj
        while obj is not None \
                  and getattr(obj, 'portal_type', None) is not None \
                  and obj.portal_type != "Story":

            obj = aq_parent(aq_inner(obj))

        if  getattr(obj, 'portal_type', None) is None:
            return Placeholder_Article()
        else:
            return _Article(obj)

    def _article_parent_id(self):
        return self._article_parent().id()

class _Article(Placeholder_Article):

    def __init__(self, obj, request=None):
        self.obj = obj
        self.request = request

    #oops, overridden built-in func 'id'.  beware.
    def id(self):
        return self.obj.UID()

    def zone(self):
        return aq_parent(self.obj).UID()

    @property
    def pubDate(self):
        return format_date(self.obj.effective())

    def url(self):
        return self.obj.absolute_url()

    def twitter(self):
        ##TODO: add url shortening.
        return self.url()

    def title(self):
        return self.obj.Title()

    def content(self):
        return utils.cleanHtml(self.obj.text())

    def audios(self):
        ###XXX IAllowed not working here
        #ac_allowed = IAllowed(self.obj.getAudioClip())
        #audio_obj = ac_allowed.allowedOrNone()

        clips = self.obj.getAudioClip()

        if clips:
            return [AudioClip(clip) for clip in clips]
        else:
            return []

    def audio(self):
        """For those who want only one audio clip"""
        clips = self.audios()
        if clips:
            return clips[0]
        else:
            return None

    def video(self):
        return None
        #return Video(self.obj.getVideoClip())

    def image(self):
        imgObj = self.obj.getFeaturedImage()
        if imgObj is None:
            return None

        scales = getMultiAdapter((imgObj, self.request), name='images')
        scaled = scales.scale('image', direction="down", width=400)

        return Image(scaled)

    def authors(self):
        """an author is a dictionary containing keys 'first', 'middle', 'last', 'email', 'id'
           this returns an iterable of authors
        """

        authors = []
        if hasattr(self.obj, "getByline") and self.obj.getByline():
            authors.append({"id": None,
                            "first": None,
                            "middle": None,
                            "last": self.obj.getByline(),
                            "email": None,
                            "description": None,
                            })

        if len(authors):
            return authors
        else:
            return None

allow_class(_Article)

class ArticleFactory(object):
    def __init__(self, lookupObj_func, request=None):
        self.getObject = lookupObj_func
        self.request = request

    def makeArticle(self, uid=None, obj=None, request=None):
        #if uid and object are both none, throw an exception.
        if uid is not None:
            obj = self.getObject(uid)
            obj = aq_inner(obj)
            if obj is None:
                return None
        elif obj is None:
            raise TypeError, "makeArticle takes a non-None uid or object argument"

        if request is None:
            request = self.request

        return _Article(obj, request=request)

    def __call__(self, uid=None, obj=None, request=None):
        return self.makeArticle(uid, obj, request)