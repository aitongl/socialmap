from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from socialmap.models import Profile

class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length=200, widget=forms.PasswordInput())
    def clean(self):
        # Calls our parent (forms.Form) .clean function
        # Gets a dictionary of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid username/password")

        # We must return the cleaned data we got from our parent.
        return cleaned_data

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length=200,
                                 label='Password', 
                                 widget=forms.PasswordInput())
    confirm_password = forms.CharField(max_length=200,
                                 label='Confirm password',  
                                 widget=forms.PasswordInput())
    email      = forms.CharField(max_length=50,
                                 widget = forms.EmailInput())
    first_name = forms.CharField(max_length=20)
    last_name  = forms.CharField(max_length=20)
    def clean(self):
        # Calls our parent (forms.Form) .clean function
        # Gets a dictionary of cleaned data as a result
        cleaned_data = super().clean()

        # Add an extra validation
        # Confirms that the two password fields match
        password1 = cleaned_data.get('password')
        password2 = cleaned_data.get('confirm_password')
        if password1 and password2 and password1 != password2:
            # Generates a form error (non-field error)
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data
    def clean_username(self):
        # Confirms that the username is not already present in the User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            # Generates a field error specific to the field (username here)
            raise forms.ValidationError("Username is already taken.")

        # We must return the cleaned data we got from the cleaned_data dictionary
        return username
    

MAX_UPLOAD_SIZE = 2500000

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ( 'grade', 'school', 'major', 'labels', 'picture')
        exclude = (
            'following',
        )
        # manipulate forms for multiline
        widgets = {
            'grade': forms.Select(attrs={'id':'id_grade_select'}, choices=[
                ('2025', 'Class of 2025'),
                ('2026', 'Class of 2026'),
                ('2027', 'Class of 2027'),
                ('2028', 'Class of 2028'),
                ('2029', 'Class of 2029'),
            ]),
            'school': forms.Select(attrs={'id':'id_grade_select'}, choices=[
                ('SCS', 'SCS'),
                ('CIT', 'CIT'),
                ('DIT', 'DIT'),
                ('MCS', 'MCS'),
                ('CFA', 'CFA'),
                ('TEP', 'TEP'),
            ]),
            'major': forms.Textarea(attrs={'id':'id_major_text', 'rows':1}),
            'labels': forms.Select(attrs={'id':'id_labels_select'}, choices=[
                ('Eating', 'Eating'),
                ('Studying together', 'Studying together'),
                ('Playing sports', 'Playing sports'),
                ('Cooking', 'Cooking'),
            ]),
            'picture': forms.FileInput(attrs={'id':'id_profile_picture'})
        }
        labels = {
            'grade' : "Grade",
            'school': "School",
            'major' : "Major",
            'labels': "Interests",
            'picture' : "Upload image"
        }

    def clean_picture(self):
        picture = self.cleaned_data['picture']
        if not picture or not hasattr(picture, 'content_type'):
            raise forms.ValidationError('You must upload a picture')
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if picture.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError(f'File too big (max size is {MAX_UPLOAD_SIZE} bytes)')
        return picture