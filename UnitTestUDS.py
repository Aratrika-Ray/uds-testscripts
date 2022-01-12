import os, sys, threading, json
<<<<<<< HEAD
=======
from posixpath import splitext
>>>>>>> 154e1f6a8025e0da49763bd00367360424e3f2ae
import Producer, Consumer
import RabbitMQConfiguration
import S3Utility
import RequestMessage
import RegressionSuite

<<<<<<< HEAD
lock = {'folderLock': False, 'subFolderLock': False, 'downloadLock': False}

class run:
    __tests = {'Unit_Test_1': "Hidden Sheets - ", 'Unit_Test_2': "Multi-Header Columns - ", 'Unit_Test_3': "Password Protected Files - ", 'Unit_Test_4': "Hidden Sheets and file with Long Name - ", 'Unit_Test_5': "Zip Files - ", 'Unit_Test_6': "UI Params - ", 'Unit_Test_7': "Color Coding - ", 'Unit_Test_8': "Large Payloads(currently not working)", 'Unit_Test_9': ".xls and .xlsx Transformation - ", 'Unit_Test_10': "AP&SP Transformation - "}
=======
lock = {'folderLock': False, 'downloadLock': False}

class run:
    __tests = {}
>>>>>>> 154e1f6a8025e0da49763bd00367360424e3f2ae
    topFolder = "RegressionTests"

    # Method called on receiving a response from UDS
    def onMessageReceived(self, ch, method, properties, body):
        response = body.decode('UTF-8')
        print('Received message - ' + response)
        self.postTest(response)

    # Upload a file to S3 bucket in a given region
    def preTest(self, uploadFilePath, rulesAssetPath, columnMappingPath):
        self.rulesAssetId = self.s3.uploadFileAWS(rulesAssetPath)
        self.columnMapAssetId = self.s3.uploadFileAWS(columnMappingPath)
        self.fileAssetId = self.s3.uploadFileAWS(uploadFilePath)
        return (self.rulesAssetId is not None) and (self.columnMapAssetId is not None) and (self.fileAssetId is not None)
        
    # Generate a MQ message and send to UDS
    def Test(self, testId, file, transform, docName="originalNameWithPrefix", docMode="interleaved"):
        MQTemplateFile = f"{self.idealFolder}/{(os.path.splitext(os.path.split(file)[1])[0]).replace('original_', '')}_RequestMessageTemplate.json"
        msg = RequestMessage.new(MQTemplateFile, testId, self.config)
        msg.newAsset(self.fileAssetId, 'no', 'tika')
        self.producer.publishMessage(msg.getRequestMessage(self.rulesAssetId,self.columnMapAssetId, transform, docName, docMode))

   # End of test
    def postTest(self, response):
        responseObject = json.loads(response)
        err =  False
        for assetsInfo in responseObject['assetsInfo']:
            try:
                if(assetsInfo['outputAssets'] != []):
                    for outputAssets in assetsInfo['outputAssets']:
                        # checking success status
<<<<<<< HEAD
                        if(outputAssets['hasTransformedAsset'] != False):
=======
                        if(outputAssets['extractedStructuredContent'] != "NONE" or outputAssets['hasTransformedAsset'] != False):
>>>>>>> 154e1f6a8025e0da49763bd00367360424e3f2ae
                            while(lock['downloadLock']): continue
                            lock['downloadLock'] = True
                            self.s3.downloadFileAWS(outputAssets['extractedStructuredContent'], self.downloadFolder)
                            lock['downloadLock'] = False
                        else:
                            err = True
<<<<<<< HEAD
                            if(outputAssets['extractedStructuredContent'] == 'NONE'):
                                self.__tests[self.testID] += "There was an error downloading one of the file -- "
                            elif("password" in outputAssets['extractedStructuredContent']):
                                self.__tests[self.testID] += "Password was not provided or it was wrong for one of the password protected files -- "
=======
                            print("\n --- There has been some error! ---\n")
>>>>>>> 154e1f6a8025e0da49763bd00367360424e3f2ae
                else:
                    err = True
                    print("\n**** NO ASSETS RECIEVED! ****\n")
            except Exception as e:
<<<<<<< HEAD
                print(f"File could not be downloaded becase error -- {e} occured!")
=======
                print(f"Error: {e} occured!")
>>>>>>> 154e1f6a8025e0da49763bd00367360424e3f2ae

        self.numTests -= 1
        self.closeChannels(self.numTests == 0, err)

<<<<<<< HEAD
    # close channels after downloaidng all files in the folder
=======
>>>>>>> 154e1f6a8025e0da49763bd00367360424e3f2ae
    def closeChannels(self, close, err):
        if(err): print("\nRegression Error: Regression testing cannot be done since there was an error with the transfored file. Either it wasn't downloaded properly or no transformed file was recieved from the server.\n")

        if(close):
<<<<<<< HEAD
            self.regressionSuite()

            self.subFolders -= 1
            lock['subFolderLock'] = False

            if(self.subFolders == 0):
                self.producer.close()
                self.consumer.close()
                
                for key in self.__tests.keys():
                    print(f"{key}: {self.__tests[key]}")
                
                lock['folderLock'] = False
                print('\n********************** End of Unit Test **********************\n')

    # start comparison of files
    def regressionSuite(self):
        unitTest = self.testID
        print(f"**** Regression test for {unitTest} ****\n")
        self.__tests[unitTest] += " Pass" if (RegressionSuite.regressionTest(self.idealFolder, self.downloadFolder) and self.__tests[unitTest] != "Fail") else " Fail"

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
            self.downloadFolder = folder.replace('original_', 'transformed_')
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
=======
            self.producer.close()
            self.consumer.close()

            self.regressionSuite()

            for key, value in self.__tests.items():
                print(f"{key}: {value}")
            
            lock['folderLock'] = False
            print('\n********************** End of Unit Test **********************\n')

    def regressionSuite(self):
        unitTest = self.testID
        print("**** Regression test for ", unitTest, " ****\n")
        status = "Pass" if RegressionSuite.regressionTest(self.idealFolder, self.downloadFolder) else "Fail"
        if(unitTest in self.__tests):
            self.__tests[unitTest] = status if self.__tests[unitTest] != "Fail" else "Fail"
        else: self.__tests[unitTest] = status


    def startTest(self, folderMap, rulesAssetPath, columnMappingPath):
        for file in folderMap['files']:
            for transformation in folderMap['files'][file]:
                ruleFilePath = rulesAssetPath[0] if transformation == 'aptrans' else rulesAssetPath[1]
                uiparams = True if folderMap['properties']['uiparams'] else False

                if(uiparams):
                    uicombinations = [('originalNameWithPrefix', f"interleaved_{transformation}_", 'interleaved'),('originalNameWithSuffix', f"_interleaved_{transformation}", 'interleaved'),('retainOriginalName', '', 'interleaved'),('newName', f"interleaved_{transformation}_newName_of_{os.path.splitext(os.path.split(file)[1])[0].replace('original_', '')}", 'interleaved'),
                    ('originalNameWithPrefix', f"new_{transformation}_", 'new'),('originalNameWithSuffix', f"_new_{transformation}", 'new'),('retainOriginalName', '', 'new'),('newName', f"new_{transformation}_newName_of_{os.path.splitext(os.path.split(file)[1])[0].replace('original_', '')}", 'new')]
                    self.numTests = len(uicombinations)
                    for ui in uicombinations:
                        if(self.preTest(file, ruleFilePath, columnMappingPath)):
                            self.Test(self.testID, file, ui[1], ui[0], ui[2])
                else:
                    if(self.preTest(file, ruleFilePath, columnMappingPath)):
                        self.Test(self.testID, file, f"{transformation}_")
>>>>>>> 154e1f6a8025e0da49763bd00367360424e3f2ae

    # constructor
    def __init__(self, testId, description, topFolder, unitFolderMap, rulesAssetPath, columnMappingPath):
        self.config = RabbitMQConfiguration.instance()
        self.s3 = S3Utility.instance(self.config.getS3Region(), self.config.getS3Bucket())
        self.consumer = Consumer.newConsumer(self.config, self.onMessageReceived)
        self.producer = Producer.newProducer(self.config)

        print(f"\n\033[1m*************** Running test {testId} ***************\033[0m")
        print(f"\033[1mDescription:\033[0m {description}\n")

        self.testID = testId
        self.testDesc = description
        self.topFolder = topFolder
<<<<<<< HEAD
        self.subFolders = 0
        self.numTests = 0 
        self.downloadFolder = f"{self.topFolder}/{testId}"
        self.idealFolder = self.downloadFolder
=======
        self.numTests = 0
        for file in unitFolderMap['files']:
            self.numTests += len(unitFolderMap['files'][file])       
        self.downloadFolder = f"{self.topFolder}/{testId}"
        self.idealFolder = self.downloadFolder
        if(unitFolderMap['properties']['zipped']):
            file = next(iter(unitFolderMap['files']))
            self.downloadFolder = os.path.split(file)[0].replace('original_', 'transformed')
            self.idealFolder = self.downloadFolder.replace('transformed_', 'expected_')
>>>>>>> 154e1f6a8025e0da49763bd00367360424e3f2ae
        
        self.startTest(unitFolderMap, rulesAssetPath, columnMappingPath)       


def setTests(unitFolderMap, ap, sp, map, topFolder):
<<<<<<< HEAD
    for unitTestFolder in unitFolderMap:
        while(lock['folderLock']): continue
        if(unitTestFolder != 'Unit_Test_6' and unitFolderMap != 'Unit_Test_8'):
            lock['folderLock'] = True
            run(unitTestFolder, f"UDS testing for {unitTestFolder}", topFolder, unitFolderMap[unitTestFolder], [ap, sp], map)
=======
    for uniTestFolder in unitFolderMap:
        while(lock['folderLock']): continue
        lock['folderLock'] = True
        run(uniTestFolder, f"UDS testing for {uniTestFolder}", topFolder, unitFolderMap[uniTestFolder], [ap, sp], map)
>>>>>>> 154e1f6a8025e0da49763bd00367360424e3f2ae
