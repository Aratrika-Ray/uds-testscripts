import os
import sys
from UDSTest import run

# Disable
def blockstdout():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablestdout():
    sys.stdout = sys.__stdout__

class runTests:
    topFolder = 'RegressionTests'
    ap_rules = 'ap_rules.dslr'
    sp_rules = 'sp_rules.dslr'
    mapping = 'column-map1.json'

    def __init__(self):
        folders = [folder for folder in os.listdir(self.topFolder) if os.path.isdir(os.path.join(self.topFolder,folder))]

        for folder in folders:
            #og_files = [files for file in os.listdir(folder) if file.startswith('original_')]
            expected_files = [file for file in os.listdir(os.path.join(self.topFolder,folder)) if file.startswith('expected_')]
            self.checkRules(expected_files, folder)

            # need to check if the expected file is an ap or sp or both transformed
            # depending on that, need to feed in the ap/sp file paths
            # need to call UDS.run() for each original file in the folder
            # if original file is password protected need to ask for password on commandline
            # if wrong password then continue with the other test cases but output as:
            #              Unit_Test_Password: Password incorrect/ required/ other response
            # Response for incorrect & password not given --> Received message - {"requestMsgId":"reqMsgId_Unit_Test_AP","dataExtractionIdentifier":"bd919a44-2f8f-4233-9b4b-79639ee3fa36","assetsInfo":[{"assetId":"cf876112-63bd-11ec-aa8f-06de44122f4d","outputAssets":[{"extractedContent":"","extractedStructuredContent":"{\"passwordProtected\": true }","status":"DATAEXTRACT_SUCCESS","startTime":1640242742832,"extractionTimeInMilis":293,"hasTransformedAsset":false,"passwordProtected":true,"vars":{}}]}]}

    def checkRules(self, expected_files, folder):
        rules = 0

        for file in expected_files:
            pwd = ""
            fileBreakdown = file.split('_')
            filePath = f"{self.topFolder}/{folder}/{'_'.join(fileBreakdown[2:])}"
            if(os.path.exists(filePath)):
                print(filePath)
                try:
                    if(fileBreakdown[-1].startswith('pass')):
                        pwd = input(f"\nPlease provide the password for file {filePath}: ")
                        blockstdout()
                    
                    enablestdout()
                    if(fileBreakdown[1].lower()=="aptrans"): rules = 1
                    elif(fileBreakdown[1].lower()=="sptrans"): rules = 2

                    if(rules == 1): run(f"{folder}-AP", f"AP transformation for {filePath}", filePath, [self.ap_rules], self.mapping, pwd)
                    elif(rules == 2): run(f"{folder}-SP", f"SP transformation for {filePath}", filePath, [self.sp_rules], self.mapping, pwd)
                except Exception as e:
                    print(f"Error {e} occured in RunTests.py!")

runTests()
