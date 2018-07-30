from elastalert.alerts import Alerter
from elastalert.util import elastalert_logger
import pika

class RabbitMQAlerter(Alerter):
    """ Publishes a message to RabbitMQ for each alert """
    required_options = frozenset(
            ['rabbitmq_host', 'rabbitmq_port', 'rabbitmq_user', 'rabbitmq_pass',
                'rabbitmq_vhost', 'rabbitmq_exchange', 'rabbitmq_key'])

    def __init__(self, rule):
        super(RabbitMQAlerter, self).__init__(rule)
        self.rabbitmq_host = self.rule.get('rabbitmq_host', 'localhost')
        self.rabbitmq_port = self.rule.get('rabbitmq_port', '5672')
        self.rabbitmq_user = self.rule.get('rabbitmq_user', None)
        self.rabbitmq_pass = self.rule.get('rabbitmq_pass', None)
        self.rabbitmq_exchange = self.rule.get('rabbitmq_exchange', 'default')
        self.rabbitmq_key = self.rule.get('rabbitmq_key', 'default')
        self.rabbitmq_vhost = self.rule.get('rabbitmq_vhost', None)

    def alert(self, matches):
        body = self.create_alert_body(matches)
        alert_body = body.replace('\\', '\\\\')

        """ Setup connection to RabbitMQ """

        credentials = pika.PlainCredentials(self.rabbitmq_user, self.rabbitmq_pass)
        connection = pika.BlockingConnection(pika.ConnectionParameters(self.rabbitmq_host, self.rabbitmq_port,
                                                                       self.rabbitmq_vhost, credentials))
        channel = connection.channel()
        channel.basic_publish(exchange=self.rabbitmq_exchange, routing_key=self.rabbitmq_key, body=alert_body)
        connection.close()
        elastalert_logger.info("Alert sent to RabbitMQ")

    def get_info(self):
        return {'type': 'rabbitmq',
                'rabbitmq_host': self.rabbitmq_host,
                'rabbitmq_port': self.rabbitmq_port,
                'rabbitmq_user': self.rabbitmq_user,
                'rabbitmq_pass': self.rabbitmq_pass,
                'rabbitmq_exchange': self.rabbitmq_exchange,
                'rabbitmq_key': self.rabbitmq_key,
                'rabbitmq_vhost': self.rabbitmq_vhost}
