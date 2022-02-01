from datetime import datetime
import os, sys, threading, json
import Producer, Consumer
import RabbitMQConfiguration
import S3Utility
import RequestMessage
import RegressionSuite
from fileChecking import errorChecking
from Regress import setrabbitmqconn

sys.stdout = open(f"regression_report_{datetime.now()}.txt")

lock = {'folderLock': False, 'subFolderLock': False, 'downloadLock': False}
# tests = {'Unit_Test_1': "Hidden Sheets - ", 'Unit_Test_2': "Multi-Header Columns AND Multiple File Transformation - ", 'Unit_Test_3': "Password Protected Files AND Wrong Password Case - ", 'Unit_Test_4': "Hidden Sheets AND File with Long Name - ", 'Unit_Test_5': "Zip Files AND Multiple Zip File Transformation- ", 'Unit_Test_6': "UI Params - ", 'Unit_Test_7': "Color Coding - ", 'Unit_Test_8': "Large Payloads - ", 'Unit_Test_9': ".xls and .xlsx Transformation - ", 'Unit_Test_10': "AP&SP Transformation - ",
#     'NeuralNetClassifier_Unit_Test_1': "Hidden Sheets - ", 'NeuralNetClassifier_Unit_Test_2': "Multi-Header Columns AND Multiple File Transformation - ", 'NeuralNetClassifier_Unit_Test_3': "Password Protected Files AND Wrong Password Case - ", 'NeuralNetClassifier_Unit_Test_4': "Hidden Sheets AND File with Long Name - ", 'NeuralNetClassifier_Unit_Test_5': "Zip Files AND Multiple Zip File Transformation- ", 'NeuralNetClassifier_Unit_Test_6': "UI Params - ", 'NeuralNetClassifier_Unit_Test_7': "Color Coding - ", 'NeuralNetClassifier_Unit_Test_8': "Large Payloads(currently not working)", 'NeuralNetClassifier_Unit_Test_9': ".xls and .xlsx Transformation - ", 'NeuralNetClassifier_Unit_Test_10': "AP&SP Transformation - "}

def sysExit():
    sys.exit(0)

class run:
    topFolder = "RegressionTests"
    tests = {'Unit_Test_1': "Hidden Sheets - ", 'Unit_Test_2': "Multi-Header Columns AND Multiple File Transformation - ", 'Unit_Test_3': "Password Protected Files AND Wrong Password Case - ", 'Unit_Test_4': "Hidden Sheets AND File with Long Name - ", 'Unit_Test_5': "Zip Files AND Multiple Zip File Transformation- ", 'Unit_Test_6': "UI Params - ", 'Unit_Test_7': "Color Coding - ", 'Unit_Test_8': "Large Payloads - ", 'Unit_Test_9': ".xls and .xlsx Transformation - ", 'Unit_Test_10': "AP&SP Transformation - ",
    'NeuralNetClassifier_Unit_Test_1': "Hidden Sheets - ", 'NeuralNetClassifier_Unit_Test_2': "Multi-Header Columns AND Multiple File Transformation - ", 'NeuralNetClassifier_Unit_Test_3': "Password Protected Files AND Wrong Password Case - ", 'NeuralNetClassifier_Unit_Test_4': "Hidden Sheets AND File with Long Name - ", 'NeuralNetClassifier_Unit_Test_5': "Zip Files AND Multiple Zip File Transformation- ", 'NeuralNetClassifier_Unit_Test_6': "UI Params - ", 'NeuralNetClassifier_Unit_Test_7': "Color Coding - ", 'NeuralNetClassifier_Unit_Test_8': "Large Payloads(currently not working)", 'NeuralNetClassifier_Unit_Test_9': ".xls and .xlsx Transformation - ", 'NeuralNetClassifier_Unit_Test_10': "AP&SP Transformation - "}


    # Method called on receiving a response from UDS
    def onMessageReceived(self, ch, method, properties, body):
        response = body.decode('UTF-8')
        print(f"Consumed Message - {response}")
        self.postTest(response)

    # Upload a file to S3 bucket in a given region
    def preTest(self, uploadFilePath, rulesAssetPath, columnMappingPath):
        self.rulesAssetId = self.s3.uploadFileAWS(rulesAssetPath)
        self.columnMapAssetId = self.s3.uploadFileAWS(columnMappingPath)
        self.fileAssetId = self.s3.uploadFileAWS(uploadFilePath)
        return (self.rulesAssetId is not None) and (self.columnMapAssetId is not None) and (self.fileAssetId is not None)
        
    # Generate a MQ message and send to UDS
    def Test(self, testId, file, transform, docName="originalNameWithPrefix", docMode="interleaved"):
        MQTemplateFile = f"{self.idealFolder.replace('NeuralNetClassifier_', '')}/{(os.path.splitext(os.path.split(file)[1])[0]).replace('original_', '')}_RequestMessageTemplate.json"
        msg = RequestMessage.new(MQTemplateFile, testId, self.config)
        msg.newAsset(self.fileAssetId, 'no', 'tika')

        pubMsg = msg.getRequestMessage(self.rulesAssetId,self.columnMapAssetId, transform, docName, docMode)
        self.producer.publishMessage(pubMsg)
        print(f"Published Message: {pubMsg}")

   # End of test
    def postTest(self, response):
        responseObject = json.loads(response)
        for assetsInfo in responseObject['assetsInfo']:
            try:
                if(assetsInfo['outputAssets'] != []):
                    for outputAssets in assetsInfo['outputAssets']:
                        # checking success status
                        if(outputAssets['hasTransformedAsset'] != False):
                            while(lock['downloadLock']): continue
                            lock['downloadLock'] = True
                            filemetadata, downloaded = self.s3.downloadFileAWS(outputAssets['extractedStructuredContent'], self.downloadFolder)
                            print(f"{downloaded}\n{filemetadata}")
                            lock['downloadLock'] = False
                        else:
                            if(outputAssets['extractedStructuredContent'] == 'NONE'):
                                print(f"There was an error downloading one of the files in {self.testID}")
                            elif("password" in outputAssets['extractedStructuredContent']):
                                self.tests[self.testID] += "Password was not provided or it was wrong for one of the password protected files -- "
                else:
                    print("\n**** NO ASSETS RECIEVED! ****\n")
            except Exception as e:
                print(f"File could not be downloaded becase error -- {e} occured!")

        self.numTests -= 1
        self.closeChannels(self.numTests == 0)

    # close channels after downloaidng all files in the folder
    def closeChannels(self, close):
        if(close):
            errorChecking(self.downloadFolder)
            self.regressionSuite()

            self.subFolders -= 1
            lock['subFolderLock'] = False

            if(self.subFolders == 0):
                self.producer.close()
                self.consumer.close()
                
                lock['folderLock'] = False
                print(f'\n********************** End of {self.testID}**********************\n')

    # start comparison of files
    def regressionSuite(self):
        unitTest = self.testID
        print(f"**** Regression test for {unitTest} ****\n")
        subFolder = self.idealFolder.split('/')[-1]
        self.tests[unitTest] += subFolder if 'Unit_Test_' not in subFolder else ""
        self.tests[unitTest] += " \033[1mPass\033[0m " if (RegressionSuite.regressionTest(self.idealFolder, self.downloadFolder) and self.tests[unitTest] != "Fail") else " \033[1mFail\033[0m "

    # set values for pretesing and testing
    def startTest(self, folderMap, rulesAssetPath, columnMappingPath):
        uiparams = True if folderMap['properties']['uiparams'] else False
        
        subFolder = {}
        for file in folderMap['files']:
            folder = os.path.split(file)[0]
            if(not folder in subFolder): subFolder[folder] = [(file, folderMap['files'][file])]
            else: subFolder[folder].append((file, folderMap['files'][file]))
        self.subFolders = len(subFolder)

        for folder in subFolder:
            while(lock['subFolderLock']): continue
            self.numTests = 0
            lock['subFolderLock'] = True
            self.downloadFolder = folder.replace('original_', 'transformed_') if not self.newClassifier else folder.replace("/Unit", "/NeuralNetClassifier_Unit").replace('original', 'transformed')
            self.idealFolder = self.downloadFolder.replace('transformed_', 'expected_')
            for file in subFolder[folder]:
                self.numTests += len(file[1])

            for file in subFolder[folder]:
                for transformation in file[1]:
                    ruleFilePath = rulesAssetPath[0] if transformation == 'aptrans' else rulesAssetPath[1]

                    if(uiparams):
                        uicombinations = [('originalNameWithPrefix', f"interleaved_{transformation}_", 'interleaved'),('originalNameWithSuffix', f"_interleaved_{transformation}", 'interleaved'),('retainOriginalName', '', 'interleaved'),('newName', f"interleaved_{transformation}_newName_of_{os.path.splitext(os.path.split(file[0])[1])[0].replace('original_', '')}", 'interleaved'),
                        ('originalNameWithPrefix', f"new_{transformation}_", 'new'),('originalNameWithSuffix', f"_new_{transformation}", 'new'),('retainOriginalName', '', 'new'),('newName', f"new_{transformation}_newName_of_{os.path.splitext(os.path.split(file[0])[1])[0].replace('original_', '')}", 'new')]
                        self.numTests = len(uicombinations)
                        for ui in uicombinations:
                            if(self.preTest(file[0], ruleFilePath, columnMappingPath)):
                                self.Test(self.testID, file[0], ui[1], ui[0], ui[2])
                    else:
                        if(self.preTest(file[0], ruleFilePath, columnMappingPath)):
                            self.Test(self.testID, file[0], f"{transformation}_")

    # constructor
    def __init__(self, testId, description, topFolder, unitFolderMap, rulesAssetPath, columnMappingPath, new, file):
        self.config = RabbitMQConfiguration.instance()
        self.s3 = S3Utility.instance(self.config.getS3Region(), self.config.getS3Bucket())
        self.consumer = Consumer.newConsumer(self.config, self.onMessageReceived)
        self.producer = Producer.newProducer(self.config)
        setrabbitmqconn(type(self.producer), self.consumer)
        self.logFile = file

        self.newClassifier = new
        self.testID = testId if not self.newClassifier else f"NeuralNetClassifier_{testId}"
        self.testDesc = description

        print(f"\n\033[1m*************** Running test {self.testID} ***************\033[0m")
        print(f"\033[1mDescription:\033[0m {self.testDesc}\n")

        self.topFolder = topFolder
        self.subFolders = 0
        self.numTests = 0 
        self.downloadFolder = f"{self.topFolder}/{testId}" if not self.newClassifier else f"{self.topFolder}/NeuralNetClassifier_{testId}"
        self.idealFolder = self.downloadFolder
        
        self.startTest(unitFolderMap, rulesAssetPath, columnMappingPath)       


def setTests(unitFolderMap, ap, sp, map, topFolder, new=False):
    for unitTestFolder in unitFolderMap:
        while(lock['folderLock']): continue
        lock['folderLock'] = True
        run(unitTestFolder, f"UDS testing for {unitTestFolder}", topFolder, unitFolderMap[unitTestFolder], [ap, sp], map, new)
    
    while(not (lock['folderLock']==False and lock['downloadLock']==False and lock['subFolderLock']==False)): continue
    return True, run.tests