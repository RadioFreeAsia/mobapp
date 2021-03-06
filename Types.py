""" Glue together Plone schema with mobapp / pangea types.
    This maps, for example, an RFA 'story' to a BBG "Article"
"""

import datetime
from pytz import timezone
from pytz import UTC

import urlparse
from os.path import basename

from zope.component import getMultiAdapter

from Acquisition import aq_inner,aq_parent
from Products.CMFCore.utils import getToolByName
from AccessControl import allow_class

from Products.rfasite.interfaces import IAllowed
from Products.rfasite.interfaces import IImage, ISlideshow
from rfa.kaltura.interfaces import IKalturaVideo

import utils

def format_date(date, tzinfo=None):

    ### TODO: calling this function with the Plone default datetime (year=1000)
    ### will generate exceptions.  This case must be handled
    ### This can be aggrivated by requesting an article that does not exist, 
    ### through articles.xml view, among other ways.

    #Are we a datetime or a DateTime?
    if hasattr(date, 'utcdatetime'): #we are a Zope DateTime!
        date = date.utcdatetime()

    #else: #we are a python datetime!
    #    date = date

    #calling this function 'naive' will attach a UTC timezone
    if date.tzinfo is None and tzinfo is None:
        date = UTC.localize(date)

    #calling this function with a tzinfo arg will:
    elif tzinfo is not None:
        if date.tzinfo is None: #localize an existing naive datetime
            date = tzinfo.localize(date)
        else: #convert a non-naive datetime into the provided timezone
            date = date.astimezone(tzinfo)

    if date.tzinfo.tzname(date) is not None:
        return date.strftime("%a, %d %b %Y %H:%M:%S %Z")
    else: #we only have a UTC offset
        return date.strftime("%a, %d %b %Y %H:%M:%S %z")

class Placeholder_Article(object):
    """A representation of a "Null" Article"""
    default_id = "_placeholder_id"
    placeholder = True

    def __init__(self):
        self._pubDate = None
        self._title = None
        self._content = None
        self._id = None
        self._url = None
    
    @property
    def id(self):
        if self._id is None:
            return self.default_id
        else:
            return self._id
        
    @id.setter
    def id(self, value):
        self._id = value
    
    def zone(self):
        return 0
    
    @property
    def pubDate(self):
        if self._pubDate is None:
            return format_date(datetime.datetime(1900,1,1,0,0))
        else:
            return format_date(self._pubDate)
    
    @pubDate.setter
    def pubDate(self, datetime_value):   
        self._pubDate = datetime_value    
        
    @property
    def url(self):
        #written this way for readability & maintainability, don't change.
        if self._url is None:
            return None
        else:
            return self._url
        
    @url.setter
    def url(self, value):
        self._url = value
    
    def twitter(self):
        return None
    
    @property
    def title(self):
        if self._title is None:
            return "placeholder article"
        else:
            return self._title
        
    @title.setter
    def title(self, value):
        self._title = value
    
    @property
    def content(self):
        if self._content is None:
            return "placeholder article"
        else:
            return self._content
    
    @content.setter
    def content(self, value):
        self._content = value
    
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

    placeholder = True

    def getUser(self):
        class fakeuser(object):
            def getId(self):
                return "None"

        return fakeuser()

    def getProperty(self, prop):
        return ""


class AudioClip(object):
    def __init__(self, ploneObj=None, streamerSegment=None, localTz=None):
        if not any([ploneObj, streamerSegment]):
            raise ValueError, "must provide either ploneObj or streamerSegment to AudioClip init"

        self.obj = ploneObj
        self.segment = streamerSegment
        self.localTz = localTz

    def __filename(self):
        if self.obj:
            try:
                return self.obj.getFilename()
            except AttributeError:
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
        return 5400 #90 mins - just a non-zero number

    def url(self):
        if self.obj:
            url = self.obj.absolute_url()
            if not url.endswith(".mp3"):
                url +="?f="+self.obj.getFilename()
            return url
        else:
            return self.segment['streaming_url']

    def _dateUTC(self):
        if self.obj:
            if self.obj.effective().year() > 2000:
                date = self.obj.effective()
            else:
                date = self.obj.created()

        else:
            date = self.segment['filedate']

        return date

    def date(self):
        return format_date(self._dateUTC())

    def datelocal(self):
        if self.obj:
            return None #TODO
        else:
            localdate = self._dateUTC().astimezone(self.localTz)
            return format_date(localdate)

    def title(self):
        if self.obj:
            return self.obj.Title()
        else:
            return self.segment['lang']

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
        try:
            return self.obj.getContentType()
        except AttributeError:
            mt_tool = getToolByName(self.obj.getSubsite(), "mimetypes_registry")
            return mt_tool.lookupExtension(self.__filename())


class Media(object):
    _parent = None

    def __init__(self):
        raise NotImplementedError, "Can't instantiate abstract parent 'media'"

    @property
    def article_parent(self):
        """Returns a Placeholder_Article if Media has no parent that's a Story
           Otherwise, return the story this Media object is contained within
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
            self._parent = Placeholder_Article()
        else:
            self._parent = _Article(obj)
        return self._parent

    @property
    def article_parent_id(self):
        return self.article_parent.id

class Image(Media):

    def __init__(self, imgObj, order=0):
        self.obj = imgObj
        self.order = None

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

class PhotoGallery(Media):
    def __init__(self, obj=[], g_id="NaN", title=""):
        self._images = list()
        self.id = g_id
        self.title=title
        self.obj = obj

        if ISlideshow.providedBy(obj):
            if g_id=="NaN":
                self.id = obj.UID()
            if title=="":
                self.title = obj.Title()
            self.addSlideshow(obj)
        elif IImage.providedBy(obj):
            self.addImage(obj)
        else:
            for image in obj:
                if IImage.providedBy(image):
                    self.addImage(image)

    def __getitem__(self, index):
        return self._images[index]

    def __len__(self):
        return self.count

    def __iter__(self):
        #thread safe? you wish!
        i=0
        while i < self.count:
            yield self._images[i]
            i+=1
        raise StopIteration

    def photos(self):
        return self._images

    def addImage(self, image):
        image.order=self.count
        self._images.append(image)

    @property
    def count(self):
        return len(self._images)

    def addSlideshow(self, slideshow):
        ### check slideshow values to make sure they are plone image type.
        for ATimage in slideshow.values():
            image = Image(ATimage)
            self.addImage(image)

    def mergeGallery(self, gallery):
        """provided another PhotoGallery type, merge it into this one"""
        if gallery is self:
            raise AssertionError, "merging with yourself is not really a good idea.  If you really meant to do this, use copy()"

        for image in gallery:
            self.addImage(image)

    def setId(self, g_id):
        self.id = g_id



class Video(Media):
    """Mobapp representation of a video"""
    def __init__(self, obj):
        self.obj = obj
        self.kalturaObj = getattr(self.obj, 'KalturaObject', None)
        
        #if we are a video within a bogus 'placeholder' article, 
        #set attributes on the placeholder to make the mobile app work correctly.
        if self.article_parent.placeholder:
                
            self.article_parent.title = self.title()
            self.article_parent.content = None
            self.article_parent.id = self.guid()
            self.article_parent.url = self.vidpageUrl()
            
            #try using the date from plone video object.
            if self.obj.effective().year() > 1000:  #if it's not set, year will be 1000
                self.article_parent.pubDate = self.obj.effective()
            else:
                #use the date in the kalturaObject
                self.article_parent.pubDate = datetime.datetime.fromtimestamp(self.kalturaObj.getUpdatedAt())
            
                
    def id(self):
        return self.guid()

    def relType(self):
        """Defines relation between article and video => 0=SameItem, 1=MainImage,2=EmbededInContent"""
        #if this video is wrapped in a placeholder, then it's a stand-alone video and should be considered 'sameItem'
        if self.article_parent.placeholder:
            return 0
        
        return 2 #otherwise, it's a video embedded in a story

    def duration(self):
        """Duration of the video data (seconds)"""
        return 600 #XXX TODO

    def width(self):
        """Width (pixels) of the video"""
        return 176 #XXX TODO

    def height(self):
        """Height (pixels) of the video"""
        return 144 #XXX TODO

    def url(self):
        """Location of the video file"""
        if self.kalturaObj:
            return self.kalturaObj.dataUrl
        else:
            return None
        
    def vidpageUrl(self):
        #XXX does not support dynamic video page name
        #XXX makes assumption that video page is always
        # rfa.org/language/video
        base = self.obj.getSubsite().absolute_url()
        url = base + '/video' + '?v={entryId}'
        
        return url.format(entryId=self.kalturaObj.getId())

    def date(self):
        """Publication date"""
        return datetime.datetime.now() ###TODO
        #return self.article_parent.pubDate(date)

    def title(self):
        """Title of the video item"""
        return self.obj.Title()

    def description(self):
        """Description for the video item"""
        return self.obj.Description()

    def guid(self):
        return self.obj.UID()
    
    def thumbnail(self):
        url = self.kalturaObj.getThumbnailUrl()
        return url

class _Article(Placeholder_Article):

    placeholder = False

    def __init__(self, obj, request=None):
        self.obj = obj
        self.request = request
        self._gallery = None
        self._video = None

    @property
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
        renderedText = self.obj.getText()
        return utils.cleanHtml(renderedText)
    
    def intro(self):
        return self.obj.Description()

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
        """return a single kalturaVideo as a Video within the cp_container body slot"""
        #Videos are embedded via the Layout Tab, so we must journey into cp_container to find it.
        cp = getattr(self.obj, 'cp_container', None)
        if cp is None:
            return None

        if self._video is not None:
            return self._video

        slot = cp.filled_slots['body']
        for elem in slot.values():
            obj = elem.getTarget()
            if IKalturaVideo.providedBy(obj): #XXX use IVideo when it appears - IKalturaVideo should inherit from it.
                #be lazy.  The first Video you find is all you get!
                self._video = Video(obj)
                return self._video

        return self._video
    
    
    @property
    def gallery(self):
        """return a single rfasite.slideshow as a PhotoGallery associated with the article"""

        #slideshows are embedded via the Layout Tab, so we must journey into cp_container to find it.
        cp = getattr(self.obj, 'cp_container', None)
        if cp is None:
            return None

        if self._gallery is not None:
            return self._gallery

        slots = cp.filled_slots.values()
        for slot in slots:
            for elem in slot.values():
                obj = elem.getTarget()
                if ISlideshow.providedBy(obj):
                    #be lazy.  The first gallery you find is all you get!
                    self._gallery = PhotoGallery(obj)

        return self._gallery

    @gallery.setter
    def gallery(self, obj):
        if isinstance(obj, PhotoGallery):
            self._gallery = obj
        else:
            raise TypeError, "Not a PhotoGallery Object"

    def image(self):
        imgObj = self.obj.getFeaturedImage()
        if imgObj is None:
            return None

        return Image(self.obj.getFeaturedImage())

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
