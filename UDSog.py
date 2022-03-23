import Producer, Consumer
import RabbitMQConfiguration
import S3Utility
import RequestMessage
import os, sys, json
import argparse

class run:
    # Method called on receiving a response from UDS
    def onMessageReceived(self, ch, method, properties, body):
        response = body.decode('UTF-8')
        print('\nReceived message - ' + response)
        self.postTest(response)

    # Upload a file to S3 bucket in a given region
    def preTest(self, testId, description, uploadFilePath, rulesAssetPath, columnMappingPath):
        print('*************** Running test ' + testId + ' ***************')
        print('Description : ' + description)
        self.rulesAssetId = self.s3.uploadFileAWS(rulesAssetPath)
        self.columnMapAssetId = self.s3.uploadFileAWS(columnMappingPath)
        self.fileAssetId = self.s3.uploadFileAWS(uploadFilePath)

        return (self.rulesAssetId is not None) and (self.columnMapAssetId is not None) and (self.fileAssetId is not None)
        
    # Generate a MQ message and send to UDS
    def Test(self, testId, file, transform, docName="originalNameWithPrefix", docMode="interleaved"):
        MQTemplateFile = "RequestMessageTemplate.json"
        msg = RequestMessage.new(MQTemplateFile, testId, self.config)
        msg.newAsset(self.fileAssetId, 'no', 'tika')

        pubMsg = msg.getRequestMessage(self.rulesAssetId,self.columnMapAssetId, transform, docName, docMode)
        self.producer.publishMessage(pubMsg)
        print(f"Published Message: {pubMsg}")
        self.numTests += 1

    # End of test
    def postTest(self, response):
        responseObject = json.loads(response)
        testID = responseObject['requestMsgId'].split("_")
        folderName = "_".join(testID[1:])
        msg = "postTest issues"
        for assetsInfo in responseObject['assetsInfo']:
            try:
                for outputAssets in assetsInfo['outputAssets']:
                # checking success status
                    if(outputAssets['hasTransformedAsset'] != False):
                        self.s3.downloadFileAWS(outputAssets['extractedStructuredContent'], folderName)
                    else:
                        err = True
                        if(outputAssets['extractedStructuredContent'] == 'NONE'):
                            msg += 'There was an error downloading the file -- '
                        elif("password" in outputAssets['extractedStructuredContent']):
                            msg += 'Password was not provided or it was wrong for one of the password protected files -- '
                        print(f"\n-------- {msg} ------\n") 
            except Exception as e:
                print(f"{msg}\nerror: {e} occured!")

        self.numTests -= 1
        self.closeChannels(folderName, self.numTests==0)

    def closeChannels(self, folderName, close):
        # compare expected and tranformed file and ouput Success/Failure
#        self.regressionSuite(folderName)
         if(close):
            self.producer.close()
            self.consumer.close()

            print('\n********************** End of Test **********************\n')

    def regressionSuite(self, unitTestFolder):
        print("**** Regression test for ", unitTestFolder, " ****\n")
        status = "Pass" if RegressionSuite.regressionTest(unitTestFolder) else "Fail"
        if(unitTestFolder in self.__tests):
            self.__tests[unitTestFolder] = status if self.__tests[unitTestFolder] != "Fail" else "Fail"
        else: self.__tests[unitTestFolder] = status

    # constructor
    def __init__(self, testId, description, uploadFilePath, ruleFilePath, columnMappingPath):
        self.config = RabbitMQConfiguration.instance()
        self.s3 = S3Utility.instance(self.config.getS3Region(), self.config.getS3Bucket())
        self.consumer = Consumer.newConsumer(self.config, self.onMessageReceived)
        self.producer = Producer.newProducer(self.config)
        self.numTests = 8 if args.ui else len(ruleFilePath)

        uiparams = True if args.ui else False
        transformation = 'aptrans' if 'ap' in ruleFilePath[0] else 'sp'
        if(uiparams):
            uicombinations = [('originalNameWithPrefix', f"interleaved_{transformation}_", 'interleaved'),('originalNameWithSuffix', f"_interleaved_{transformation}", 'interleaved'),('newName', f"interleaved_{transformation}_newName_of_{os.path.splitext(uploadFilePath)[0]}", 'interleaved'),
            ('originalNameWithPrefix', f"new_{transformation}_", 'new'),('originalNameWithSuffix', f"_new_{transformation}", 'new'),('newName', f"new_{transformation}_newName_of_{os.path.splitext(uploadFilePath)[0]}", 'new')]
            for ui in uicombinations:
                if(self.preTest(testId, description, uploadFilePath, ruleFilePath[0], columnMappingPath)):
                    self.Test(testId, uploadFilePath, ui[1], ui[0], ui[2])
        else:
            if(self.preTest(testId, description, uploadFilePath, ruleFilePath[0], columnMappingPath)):
                self.Test(testId, uploadFilePath, f"{transformation}_")

            
# parser for command line flags
parser = argparse.ArgumentParser()
parser.add_argument("-f", type=str, required=True)
parser.add_argument("-ap", type=str)
parser.add_argument("-sp", type=str)
parser.add_argument("-m", type=str, required=True)
parser.add_argument("-r", type=str)
parser.add_argument("-ui", type=str)
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
