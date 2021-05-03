from simple_salesforce import Salesforce, SalesforceLogin, SFType
import json 
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

standardfields = ['_','Id', 'DeveloperName', 'MasterLabel', 'Language', 'NamespacePrefix', 'Label', 'QualifiedApiName']

class Utils:

    def __init__(self, outputPath):
        self.outputPath = outputPath

    def inizialize_by_file(self, logininfopath, organization):
        print(logininfopath)
        loginInfo = json.load(open(logininfopath))
        self.username       = loginInfo[organization]['username']
        self.password       = loginInfo[organization]['password']
        self.security_token = loginInfo[organization]['security_token']
        self.domain         = loginInfo[organization]['domain']

    def inizialize_by_value(self,username,password,security_token,domain):
        self.username       = username
        self.password       = password
        self.security_token = security_token
        self.domain         = domain

    def setCustomMetadataName(self, CustomMetadataNameWithoutMdt):
        self.custom_metadata_name = CustomMetadataNameWithoutMdt
        self.salesforce_retrieveCustomMetadataDefinition(self.custom_metadata_name+'__mdt')

    def salesforce_login(self):
        self.session_id, self.instance = SalesforceLogin(username=self.username, password=self.password, security_token=self.security_token, domain=self.domain)
        self.sf = Salesforce(instance=self.instance, session_id=self.session_id)
        print('I was able to log in Salesforce')

    def salesforce_retrieveCustomMetadataDefinition(self, customMetadataName):
        project = SFType(customMetadataName,self.session_id,self.instance)
        project_metadata = project.describe()
        self.cmDefinition = project_metadata.get('fields')
        print('I was able to recover the definition for: '+customMetadataName)

    def createXML(self, csvline):
        print('I\'m working on: '+csvline['DeveloperName'])
        CustomMetadata = ET.Element('CustomMetadata')
        CustomMetadata.set('xmlns', 'http://soap.sforce.com/2006/04/metadata')
        CustomMetadata.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        CustomMetadata.set('xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')
        label = ET.SubElement(CustomMetadata, 'label')
        label.text = csvline['Label'] if csvline['Label'] != None else csvline['DeveloperName']
        protected = ET.SubElement(CustomMetadata, 'protected')
        protected.text = 'false'
        
        for csvfield in csvline:
            if csvfield not in standardfields:
                values = ET.SubElement(CustomMetadata, 'values')
                field = ET.SubElement(values, 'field')
                field.text = csvfield
                value = ET.SubElement(values, 'value')
                valuekey, valuevalue = self.definetype(csvfield,csvline[csvfield])
                value.set(valuekey,valuevalue)
                value.text = csvline[csvfield]
        
        reparsed = minidom.parseString(ET.tostring(CustomMetadata, method='xml'))
        finalparsed = reparsed.toprettyxml(indent="    ", encoding = 'UTF-8')
        filename = self.custom_metadata_name + '.'+csvline['DeveloperName']+'.md-meta.xml'
        myfile = open(self.outputPath+'/'+filename, "wb")
        print('I\'m going to save: '+csvline['DeveloperName'])
        myfile.write(finalparsed)

    def definetype(self, fieldname, value):
        xsitype = 'xsi:nil'
        xsdvalue = 'true'
        if(value != None and value != ''):
            xsitype = 'xsi:type'
            xsdvalue = self.getType(fieldname)
        
        return xsitype,xsdvalue

    def getType(self, fieldname):
        for field in self.cmDefinition:
            if field['name'] == fieldname:
                soapType = field['soapType']
                if soapType == 'tns:ID':
                    return 'xsd:string'
                else:
                    return soapType
