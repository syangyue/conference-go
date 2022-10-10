from datetime import datetime
import json
import pika
from pika.exceptions import AMQPConnectionError
import django
import os
import sys
import time
from attendees.models import AccountVO
sys.path.append("")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "attendees_bc.settings")
django.setup()




while True:
    try:
        # Declare a function to update the AccountVO object (ch, method, properties, body)
        def update_account_VO(ch, method, properties, body):

            #   content = load the json in body
            content = json.loads(body)
            first_name = content["first_name"]
            last_name = content["last_name"]
            email = content["email"]
            is_active = content["is_active"]
            updated_string = content["updated"]
            #   updated = convert updated_string from ISO string to datetime
            updated = datetime.fromisoformat(updated_string)

            print("UPDATE ACCOUNT VO IS HERE")
            print("is active:", is_active)

            #   if is_active:
            if is_active:
                AccountVO.objects.update_or_create(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    is_active=is_active,
                    updated=updated,
                    defaults={"email": email},
                )
            else:
                AccountVO.objects.filter(email=email).delete()

            #       Use the update_or_create method of the AccountVO.objects QuerySet
            #           to update or create the AccountVO object
            #   otherwise:
            #       Delete the AccountVO object with the specified email, if it exists

            # Based on the reference code at
            #   https://github.com/rabbitmq/rabbitmq-tutorials/blob/master/python/receive_logs.py
            # infinite loop

        def main():
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host="rabbitmq")
            )
            channel = connection.channel()

            channel.exchange_declare(
                exchange="account_info", exchange_type="fanout"
            )

            result = channel.queue_declare(queue="", exclusive=True)
            queue_name = result.method.queue

            channel.queue_bind(exchange="account_info", queue=queue_name)

            # def callback(ch, method, properties, body):
            #     print(" [x] %r" % body.decode())

            # print(" [*] Waiting for logs. To exit press CTRL+C")

            print("PIKACHU")

            channel.basic_consume(
                queue=queue_name,
                on_message_callback=update_account_VO,
                auto_ack=True,
            )

            channel.start_consuming()

        if __name__ == "__main__":
            try:
                main()
            except KeyboardInterrupt:
                print("Interrupted")
                try:
                    sys.exit(0)
                except SystemExit:
                    os._exit(0)

    #       create the pika connection parameters
    #       create a blocking connection with the parameters
    #       open a channel
    #       declare a fanout exchange named "account_info"
    #       declare a randomly-named queue
    #       get the queue name of the randomly-named queue
    #       bind the queue to the "account_info" exchange
    #       do a basic_consume for the queue name that calls
    #           function above
    #       tell the channel to start consuming
    except AMQPConnectionError:
        print("Could not connect to RabbitMQ BUT I LIKE CATS")
        time.sleep(2.0)
#       print that it could not connect to RabbitMQ
#       have it sleep for a couple of seconds
