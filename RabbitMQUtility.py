import pika

class instance:
    def getChannel(self):
        return self.channel
                
    # defines the connection paramters for the RabbitMQ queue
    def getConnectionParameters(self,config):
        creds = pika.PlainCredentials(config.getUsername(),config.getPassword())
        return pika.ConnectionParameters(host=config.getHostname(),port=config.getPort(),credentials=creds, heartbeat=300)
        
    # Close the queue
    def close(self):
        self.channel.stop_consuming()
        self.channel.close()
        self.connection.close()
     
    # constructor
    def __init__(self, name, config):
        self.connection = pika.BlockingConnection(self.getConnectionParameters(config))
        self.channel = self.connection.channel()
        print(name + ' Queue initialization successful')

