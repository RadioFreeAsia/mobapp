"""ODD Unbrella App RSS Views"""

import datetime
import pytz

from Acquisition import aq_inner

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from Products.rfasite.browser import SearchRetailView, RetailNavigationView, AudioArchiveView

import Types
import utils

SITEID = 0  #There is only one site, and it's rfa.org

class MobappBaseView(BrowserView):

    MaxArticles = 30
    DefaultDays = 30

    #TODO: move query to base and populate with, at least, "published" state.
    def __init__(self, context, request):
        super(MobappBaseView, self).__init__(context, request)

        self.cirequest = utils.CaseInsensitiveDict()
        for key, value in request.form.iteritems():
            self.cirequest[key]=value

        #although this should ALWAYS be called in subsite context...
        self.subsite = context.getSubsite()
        self.SiteID = self.cirequest.get('SiteID', 0) #Ignored.

        self.ZoneID = self.cirequest.get("ZoneID", "")
        self.ZoneIDs = self.ZoneID.split("|")
        if self.ZoneIDs == [""]:
            self.ZoneIDs = []

        self.Zone = self.cirequest.get("Zone","")
        self.Zones = self.Zone.split("|")
        if self.Zones == [""]:
            self.Zones = []

        self.DayCount = int(self.cirequest.get("DayCount", self.DefaultDays))
        self.Count = int(self.cirequest.get("Count", 30))
        if self.Count > self.MaxArticles:
            self.Count=self.MaxArticles

        self.ArticleID = self.cirequest.get("ArticleId", None)
        self.AuthorID = self.cirequest.get("AuthorId", None)
        self.Title = utils.toBool(self.cirequest.get("Title", True))
        self.TitleAsCDATA = utils.toBool(self.cirequest.get("TitleAsCDATA", False))
        self.Content = utils.toBool(self.cirequest.get("Content", True))
        self.ContentAsCDATA = utils.toBool(self.cirequest.get("ContentAsCDATA", False))
        self.Image = utils.toBool(self.cirequest.get("Image", True))
        self.ImageTitle = utils.toBool(self.cirequest.get("ImageTitle", True))
        self.Authors = utils.toBool(self.cirequest.get("Authors", True))
        self.AuthorsFullName = utils.toBool(self.cirequest.get("AuthorsFullName", False))
        self.html = utils.toBool(self.cirequest.get("html", False))

        if self.html:
            self.ContentAsCDATA = True
            self.TitleAsCDATA = True

        self.catalog = getToolByName(self.context, 'portal_catalog')

        if self.Zones:
            #we got some Section names we have to look up ID's for
            for sectionName in self.Zones:
                ### IS there a way to get an exact match??????
                brains = self.catalog.searchResults(portal_type="Section",Title=sectionName)
                uid = brains[0].UID #first element by default
                for brain in brains:
                    if brain.Title.upper()==sectionName.upper():
                        uid=brain.UID
                        break

                self.ZoneIDs.append(uid)


        self.Article = Types.ArticleFactory(lookupObj_func=self.subsite.reference_catalog.lookupObject,
                                            request=self.request)


        #set the timezone
        tzOffset = getattr(self.context, 'getTimezoneOffset', lambda: 0)()

        #we assume US/Eastern when we don't have a timezone offset set.
        #XXX we shouldn't set numeric offsets, we should set tzinfo objects to support DST
        if tzOffset == 0 or tzOffset is None:
            self.subsiteTz = pytz.timezone('US/Eastern')
        else:
            #convert to minutes
            offset = int(tzOffset*60)
            self.subsiteTz = pytz.FixedOffset(offset)

    def items(self):
        self.info  = {"site": SITEID,
                      "showImg": self.Image,
                      "showTitle": self.Title,
                      "showImgTitle": self.ImageTitle,
                      "CDATA_Title": self.TitleAsCDATA,
                      "showContent": self.Content,
                      "CDATA_Content": self.ContentAsCDATA,
                      "showAuthors": self.Authors,
                      "AuthorFullName": self.AuthorsFullName}


class MobappZoneView(MobappBaseView):
    """zones.zml view"""
    def __init__(self, context, request):
        super(MobappZoneView, self).__init__(context, request)
        if not self.ZoneID:
            self.ZoneID = self.subsite.UID()
        else:
            self.ZoneID = self.ZoneIDs[0]

    def getZonesFromNav(self):
        """Return dictionary of zones based on
           how the RetailNav returns
        """
        view = RetailNavigationView(self.context, self.request)
        navs = view.navigation()
        zones = self._makeZoneInfo([n['brain'] for n in navs])

        return zones

    def getZonesFromList(self, zoneList):
        """generates a dictionary of zones based on a configured list of paths relative to subsite
           zone = {ZoneId, SiteID, Title, hash, path}
        """
        rootPath = '/'.join(self.subsite.getPhysicalPath())
        zonePaths = [ rootPath+'/'+id for id in zoneList ]

        pathquery = {'query': zonePaths, 'depth': 0}

        sectionBrains = self.catalog.searchResults(path=pathquery,
                                                   portal_type='Section')
        zones = self._makeZoneInfo(sectionBrains)

        #preserve order of zones configured for top-level.
        for zone_info in zones:
            topZoneValue = zone_info['path'][len(rootPath+'/'):]
            sortKey = zoneList.index(topZoneValue)
            zone_info['sortKey'] = sortKey
        zones.sort(key=lambda zone:zone['sortKey'])

        return zones

    def getZonesFromSubsiteProperty(self):
        zoneList = self.subsite.getProperty('mobapp_zones', None)
        if zoneList:
            return self.getZonesFromList(zoneList)
        else:
            return None


    def getZonesFromPath(self, parentZones):
        """Given a parent zone (section) return all child Sections
           Used for 'subzone' query, when zoneID parameter is provided
        """

        sectionBrains = self.catalog.searchResults(path=parentZones,
                                                   portal_type='Section',
                                                   depth=1)
        zones = self._makeZoneInfo(sectionBrains)
        return zones


    def _makeZoneInfo(self, sectionBrains):
        """ Turn a set of brains from a catalog query into zone info for templates"""
        zones = []
        for sectionBrain in sectionBrains:
            if publicFolder(sectionBrain):
                zone_info = {"ZoneID": sectionBrain.UID,
                             "SiteID": SITEID,
                             "Title": sectionBrain.Title,
                             "hash": utils.getFolderModificationDate(sectionBrain, self.catalog),
                             "path": sectionBrain.getPath()
                             }
                zones.append(zone_info)
        return zones


    def items(self):
        super(MobappZoneView, self).items()
        if self.subsite.UID() == self.ZoneID:
            parentZone = self.subsite
        else:
            parentZone = self.subsite.reference_catalog.lookupObject(self.ZoneID)

        if parentZone == self.subsite:
            #this is a query from the root:
            zones = self.getZonesFromSubsiteProperty()
            if zones is None:
                #no configuration, use the subsite's default navigation setup.
                zones = self.getZonesFromNav()

        else:
            #this is a query for sub-zones given a zone.
            zones = self.getZonesFromPath(parentZone)

        self.info["zones"] = zones

        return self.info


class MobappArticlesView(MobappBaseView):

    def items(self):
        super(MobappArticlesView, self).items()
        self.info['articles'] = []

        if self.ArticleID:
            article = self.Article(self.ArticleID)
            if article:
                self.info["articles"].append(article)
            return self.info

        query = {}
        query['portal_type'] = "Story"
        query['review_state'] = "published"

        end = datetime.datetime.utcnow() + datetime.timedelta(minutes=1)
        start = datetime.datetime.utcnow() - datetime.timedelta(days=self.DayCount)

        date_range_query = {'query':(start,end), 'range':'min:max'}
        query['effective'] = date_range_query

        if self.ZoneIDs:
            sectionBrains = self.catalog.searchResults(UID=self.ZoneIDs)
            zonePaths = [brain.getPath() for brain in sectionBrains]
            query['path'] = {'query':zonePaths, 'depth':2}

        if self.AuthorID:
            query['Creator'] = self.AuthorID

        articleBrains = self.catalog.search(query_request=query,
                                            sort_index = 'effective',
                                            reverse = 1,
                                            limit=self.Count)[:self.Count]


        for brain in articleBrains:
            article = self.Article(brain.UID, request=self.request)
            self.info["articles"].append(article)

        return self.info


class MobappAudioArchiveView(MobappBaseView):
    def __init__(self, context, request):
        super(MobappAudioArchiveView, self).__init__(context, request)
        self.AudioId = self.request.get("AudioId", "")

    def items(self):
        super(MobappAudioArchiveView, self).items()
        from Products.rfasite.interfaces import IProgramSegmentsFinder
        adapter = IProgramSegmentsFinder(self.subsite)
        segments = adapter()

        self.info["programs"] = []

        #if self.AudioId: #XXX figure out how to look up by ID, if needed

        for s in segments:
            audioObj = Types.AudioClip(streamerSegment=s, localTz=self.subsiteTz)
            if audioObj is not None:
                self.info["programs"].append(audioObj)

        return self.info

class MobappBreakingNewsView(MobappBaseView):
    """Fakes a breaking news article using the placeholder
       All we have is a title at this point"""
    def items(self):
        super(MobappBreakingNewsView, self).items()
        self.info["articles"] = []
        breaking_news_string = self.subsite.getBreakingNews()
        if breaking_news_string:
            article = Types.Placeholder_Article()
            article.title = breaking_news_string
            article.content = breaking_news_string
            article.pubDate = str(datetime.datetime.utcnow())  #TODO - maybe effective on subsite?
            self.info["articles"].append(article)

        return self.info

class MobappMediaView(MobappBaseView):
    """Present videos and slideshows as a selection of media
    """
    DefaultDays = 90
    photo_types = ["Slideshow",]
    #we need an IVideo interface marker!
    #video_types = ["VideoLink", "YoutubeLink", "Kaltura Video"] 
    video_types = ["Kaltura Video"]

    def __init__(self, context, request):
        super(MobappMediaView, self).__init__(context, request)
        self.Media = self.request.get("media", "").upper()
        
        #backwards compatability - capital 'M' on media:
        if not self.Media:
            self.Media = self.request.get("Media", "").upper()
        
        self.MediaID = self.request.get("MediaId", "")

        self.Videos = False
        self.Photos = False

        if "V" in self.Media:
            self.Videos = True
        if "P" in self.Media:
            self.Photos = True

    def add_media(self, media_obj):

        dest_article = None
        #search to see if we have this article already.
        for article in self.info["articles"]:
            if article.id() == media_obj.article_parent_id:
                dest_article = article
                break

        if dest_article is None:
            dest_article = media_obj.article_parent
            self.info["articles"].append(dest_article)

        if isinstance(media_obj, Types.PhotoGallery):
            dest_article.gallery = media_obj
        if isinstance(media_obj, Types.Video):
            dest_article.video = media_obj

    def query_photos(self):
        query ={}
        media_types = self.photo_types

        if self.ZoneIDs:
            sectionBrains = self.catalog.searchResults(UID=self.ZoneIDs)
            zonePaths = [brain.getPath() for brain in sectionBrains]
            query['path'] = {'query':zonePaths, 'depth':2}

        #we search for published articles, and return media within those articles.
        # This avoids requiring Slideshows and Videos to be 'published'
        query['portal_type'] = "Story"
        query['review_state'] = "published"
        end = datetime.datetime.utcnow() + datetime.timedelta(minutes=1)
        start = datetime.datetime.utcnow() - datetime.timedelta(days=self.DayCount)
        query['effective'] = {'query':(start,end), 'range':'min:max'}

        articleBrains = self.catalog.search(query_request=query,
                                            sort_index = 'effective',
                                            reverse = 1)

        articlePaths = [brain.getPath() for brain in articleBrains]
        brains = self.catalog.search(query_request={'portal_type': media_types,
                                                    'path': {'query':articlePaths,
                                                             'depth':1}
                                                   },
                                     limit=self.Count)[:self.Count]


        zope_objects = [brain.getObject() for brain in brains]        
    
        return zope_objects
            
            
    def query_videos(self):
        query ={}
        media_types = self.video_types
        
        #for now, videos (Kaltura) do not have zones - revisit
        #if self.ZoneIDs:
        #    sectionBrains = self.catalog.searchResults(UID=self.ZoneIDs)
        #    zonePaths = [brain.getPath() for brain in sectionBrains]
        #    query['path'] = {'query':zonePaths, 'depth':2}
        
        
        query['portal_type'] = media_types
        query['review_state'] = ["published", "visible"]
        brains = self.catalog.search(query_request=query,
                                     sort_index = 'effective',
                                     reverse = 1,
                                     limit=self.Count)[:self.Count]
        
        zope_objects = [brain.getObject() for brain in brains]
        
        return zope_objects

    def items(self):
        super(MobappMediaView, self).items()

        self.info["articles"] = []
        zope_objects = []

        if self.MediaID: #provided an id: return just that object
            obj = self.subsite.reference_catalog.lookupObject(self.MediaID)
            if obj:
                zope_objects.append(obj)

        else: #we query the catalog
            if self.Photos:
                zope_objects += self.query_photos()
            if self.Videos:
                zope_objects += self.query_videos()

        for obj in zope_objects:
            if obj.portal_type in self.photo_types:
                self.add_media(Types.PhotoGallery(obj))
            elif obj.portal_type in self.video_types: #IVideo.providedBy(obj) is what this should say.
                self.add_media(Types.Video(obj))

        return self.info

class MobappSchedulerView(MobappBaseView):
    def items(self):
        #English service does not have a schedule of programs from RFA
        super(MobappSchedulerView, self).items()
        self.info["programs"]=[]

        return self.info

class MobappSearchView(MobappBaseView, SearchRetailView):

    def __init__(self, context, request):
        MobappBaseView.__init__(self, context, request)
        self.search_text = self.request.get("q", "")
        self.results = self._getResults()

        #just pass some stuff to batch 1 page
        self.b_start = 0
        self.b_size = 30

    def items(self):
        super(MobappSearchView, self).items()

        self.info["articles"] = []

        if not self.search_text:
            #no results if no query
            return self.info

        articleBrains = self.batch()

        for brain in articleBrains:
            self.info["articles"].append(self.Article(brain.UID))

        return self.info

class MobappTopStoriesView(MobappBaseView):

    def __init__(self, context, request):
        """ request parameter 'odd' will guarantee an odd number of results returned, if total number of results is greater than 3"""
        super(MobappTopStoriesView, self).__init__(context, request)
        self.odd = self.request.get("odd", 0) #not implemented
        self.Count = 5

    def items(self):
        super(MobappTopStoriesView, self).items()
        self.info["articles"] = []

        # First top story is 'the top story'

        top_story_obj  = self.subsite.getTopStory()
        top_story = self.Article(obj=top_story_obj, request=self.request)
        self.info["articles"].append(top_story)

        query = {'portal_type': "Story",
                 'review_state': "published",
                 }
        articleBrains = self.catalog.search(query_request=query,
                                            sort_index = 'effective',
                                            reverse = 1,
                                            limit=self.Count)[:self.Count]

        #take the top story out of the result, if there
        filteredBrains = [brain for brain in articleBrains if brain.UID != top_story_obj.UID()]
        #if we didn't take out a story, then truncate the list from the end.
        articleBrains = filteredBrains[:4]

        for brain in articleBrains:
            article = self.Article(brain.UID, request=self.request)
            self.info["articles"].append(article)

        #assert(len(self.info["articles"]) == self.Count)

        return self.info


def privateFolder(sectionBrain):
    exclude_from_nav = getattr(sectionBrain, 'exclude_from_nav', True)

    #any section included in navigation is public.
    if exclude_from_nav == False:
        return False

    sectionObj = sectionBrain.getObject()
    include_in_sitemap = getattr(sectionObj, 'include_in_sitemap', False)

    #if section is set to show in sitemap (although not in nav) it's public
    if include_in_sitemap == True:
        return False

    return True

def publicFolder(sectionBrain):
    return not privateFolder(sectionBrain)
