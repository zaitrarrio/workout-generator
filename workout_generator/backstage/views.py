import datetime
import os

from boto import dynamodb2
from boto.dynamodb2.table import Table

from django.http import Http404
from django.shortcuts import render_to_response

from workout_generator.user.models import User
from workout_generator.datetime_tools import datetime_to_timestamp_ms


TABLE_NAME = os.environ['AWS_TABLE_NAME']
REGION = "us-east-1"


class BackstageViews(object):

    @classmethod
    def _validate_user(cls, request):
        password = os.environ['BACKSTAGE_PASSWORD']
        if request.GET.get('password', '') != password:
            raise Http404

    @classmethod
    def home(cls, request):
        cls._validate_user(request)
        # FIXME page_size gets overstuffed
        page_index = int(request.GET.get("page_index", 0))
        users = User.get_paged_users(page_index)
        render_data = {
            "next": page_index + 1,
            "prev": max(page_index - 1, 0),
            "get_params": request.GET,
            "users": users
        }
        return render_to_response("backstage/home.html", render_data)

    @classmethod
    def user(cls, request, user_id):
        cls._validate_user(request)
        user = User.get_by_id(user_id)
        render_data = {
            "lines": cls._get_dynamo_for_user(user_id).replace(" ", "&nbsp;").split("\n"),
            "user": user
        }
        return render_to_response("backstage/user.html", render_data)

    @classmethod
    def _get_dynamo_for_user(cls, user_id):
        conn = dynamodb2.connect_to_region(
            REGION,
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        )
        table = Table(
            TABLE_NAME,
            connection=conn
        )
        results = table.query_2(
            user_id_hash__eq="workout_%s" % user_id,
            timestamp__between=[
                datetime_to_timestamp_ms(datetime.datetime.utcnow() - datetime.timedelta(days=7)),
                datetime_to_timestamp_ms(datetime.datetime.utcnow())
            ]
        )
        for dynamo_item in results:
            return dynamo_item.get("message", "")
        return "This is a test\n   this is a test"
        return ""
