# CSV To Salesforce CustomMetadata

1. Obtain your security token: [your salesforce domain]//_ui/system/security/ResetApiTokenEdit?retURL=%2Fui%2Fsetup%2FSetup%3Fsetupid%3DPersonalInfo&setupid=ResetApiToken

1. Compile login.json with your credentials

1. With Salesforce Inspector make a query (all fields) on custom metadata and copy-paste csv in CSV_TO_CONVERT.csv

1. start main.py like:
    1. python main.py -o C:\Users\*\Documents\Repository\force-app\main\default\customMetadata -i C:\Users\*\Documents\CSV_TO_CONVERT.csv -c C:\Users\*\Documents\login.json -z yourdevname1 
    
    1. Or see documentation if you don't want use login.json

1. Waiting until the end
