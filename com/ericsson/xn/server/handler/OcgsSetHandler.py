#encoding=utf-8
'''
Created on Aug 26, 2015

@author: lowitty
'''
import logging, time, random, copy, sys
from xml.etree import ElementTree
logOcgsSetValue = logging.getLogger('server.OcgsSetValue')
isAvaiable = True

versionTuple = sys.version_info[:2]
version = '.'.join(repr(v) for v in versionTuple)


class OcgsSetValue():
    def __init__(self, line, xmlpath):
        global isAvaiable, version
        
        self.returnStr = ""
        self.nodePara = ["nodeid", "x1neip", "x1neport", "tx1normal", "tx1nomsg", "x2neip", "x2neport", "tx2normal", "tx2checkstate", "cputhreshold", "maxtargets", "lionoff", "licids"]
        self.licPara = ["x1ki", "x1password", "x1sqn", "x1licip", "x1licport", "x2ki", "x2password", "x2sqn", "x2licaddrs"]
        res, cmds = self.checkCmdFormat(line)
        if(res):#Parameter check passed, will try to set the value to XML.
            if(self.isFileAvaiable()):   
                try:
                    self.er = ElementTree.parse(xmlpath)
                    res = self.setValue(cmds)
                    if(res):
                        if('2.7' == version):
                            self.er.write(xmlpath, encoding='utf-8', xml_declaration=True, method='xml')
                        else:
                            self.er.write(xmlpath, encoding='utf-8')
                        logOcgsSetValue.info('Successfully set the value to node.')
                        self.returnStr="result=successful"
                    else:
                        logOcgsSetValue.error('Try to modify the XML failed.')
                        self.returnStr="result=failed\nerrordesc=Try to modify the XML failed."
                except Exception as e:
                    logOcgsSetValue.error('Try to set the value to XML configuration file failed.' + e.args)
                    self.returnStr="result=failed\nerrordesc=Try to set the value to XML configuration file failed."
                finally:
                    isAvaiable = True
            else:
                logOcgsSetValue.error('The simulator is too busy, unable to set the values, please try again.')
                self.returnStr="result=failed\nerrordesc=Server is too busy to handle the setting action."
            
            
    
    def isFileAvaiable(self):
        global isAvaiable
        i = 0
        while(i < 15):
            if(isAvaiable):
                isAvaiable = False
                return True
            time.sleep(1)
            i += 1
        return False
   
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
            logOcgsSetValue.error('Try to set node value error, msg: ' + e.args)
            return False
    
    def setLicValue(self, licinfo):
        if(licinfo.has_key('id')):
            licid = licinfo['id']
            lickv = licinfo['lickv']
            lic = self.findLicByID(licid)
            if(lic is not None):
                try:
                    for k, v in lickv:
                        lic.find(k).text = v
                    return True
                except Exception as e:
                    logOcgsSetValue.error('Try to set LIC value ERROR, msg: ' + e.args)
                    return False
            else:
                logOcgsSetValue.error('The licid that you specified does not exist!')
                self.returnStr="result=failed\nerrordesc=The licid that you specified does not exist!"
                return False
        else:
            logOcgsSetValue.info("No lic related parameters will be set.")
            return True
    
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
            logOcgsSetValue.error('The number of the command is not correct.')
            self.returnStr="result=failed\nerrordesc=The number of setting command is not correct."
            return False, None
        else:
            if('x_modify_conf' != licmd[0]):
                logOcgsSetValue.info('The command received cannot be recognized.')
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
                            logOcgsSetValue.error('Un-recognized parameter found, will exit as failed.')
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
                                    logOcgsSetValue.error('The value of parameter lionoff of OCGS can only be on or off.')
                                    self.returnStr="result=failed\nerrordesc=The value of parameter lionoff of OCGS can only be on or off. Value: " + licmd[i + 1]
                                    return False, None
                                nodeinfo.append((licmd[i][1:], licmd[i + 1]))
                            else:
                                logOcgsSetValue.error('Un-recognized parameter found, will exit as failed.')
                                self.returnStr="result=failed\nerrordesc=The command received cannot be recognized. Parameter: " + licmd[i]
                                return False, None
                
                licinfo['lickv'] = lickv
                cmds['licinfo'] = licinfo
                cmds['nodeinfo'] = nodeinfo
        return True, cmds
    
    def returnRes(self):
        return self.returnStr.rstrip().encode('utf-8')


class OcgsLicAddRemove():
    
    def __init__(self, line, xmlpath):
        line = line.strip()
        global isAvaiable, version
        self.res = ""
        if(line not in ["ocgslicaddone", "ocgslicremoveone"]):
            self.res = "result=failed\nerrordesc=Command to add/remove LIC is in wrong format!"
            logOcgsSetValue.error('Command to add/remove LIC is in wrong format!')
        else:
            if(self.isFileAvaiable()):
                try:
                    er = ElementTree.parse(xmlpath)
                    licids = er.find('./licids')
                    lics = er.findall('./lic')
                    
                    licuds_true = []
                    for lic in lics:
                        licuds_true.append(lic.find('id').text)
                    
                    if('ocgslicaddone' == line):
                        avai_licids = ["1000", "2000", "3000", "4000", "5000", "6000", "7000", "8000"]
                        ids_canused = [k for k in avai_licids if k not in licuds_true]
                        if(len(ids_canused) > 0):
                            random.shuffle(ids_canused)
                            id_text = ids_canused[0]
                            lastlic = lics[len(lics) - 1]
                            copylic = copy.deepcopy(lastlic)
                            copylic.find('id').text = id_text
                            licids.text = ",".join(i for i in licuds_true) + "," + id_text
                            er.getroot().append(copylic)
                            
                            if('2.7' == version):
                                er.write(xmlpath, encoding='utf-8', xml_declaration=True, method='xml')
                            else:
                                er.write(xmlpath, encoding='utf-8')
                            
                            #er.write(xmlpath, encoding='utf-8', xml_declaration=True, method='xml')
                            self.res = "result=successfully"
                            logOcgsSetValue.info('Successfully add a LIC.')
                        else:
                            self.res = "result=failed\nerrordesc=There are 8 LICs on the node now, cannot added any more."
                            logOcgsSetValue.error('here are 8 LICs on the node now, cannot added any more.')
                    else:
                        if(len(lics) > 1):
                            lastlic = lics[len(lics) - 1]
                            er.getroot().remove(lastlic)
                            ids = ",".join(t.find('id').text for t in er.findall('./lic'))
                            er.find('./licids').text = ids
                            
                            #er.write(xmlpath, encoding='utf-8', xml_declaration=True, method='xml')
                            if('2.7' == version):
                                er.write(xmlpath, encoding='utf-8', xml_declaration=True, method='xml')
                            else:
                                er.write(xmlpath, encoding='utf-8')
                            
                            self.res = "result=successfully"
                            logOcgsSetValue.info('Successfully remove the last LIC.')
                        else:
                            self.res = "result=failed\nerrordesc=There is only one LIC on the node now, cannot be removed any more."
                            logOcgsSetValue.error('There is only one LIC on the node now, cannot be removed any more.')
                except Exception as e:
                    self.res = "result=failed\nerrordesc=Mostly is that the XML file format is bad."
                    logOcgsSetValue.error('Mostly is that the XML file format is bad. msg: ' + e.args)
                finally:
                    isAvaiable = True
            else:
                self.res = "result=failed\nerrordesc=Server is busy when try to add/remove LICs."
                logOcgsSetValue.error('Server is busy when try to add/remove LICs')
    
    def isFileAvaiable(self):
        global isAvaiable
        i = 0
        while(i < 15):
            if(isAvaiable):
                isAvaiable = False
                return True
            time.sleep(1)
            i += 1
        return False
    
    def getRes(self):
        return self.res.rstrip().encode('utf-8')

'''xmlpath = '/Users/lowitty/git/server/config/ocgs/ocgs_node1.xml'
e = OcgsLicAddRemove("ocgslicremoveone", xmlpath)
e = OcgsLicAddRemove("ocgslicaddone", xmlpath)
print e.getRes()

cmds = "x_modify_conf -x2neport 3333 -licid 9000 -x1sqn 4321 -x2sqn 4321 -x2neport 2222"
ha = OcgsSetValue(cmds, xmlpath)
print ha.returnRes()'''