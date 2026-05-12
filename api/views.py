from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

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

        # send_registration_confirmation_email.delay(user.id)

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



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    return Response({
        "id": request.user.id,
        "email": request.user.email,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    email = (request.data.get('email') or '').strip().lower()
    if not email:
        return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email__iexact=email).first()
    if user:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        frontend_base = getattr(settings, 'PASSWORD_RESET_FRONTEND_URL', 'http://localhost:3000').rstrip('/')
        reset_url = f"{frontend_base}/password-reset/{uid}/{token}"

        subject = 'Reset your Password'
        html_message = render_to_string(
            'questions/password-reset.html',
            {
                'first_name': getattr(user, 'first_name', ''),
                'reset_url': reset_url,
            },
        )

        message = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        message.content_subtype = 'html'
        message.send(fail_silently=False)

    return Response(
        {'message': 'If an account with that email exists, a reset link has been sent.'},
        status=status.HTTP_200_OK,
    )


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        return Response({'error': 'Invalid or expired reset link.'}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        return Response({'message': 'Reset link is valid.'}, status=status.HTTP_200_OK)

    password = request.data.get('password')
    confirm_password = request.data.get('confirm_password')

    if not password or not confirm_password:
        return Response(
            {'error': 'Both password fields are required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if password != confirm_password:
        return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(password)
    user.save(update_fields=['password'])
    return Response({'message': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)
