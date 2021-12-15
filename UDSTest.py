import Producer 
import Consumer
import RabbitMQConfiguration
import S3Utility
import RequestMessage
import json
import argparse

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
    def Test(self, testId, transformType):
        msg = RequestMessage.new(testId, self.config)
        msg.newAsset(self.fileAssetId, 'no', 'tika')
        self.producer.publishMessage(msg.getRequestMessage(self.rulesAssetId,self.columnMapAssetId,'TRANSFORM_MODE', transformType))

    # End of test
    def postTest(self, response):
        responseObject = json.loads(response)
        for assetsInfo in responseObject['assetsInfo']:
            for outputAssets in assetsInfo['outputAssets']:
                # checking success status
                if(outputAssets['status'] == "DATAEXTRACT_SUCCESS"):
                    self.s3.downloadFileAWS(outputAssets['extractedStructuredContent'])
                    self.apDownload = True
                else: print("\n There has been some error!", outputAssets['status'], "\n")
        self.producer.close()
        self.consumer.close()
        print('********************** End of Test **********************')
   
    # constructor
    def __init__(self, testId, description, uploadFilePath, rulesAssetPath, columnMappingPath):
        self.config = RabbitMQConfiguration.instance()
        self.s3 = S3Utility.instance(self.config.getS3Region(), self.config.getS3Bucket())
        self.consumer = Consumer.newConsumer(self.config, self.onMessageReceived)
        self.producer = Producer.newProducer(self.config)
        self.apDownload = False
        
        # if(self.preTest(testId, description, uploadFilePath, rulesAssetPath[0], columnMappingPath)):
        #     self.Test(testId)

        # for both ap and sp rules
        if(len(rulesAssetPath) > 1):
            if(self.preTest(testId, description, uploadFilePath, rulesAssetPath[0], columnMappingPath)):
                self.Test(testId, "aptrans_")
            # after ap download, start sp process
            self.consumer = Consumer.newConsumer(self.config, self.onMessageReceived)
            self.producer = Producer.newProducer(self.config)
            if(self.apDownload and self.preTest(testId, description, uploadFilePath, rulesAssetPath[1], columnMappingPath)):
                self.Test(testId, "sptrans_")
        else:
            transformType = "aptrans_" if testId[len(testId)-2:]=="AP" else "sptrans_"
            if(self.preTest(testId, description, uploadFilePath, rulesAssetPath[0], columnMappingPath)):
                self.Test(testId, transformType)
            
# run('Unit_Test','This is a template dry run', 'Scheme_605685_fortest.xlsx', 'rules.dslr', 'column-map1.json')
# parser for command line flags
parser = argparse.ArgumentParser()
parser.add_argument("-f", type=str, required=True)
parser.add_argument("-ap", type=str)
parser.add_argument("-sp", type=str)
parser.add_argument("-map", type=str, required=True)

args = parser.parse_args()

# check for all rules combination    
# ap & sp
if(args.ap and args.sp): 
    run('Unit_Test_AP_SP','This is a template dry run for ap and sp transform', args.f, [args.ap, args.sp], args.map)
#ap only
elif(args.ap):
    run('Unit_Test_AP','This is a template dry run for ap transform', args.f, [args.ap], args.map)
#sp only
elif(args.sp):
    run('Unit_Test_SP','This is a template dry run for sp transform', args.f, [args.sp], args.map)
# neither
else: 
    print("Please use an AP or SP rule file to continue...")