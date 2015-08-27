#encoding=utf-8
'''
Created on Aug 26, 2015

@author: lowitty
'''
import xml.sax
import logging
logOcgsParser = logging.getLogger('server.OcgsParser')


class OcgsSaxHandler(xml.sax.ContentHandler):
    def __init__(self):
        xml.sax.ContentHandler.__init__(self)
        logOcgsParser.info('SAX handler init.')
        self.node = {}
        self.nodePara = {}
        self.lics = []
        self.lic = {}
        self.isLic = False
        self.key = None
    
    def startElementNS(self, name, qname, attrs):
        self.startElement(name, attrs)
    
    def endElementNS(self, name, qname):
        self.endElement(name)
    
    def startElement(self, name, attrs):
        if('lic' == name):
            self.isLic = True
            logOcgsParser.info('Found a lic information.')
        self.key = name
    
    def characters(self, content):
        if(self.isLic):
            if('lic' != self.key):
                if(self.key is not None):
                    self.lic[self.key] = content
        else:
            if('node' != self.key):
                if(self.key is not None):
                    self.nodePara[self.key] = content
    
    def endElement(self, name):
        if(name == self.key):
            self.key = None
        if('lic' == name):
            self.isLic = False
            self.lics.append(self.lic)
            self.lic = {}
    
    
    def endDocument(self):
        self.node["nodePara"] = self.nodePara
        self.node["lics"] = self.lics
        logOcgsParser.info('End the parsing of XML.')


class OcgsNodeInfo():
    def __init__(self, xmlpath):
        self.nodeInfo = ""
        try:
            self.xmlpath = xmlpath
            parser = xml.sax.make_parser()
            handler = OcgsSaxHandler()
            parser.setContentHandler(handler)
            parser.parse(open(self.xmlpath, 'r'))
            nodeDraft = handler.node
            self.nodeInfo += "result=successful\n"
            for key, value in nodeDraft["nodePara"].iteritems():
                self.nodeInfo += key + "=" + value +"\n"
            for lic in  nodeDraft["lics"]:
                licid = lic["id"]
                for key, value in lic.iteritems():
                    if('id' != key):
                        self.nodeInfo += licid + "::" + key + "=" + value + "\n"
        except Exception as e:
            self.nodeInfo = "result=failed\nerrordesc=failed to get config, msg: " + e.args
        
    
    
    def getNodeInfo(self):
        return self.nodeInfo.rstrip().encode('utf-8')
    
    
'''han = OcgsNodeInfo('/Users/lowitty/git/server/config/ocgs/ocgs_node.xml')
print han.getNodeInfo()'''