import argparse
from csv import DictReader
from re import search
from salesforceUtils import Utils

 
# Initialize parser
parser = argparse.ArgumentParser()
 
# Adding optional argument
parser.add_argument("-o", "--Output", help = "Output Directory Path")
parser.add_argument("-i", "--InputFile", help = "Input File Path")
parser.add_argument("-c", "--Credentials", help = "Path of Credentials")
parser.add_argument("-z", "--Organization", help = "Organization Name in Credentials file")
parser.add_argument("-u", "--Username", help = "Write your Salesforce Username")
parser.add_argument("-p", "--Password", help = "Write your Salesforce Password")
parser.add_argument("-t", "--SecurityToken", help = "Write your Salesforce Security Token")
parser.add_argument("-d", "--Domain", help = "test or prod")
 
# Read arguments from command line
args = parser.parse_args()

# Check correct params filled
assert ((args.Output and args.InputFile) and ((args.Credentials and args.Organization) or (args.Username and args.Password and args.SecurityToken and args.Domain)))
print('Initialization Succedeed')


sfdu = Utils( outputPath=args.Output )
if(args.Credentials):
    sfdu.inizialize_by_file(logininfopath=args.Credentials, organization=args.Organization)
else:
    sfdu.inizialize_by_value(username=args.Username,password=args.Password, security_token=args.SecurityToken, domain=args.Domain)

sfdu.salesforce_login()

try: 
    with open(args.InputFile, 'r' ) as csv_file:
        sfdu.setCustomMetadataName((search('\[(.*)__mdt\]',csv_file.read())).group(1))
        csv_file.close()

    with open(args.InputFile, 'r' ) as csv_file:
        reader = DictReader(csv_file)
        for line in reader:
            sfdu.createXML(line)
        csv_file.close()
        print('My work here is done')
except:
    print('GENERIC ERROR')
