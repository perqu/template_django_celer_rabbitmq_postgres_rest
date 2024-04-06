from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer, AuthSerializer
from utils.permissions import HasGroupPermission
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from utils.paginators import SmallResultsSetPagination
from knox.views import LoginView as KnoxLoginView
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.contrib.auth import login
from utils.throttle import LoginThrottle

from utils.scheme import KnoxTokenScheme
class LoginAPIView(KnoxLoginView):
    """
    A view to handle user authentication and token generation.
    """
    throttle_classes = [LoginThrottle]
    serializer_class = AuthSerializer
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        """
        Authenticate user and generate a token.

        Required parameters in the request:
        - username: The username of the user (string).
        - password: The password of the user (string).
        """
        serializer = AuthTokenSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginAPIView, self).post(request, format=None)

class UserListView(APIView):
    """
    A view to list all users or create a new user.
    """
    serializer_class = UserSerializer
    permission_classes = [HasGroupPermission]
    required_groups = ['IT']
    pagination_class = SmallResultsSetPagination

    @extend_schema(
        parameters=[
            OpenApiParameter(name="page_size", type=OpenApiTypes.INT, description='Page Size for pagination.', required=False),
            OpenApiParameter(name="page", type=OpenApiTypes.INT, description='Page number for pagination.', required=False),
        ],
    )
    def get(self, request):
        """
        Get a list of paginated users.

        Example:
        http://localhost:8000/users?page=2&page_size=20
        """
        users = User.objects.all().order_by('username')

        paginator = self.pagination_class()
        paginated_users = paginator.paginate_queryset(users, request)

        serializer = self.serializer_class(paginated_users, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a new user.

        Required parameters in the request:
        - username: The username of the user (string).
        - email: The email of the user (string).
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):
    """
    A view to retrieve, update or delete an user instance.
    """
    serializer_class = UserSerializer
    permission_classes = [HasGroupPermission]
    required_groups = ['IT']

    def get_object(self, uuid):
        """
        Retrieve an user object by its UUID.

        parameters:
         - uuid: The UUID of the user to retrieve (string).

        return: User object if found, None otherwise.
        """
        try:
            return User.objects.get(uuid=uuid)
        except User.DoesNotExist:
            return None

    def get(self, request, uuid):
        """
        Retrieve details of an user by UUID.

        Required parameter in the URL:
        - uuid: The UUID of the user to retrieve (string).
        """
        user = self.get_object(uuid)
        if user:
            serializer = self.serializer_class(user)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, uuid):
        """
        Update an user instance partially.

        Possible parameters in the request:
        - username: The username of the user (string).
        - email: The email of the user (string).
        """
        user = self.get_object(uuid)
        if user:
            serializer = self.serializer_class(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, uuid):
        """
        Delete an user by UUID.

        Required parameter in the URL:
        - uuid: The UUID of the user to delete (string).
        """
        user = self.get_object(uuid)
        if user:
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)
