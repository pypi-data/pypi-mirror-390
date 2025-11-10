from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework.response import Response
from django.conf import settings
from django.core.cache import cache
from .tokens import issue_user_tokens
from django.contrib.auth import get_user_model
from datetime import datetime
from hashlib import md5
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


User = get_user_model()

scenario_dict = {
    scenario.key: scenario 
    for scenario in settings.USER_STEP_SCENARIO
}

def create_user_id(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    timestamp = datetime.now().timestamp()
    print("user", ip, "started to logged in on", timestamp)
    user_id = md5(f"{ip}$%^&*{timestamp}".encode()).hexdigest()
    return user_id

class OptionsView(APIView):

    def get(self, request):
        return Response({
            scenario.key: scenario.schema
            for scenario in settings.USER_STEP_SCENARIO
        })

class ValidateScenarioView(APIView):
    def post(self, request, scenario_key):

        options = request.data.get("options")
        user_payload = request.data.get("payload", None)
        user_id = request.data.get("user_id", create_user_id(request))
        
        # get scenario from scenario_dict
        scenario = scenario_dict.get(scenario_key)
        if not scenario:
            return Response({"error": "Scenario not found"}, status=status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED)

        # check for scenario step is right
        user_scenario_step = cache.get(f"user_scenario_step_{user_id}", settings.USER_STEP_SCENARIO[0].key)
        if user_scenario_step != scenario_key:
            return Response({"error": "Scenario step not true"}, status=status.HTTP_400_BAD_REQUEST)

        # check for scenraio validation
        response = scenario.validate(
            user_payload=user_payload or {}, 
            scenario_options=options
        )
        if response.status_code != 200:
            return response

        # get new user id from scenario and check it's exists

        # check for user authenticated successfully all steps
        if scenario_key == settings.USER_STEP_SCENARIO[-1].key:
            user = scenario.get_user(user_id, options)
            if not user:
                return Response({"error": "User not found"}, status=status.HTTP_401_UNAUTHORIZED)

            access_token, refresh_token, access_max_age, refresh_max_age = issue_user_tokens(
                user_id=str(user.id),
                username=user.username,
            )
            print(list(user.groups.values_list("name", flat=True)))
            cache.delete(f"user_scenario_step_{user_id}")
            return Response(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "Bearer",
                    "expires_in": access_max_age,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "permits": list(user.groups.values_list("name", flat=True)),
                    },
                },
                status=status.HTTP_200_OK,
            )
        

        # find next step to scenario step and TTL
        for index, scn in enumerate(settings.USER_STEP_SCENARIO):
            if scn.key == scenario_key:
                next_scenario_key = settings.USER_STEP_SCENARIO[index + 1].key
                next_scenario_TTL = settings.USER_STEP_SCENARIO[index + 1].each_user_TTL
                break
        # if not exists means user is on first step
        else:
            next_scenario_key = settings.USER_STEP_SCENARIO[1].key
            next_scenario_TTL = settings.USER_STEP_SCENARIO[1].each_user_TTL
        
        # add to cache
        cache.set(f"user_scenario_step_{user_id}", next_scenario_key, next_scenario_TTL)
        
        # add payload to response and sign and go to next step  
        step_payload = scenario.sign(user_payload)
        return Response(
            {"payload": step_payload, "user_id": user_id},
            status=status.HTTP_202_ACCEPTED
        )


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=True)


class RefreshTokenView(APIView):
    """
    Exchange a valid refresh token for new access and refresh tokens.
    """
    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        provided_refresh = serializer.validated_data["refresh_token"]
        try:
            incoming = RefreshToken(provided_refresh)
        except TokenError:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = str(incoming.get("uid") or incoming.get("user_id") or "")
        username = incoming.get("username")
        if not user_id:
            return Response({"error": "Malformed refresh token"}, status=status.HTTP_400_BAD_REQUEST)

        access_token, refresh_token, access_max_age, _ = issue_user_tokens(
            user_id=user_id,
            username=username,
        )

        return Response(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer",
                "expires_in": access_max_age,
            },
            status=status.HTTP_200_OK,
        )

