import os
import Producer 
import Consumer
import RabbitMQConfiguration
import S3Utility
import RequestMessage
import json
import RegressionSuite

class run:
    __tests = {}
    __password = ""

    # Method called on receiving a response from UDS
    def onMessageReceived(self, ch, method, properties, body):
        response = body.decode('UTF-8')
        print('Received message - ' + response)
        self.postTest(response)

    # Upload a file to S3 bucket in a given region
    def preTest(self, testId, description, uploadFilePath, rulesAssetPath, columnMappingPath):
        print('*************** Running test ' + testId + ' ***************')
        print('Description : ' + description)
        print('Rules : ' + rulesAssetPath)
        self.rulesAssetId = self.s3.uploadFileAWS(rulesAssetPath)
        self.columnMapAssetId = self.s3.uploadFileAWS(columnMappingPath)
        self.fileAssetId = self.s3.uploadFileAWS(uploadFilePath)
        return (self.rulesAssetId is not None) and (self.columnMapAssetId is not None) and (self.fileAssetId is not None)
        
    # Generate a MQ message and send to UDS
    def Test(self, testId):
        filePrefix = "aptrans_" if testId.split('-')[1]=="AP" else "sptrans_"
        msg = RequestMessage.new(testId, self.config)
        msg.newAsset(self.fileAssetId, 'no', 'tika')
        self.producer.publishMessage(msg.getRequestMessage(self.rulesAssetId,self.columnMapAssetId,'TRANSFORM_MODE', filePrefix, self.__password))

    # End of test
    def postTest(self, response):
        responseObject = json.loads(response)
        testID = responseObject['requestMsgId'].split('_')
        unitTest = "_".join(testID[1:])
        folderName = f"RegressionTests/{unitTest.split('-')[0]}"
        err =  False
        for assetsInfo in responseObject['assetsInfo']:
            if(assetsInfo['outputAssets'] != []):
                for outputAssets in assetsInfo['outputAssets']:
                    # checking success status
                    if(outputAssets['extractedStructuredContent'] != "NONE" or outputAssets['hasTransformedAsset'] != False):
                        self.s3.downloadFileAWS(outputAssets['extractedStructuredContent'], folderName)
                    else:
                        err = True
                        print("\n --- There has been some error! ---\n")
            else:
                err = True
                print("\n**** NO ASSETS RECIEVED! ****\n")

        self.numTests -= 1
        self.closeChannels(folderName, self.numTests==0, err)

    def closeChannels(self, folderName, close, err):
        # compare expected and tranformed file and ouput Success/Failure
        if(not err): self.regressionSuite(folderName)
        elif(err): print("\nRegression Error: Regression testing cannot be done since there was an error with the transfored file. Either it wasn't downloaded properly or no transformed file was recieved from the server.\n")

        if(close):
            self.producer.close()
            self.consumer.close()
            for key, value in self.__tests.items():
                print(f"{key}: {value}")
            
            print('\n********************** End of Test **********************\n')

    def regressionSuite(self, transformedFolder):
        print("**** Regression test for ", transformedFolder, " ****\n")
        status = "Pass" if RegressionSuite.regressionTest(transformedFolder) else "Fail"
        if(transformedFolder in self.__tests):
            self.__tests[transformedFolder] = status if self.__tests[transformedFolder] != "Fail" else "Fail"
        else: self.__tests[transformedFolder] = status

    # constructor
    def __init__(self, testId, description, uploadFilePath, rulesAssetPath, columnMappingPath, password=""):
        self.config = RabbitMQConfiguration.instance()
        self.s3 = S3Utility.instance(self.config.getS3Region(), self.config.getS3Bucket())
        self.consumer = Consumer.newConsumer(self.config, self.onMessageReceived)
        self.producer = Producer.newProducer(self.config)
        self.numTests = len(rulesAssetPath)
        self.__password = password

        for rule in rulesAssetPath:    
            if(self.preTest(testId, description, uploadFilePath, rule, columnMappingPath)):
                self.Test(testId)
