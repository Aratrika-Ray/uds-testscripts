import Producer 
import Consumer
import RabbitMQConfiguration
import S3Utility
import RequestMessage
import json
import argparse
import RegressionSuite
import threading

def regressionSuite(transformedFolder):
    RegressionSuite("path to idealFolder", transformedFolder)

class run:
    # Method called on receiving a response from UDS
    def onMessageReceived(self, ch, method, properties, body):
        response = body.decode('UTF-8')
        print('Received message - ' + response)
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
    def Test(self, testId):
        filePrefix = "aptrans_" if testId[len(testId)-2:]=="AP" else "sptrans_"
        msg = RequestMessage.new(testId, self.config)
        msg.newAsset(self.fileAssetId, 'no', 'tika')
        self.producer.publishMessage(msg.getRequestMessage(self.rulesAssetId,self.columnMapAssetId,'TRANSFORM_MODE', filePrefix))

    # End of test
    def postTest(self, response):
        responseObject = json.loads(response)
        testID = responseObject['requestMsgId'].split("_")
        folderName = "_".join(testID[1:])
        for assetsInfo in responseObject['assetsInfo']:
            for outputAssets in assetsInfo['outputAssets']:
                # checking success status
                if(outputAssets['status'] == "DATAEXTRACT_SUCCESS"):
                    filePath = self.s3.downloadFileAWS(outputAssets['extractedStructuredContent'], folderName)
                else:
                    print("\n ---There has been some error! **", outputAssets['status'], "**---\n")
        self.producer.close()
        self.consumer.close()
        print('********************** End of Test **********************')
        
        # compare expected and tranformed file and ouput Success/Failure
        regressionSuite(folderName)
   
    # constructor
    def __init__(self, testId, description, uploadFilePath, rulesAssetPath, columnMappingPath):
        self.config = RabbitMQConfiguration.instance()
        self.s3 = S3Utility.instance(self.config.getS3Region(), self.config.getS3Bucket())
        self.consumer = Consumer.newConsumer(self.config, self.onMessageReceived)
        self.producer = Producer.newProducer(self.config)
                
        if(self.preTest(testId, description, uploadFilePath, rulesAssetPath, columnMappingPath)):
            self.Test(testId)
            
# parser for command line flags
parser = argparse.ArgumentParser()
parser.add_argument("-f", type=str, required=True)
parser.add_argument("-ap", type=str)
parser.add_argument("-sp", type=str)
parser.add_argument("-m", type=str, required=True)
parser.add_argument("-r", type=str)
args = parser.parse_args()

def runAP(file, aprules, mapping):
    run('Unit_Test_AP','This is a template dry run for ap transform', file, aprules, mapping)

def runSP(file, sprules, mapping):
    run('Unit_Test_SP','This is a template dry run for sp transform', file, sprules, mapping)

def runAP_SP(file, aprules, sprules, mapping):
    runAP(file, aprules, mapping)
    runSP(file, sprules, mapping)

if(not args.r):
    # ap & sp
    if(args.ap and args.sp): 
        runAP_SP(args.f, args.ap, args.sp, args.m)
    #ap only
    elif(args.ap):
        runAP(args.f, args.ap, args.m)
    #sp only
    elif(args.sp):
        runSP(args.f, args.sp, args.m)
    # neither
    else: 
        print("Please use an AP or SP rule file to continue...")
# regression test suite
elif(args.r):
    print("\n********** Running all 3 test cases **********\n")
    
    t1 = threading.Thread(target=runAP(args.f, args.ap, args.m))
    t2 = threading.Thread(target=runSP(args.f, args.sp, args.m))
    t3 = threading.Thread(target=runAP_SP(args.f, args.ap, args.sp, args.m))

    #run only ap
    print("ONLY AP\n")
    t1.start()

    #run only sp
    print("ONLY SP\n")
    t1.join()
    t2.start()

    #run both AP and SP
    print("BOTH AP & SP\n")
    t2.join()
    t3.start()
