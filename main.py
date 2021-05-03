from csv import DictReader
from re import search
from salesforceUtils import Utils

sfdu = Utils('yourdevname1','test')
sfdu.salesforce_login()

filename = 'CSV_TO_CONVERT.csv'
try: 
    with open(filename, 'r' ) as csv_file:
        sfdu.setCustomMetadataName((search('\[(.*)__mdt\]',csv_file.read())).group(1))
        csv_file.close()

    with open(filename, 'r' ) as csv_file:
        reader = DictReader(csv_file)
        for line in reader:
            sfdu.createXML(line)
        csv_file.close()
        print('My work here is done')
except:
    print('GENERIC ERROR')
