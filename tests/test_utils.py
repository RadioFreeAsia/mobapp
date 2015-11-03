import unittest

from kss.core.BeautifulSoup import BeautifulSoup
import urlparse

from ..utils import cleanHtml
from ..utils import replaceEmbedsWithIframes
from ..utils import removeStylesFromInlineImages
from ..utils import removeWidthHeightFromInlineImages

import re

#Run with ./bin/test Products.rfasite.mobapp

class CleanHtmlTests(unittest.TestCase):
    
    def testReturnsSane(self):
        inputString = "<div> I don't care </div>"
        result = cleanHtml(inputString)
        self.assertEqual(inputString, result)

class InlineImageTests(unittest.TestCase):
    """resulting html of body that contains inline captioned images"""
    
    def testNoInlineStyles(self):
        inputString = """<p>
  <div style="width:620px;" class="image-inline captioned"> 
   <div style="width:620px;"> 
     <img src="http://www.rfa.org/cantonese/news/HK-clearance-12082014074647.html/1208HK-CLEARANCE-Benny-Tai620.jpg" 
          alt="1208HK-CLEARANCE-Benny-Tai620.jpg" 
          title="1208HK-CLEARANCE-Benny-Tai620.jpg" 
          height="613" width="620" /> 
   </div> 
   <div class="image-caption" style="width:620px;"> 
      caption text here
   </div> 
  </div>
</p> 
And Again!
<p>
  <div style="width:620px;" class="image-inline captioned"> 
   <div style="width:620px;"> 
     <img src="http://www.rfa.org/cantonese/news/HK-clearance-12082014074647.html/1208HK-CLEARANCE-Benny-Tai620.jpg" 
          alt="1208HK-CLEARANCE-Benny-Tai620.jpg" 
          title="1208HK-CLEARANCE-Benny-Tai620.jpg" 
          height="613" width="620" /> 
   </div> 
   <div class="image-caption" style="width:620px;"> 
      caption text here
   </div> 
  </div>
</p>
"""
        
        inputSoup = BeautifulSoup(inputString)
        
        resultSoup = removeStylesFromInlineImages(inputSoup)
        
        divElemList = resultSoup.findAll('div', attrs={'class': lambda x: x and re.search('image-inline(\s|$)', x)})
        
        def theTest(elem):
            if isinstance(elem, basestring):
                return
            self.assertIsNone(elem.get('style'))
            for elem in elem.contents:
                theTest(elem)
        
        for elem in divElemList:
            theTest(elem)
            
    def testNoImageSizeSpecified(self):
        inputString = """<p>
  <div style="width:620px;" class="image-inline captioned"> 
   <div style="width:620px;"> 
     <img src="http://www.rfa.org/cantonese/news/HK-clearance-12082014074647.html/1208HK-CLEARANCE-Benny-Tai620.jpg" 
          alt="1208HK-CLEARANCE-Benny-Tai620.jpg" 
          title="1208HK-CLEARANCE-Benny-Tai620.jpg" 
          height="613" width="620" /> 
   </div> 
   <div class="image-caption" style="width:620px;"> 
      caption text here
   </div> 
  </div>
</p> 
And Again!
<p>
  <div style="width:620px;" class="image-inline captioned"> 
   <div style="width:620px;"> 
     <img src="http://www.rfa.org/cantonese/news/HK-clearance-12082014074647.html/1208HK-CLEARANCE-Benny-Tai620.jpg" 
          alt="1208HK-CLEARANCE-Benny-Tai620.jpg" 
          title="1208HK-CLEARANCE-Benny-Tai620.jpg" 
          height="613" width="620" /> 
   </div> 
   <div class="image-caption" style="width:620px;"> 
      caption text here
   </div> 
  </div>
</p>
"""
        inputSoup = BeautifulSoup(inputString)
        
        resultSoup = removeWidthHeightFromInlineImages(inputSoup)
        
        images = resultSoup.findAll('img')
        
        for img in images:
            self.assertIsNone(img.get('height'))
            self.assertIsNone(img.get('width'))
        
        

class ReplaceEmbedsTests(unittest.TestCase):
        

    def testNotYoutube(self):
        """This should do nothing"""
        
        inputString="""<p>
<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,40,0" height="25" id="audioplayer1" width="240">
<param name="data" value="http://www.rfa.org/vietnamese/manuallyupload/audio-player/player.swf" />
<param name="FlashVars" value="playerID=1&amp;bg=0x00FFFF&amp;leftbg=0x3366FF&amp;lefticon=0xFFFFFF&amp;rightbg=0xFF6633&amp;rightbghover=0x999999&amp;righticon=0x14FF14&amp;righticonhover=0xffffff&amp;text=0x666666&amp;slider=0x666666&amp;track=0xFFFFFF&amp;border=0x666666&amp;loader=0x9FFFB8&amp;soundFile=http://www.rfa.org/vietnamese/in_depth/role-of-vn-nati-assem-questioned-12032013124357.html/12032013-hienphap-tq.mp3" />
<param name="quality" value="high" />
<param name="menu" value="false" />
<param name="bgcolor" value="FFFFFF" />
<param name="src" value="http://www.rfa.org/vietnamese/manuallyupload/audio-player/player.swf" />
<param name="flashvars" value="playerID=1&amp;bg=0x00FFFF&amp;leftbg=0x3366FF&amp;lefticon=0xFFFFFF&amp;rightbg=0xFF6633&amp;rightbghover=0x999999&amp;righticon=0x14FF14&amp;righticonhover=0xffffff&amp;text=0x666666&amp;slider=0x666666&amp;track=0xFFFFFF&amp;border=0x666666&amp;loader=0x9FFFB8&amp;soundFile=http://www.rfa.org/vietnamese/in_depth/role-of-vn-nati-assem-questioned-12032013124357.html/12032013-hienphap-tq.mp3" /><embed height="25" width="240" src="http://www.rfa.org/vietnamese/manuallyupload/audio-player/player.swf" bgcolor="FFFFFF" menu="false" quality="high" flashvars="playerID=1&amp;bg=0x00FFFF&amp;leftbg=0x3366FF&amp;lefticon=0xFFFFFF&amp;rightbg=0xFF6633&amp;rightbghover=0x999999&amp;righticon=0x14FF14&amp;righticonhover=0xffffff&amp;text=0x666666&amp;slider=0x666666&amp;track=0xFFFFFF&amp;border=0x666666&amp;loader=0x9FFFB8&amp;soundFile=http://www.rfa.org/vietnamese/in_depth/role-of-vn-nati-assem-questioned-12032013124357.html/12032013-hienphap-tq.mp3" data="http://www.rfa.org/vietnamese/manuallyupload/audio-player/player.swf" id="audioplayer1" type="application/x-shockwave-flash"></embed>
</object>
</p>"""
        
        inputSoup = BeautifulSoup(inputString)
        
        resultSoup = replaceEmbedsWithIframes(inputSoup)
        
        self.assertEqual(str(inputSoup), str(resultSoup))
        
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
        
        self.assertEqual('100%', iframeElem.get('width'))
        
    
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
        
    def testIframeClass(self):
        """resulting iframe class attr should be 'YouTube'"""
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
        cssClass = iframeElem.get('class')
        
        self.assertEqual(cssClass, "YouTube")
        
    def test_noParams(self):
        """input object / embed code without params"""
        inputString = """<p> <object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,40,0" height="315" width="560"> 
                              <embed height="315" width="560" src="https://www.youtube.com/v/QhYO_KwL2P0?hl=en_GB&amp;version=3&amp;rel=0&amp;controls=0&amp;showinfo=0" allowscriptaccess="always" allowfullscreen="true" type="application/x-shockwave-flash">
                              </embed> 
                             </object>
                      """
        
        inputSoup = BeautifulSoup(inputString)
        
        resultSoup = replaceEmbedsWithIframes(inputSoup)
        iframeElem = resultSoup.find('iframe')
        src = iframeElem.get('src')

        parsed = urlparse.urlparse(src)
        
        self.assertEqual('', parsed.query)
        
    def test_youtubeUrl(self):
        inputString = """<p> <object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" 
                                     codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,40,0" 
                                     height="315" width="560">
                               <embed height="315" width="560" src="https://www.youtube.com/v/Pda1tQxWOIQ" 
                                      allowscriptaccess="always" allowfullscreen="true" 
                                      type="application/x-shockwave-flash"/>
                             </object>
                         </p>
                      """
        
        inputSoup = BeautifulSoup(inputString)
        
        resultSoup = replaceEmbedsWithIframes(inputSoup)
        iframeElem = resultSoup.find('iframe')
        src = iframeElem.get('src')

        parsed = urlparse.urlparse(src)
        self.assertEqual(src, '//www.youtube.com/embed/Pda1tQxWOIQ')
        
    def test_youtubeUrlWithoutVPath(self):
        inputString = """<p> <object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" 
                                     codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,40,0" 
                                     height="315" width="560">
                               <embed height="315" width="560" src="https://www.youtube.com/Pda1tQxWOIQ" 
                                      allowscriptaccess="always" allowfullscreen="true" 
                                      type="application/x-shockwave-flash"/>
                             </object>
                         </p>
                      """
        
        inputSoup = BeautifulSoup(inputString)
        
        resultSoup = replaceEmbedsWithIframes(inputSoup)
        iframeElem = resultSoup.find('iframe')
        src = iframeElem.get('src')

        parsed = urlparse.urlparse(src)
        self.assertEqual(src, '//www.youtube.com/embed/Pda1tQxWOIQ')
        
        #self.assertEqual('', parsed.query)
        
    def test_divTagWrapper(self):
        inputString = """<p> <object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" 
                                     codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,40,0" 
                                     height="315" width="560">
                               <embed height="315" width="560" src="https://www.youtube.com/Pda1tQxWOIQ" 
                                      allowscriptaccess="always" allowfullscreen="true" 
                                      type="application/x-shockwave-flash"/>
                             </object>
                         </p>
                      """
        
        inputSoup = BeautifulSoup(inputString)
        
        resultSoup = replaceEmbedsWithIframes(inputSoup)
        
        divElement = resultSoup.find('div', attrs={'class': 'videoWrapper'})
        self.assertIsNotNone(divElement, 'Should contain a <div class="videoWrapper">')
        
        iframeElem = divElement.iframe
        
        self.assertIsNotNone(iframeElem, '<div class="videoWrapper"> should contain an iframe')
        
        src = iframeElem.get('src')
        parsed = urlparse.urlparse(src)
        self.assertEqual(src, '//www.youtube.com/embed/Pda1tQxWOIQ')
        
                
def test_suite():
    return unittest.TestSuite( 
        (unittest.makeSuite(ReplaceEmbedsTests),
         unittest.makeSuite(InlineImageTests),
         unittest.makeSuite(CleanHtmlTests),
         )  
    )