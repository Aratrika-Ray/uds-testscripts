import os
import Producer 
import Consumer
import RabbitMQConfiguration
import S3Utility
import RequestMessage
import json
<<<<<<< HEAD
import RegressionSuite

class run:
    __tests = {}
    __password = ""
=======
import argparse
import RegressionSuite
import threading

class run:
    __tests = {}
>>>>>>> ca021bb0b21902343875533183cdf1725fcf2ea6

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
<<<<<<< HEAD
    def Test(self, testId):
        filePrefix = "aptrans_" if testId.split('-')[1]=="AP" else "sptrans_"
=======
    def Test(self, testId, prefix):
        filePrefix = "aptrans_" if prefix[:2]=="ap" else "sptrans_"
>>>>>>> ca021bb0b21902343875533183cdf1725fcf2ea6
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
<<<<<<< HEAD
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
=======
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
>>>>>>> ca021bb0b21902343875533183cdf1725fcf2ea6

        if(close):
            self.producer.close()
            self.consumer.close()
            for key, value in self.__tests.items():
                print(f"{key}: {value}")
            
            print('\n********************** End of Test **********************\n')

<<<<<<< HEAD
    def regressionSuite(self, transformedFolder):
        print("**** Regression test for ", transformedFolder, " ****\n")
        status = "Pass" if RegressionSuite.regressionTest(transformedFolder) else "Fail"
=======

    def regressionSuite(self, transformedFolder):
        print("**** Regression test for ", transformedFolder, " ****\n")
        status = "Pass" if RegressionSuite.regressionTest("Input_Files", transformedFolder) else "Fail"
>>>>>>> ca021bb0b21902343875533183cdf1725fcf2ea6
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
<<<<<<< HEAD
        self.__password = password

        for rule in rulesAssetPath:    
            if(self.preTest(testId, description, uploadFilePath, rule, columnMappingPath)):
                self.Test(testId)
=======

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
>>>>>>> ca021bb0b21902343875533183cdf1725fcf2ea6
