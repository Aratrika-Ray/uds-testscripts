import yaml
from os.path import dirname, abspath

class instance:
    def getHostname(self):
        return self.HOSTNAME

    def getPort(self):
        return self.PORT

    def getUsername(self):
        return self.USERNAME

    def getPassword(self):
        return self.PASSWORD

    def getPublishExchange(self):
        return self.PUBLISH_EXCHANGE

    def getPublishRoutingKey(self):
        return self.PUBLISH_ROUTING_KEY

    def getPublishQueue(self):
        return self.QUEUE

    def getConsumeExchange(self):
        return self.CONSUME_EXCHANGE

    def getConsumeQueue(self):
        return self.CONSUME_QUEUE_SUFFIX

    def getConsumeRoutingKey(self):
        return self.CONSUME_ROUTING_QUEUE_SUFFIX

    def getS3Region(self):
        return self.S3REGION

    def getS3Bucket(self):
        return self.S3BUCKET

    # Read the UDS RabbitMQ configurations
    def getRabbitMQConfiguration(self):
        parentDir = dirname(dirname(abspath(__file__)))
        with open(parentDir + '/config/uds.yml','r') as stream:
            try:
                configurations = yaml.full_load(stream)
                # RabbitMQ configurations read from uds.yml
                self.HOSTNAME = configurations['messagequeue']['host']
                self.PORT = configurations['messagequeue']['port']
                self.USERNAME = configurations['messagequeue']['user']
                self.PASSWORD = configurations['messagequeue']['password']
                self.PUBLISH_EXCHANGE = configurations['messagequeue']['exchange']
                self.PUBLISH_ROUTING_KEY = configurations['messagequeue']['routingKey']
                self.QUEUE = configurations['messagequeue']['queue']

                # Additional RabbitMQ configurations
                self.CONSUME_EXCHANGE = 'UDS_RESPONSE_UNIT_TEST'
                self.CONSUME_QUEUE_SUFFIX = 'UEN_DATAEXT_UNIT_TEST'
                self.CONSUME_ROUTING_QUEUE_SUFFIX = self.CONSUME_QUEUE_SUFFIX
                self.OCR_ENGINE = 'tika'

                # S3 configurations
                self.S3REGION = configurations['awsS3Region']
                self.S3BUCKET = 'ushurdev'
                print('RabbitMQ configurations retrieved successfully')
            except Exception as e:
                print('Failed to load uds.yml')
                print(e)

    # constructor
    def __init__(self):
        self.getRabbitMQConfiguration()