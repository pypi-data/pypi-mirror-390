from .utils import BaseScenario
from rest_framework.response import Response
from django.contrib.auth import authenticate

class UsernamePasswordScenario(BaseScenario):

    schema = {
        "type": "object",
        "properties": {
            "username": {
                "type": "string",
                "minLength": 3,
                "maxLength": 255
            },
            "password": {
                "type": "string",
                "minLength": 8,
                "maxLength": 255
            }
        },
        "required": ["username", "password"]
    }


    def __init__(self, name, key="username-password", each_user_TTL=300) -> None:
        super().__init__(name, key, each_user_TTL)

    def get_user(self, user_id, options):
        return authenticate(username=options.get("username"), password=options.get("password"))
    
    def validate(self, user_payload, scenario_options) -> Response:
        return Response()