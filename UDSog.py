import Producer 
import Consumer
import RabbitMQConfiguration
import S3Utility
import RequestMessage
import json
import argparse
import RegressionSuite
import threading
import os

class run:
    __tests = {}

    # Method called on receiving a response from UDS
    def onMessageReceived(self, ch, method, properties, body):
        response = body.decode('UTF-8')
        print('Received message - ' + response)
        self.postTest(response)

    # Upload a file to S3 bucket in a given region
    def preTest(self, testId, description, uploadFilePath, rulesAssetPath, columnMappingPath):
        print('*************** Running test ' + testId + ' ***************')
        print('Description : transforming ' + uploadFilePath) 
        print('Rules : ' + rulesAssetPath)
        self.rulesAssetId = self.s3.uploadFileAWS(rulesAssetPath)
        self.columnMapAssetId = self.s3.uploadFileAWS(columnMappingPath)
        self.fileAssetId = self.s3.uploadFileAWS(uploadFilePath)
        return (self.rulesAssetId is not None) and (self.columnMapAssetId is not None) and (self.fileAssetId is not None)
        
    # Generate a MQ message and send to UDS
    def Test(self, testId, prefix):
        print("In Test")
        filePrefix = "aptrans_" if prefix[:2]=="ap" else "sptrans_"
        msg = RequestMessage.new(testId, self.config)
        msg.newAsset(self.fileAssetId, 'no', 'tika')
        self.producer.publishMessage(msg.getRequestMessage(self.rulesAssetId,self.columnMapAssetId,'TRANSFORM_MODE', filePrefix, "601597"))

    # End of test
    def postTest(self, response):
        responseObject = json.loads(response)
        testID = responseObject['requestMsgId'].split("_")
        folderName = "_".join(testID[1:])
        for assetsInfo in responseObject['assetsInfo']:
            for outputAssets in assetsInfo['outputAssets']:
                # checking success status
                if(outputAssets['status'] == "DATAEXTRACT_SUCCESS"):
                    self.s3.downloadFileAWS(outputAssets['extractedStructuredContent'], folderName)
                else:
                    print("\n ---There has been some error! **", outputAssets['status'], "**---\n")

        self.numTests -= 1
        self.closeChannels(folderName, self.numTests==0)

    def closeChannels(self, folderName, close):
        # compare expected and tranformed file and ouput Success/Failure
        self.regressionSuite(folderName)

        if(close):
            self.producer.close()
            self.consumer.close()
            for key, value in self.__tests.items():
                print(f"{key}: {value}")
            print('\n********************** End of Test **********************\n')

    def regressionSuite(self, unitTestFolder):
        print("**** Regression test for ", unitTestFolder, " ****\n")
        status = "Pass" if RegressionSuite.regressionTest(unitTestFolder) else "Fail"
        if(unitTestFolder in self.__tests):
            self.__tests[unitTestFolder] = status if self.__tests[unitTestFolder] != "Fail" else "Fail"
        else: self.__tests[unitTestFolder] = status

    # constructor
    def __init__(self, testId, description, uploadFilePath, rulesAssetPath, columnMappingPath):
        self.config = RabbitMQConfiguration.instance()
        print(f"s3 bucket --> {self.config.getS3Bucket()}")
        self.s3 = S3Utility.instance(self.config.getS3Region(), self.config.getS3Bucket())
        self.consumer = Consumer.newConsumer(self.config, self.onMessageReceived)
        self.producer = Producer.newProducer(self.config)
        self.numTests = len(rulesAssetPath)

        for rule in rulesAssetPath:    
            if(self.preTest(testId, description, uploadFilePath, rule, columnMappingPath)):
                self.Test(testId, rule)
            
# parser for command line flags
parser = argparse.ArgumentParser()
parser.add_argument("-f", type=str, required=True)
parser.add_argument("-ap", type=str)
parser.add_argument("-sp", type=str)
parser.add_argument("-m", type=str, required=True)
parser.add_argument("-r", type=str)
args = parser.parse_args()

def runTest(testID, testDesc, file, rules, mapping):
    run(testID, testDesc, file, rules, mapping)

if(not args.r):
    # ap & sp
    if(args.ap and args.sp): 
        runTest('Unit_Test_AP_SP','This is a template dry run for ap&sp transform', args.f, [args.ap, args.sp], args.m)
    #ap only
    elif(args.ap):
        runTest('Unit_Test_AP','This is a template dry run for ap transform', args.f, [args.ap], args.m)
    #sp only
    elif(args.sp):
        runTest('Unit_Test_SP','This is a template dry run for sp transform', args.f, [args.sp], args.m)
    # neither
    else: 
        print("Please use an AP or SP rule file to continue...")
# regression test suite
elif(args.r):
    print("\n********** Running all 3 test cases **********\n")
    
    threads = []
    t1 = threading.Thread(target=runTest('Unit_Test_AP_SP','This is a template dry run for ap&sp transform', args.f, [args.ap, args.sp], args.m))
    t2 = threading.Thread(target=runTest('Unit_Test_AP','This is a template dry run for ap transform', args.f, [args.ap], args.m))
    t3 = threading.Thread(target=runTest('Unit_Test_SP','This is a template dry run for sp transform', args.f, [args.sp], args.m))
    threads.extend((t1, t2, t3))

    for thread in threads:
        thread.start()
        thread.join()
