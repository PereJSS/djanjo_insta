from django import forms

from django.contrib.auth.models import User

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'username', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            from profiles.models import UserProfile
            UserProfile.objects.create(user=user)

        return user
    


class LoginForm(forms.Form):

    username = forms.CharField(label='Email')
    password = forms.CharField(label='password', widget=forms.PasswordInput())
    

class FollowForm(forms.Form):
    profile_pk = forms.IntegerField(widget=forms.HiddenInput())
    action = forms.ChoiceField(
        choices=[('follow', 'Seguir'), ('unfollow', 'Dejar de seguir')],
        widget=forms.HiddenInput(),
        required=False,
    )