#encoding=utf-8
'''
Created on Aug 26, 2015

@author: lowitty
'''
import logging
from xml.etree import ElementTreeß
log = logging.getLogger('server.OcgsSetValue')

class OcgsSetValue():
    def __init__(self, line, xmlpath):
        self.returnStr = ""
        self.nodePara = ["nodeid", "x1neip", "x1neport", "tx1normal", "tx1nomsg", "x2neip", "x2neport", "tx2normal", "tx2checkstate", "cputhreshhold", "maxtargets", "lionoff", "licids"]
        self.licPara = ["x1ki", "x1password", "x1sqn", "x1licip", "x1licport", "x2ki", "x2password", "x2sqn", "x2licaddrs"]
        res, cmds = self.checkCmdFormat(line)
        if(res):#Parameter check passed, will try to set the value to XML.
            try:
                self.er = ElementTree.parse(xmlpath)
                res = self.setValue(cmds)
                if(res):
                    self.er.write(xmlpath, encoding='utf-8', xml_declaration=True, method='xml')
                    log.info('Successfully set the value to node.')
                    self.returnStr="result=successful"
                else:
                    log.error('Try to modify the XML failed.')
                    self.returnStr="result=failed\nerrordesc=Try to modify the XML failed."
            except Exception as e:
                log.error('Try to set the value to XML configuration file failed.')
                self.returnStr="result=failed\nerrordesc=Try to set the value to XML configuration file failed."
   
    def setValue(self, cmds):
        nodeRes = self.setNodevalue(cmds['nodeinfo'])
        licRes = self.setLicValue(cmds['licinfo'])
        return nodeRes and licRes
    
    def setNodevalue(self, nodeinfo):
        try:
            for k, v in nodeinfo:
                self.er.find('./' + k).text = v
            return True
        except Exception as e:
            return False
    
    def setLicValue(self, licinfo):
        licid = licinfo['id']
        lickv = licinfo['lickv']
        lic = self.findLicByID(licid)
        if(lic is not None):
            try:
                for k, v in lickv:
                    lic.find(k).text = v
                return True
            except Exception as e:
                return False
        else:
            log.error('The licid that you specified does not exist!')
            self.returnStr="result=failed\nerrordesc=The licid that you specified does not exist!"
            return False
    
    def findLicByID(self, id):
        for lic in self.er.findall('./lic'):
            if(id == lic.find('id').text):
                return lic
        return None

    def checkCmdFormat(self, line):
        licmd = line.strip().split()
        cmds = {}
        nodeinfo = []
        licinfo = {}
        lickv = []
        if(len(licmd) % 2 == 0):
            log.error('The number of the command is not correct.')
            self.returnStr="result=failed\nerrordesc=The number of setting command is not correct."
            return False, None
        else:
            if('x_modify_conf' != licmd[0]):
                log.info('The command received cannot be recognized.')
                self.returnStr="result=failed\nerrordesc=The command received cannot be recognized."
                return False, None
            else:
                foundLic = False
                for i in range(1, len(licmd), 2):
                    if(foundLic):
                        #these are the lic parameters
                        if(licmd[i][1:] in self.licPara):
                            lickv.append(( (licmd[i][1:], licmd[i + 1]) ))
                        else:
                            log.error('Un-recognized parameter found, will exit as failed.')
                            self.returnStr="result=failed\nerrordesc=The command received cannot be recognized. Parameter: " + licmd[i]
                            return False, None
                    else:
                        if(licmd[i][1:] == "licid"):
                            foundLic = True
                            licinfo['id'] = licmd[i + 1]
                        else:
                            #These are the parameters of node itself.
                            if(licmd[i][1:] in self.nodePara):#Check if the parameter exists and if the value is legal.
                                if('lionoff' == licmd[i][1:] and licmd[i + 1] not in ["on", "off"]):
                                    log.error('The value of parameter lionoff of OCGS can only be on or off.')
                                    self.returnStr="result=failed\nerrordesc=The value of parameter lionoff of OCGS can only be on or off. Value: " + licmd[i + 1]
                                    return False, None
                                nodeinfo.append((licmd[i][1:], licmd[i + 1]))
                            else:
                                log.error('Un-recognized parameter found, will exit as failed.')
                                self.returnStr="result=failed\nerrordesc=The command received cannot be recognized. Parameter: " + licmd[i]
                                return False, None
                
                licinfo['lickv'] = lickv
                cmds['licinfo'] = licinfo
                cmds['nodeinfo'] = nodeinfo
        return True, cmds
    
    def returnRes(self):
        return self.returnStr.rstrip().encode('utf-8')

'''xmlpath = '/Users/lowitty/git/server/config/ocgs/ocgs_node1.xml'
cmds = "x_modify_conf -x2neport 3333 -licid 9000 -x1sqn 4321 -x2sqn 4321 -x2neport 2222"
ha = OcgsSetValue(cmds, xmlpath)
print ha.returnRes()'''