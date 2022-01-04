import Producer, Consumer
import RabbitMQConfiguration
import S3Utility
import RequestMessage
import os, sys, json

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
        msg = RequestMessage.new(testId, self.config)
        msg.newAsset(self.fileAssetId, 'no', 'tika')
        self.producer.publishMessage(msg.getRequestMessage(self.rulesAssetId,self.columnMapAssetId,'TRANSFORM_MODE'))

    # End of test
    def postTest(self, response):
        responseObject = json.loads(response)
        for assetsInfo in responseObject['assetsInfo']:
            for outputAssets in assetsInfo['outputAssets']:
                self.s3.downloadFileAWS(outputAssets['extractedStructuredContent'])
        self.producer.close()
        self.consumer.close()
        print('********************** End of Test **********************')
   
    # constructor
    def __init__(self, testId, description, uploadFilePath, rulesAssetPath, columnMappingPath):
        self.config = RabbitMQConfiguration.instance()
        self.s3 = S3Utility.instance(self.config.getS3Region(), self.config.getS3Bucket())
        self.consumer = Consumer.newConsumer(self.config, self.onMessageReceived)
        self.producer = Producer.newProducer(self.config)
        
        if(self.preTest(testId, description, uploadFilePath, rulesAssetPath, columnMappingPath)):
            self.Test(testId)
            
run('Unit_Test','This is a template dry run', 'Scheme_605685_fortest.xlsx', 'ap_rules.dslr', 'column-map1.json')