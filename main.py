import csv
from salesforceUtils import Utils

sfdu = Utils('yourdevname1','test')
sfdu.salesforce_login()
sfdu.salesforce_retrieveCustomMetadata()

with open('Test.csv', 'r' ) as csv_file:
    reader = csv.DictReader(csv_file)
    for line in reader:
        sfdu.createXML(line)
    print('My work here is done')