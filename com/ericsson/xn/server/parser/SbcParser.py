#encoding=utf-8
'''
Created on Dec 8, 2015

@author: lowitty
'''
import logging
logSbcParser = logging.getLogger('server.SbcParser')
import xml.sax

class SbcSaxHandler(xml.sax.ContentHandler):
    
    def __init__(self):
        xml.sax.ContentHandler.__init__(self)
        logSbcParser.info('SbcParser start to work.')
        self.node = {}
        self.nodeParas = {}
        self.channels = {}
        self.channel = {}
        self.isChannel = False
        self.key = None
    
    def startElementNS(self, name, qname, attrs):
        self.startElementNS(name, attrs)
        
    def endElementNS(self, name, qname):
        self.endElementNS(name)
        
    def startElement(self, name, attrs):
        if('channel' == name):
            logSbcParser.info('Found a channel.')
            self.isChannel = True
        self.key = name
    
    def characters(self, content):
        if(self.isChannel):
            if('channel' != self.key):
                if(self.key is not None):
                    self.channel[self.key] = content
        else:
            if('node' != self.key):
                if(self.key is not None):
                    self.nodeParas[self.key] = content
    
    def endElement(self, name):
        if(name == self.key):
            self.key = None
        if('channel' == name):
            self.isChannel = False
            self.channels[self.channel['channelId']] = self.channel
            self.channel = {}
    
    def endDocument(self):
        self.node['nodeParas'] = self.nodeParas
        self.node['channels'] = self.channels
        logSbcParser.info('Finish to parse the SBC configuration file.')
        
        
class SbcNodeInfo():
    
    def __init__(self, xmlPath):
        parser = xml.sax.make_parser()
        handler = SbcSaxHandler()
        parser.setContentHandler(handler)
        parser.parse(open(xmlPath, 'r'))
        self.node = handler.node
        
    def getNodeInfoMap(self):
        return self.node
    
    
nodeInfoInstance = SbcNodeInfo('/Users/lowitty/git/server/config/sbc/sbc_node.xml')
node = nodeInfoInstance.getNodeInfoMap()
i = 1
    