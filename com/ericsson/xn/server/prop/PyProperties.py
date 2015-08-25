#encoding=utf-8
'''
Created on Aug 24, 2015

@author: lowitty
'''
import os
class Properties():
    
    def __init__(self, propertyFile):
        self.path = os.path.normpath(propertyFile)
        if(not os.path.isfile(self.path)):
            raise IOError("The path that you specified is not a file.")
        else:
            self.file = open(self.path, 'rb')
            lines = self.file.readlines()
            self.mappings = {}
            for line in lines:
                keyValue = line.split('=')
                if(len(keyValue) > 1):
                    self.mappings[keyValue[0]] = keyValue[1].rstrip('\r').rstrip('\n')
            self.file.close()
                    
    def getProperty(self, key):
        if(self.mappings.has_key(key)):
            return self.mappings[key]
        else:
            return None
        
    def setProperty(self, key, value):
        if(self.mappings.has_key(key)):
            self.mappings[key] = value
            
    def store(self):
        if(not os.path.isfile(self.path)):
            raise IOError("The path that you specified is not a file.")
        else:
            lKeyValue = []
            for key, value in self.mappings.iteritems():
                lKeyValue.append(key + '=' + value + '\n')
            f = open(self.path, 'wb')
            f.writelines(lKeyValue)
            f.flush()
            f.close()
                    
        