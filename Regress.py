conn = {'producerConn': None, 'consumerConn': None}

def setrabbitmqconn(producer, consumer):
    conn['producerConn'] = producer
    conn['consumerConn'] = consumer

def getrabbitmqconn():
    return conn