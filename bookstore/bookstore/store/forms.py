from django import forms
from .models import UserProfile
from .models import Comment, Rating

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = UserProfile
        fields = ["username", "email", "phone", "address", "password"]
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['value']
        widgets = {
            'value': forms.RadioSelect(choices=[(i, f"{i} ★") for i in range(1, 6)])
        }

class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=100)
    address = forms.CharField(widget=forms.Textarea)
    phone = forms.CharField(max_length=15)
    email = forms.EmailField()