from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

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
