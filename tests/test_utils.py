import unittest

from kss.core.BeautifulSoup import BeautifulSoup
import urlparse

from ..utils import replaceEmbedsWithIframes

#Run with ./bin/test Products.rfasite.mobapp

class ReplaceEmbedsTests(unittest.TestCase):
        

    def testNoHeight(self):
        """resulting iframe output should not contain height parameter"""
        
        inputString = """<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000"
        codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,40,0"
            height="360" width="640">
      <param name="allowFullScreen" value="true" />
      <param name="allowscriptaccess" value="always" />
      <param name="src" value="https://www.youtube.com/v/kc658mQqoU0" />
      <param name="allowfullscreen" value="true" />
      <embed height="360" width="640" src="https://www.youtube.com/v/kc658mQqoU0" allowscriptaccess="always" allowfullscreen="true" type="application/x-shockwave-flash">
      </embed>
    </object>
            """
        
        
        inputSoup = BeautifulSoup(inputString)
        
        resultSoup = replaceEmbedsWithIframes(inputSoup)
        iframeElem = resultSoup.find('iframe')
        
        self.assertIsNone(iframeElem.get('height'), "Height was defined - should be None")
        
    def testWidth100(self):
        """resulting iframe output should have width set to %100"""
        inputString = """<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000"
        codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,40,0"
            height="360" width="640">
      <param name="allowFullScreen" value="true" />
      <param name="allowscriptaccess" value="always" />
      <param name="src" value="https://www.youtube.com/v/kc658mQqoU0" />
      <param name="allowfullscreen" value="true" />
      <embed height="360" width="640" src="https://www.youtube.com/v/kc658mQqoU0" allowscriptaccess="always" allowfullscreen="true" type="application/x-shockwave-flash">
      </embed>
    </object>
            """
        
        
        inputSoup = BeautifulSoup(inputString)
        
        resultSoup = replaceEmbedsWithIframes(inputSoup)
        iframeElem = resultSoup.find('iframe')
        
        self.assertEqual('%100', iframeElem.get('width'))
        
    
    def testNoAllowFullscreen(self):
        """resulting iframe output should have width set to %100"""
        inputString = """<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000"
        codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,40,0"
            height="360" width="640">
      <param name="allowFullScreen" value="true" />
      <param name="allowscriptaccess" value="always" />
      <param name="src" value="https://www.youtube.com/v/kc658mQqoU0" />
      <param name="allowfullscreen" value="true" />
      <embed height="360" width="640" src="https://www.youtube.com/v/kc658mQqoU0" allowscriptaccess="always" allowfullscreen="true" type="application/x-shockwave-flash">
      </embed>
    </object>
            """
        
        
        inputSoup = BeautifulSoup(inputString)
        
        resultSoup = replaceEmbedsWithIframes(inputSoup)
        iframeElem = resultSoup.find('iframe')
        self.assertIsNone(iframeElem.get('allowfullscreen'))
    
    def testIframeSrcNoParams(self):
        """resulting iframe src should not contain any parameters"""
        inputString = """<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000"
        codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,40,0"
            height="360" width="640">
      <param name="allowFullScreen" value="true" />
      <param name="allowscriptaccess" value="always" />
      <param name="src" value="https://www.youtube.com/v/QhYO_KwL2P0?hl=en_GB&amp;version=3&amp;rel=0&amp;controls=0&amp;showinfo=0" />
      <param name="allowfullscreen" value="true" />
      <embed height="360" width="640" src="https://www.youtube.com/v/kc658mQqoU0" allowscriptaccess="always" allowfullscreen="true" type="application/x-shockwave-flash">
      </embed>
    </object>
            """
        inputSoup = BeautifulSoup(inputString)
        
        resultSoup = replaceEmbedsWithIframes(inputSoup)
        iframeElem = resultSoup.find('iframe')
        src = iframeElem.get('src')

        parsed = urlparse.urlparse(src)
        
        self.assertEqual('', parsed.query)
                
def test_suite():
    return unittest.TestSuite( 
        (unittest.makeSuite(ReplaceEmbedsTests),
         )  
    )