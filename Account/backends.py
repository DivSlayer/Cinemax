from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class CaseInsensitiveModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            case_insensitive_username_field = "{}__iexact".format(
                UserModel.USERNAME_FIELD
            )
            print(username)
            user = UserModel._default_manager.get(
                **{case_insensitive_username_field: username}
            )
        except UserModel.DoesNotExist:
            print("User not found")
            UserModel().set_password(password)
        else:
            print("User is authenticated")
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
