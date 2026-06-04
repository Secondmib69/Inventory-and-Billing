from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model



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

