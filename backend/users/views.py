from .serializers import UserCreateSerializer, UserSerializer, User
from rest_framework import generics
from dj_rest_auth.jwt_auth import JWTCookieAuthentication
from .permissions import StaffOrAuthenticatedReadOnly
from drf_spectacular.utils import extend_schema, extend_schema_view
from config.openapi import TAG_USERS, path_id_param


@extend_schema_view(
    get=extend_schema(
        tags=[TAG_USERS],
        summary='List users',
        description=(
            'Returns all users. Staff can list all accounts; '
            'non-staff authenticated users may only use GET on this endpoint.'
        ),
        responses={200: UserSerializer(many=True)},
    ),
    post=extend_schema(
        tags=[TAG_USERS],
        summary='Create user',
        description=(
            'Create a new user account. Staff only on this endpoint. '
            'Non-superusers cannot set `is_staff` on create.'
        ),
        request=UserCreateSerializer,
        responses={201: UserCreateSerializer},
    ),
)
class UserListAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    permission_classes = [StaffOrAuthenticatedReadOnly]
    authentication_classes = [JWTCookieAuthentication]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer


@extend_schema_view(
    get=extend_schema(
        tags=[TAG_USERS],
        summary='Retrieve user',
        description=(
            'Fetch a user by ID. Field visibility depends on the caller: '
            'users see a reduced set on their own profile; staff and superusers see more.'
        ),
        parameters=[path_id_param('user')],
        responses={200: UserSerializer},
    ),
    put=extend_schema(
        tags=[TAG_USERS],
        summary='Update user',
        description=(
            'Full update. Writable fields depend on role: regular users may only edit '
            'their own profile; staff cannot modify other staff/superusers.'
        ),
        parameters=[path_id_param('user')],
        request=UserSerializer,
        responses={200: UserSerializer},
    ),
    patch=extend_schema(
        tags=[TAG_USERS],
        summary='Partially update user',
        description='Partial update with the same permission rules as PUT.',
        parameters=[path_id_param('user')],
        request=UserSerializer,
        responses={200: UserSerializer},
    ),
    delete=extend_schema(
        tags=[TAG_USERS],
        summary='Delete user',
        description='Delete a user account. Subject to staff/superuser object-level rules.',
        parameters=[path_id_param('user')],
        responses={204: None},
    ),
)
class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [StaffOrAuthenticatedReadOnly]
    authentication_classes = [JWTCookieAuthentication]
    serializer_class = UserSerializer
    lookup_url_kwarg = 'id'
