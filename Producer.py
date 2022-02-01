import RabbitMQUtility
import threading

class newProducer:
    # Send message on the queue
    def publishMessage(self, message):
        self.queue.getChannel().basic_publish(exchange=self.config.getPublishExchange(), routing_key=self.config.getPublishRoutingKey(), body=message)
        return message
            
    # close RabbitMQ connection
    def close(self):
        self.queue.close()
        
    # constructor
    def __init__(self,config):
        self.config = config
        self.queue = RabbitMQUtility.instance('Producer', config)