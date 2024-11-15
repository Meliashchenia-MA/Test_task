from django import forms
from .models import User, UploadModel

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 5, 'cols': 54}),
        }



class UploadForm(forms.ModelForm):
    class Meta:
        model = UploadModel
        fields = ['original_image']