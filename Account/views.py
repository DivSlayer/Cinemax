from django.shortcuts import render
from Account.forms import RegistrationForm
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from Account.models import Account, Plan
from Account.serializers import AccountSerializer, PlanSerializer
from django.contrib.auth import get_user_model


User = get_user_model()
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class CustomTokenRefreshView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Validate existing refresh token
            old_refresh = RefreshToken(refresh_token)
            user_id = old_refresh.payload.get('user_id')
            user = User.objects.get(id=user_id)
            
            # Create new tokens
            new_refresh = RefreshToken.for_user(user)
            new_access = new_refresh.access_token

            return Response({
                'access': str(new_access),
                'refresh': str(new_refresh),
            }, status=status.HTTP_200_OK)

        except Exception as e:
            
            print(e)
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )


class DetailsApi(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        serialized = AccountSerializer(user)
        return Response(serialized.data)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class RegisterUser(APIView):
    def post(self, request):
        form = RegistrationForm(request.data)
        if form.is_valid():
            form.save()
            email = form.cleaned_data["email"].lower()
            user = Account.objects.get(email=email)
            auth_tokens = get_tokens_for_user(user)
            return Response(auth_tokens)
        else:
            return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)


class PlansList(APIView):
    def get(self, request):
        uuid = request.GET.get("uuid", None)
        if uuid is None:
            plans = Plan.objects.all()
            serialized = PlanSerializer(plans, many=True)
            return Response(serialized.data)
        else:
            try:
                plan = Plan.objects.get(uuid=uuid)
                serialized = PlanSerializer(plan)
                return Response(serialized.data)
            except Plan.DoesNotExist as e:
                return Response(status=status.HTTP_400_BAD_REQUEST)


class PurchasePlan(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, uuid):
        try:
            plan = Plan.objects.get(uuid=uuid)
            user = request.user
            user.plan = plan
            user.save()
            return Response(AccountSerializer(user).data)
        except Plan.DoesNotExist as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
