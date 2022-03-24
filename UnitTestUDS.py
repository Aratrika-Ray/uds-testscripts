from datetime import datetime
import os, sys, json
import Producer, Consumer
import RabbitMQConfiguration
import S3Utility
import RequestMessage
import RegressionSuite
from FileChecking import errorChecking

lock = {'folderLock': False, 'subFolderLock': False, 'downloadLock': False}

class run:
    topFolder = "RegressionTests"
    tests = {'Unit_Test_1': "Hidden Sheets - ", 'Unit_Test_2': "Multi-Header Columns AND Multiple File Transformation - ", 'Unit_Test_3': "Password Protected Files AND Wrong Password Case - ", 'Unit_Test_4': "Hidden Sheets AND File with Long Name - ", 'Unit_Test_5': "Zip Files AND Multiple Zip File Transformation- ", 'Unit_Test_6': "UI Params - ", 'Unit_Test_7': "Color Coding - ", 'Unit_Test_8': "Large Payloads - ", 'Unit_Test_9':".xls and .xlsx Transformation - ", 'Unit_Test_10': "AP&SP Transformation - ", 'Unit_Test_11': "New Classifier & Extraneous Row Fix - ", 'Unit_Test_12': "Wrong Password Case - ", 'Unit_Test_13': "Exception Sheet Errors & Scheme Level Errors - ", 'Unit_Test_14': "Miro Details in Total Sheet - ", 'Unit_Test_15': "Paypoint Information in Transformed Sheet - ",
    'NeuralNetClassifier_Unit_Test_1': "Hidden Sheets - ", 'NeuralNetClassifier_Unit_Test_2': "Multi-Header Columns AND Multiple File Transformation - ", 'NeuralNetClassifier_Unit_Test_3': "Password Protected Files AND Wrong Password Case - ", 'NeuralNetClassifier_Unit_Test_4': "Hidden Sheets AND File with Long Name - ", 'NeuralNetClassifier_Unit_Test_5': "Zip Files AND Multiple Zip File Transformation- ", 'NeuralNetClassifier_Unit_Test_6': "UI Params - ", 'NeuralNetClassifier_Unit_Test_7': "Color Coding - ", 'NeuralNetClassifier_Unit_Test_8': "Large Payloads - ", 'NeuralNetClassifier_Unit_Test_9': ".xls and .xlsx Transformation - ", 'NeuralNetClassifier_Unit_Test_10': "AP&SP Transformation - ", 'NeuralNetClassifier_Unit_Test_11': "New Classifier & Extraneous Row Fix - ", 'NeuralNetClassifier_Unit_Test_12': "Wrong Password Case - ", 'NeuralNetClassifier_Unit_Test_13': "Exception Sheet Errors & Scheme Level Errors - ", 'NeuralNetClassifier_Unit_Test_14': "Miro Details in Total Sheet - ", 'NeuralNetClassifier_Unit_Test_15': "Paypoint Information in Transformed Sheet - " }

    # Method called on receiving a response from UDS
    def onMessageReceived(self, ch, method, properties, body):
        response = body.decode('UTF-8')
        print(f"\nConsumed Message - {response}")
        self.postTest(response)

    # Upload a file to S3 bucket in a given region
    def preTest(self, uploadFilePath, rulesAssetPath, columnMappingPath):
        self.rulesAssetId = self.s3.uploadFileAWS(rulesAssetPath)
        self.columnMapAssetId = self.s3.uploadFileAWS(columnMappingPath)
        self.fileAssetId = self.s3.uploadFileAWS(uploadFilePath)
        return (self.rulesAssetId is not None) and (self.columnMapAssetId is not None) and (self.fileAssetId is not None)

    # Generate a MQ message and send to UDS
    def Test(self, testId, ui, file, transform, docName="originalNameWithPrefix", docMode="interleaved"):
        # find MQ template of the file being processed
        mqtransform = "aptrans_" if ui else transform
        MQTemplateFile = f"{self.idealFolder.replace('NeuralNetClassifier_', '')}/{(os.path.splitext(os.path.split(file)[1])[0]).replace('original_', '')}_{mqtransform}RequestMessageTemplate.json"
        msg = RequestMessage.new(MQTemplateFile, testId, self.config)
        msg.newAsset(self.fileAssetId, 'no', 'tika')

        pubMsg = msg.getRequestMessage(self.rulesAssetId,self.columnMapAssetId, transform, docName, docMode)
        self.producer.publishMessage(pubMsg)
        print(f"Published Message: {pubMsg}\n")
        
        self.numTests += 1

   # End of test
    def postTest(self, response):
        responseObject = json.loads(response)
        for assetsInfo in responseObject['assetsInfo']:
            try:
                if(assetsInfo['outputAssets'] != []):
                    for outputAssets in assetsInfo['outputAssets']:
                        # checking success status
                        if(outputAssets['hasTransformedAsset'] != False):
                            filemetadata, downloaded = self.s3.downloadFileAWS(outputAssets['extractedStructuredContent'], self.downloadFolder)
                            print(f"{downloaded}\n{filemetadata}")
                        else:
                            if(outputAssets['extractedStructuredContent'] == 'NONE'):
                                print(f"There was an error downloading one of the files in {self.testID}")
                            elif("password" in outputAssets['extractedStructuredContent']):
                                self.tests[self.testID] += "Password was not provided or it was wrong for one of the password protected files --"
                else:
                    print("\n**** NO ASSETS RECIEVED! ****\n")
            except Exception as e:
                print(f"File could not be downloaded becase error -- {e} occured!")
                continue

        self.numTests -= 1
        self.closeChannels(self.numTests == 0)

    # close channels after downloaidng all files in the folder
    def closeChannels(self, close):
        if(close):
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

        idealFolder = self.downloadFolder.replace('transformed_', 'expected_')
        subFolder = idealFolder.split('/')[-1]
        self.tests[unitTest] += subFolder if 'Unit_Test_' not in subFolder else ""
        # set a Pass/Fail status againt each test case
        self.tests[unitTest] += " \033[1mPass\033[0m " if (RegressionSuite.regressionTest(idealFolder, self.downloadFolder) and self.tests[unitTest] != "Fail") else " \033[1mFail\033[0m "

    # set values for pre-tesing and testing
    def startTest(self, folderMap, rulesAssetPath, columnMappingPath):
        uiparams = True if folderMap['properties']['uiparams'] else False

        subFolder = {}
        for file in folderMap['files']:
            # in case of zipped files, create sub-folders as download folder will be different (transformed_zipfilename/)
            folder = f"{os.path.split(file)[0]}/{os.path.splitext(os.path.basename(file))[0]}" if folderMap['properties']['zipped'] else os.path.split(file)[0]
            if(not folder in subFolder): subFolder[folder] = [(file, folderMap['files'][file])]
            else: subFolder[folder].append((file, folderMap['files'][file]))
        self.subFolders = len(subFolder)
        for folder in subFolder:
            while(lock['subFolderLock']): continue
            self.numTests = 0
            lock['subFolderLock'] = True
            # set the download folder according 
            self.downloadFolder = folder.replace('original_', 'transformed_') if not self.newClassifier else folder.replace("/Unit", "/NeuralNetClassifier_Unit").replace('original', 'transformed')

            for file in subFolder[folder]:
                for transformation in file[1]:
                    ruleFilePath = rulesAssetPath[0] if transformation == 'aptrans' else rulesAssetPath[1]
                    if(uiparams):
                        # the different combinations for docprocessor name, docprocessor mode and prefix/suffix
                        uicombinations = [('originalNameWithPrefix', f"interleaved_{transformation}_", 'interleaved'),('originalNameWithSuffix',f"_interleaved_{transformation}", 'interleaved'),('retainOriginalName', '', 'interleaved'),('newName', f"interleaved_{transformation}_newName_of_{os.path.splitext(os.path.split(file[0])[1])[0].replace('original_', '')}", 'interleaved'),
                        ('originalNameWithPrefix', f"new_{transformation}_", 'new'),('originalNameWithSuffix', f"_new_{transformation}", 'new'),('retainOriginalName', '', 'new'),('newName', f"new_{transformation}_newName_of_{os.path.splitext(os.path.split(file[0])[1])[0].replace('original_', '')}", 'new')]
                        for ui in uicombinations:
                            if(self.preTest(file[0], ruleFilePath, columnMappingPath)):
                                self.Test(self.testID, True, file[0], ui[1], ui[0], ui[2])
                    else:
                        if(self.preTest(file[0], ruleFilePath, columnMappingPath)):
                            self.Test(self.testID, False, file[0], f"{transformation}_")

    # constructor
    def __init__(self, testId, description, topFolder, unitFolderMap, rulesAssetPath, columnMappingPath, new):
        self.config = RabbitMQConfiguration.instance()
        self.s3 = S3Utility.instance(self.config.getS3Region(), self.config.getS3Bucket())
        self.consumer = Consumer.newConsumer(self.config, self.onMessageReceived)
        self.producer = Producer.newProducer(self.config)

        self.newClassifier = new
        self.testID = testId if not self.newClassifier else f"NeuralNetClassifier_{testId}"
        self.testDesc = description
        if(self.testID not in self.tests): self.tests[self.testID] = "New Test Case testID(please set a brief desc): "

        print(f"\n\033[1m*************** Running test {self.testID} ***************\033[0m")
        print(f"\033[1mDescription:\033[0m {self.testDesc}\n")

        self.topFolder = topFolder
        self.subFolders = 0
        self.numTests = 0
        self.downloadFolder = f"{self.topFolder}/{testId}" if not self.newClassifier else f"{self.topFolder}/NeuralNetClassifier_{testId}"
        self.idealFolder = self.downloadFolder

        self.startTest(unitFolderMap, rulesAssetPath, columnMappingPath)


def setTests(unitFolderMap, ap, sp, map, topFolder, new=False):
#    sys.stdout = open(f"regression_report_{datetime.date(datetime.now())}.txt", "a")
    # loop the unit folder dictionary and runs one test case at a time.

    try:
        for unitTestFolder in unitFolderMap:
            while(lock['folderLock']): continue
            lock['folderLock'] = True
            run(unitTestFolder, f"UDS testing for {unitTestFolder}", topFolder, unitFolderMap[unitTestFolder], [ap, sp], map, new)

        while(not (lock['folderLock']==False and lock['subFolderLock']==False)): continue

        return True, run.tests
    # except block will finish the current running unit test and then end
    except (KeyboardInterrupt):
        sys.__stdout__.write("\033[1;31m\nKeyboard Interrupt detected!\nWaiting for the current test case to finish\n\033[0;0m")
        while(not (lock['folderLock']==False and lock['subFolderLock']==False)): continue
        for key in run.tests:
            print(f"{key}: {run.tests[key]}")
            sys.__stdout__.write(f"{key}: {run.tests[key]}\n")
        sys.exit(0)
