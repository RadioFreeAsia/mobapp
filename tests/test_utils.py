import unittest

from ..utils import replaceEmbedsWithIframes
from kss.core.BeautifulSoup import BeautifulSoup

#Run with ./bin/test Products.rfasite.mobapp

class ReplaceEmbedsTests(unittest.TestCase):
    
    def test1(self):
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
        
        expectedOutput = """<iframe src="//www.youtube.com/embed/kc658mQqoU0" width="420" frameborder="0" height="315"></iframe>
        """
        inputSoup = BeautifulSoup(inputString)
        expectSoup = BeautifulSoup(expectedOutput)
        
        result = replaceEmbedsWithIframes(inputSoup)
        
        self.assertEqual(str(result), str(expectSoup))
        
        
    
    def test2(self):
        inputString = """<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,40,0"
 height="360" width="630">
<param name="allowFullScreen" value="true" />
<param name="allowscriptaccess" value="always" />
<param name="src" value="http://www.youtube.com/v/rdOAgdQoGxM&version=3" />
<param name="allowfullscreen" value="true" /><embed height="360" width="630" src="http://www.youtube.com/v/rdOAgdQoGxM&version=3" allowscriptaccess="always" allowfullscreen="true" type="application/x-shockwave-flash"></embed>
</object>

            """
        
        expectedOutput = """<iframe src="//www.youtube.com/embed/rdOAgdQoGxM" width="420" frameborder="0" height="315"></iframe>
        """
        inputSoup = BeautifulSoup(inputString)
        expectSoup = BeautifulSoup(expectedOutput)
        
        result = replaceEmbedsWithIframes(inputSoup)
        
        self.assertEqual(str(result), str(expectSoup))
        
        
    def test3(self):
        inputString = """<object height="315" width="420" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,40,0" classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000">
<param value="true" name="allowFullScreen">
<param value="always" name="allowscriptaccess">
<param value="https://www.youtube.com/v/Rh4v5wIC7_s?version=3&amp;hl=en_US" name="src">
<param value="true" name="allowfullscreen"><embed height="315" width="420" type="application/x-shockwave-flash" allowfullscreen="true" allowscriptaccess="always" src="https://www.youtube.com/v/Rh4v5wIC7_s?version=3&amp;hl=en_US">
</object>"""
        expectedOutput = """<iframe src="//www.youtube.com/embed/Rh4v5wIC7_s" width="420" frameborder="0" height="315"></iframe>"""
        
        inputSoup = BeautifulSoup(inputString)
        expectSoup = BeautifulSoup(expectedOutput)
        
        result = replaceEmbedsWithIframes(inputSoup)
        
        self.assertEqual(str(result), str(expectSoup))
        
def test_suite():
    return unittest.TestSuite( 
        (unittest.makeSuite(ReplaceEmbedsTests),
         )  
    )