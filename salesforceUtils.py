from simple_salesforce import Salesforce, SalesforceLogin, SFType
import json 
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re

standardfields = ['_','Id', 'DeveloperName', 'MasterLabel', 'Language', 'NamespacePrefix', 'Label', 'QualifiedApiName']

class Utils:

    def __init__(self,organization,domain):
        self.organization = organization
        self.domain = domain
        self.createTree()

    def salesforce_login(self):
        loginInfo = json.load(open('login.json'))
        username = loginInfo[self.organization]['username']
        password = loginInfo[self.organization]['password']
        security_token = loginInfo[self.organization]['security_token']
        domain = self.domain
        self.session_id, self.instance = SalesforceLogin(username=username, password=password, security_token=security_token, domain=domain)
        self.sf = Salesforce(instance=self.instance, session_id=self.session_id)

    def salesforce_retrieveCustomMetadata(self):
        customMetadata = []
        metadata_org = self.sf.describe()
        for element in metadata_org['sobjects']:
            if element['name'].endswith("__mdt"):
                customMetadata.append(element['name'])

        for element in customMetadata:
            sobjectDef = self.retrieve_obj(element)
            print('Saving '+element+' Sobject Definition')
            self.saveToMetadataFolder(element,sobjectDef)

    def retrieve_obj(self, objectName):
        project = SFType(objectName,self.session_id,self.instance)
        project_metadata = project.describe()
        return project_metadata.get('fields')

    def createTree(self):
        if not os.path.exists('./Resource'):
            os.makedirs('./Resource')

        if not os.path.exists('./Resource/'+self.organization):
            os.makedirs('./Resource/'+self.organization)

        if not os.path.exists('./Result'):
            os.makedirs('./Result')

    def saveToMetadataFolder(self, filename, body):
        with open('./Resource/'+self.organization+'/'+filename+'.json','w',) as outfile:
            json.dump(body,outfile)

    def createXML(self, csvline):
        self.custom_metadata_name = (re.search('\[(.*)__mdt\]',csvline['_'])).group(1)
        print('I\'m working on: 'csvline['DeveloperName'])
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
        myfile = open('Result/'+filename, "wb")
        print('I\'m going to save: 'csvline['DeveloperName'])
        myfile.write(finalparsed)

    def definetype(self, fieldname, value):
        xsitype = 'xsi:nil'
        xsdvalue = 'true'
        if(value != None and value != ''):
            xsitype = 'xsi:type'
            xsdvalue = self.getType(fieldname)
        
        return xsitype,xsdvalue

    def getType(self, fieldname):
        file = json.load(open('./Resource/'+self.organization+'/'+self.custom_metadata_name+'__mdt.json'))
        for field in file:
            if field['name'] == fieldname:
                soapType = field['soapType']
                if soapType == 'tns:ID':
                    return 'xsd:string'
                else:
                    return soapType
