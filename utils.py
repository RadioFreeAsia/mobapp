import urlparse
from kss.core.BeautifulSoup import BeautifulSoup, Tag

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
    to_extract = soup.findAll(lambda tag: tag.name.lower() == 'script')
    for item in to_extract:
        item.extract()

    soup = replaceEmbedsWithIframes(soup)

    return unicode(soup)


def replaceEmbedsWithIframes(soup):
    """Find occurences of (youtube) embedded videos using 'object/embed' and replace it with an iframe"""

    #take this:
    #<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000"
    #        codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,40,0"
    #        height="360" width="640">
    #  <param name="allowFullScreen" value="true" />
    #  <param name="allowscriptaccess" value="always" />
    #  <param name="src" value="https://www.youtube.com/v/kc658mQqoU0" />
    #  <param name="allowfullscreen" value="true" />
    #  <embed height="360" width="640" src="https://www.youtube.com/v/kc658mQqoU0" allowscriptaccess="always" allowfullscreen="true" type="application/x-shockwave-flash">
    #  </embed>
    #</object>


    #and turn it into this:
    #<iframe src="//www.youtube.com/embed/kc658mQqoU0" allowfullscreen="" frameborder="0" width="500" height="345">
    #</iframe>

    objectTags = soup.findAll(lambda tag: tag.name.lower() == 'object')


    for oTag in objectTags:
        paramSrcTag = oTag.find('param', attrs={'name': 'src',
                                                'value': lambda s: s.find('youtube') != -1 })
        if paramSrcTag:
            url = paramSrcTag['value']
            parsed = urlparse.urlparse(url)
            v_val = parsed.path.split('/')[2]   #find the youtube 'v' id
            path = "/embed/"+v_val

            newUrl = urlparse.urlunparse(('',parsed.netloc, path,
                                          '','',''))

            iframeTag = Tag(soup, 'iframe', attrs=[(u'src',newUrl),
                                                   (u'allowfullscreen', u""),
                                                   (u'frameborder', u"0"),
                                                   (u'width',u"420"),
                                                   ]
                            )

            oTag.replaceWith(iframeTag)

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