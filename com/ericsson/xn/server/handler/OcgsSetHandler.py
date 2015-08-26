#encoding=utf-8
'''
Created on Aug 26, 2015

@author: lowitty
'''
import logging
from xml.etree import ElementTree
log = logging.getLogger('server.OcgsSetValue')

class OcgsSetValue():
    def __init__(self, line):
        self.returnStr = ""
        self.nodePara = ["nodeid", "x1neip", "x1neport", "tx1normal", "tx1nomsg", "x2neip", "x2neport", "tx2normal", "tx2checkstate", "cputhreshhold", "maxtargets", "lionoff", "licids"]
        self.licPara = ["x1ki", "x1password", "x1sqn", "x1licip", "x1licport", "x2ki", "x2password", "x2sqn", "x2licaddrs"]

    def checkCmdFormat(self, line):
        licmd = line.strip().split()
        cmds = {}
        nodeinfo = []
        licinfo = {}
        if(len(licmd) % 2 == 0):
            self.returnStr="result=failed\nerrordesc=The number of setting command is not correct."
            return False, None
        else:
            if('x_modify_conf' != licmd[0]):
                self.returnStr="result=failed\nerrordesc=The command received cannot be recognized."
                return False, None
            else:
                foundLic = False
                for i in range(1, len(licmd), 2):
                    if(foundLic):
                        #these are the lic parameters
                        pass
                    else:
                        if(licmd[i] == "licid"):
                            foundLic = True
                            licinfo['id'] = licmd[i + 1]
                        else:
                            #These are the parameters of node itself.
                            if(licmd[i] in self.nodePara):#Check if the parameter exists and if the value is legal.
                                nodeinfo.append((licmd[i], licmd[i + 1]))
                            else:
                                log.error('Un-recognized parameter found, will exit as failed.')
                                self.returnStr="result=failed\nerrordesc=The command received cannot be recognized. Parameter: " + licmd[i]
                                return False, None
    
    def returnRes(self):
        return self.returnStr.rstrip().encode('utf-8')

dom = ElementTree.parse('/Users/lowitty/git/server/config/ocgs/ocgs_node1.xml')
liconoff = dom.findall('./lionoff')[0]
print liconoff.text
liconoff.text = "on"
dom.write('/Users/lowitty/git/server/config/ocgs/ocgs_node1.xml', encoding='utf-8', xml_declaration=True, method='xml')