import json
import RabbitMQConfiguration
from random import randint


class new:
    # Get request message JSON
    def getRequestMessage(self, rulesAssetId, columnMapAssetId, filePrefix, docName, docMode):
        self.request['rulesAssetId'] = rulesAssetId
        self.request['columnMapAssetId'] = columnMapAssetId
        self.request['outputFormat']['outputDocumentName'] = docName
        self.request['outputFormat']['outputDocumentNameValue'] = filePrefix
        self.request['outputFormat']['documentOutputMode'] = docMode
        self.request['requestId'] = f"{self.request['requestMsgId'].replace('reqMsgId_', '')}@{randint(1000,9999)}"

        return json.dumps(self.request)
                
    # Add new asset to request
    def newAsset(self, id, performOCR, ocrEngine):
        asset = {
            'id':id,
            'performOCR':performOCR,
            'ocrEngine':ocrEngine
        }
        self.request['assets'].append(asset)
        
    # constructor
    def __init__(self, MQTemplateFile, testId, config):
        with open(MQTemplateFile, "r") as stream:
            try:
                template = json.load(stream)
                template['requestMsgId'] = 'reqMsgId_' + testId
                template['replyMQExchange'] = config.getConsumeExchange()
                template['replyMQRoutingKey'] = config.getConsumeRoutingKey()
                template['s3bucket'] = config.getS3Bucket()
                self.request = template
            except Exception as e:
                print(e)
