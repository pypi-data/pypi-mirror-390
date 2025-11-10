from rest_framework.response import Response
from django.core import cache
from hashlib import md5


class BaseScenario:

    schema = {}

    def __init__(self, name, key, each_user_TTL) -> None:
        self.name = name
        self.key = key
        self.each_user_TTL = each_user_TTL
    

    def validate(self, user_payload, scenario_options) -> Response:
        """
        if this function returns true
        then auth go to next scenario
        else return 401 error to user
        """
        return Response()

    @property
    def objects(self):
        return {
            "scenario": self.name,
            "schema": self.schema
        }

    def get_user(self, user_id, payload):
        return None
    
    def sign(self, previous_payload):
        previous_scenario_hash = cahce.get(previous_scenario_hash)
        return md5(previous_scenario_hash.encode()).hexdigest()


    def run(self, previous_scenario_hash:str):
        sign = self.sign(previous_scenario_hash)
        return sign
