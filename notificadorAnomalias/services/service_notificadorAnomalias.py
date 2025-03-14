from hospital.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
import json
import pika
from sys import path
from os import environ
import django

rabbit_host = 'localhost'
rabbit_user = 'hospital_user'
rabbit_password = 'isis2503'
exchange = 'monitoring_measurements'
topics = ['#']


path.append('hospital/settings.py')
environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital.settings')
django.setup()


connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=rabbit_host, credentials=pika.PlainCredentials(rabbit_user, rabbit_password)))
channel = connection.channel()

channel.exchange_declare(exchange=exchange, exchange_type='topic')

result = channel.queue_declare('', exclusive=True)
queue_name = result.method.queue

for topic in topics:
    channel.queue_bind(
        exchange=exchange, queue=queue_name, routing_key=topic)

def send_email(patient:str,correo_medico:str,id):
    subject = 'Anomalía detectadas en un paciente'
    message = 'Tu paciente'+patient+'con id: '+id+' ha presentado una anomalía en sus mediciones'
    recepient = correo_medico
    send_mail(subject, message, EMAIL_HOST_USER, [recepient])

print('> Waiting measurements. To exit press CTRL+C')

def callback(ch, method, properties, body):
    payload = json.loads(body.decode('utf8').replace("'", '"'))
    topic = method.routing_key.split('.')
    send_email(topic[0],topic[1],topic[2])
    print("Evento detectado :%r" % (str(payload)))

channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()
