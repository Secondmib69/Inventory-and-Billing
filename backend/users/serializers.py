from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model, password_validation



User = get_user_model()


class CustomRegisterSerializer(RegisterSerializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    
    # def get_cleaned_data(self):
    #     data = super().get_cleaned_data()
    #     data['first_name'] = self.validated_data.get('fist_name', '')
    #     data['last_name'] = self.validated_data.get('last_name', '')
    #     return data
    
    # def save(self, request):
    #     user = super().save(request)
    #     user.first_name = self.validated_data.get('first_name', '')
    #     user.last_name = self.validated_data.get('last_name', '')
    #     user.save()
    #     return user

    def custom_signup(self, request, user): # instead of overriding those two methods above we can use this method
        user.first_name = self.validated_data.get('first_name', '')
        user.last_name = self.validated_data.get('last_name', '')
        user.save()


class UserCreateSerializer(serializers.ModelSerializer):

    password1 = serializers.CharField(
        required=True,
        write_only=True,
        validators=[password_validation.validate_password],
        label='Password',
        help_text='Must pass Django password validators.',
    )
    password2 = serializers.CharField(
        required=True,
        write_only=True,
        label='Confirm Password',
        help_text='Must match `password1`.',
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'is_active', 'is_staff']
        extra_kwargs = {
            'username': {'help_text': 'Unique login name.'},
            'email': {'help_text': 'Unique email address.'},
            'is_active': {'help_text': 'Whether the account can log in.'},
            'is_staff': {
                'help_text': 'Staff flag. Writable only by superusers on create.',
            },
        }

    def validate(self, attrs):
        pass1 = attrs['password1']
        pass2 = attrs['password2']
        if pass1 != pass2:
            raise serializers.ValidationError('The two password fields didn\'t match.')
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password1')
        user = User.objects.create_user(**validated_data, password=password)
        return user
    
    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        if not request.user.is_superuser:
            for label, field in fields.items():
                if label == 'is_staff':
                    field.read_only = True

        return fields

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff']
        extra_kwargs = {
            'username': {'help_text': 'Unique login name.'},
            'email': {'help_text': 'Email address.'},
            'is_active': {'help_text': 'Whether the account can log in.'},
            'is_staff': {'help_text': 'Whether the user has staff privileges.'},
        }

    
    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        user = request.user
        read_only = []
        remove = []
        if request is not None:
            if user == self.instance:
                if user.is_superuser:
                    pass
                elif user.is_staff:
                    read_only.append('is_staff')
                else:
                    remove.extend(['is_active', 'is_staff'])
            elif user.is_superuser:
                read_only.extend(['username', 'first_name', 'last_name', 'email'])
            elif user.is_staff:
                read_only.extend(['username', 'first_name', 'last_name', 'email', 'is_staff'])
            else:
                remove.extend(['is_active', 'is_staff', 'email'])

        for field in read_only:
            fields[field].read_only = True
        for field in remove:
            fields.pop(field)
        return fields



                


