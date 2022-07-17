from django import forms
from .models import Post, Comment
from django.contrib.auth.models import User
from django.core import validators


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'text','image','categories','tag')


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class RegisterForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'لطفا نام کاربری خود را وارد نمایید'}), 
        label='نام کاربری',
        validators=[ 
            validators.MaxLengthValidator(limit_value=20,
                                          message='تعداد کاراکترهای وارد شده نمیتواند بیشتر از 20 باشد'),
            validators.MinLengthValidator(3,'تعداد کاراکترهای وارد شده نمیتواند کمتر از 3 باشد')])

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={'placeholder': 'لطفا ایمیل خود را وارد نمایید'}),
        label='ایمیل')

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'placeholder': 'لطفا کلمه عبور خود را وارد نمایید'}),
        label='کلمه ی عبور')
        
    re_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'placeholder': 'لطفا تکرار کلمه عبور خود را وارد نمایید'}),
        label='تکرار کلمه ی عبور'
    )

    def clean_name(self):
        name = self.cleaned_data.get('name')
        is_exists_user_by_username = User.objects.filter(
            username=name).exists()

        if is_exists_user_by_username:
            raise forms.ValidationError('این نام قبلا گرفته شده است')

        return name

    def clean_re_password(self):
        password = self.cleaned_data.get('password')
        re_password = self.cleaned_data.get('re_password')

        if password != re_password:
            raise forms.ValidationError('کلمه های عبور با یکدیگر مغایرت دارند')

        return password
