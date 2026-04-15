from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from custom_user.tokens import email_confirm_token
from questions.tasks import send_registration_confirmation_email
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        send_registration_confirmation_email.delay(user.id)

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'Registration successful! Please check your email to confirm your address.',
            },
            status=status.HTTP_201_CREATED,
        )

class LoginView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Login successful!'
        })

@api_view(['GET'])
@permission_classes([AllowAny])
def confirm_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and email_confirm_token.check_token(user, token):
        if not user.email_verified:
            user.email_verified = True
            user.save(update_fields=['email_verified'])
        return Response({'message': 'Your email has been confirmed.'})

    return Response(
        {'error': 'Invalid or expired confirmation link.'},
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    try:
        refresh_token = request.data.get("refresh")
        print(f"Logout attempt with refresh token: {refresh_token[:20] if refresh_token else 'None'}...")
        
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            print("Token blacklisted successfully")
        
        return Response({"message": "Logout successful!"}, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Logout error: {str(e)}")
        # Even if blacklisting fails, we still want to logout
        return Response({"message": "Logout successful!"}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    try:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"Attempting to refresh token: {refresh_token[:20]}...")
        token = RefreshToken(refresh_token)
        print("Token refresh successful")
        
        return Response({
            'access': str(token.access_token),
            'refresh': str(token)
        })
    except Exception as e:
        print(f"Token refresh failed: {str(e)}")
        return Response({"error": f"Invalid refresh token: {str(e)}"}, status=status.HTTP_401_UNAUTHORIZED)
