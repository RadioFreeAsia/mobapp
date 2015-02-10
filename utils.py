import urlparse
from kss.core.BeautifulSoup import BeautifulSoup, Tag
import re

def getFolderModificationDate(folderBrain, catalog):
    """Returns last time content was modified inside a folder"""

    brains = catalog.search(query_request={ "path": folderBrain.getPath(),
                                            "portal_type": 'Story',
                                            'review_state':'published'},
                            sort_index = 'effective',
                            reverse=1,
                            limit=1)

    if brains:
        return brains[0].ModificationDate
    else:
        #return the folder's modificationDate
        return folderBrain.ModificationDate

def toBool(boolstring):
    """coerse strings (from request) into real bools"""
    if str(boolstring).upper() in ('0', 'FALSE'):
        return False
    else:
        return True


def cleanHtml(content):
    soup = BeautifulSoup(content)

    soup = removeJavascript(soup)
    soup = replaceEmbedsWithIframes(soup)
    soup = removeViewFromImages(soup)
    soup = removeStylesFromInlineImages(soup)
    soup = removeWidthHeightFromInlineImages(soup)

    return unicode(soup)

def removeJavascript(soup):
    to_extract = soup.findAll(lambda tag: tag.name.lower() == 'script')
    for item in to_extract:
        item.extract()
    return soup

def removeStylesFromInlineImages(soup):
    
    def removeInlineStyle(elemlist):
        for elem in elemlist:
            if isinstance(elem, basestring):
                continue
            if elem.get('style'):
                del elem['style']
            removeInlineStyle(elem.contents)
    
    inlineImageElems = soup.findAll('div', attrs={'class': lambda x: x and re.search('image-inline(\s|$)', x)})
    removeInlineStyle(inlineImageElems)
        
    return soup

def removeWidthHeightFromInlineImages(soup):
    inlineImageElems = soup.findAll('div', attrs={'class': lambda x: x and re.search('image-inline(\s|$)', x)})
    
    for elem in inlineImageElems:
        images = elem.findAll('img')
        
        for img in images:
            if img.get('height'):
                del img['height']
            if img.get('width'):
                del img['width']
            
    return soup
        

def replaceEmbedsWithIframes(soup):
    """Find occurences of (youtube) embedded videos using 'object/embed' and replace it with an iframe"""

    #see tests.test_utils

    objectTags = soup.findAll(lambda tag: tag.name.lower() == 'object')

    url = None
    for oTag in objectTags:
        #try to find the 'src' in the param elements of the object
        paramSrcTag = oTag.find('param', attrs={'name': 'src',
                                                'value': lambda s: s.find('youtube') != -1 })
        if paramSrcTag:
            url = paramSrcTag.get('value')
            
        else: #no param tag found, get 'src' from embed attribute
            embedTag = oTag.find('embed', attrs={'src': lambda s: s.find('youtube') != -1})
            if embedTag:
                url = embedTag.get('src')
            
        if url is not None: #we found the youtube url
            
            parsed = urlparse.urlparse(url)
            v_val = parsed.path.split('/')[-1]   #find the youtube 'v' id - assume (oops) it's the last part of the path
            path = "/embed/"+v_val

            path = path.split('&')[0]
            newUrl = urlparse.urlunparse(('',parsed.netloc, path,
                                          '','',''))

            
            iframeTag = Tag(soup, 'iframe', attrs=[(u'src',newUrl),
                                                   (u'width',u"100%"),
                                                   (u'frameborder', u"0"),
                                                   (u'class', u"YouTube"),
                                                   ]
                            )

            oTag.replaceWith(iframeTag)

    return soup

def removeViewFromImages(soup):
    """Find occurances of images processed with 'resolve_uid' that have '/image' appended to the url
       and remove that view, leaving the url to the image untouched"""

    images = soup.findAll('img')

    for image in images:
        if image['src'].endswith("/image"):
            image['src'] = image['src'][:-len("/image")]

    return soup




class CaseInsensitiveDict(dict):
    def __setitem__(self, key, value):
        super(CaseInsensitiveDict, self).__setitem__(key.lower(), value)

    def __getitem__(self, key):
        return super(CaseInsensitiveDict, self).__getitem__(key.lower())

    def get(self, key, default=None):
        """Retrieve value associated with 'key' or return default value
        if 'key' doesn't exist."""
        try:
            return self[key]
        except KeyError:
            return default