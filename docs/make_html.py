##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################

# Hacked by Thomas Heller
#
# You need StructuredText from zope to build the HTML files.
# Should probably switch to reST

"""
Document = DocumentClass.DocumentClass()
HTMLNG = HTMLClass.HTMLClass()

def HTML(aStructuredString, level=1, header=1):
    st = Basic(aStructuredString)
    doc = Document(st)
    return HTMLNG(doc,header=header,level=level)
"""

import os,sys 
from StructuredText import StructuredText
import time

def document(self, doc, level, output):
    children=doc.getChildNodes()

    if self.header==1:
        output('<html>\n')
        if (children and
             children[0].getNodeName() == 'StructuredTextSection'):
            output('<head>\n<title>%s</title>\n</head>\n' %
                     children[0].getChildNodes()[0].getNodeValue())
        output('<body>\n')

    for c in children:
        getattr(self, self.element_types[c.getNodeName()])(c, level, output)

    if self.header==1:
        output('</body>\n')
        output('</html>\n')

def main():
    if "-w" in sys.argv:
        for_web = 1
        sys.argv.remove("-w")
    else:
        for_web = 0

    if len(sys.argv)>1:
        files = sys.argv[1:]
    else:
        files = os.listdir('.')
        files = filter(lambda x: x.endswith('.stx'), files)



    for f in files:

        data = open(f,'r').read()

        st = StructuredText.Basic(data)
        doc = StructuredText.Document(st)
        html = StructuredText.HTMLNG(doc, header=0)

        children = doc.getChildNodes()
        title = children[0].getChildNodes()[0].getNodeValue()

        header = '''\
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
  <head>
    <title>%s</title>
    <link rel="STYLESHEET" href="default.css">
  </head>
<body>\n''' % title

        counter = '''
<!--WEBBOT bot="HTMLMarkup" startspan ALT="Site Meter" -->
<script type="text/javascript" language="JavaScript">var site="sm4sflpfw"</script>
<script type="text/javascript" language="JavaScript1.2" src="http://sm4.sitemeter.com/js/counter.js?site=sm4sflpfw">
</script>
<noscript>
<a href="http://sm4.sitemeter.com/stats.asp?site=sm4sflpfw" target="_top">
<img src="http://sm4.sitemeter.com/meter.asp?site=sm4sflpfw" alt="Site Meter" border=0></a>
</noscript>
<!-- Copyright (c)2000 Site Meter -->
<!--WEBBOT bot="HTMLMarkup" Endspan -->

<a href="http://sourceforge.net">
<img src="http://sourceforge.net/sflogo.php?group_id=71702&amp;type=1"
width="88" height="31" border="0" alt="SourceForge.net Logo">
</a>
        '''

        footer = '''
<hr>
<!--PLACEHOLDER-->
<small>Page updated: %s</small>
</body></html>
'''
        pathname = f.replace('.stx','.html')
        outfile = open(pathname, "w")
        outfile.write(header)
        outfile.write(html)
        f = footer % time.asctime()
        if for_web:
            f = f.replace("<!--PLACEHOLDER-->", counter)
        outfile.write(f)
        print pathname

if __name__ == '__main__':
    main()
