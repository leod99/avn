# this script get metrics from remote hosts and send to kafka topic
import logging, os, time
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
from datetime import datetime
from fabric2 import Connection


KAFKA_SERVER = 'kafka-282e881e-chrdeng9-e577.aivencloud.com:16120'
SCHEMA_REGISTRY_URL = 'https://avnadmin:passwordi2s@kafka-282e881e-chrdeng9-e577.aivencloud.com:16123'
# Kafka server cert/key file relative path
CAFILE = '/secrets/ca.pem'
CERTFILE = '/secrets/service.cert'
KEYFILE = '/secrets/service.key'
# Kafka topic
TOPIC = 'metrics'

# login user on remote hosts
USER = 'ec2-user'
# pem key file to login remote hosts
KEY_FILE = 'monitoradmin.pem'
HOSTS_FILE = 'hostnames.txt'

#TODO read from json file
value_schema_str = """
{"namespace": "com.aiven.monitor",
 "type": "record",
 "name": "metrics",
 "fields": [
     {"name": "host", "type": "string"},
     {"name": "cpu",  "type": "float"},
     {"name": "memory",  "type": "float"},
     {"name": "disk",  "type": "float"},
     {"name": "timestamp",  "type": "string"},
     {"name": "desc",  "type": "string"}
 ]
}
"""
key_schema_str = """
{"namespace": "com.aiven.monitor",
 "type": "record",
 "name": "key",
 "fields": [
     {"name": "key",  "type": "string"}
 ]
}
"""

value_schema = avro.loads(value_schema_str)
key_schema = avro.loads(key_schema_str)


# Kafka topic producer
class Producer():
    def __init__(self):
        os.chdir(os.path.dirname(__file__))
        pwd = os.getcwd()

        self._producer = AvroProducer({
            'bootstrap.servers': KAFKA_SERVER,
            'schema.registry.url': SCHEMA_REGISTRY_URL,
            'security.protocol': 'ssl',
            'ssl.ca.location': pwd + CAFILE,
            'ssl.certificate.location': pwd + CERTFILE,
            'ssl.key.location': pwd + KEYFILE

            }, default_key_schema=key_schema, default_value_schema=value_schema)

    def produce(self, topic, value):
        self._producer.produce(topic=topic, value=value)

    def flush(self):
        self._producer.flush()


def remote_info(c, hostname):
    """Get metrics from remote host

    Args:
       c: fabrics.Connection object
       hostname (str): host DNS name 
    Returns:
       dict of metrics
    """
    c.run('uptime')
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
    print("datetime: %s" % dt_string)
    #cpu used in percentage %
    cpu = c.run("LC_ALL=C top -bn1 | grep 'Cpu(s)' | sed 's/.*,[ ]*\([0-9.]*\).* id.*/\\1/' | awk '{print 100 - $1}'")

    # memory used percentage
    mem = c.run("free -m | awk '/Mem:/ { printf(\"%3.1f%%\", $3/$2*100) }'")
    # disk space used percentage
    hdd = c.run("df -h / | awk '/\// {print $(NF-1)}'")

    res = "Usage CPU %s%%, MEM %s, DISK %s" % (cpu.stdout, mem.stdout, hdd.stdout)
    print("ok:%s" % cpu.ok)

    res = {}
    if cpu.ok and mem.ok and hdd.ok:
        res = {
                'host': hostname,
                'cpu': float(cpu.stdout.strip()),
                'memory': float(mem.stdout.strip()[:-1]),
                'disk': float(hdd.stdout.strip()[:-1]),
                'timestamp': dt_string,
                'desc': ''
              }
    else:
        print("Error: %s\n%s\n%s" % (cpu.stderr, mem.stderr, hdd.stderr))
    return res


def main(unused_argv=0):

    producer = Producer()
    # load host names from file
    filename = os.getcwd() + "/" + HOSTS_FILE
    hosts = [line.rstrip('\n') for line in open(filename)]

    for host in hosts:
        print("host: %s" % host)
        if not host or not bool(host.strip()):
            continue
        host = host.strip()
        #TODO add try catch
        #try:
        c = Connection(
            host = host,
            user = USER,
            connect_kwargs = {
                "key_filename": os.getcwd() + "/hostsecrets/" + KEY_FILE,
            }
        )
        with c:
          res = remote_info(c, host)
          print('res:%s' % res)
          if len(res) > 0:
              # send message if it's not empty
              producer.produce(TOPIC, res)
        #except e:
    producer.flush()
    print("done")


if __name__ == '__main__':
    main()
