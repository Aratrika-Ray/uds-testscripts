import RabbitMQUtility
import threading

class newConsumer:
    # Listen for response messages    
    def consumeMessage(self, callback):
        self.queue.getChannel().exchange_declare(exchange = self.config.getConsumeExchange(), exchange_type = 'direct')
        self.queue.getChannel().queue_declare(queue=self.config.getConsumeQueue())
        self.queue.getChannel().queue_bind(exchange=self.config.getConsumeExchange(), queue=self.config.getConsumeQueue(), routing_key=self.config.getConsumeRoutingKey())
        self.queue.getChannel().basic_consume(queue=self.config.getConsumeQueue(), on_message_callback=callback, auto_ack=True)
        self.queue.getChannel().start_consuming()
    
    # close RabbitMQ connection
    def close(self):
#        self.queue.getChannel().stop_consuming()
        self.queue.close()
        
    # constructor
    def __init__(self, config, callback):
        self.config = config
        self.queue = RabbitMQUtility.instance('Consumer', config)
        threading.Thread(target = self.consumeMessage, args = (callback,)).start()
