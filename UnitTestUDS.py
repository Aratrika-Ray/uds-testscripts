import os, sys, threading, json
from posixpath import splitext
import Producer, Consumer
import RabbitMQConfiguration
import S3Utility
import RequestMessage
import RegressionSuite

folderLock = {"lock": False}

class run:
    __tests = {}
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
    def Test(self, testId, file, password, prefix):
        MQTemplateFile = f"{self.idealFolder}/{os.path.splitext(os.path.split(file)[1])[0]}_RequestMessageTemplate.json"
        msg = RequestMessage.new(MQTemplateFile, testId, self.config)
        msg.newAsset(self.fileAssetId, 'no', 'tika')
        self.producer.publishMessage(msg.getRequestMessage(self.rulesAssetId,self.columnMapAssetId,'TRANSFORM_MODE', prefix))

    # End of test
    def postTest(self, response):
        responseObject = json.loads(response)
        err =  False
        for assetsInfo in responseObject['assetsInfo']:
            if(assetsInfo['outputAssets'] != []):
                for outputAssets in assetsInfo['outputAssets']:
                    # checking success status
                    if(outputAssets['extractedStructuredContent'] != "NONE" or outputAssets['hasTransformedAsset'] != False):
                        self.s3.downloadFileAWS(outputAssets['extractedStructuredContent'], self.downloadFolder)
                    else:
                        err = True
                        print("\n --- There has been some error! ---\n")
            else:
                err = True
                print("\n**** NO ASSETS RECIEVED! ****\n")

        self.numTests -= 1
        self.closeChannels(self.numTests == 0, err)

    def closeChannels(self, close, err):
        if(err): print("\nRegression Error: Regression testing cannot be done since there was an error with the transfored file. Either it wasn't downloaded properly or no transformed file was recieved from the server.\n")

        if(close):
            self.producer.close()
            self.consumer.close()

            self.regressionSuite()

            for key, value in self.__tests.items():
                print(f"{key}: {value}")
            
            folderLock['lock'] = False
            print('\n********************** End of Unit Test **********************\n')

    def regressionSuite(self):
        unitTest = self.testID
        print("**** Regression test for ", unitTest, " ****\n")
        status = "Pass" if RegressionSuite.regressionTest(self.idealFolder, self.downloadFolder) else "Fail"
        if(unitTest in self.__tests):
            self.__tests[unitTest] = status if self.__tests[unitTest] != "Fail" else "Fail"
        else: self.__tests[unitTest] = status

    # constructor
    def __init__(self, testId, description, topFolder, unitFolderMap, rulesAssetPath, columnMappingPath):
        self.config = RabbitMQConfiguration.instance()
        self.s3 = S3Utility.instance(self.config.getS3Region(), self.config.getS3Bucket())
        self.consumer = Consumer.newConsumer(self.config, self.onMessageReceived)
        self.producer = Producer.newProducer(self.config)

        print(f"\n\033[1m*************** Running test {testId} ***************\033[0m")
        print(f"\033[1mDescription:\033[0m {description}\n")

        self.numTests = 0
        for file in unitFolderMap['files']:
            self.numTests += len(unitFolderMap['files'][file])
        
        self.testID = testId
        self.downloadFolder = f"{self.topFolder}/{testId}"
        self.idealFolder = self.downloadFolder
        if(unitFolderMap['properties']['zipped']):
            zipFilebreakdown = next(iter(unitFolderMap['files'])).split('/')
            self.downloadFolder = f"{'/'.join(zipFilebreakdown[0:2])}/transformed_{zipFilebreakdown[2]}"
            self.idealFolder = self.downloadFolder.replace('transformed_', 'expected_')
        
        self.testDesc = description
        self.topFolder = topFolder

        for file in unitFolderMap['files']:
            for transformation in unitFolderMap['files'][file]:
                ruleFilePath = rulesAssetPath[0] if transformation == 'aptrans' else rulesAssetPath[1]
                prefix = "aptrans_" if transformation == 'aptrans' else "sptrans_"
                password = True if file.endswith('_pass.xlsx') else False
                
                if(self.preTest(file, ruleFilePath, columnMappingPath)):
                    self.Test(testId, file, password, prefix)

def setTests(unitFolderMap, ap, sp, map, topFolder):
    for uniTestFolder in unitFolderMap:
        while(folderLock['lock']): continue
        folderLock['lock'] = True
        run(uniTestFolder, f"UDS testing for {uniTestFolder}", topFolder, unitFolderMap[uniTestFolder], [ap, sp], map)