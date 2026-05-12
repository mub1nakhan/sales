from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from .models import User
from .serializers import UserSerializer


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username", "password", "password_confirm",
            "first_name", "last_name", "phone", "email",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError({"password_confirm": "Parollar mos kelmadi."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


_token_response = inline_serializer(
    name="TokenResponse",
    fields={
        "user": UserSerializer(),
        "access": serializers.CharField(),
        "refresh": serializers.CharField(),
    },
)


@extend_schema(tags=["Auth"])
class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Ro'yxatdan o'tish",
        description="Yangi foydalanuvchi yaratadi va access/refresh tokenlar qaytaradi.",
        request=RegisterSerializer,
        responses={201: _token_response},
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = _get_tokens(user)
        return Response(
            {"user": UserSerializer(user).data, **tokens},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Auth"])
class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Kirish (Login)",
        description="Username va parol bilan kiradi, JWT tokenlar qaytaradi.",
        request=LoginSerializer,
        responses={
            200: _token_response,
            401: OpenApiResponse(description="Username yoki parol noto'g'ri"),
            403: OpenApiResponse(description="Foydalanuvchi faol emas"),
        },
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            return Response(
                {"detail": "Username yoki parol noto'g'ri."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not user.is_active:
            return Response(
                {"detail": "Foydalanuvchi faol emas."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response({"user": UserSerializer(user).data, **_get_tokens(user)})


@extend_schema(tags=["Auth"])
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Chiqish (Logout)",
        description="Refresh tokenni qora ro'yxatga qo'shadi (bekor qiladi).",
        request=inline_serializer(
            name="LogoutRequest",
            fields={"refresh": serializers.CharField()},
        ),
        responses={200: OpenApiResponse(description="Muvaffaqiyatli chiqildi")},
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token talab qilinadi."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"detail": "Token noto'g'ri yoki muddati o'tgan."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"detail": "Muvaffaqiyatli chiqildi."})


def _get_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}
