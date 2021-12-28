import json
import RabbitMQConfiguration

class new:
    # Get request message JSON
    def getRequestMessage(self, rulesAssetId, columnMapAssetId, docProcessingMode, filePrefix, password):
        self.request['rulesAssetId'] = rulesAssetId
        self.request['columnMapAssetId'] = columnMapAssetId
        self.request['docProcessingMode'] = docProcessingMode
        self.request['outputFormat']['outputDocumentNameValue'] = filePrefix
        self.request['filePassword'] = password
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
    def __init__(self, testId, config):
        with open('RequestMessageTemplate.json','r') as stream:
            try:
                template = json.load(stream)
                template['requestMsgId'] = 'reqMsgId_' + testId
                template['replyMQExchange'] = config.getConsumeExchange()
                template['replyMQRoutingKey'] = config.getConsumeRoutingKey()
                template['s3bucket'] = config.getS3Bucket()
                self.request = template 
            except Exception as e:
                print(e)

