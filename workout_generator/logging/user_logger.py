import datetime
import os
import time

from boto.dynamodb2 import connect_to_region
from boto.dynamodb2.table import Table

from django.conf import settings

AWS_TABLE_NAME = os.environ['AWS_TABLE_NAME']
REGION = "us-east-1"


def datetime_to_timestamp_ms(datetime_obj):
    return int(time.mktime(datetime_obj.timetuple()) * 1000 + (datetime_obj.microsecond / 1000))


class UserLogger(object):

    def __init__(self, user, prefix):
        connection = connect_to_region(
            REGION,
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        )
        self.table = Table(
            AWS_TABLE_NAME,
            connection=connection
        )
        self.prefix = prefix
        self.user = user
        self.messages = []

    @classmethod
    def for_user_and_prefix(cls, user, prefix):
        return UserLogger(user, prefix)

    def add_message(self, message):
        self.messages.append(message)

    def commit(self):
        required_hash_data = {
            "user_id_hash": "%s_%s" % (self.prefix, self.user.id),
            "timestamp": datetime_to_timestamp_ms(datetime.datetime.utcnow())
        }
        message_data = {
            "message": "\n".join(self.messages)
        }
        final_dynamo_data = dict(required_hash_data.items() + message_data.items())
        if getattr(settings, "TEST_RUN", False):
            # print "MOCK Sending Message: %s" % final_dynamo_data
            print "MOCK Sending Message:"
            for message in self.messages:
                for line in message.split("\n"):
                    print line
            return
        print "GOT HERE ABOUT TO SEND DATA"
        print len(message_data["message"])
        self.table.put_item(data=final_dynamo_data)
