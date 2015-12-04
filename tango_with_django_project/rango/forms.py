from django import forms
from django.contrib.auth.models import User
from rango.models import Page, Category, UserProfile
from registration.forms import RegistrationFormUniqueEmail
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text="Please enter the category name.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    #an inlind class to provide additional information on the form.
    class Meta:
        #provide an association between the ModelForm and a model.
        model = Category
        fields = ('name',)
        
    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'category_form'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = 'post'
        self.helper.form_action = '/rango/add_category/'
        
        self.helper.add_input(Submit('submit', 'Add Category'))

class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128, help_text="Please enter the title of the page.")
    url = forms.URLField(max_length=200, help_text="Please enter the URL of the page.", widget=forms.TextInput())
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    
    class Meta:
        #Provide connection between the ModelForm and the model itself.
        model = Page
        exclude = ('category',)
        
        #What fields do we want to include in our form?
        #This way we don't need every field in the model present.
        #Some fields may allow NULL values so we may not want to include them
        #Here we are hiding the foreign key.
        #we can either exclude the category field from the form,
        #or specify the fields to include and not include the category.
        #can either: exclude = ('category',)
        #or: fields = ('title', 'url', 'views')
    
    def clean(self):
        print "Running Clean"
        cleaned_data = super(PageForm, self).clean()
        url = cleaned_data.get('url')
        
        #If URLS is not empty and doesn't starts with http://, prepend http://
        if url and not url.startswith('http://'):
            url = 'http://' + url
            cleaned_data['url'] = url
        
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        
        self.helper.add_input(Submit('submit', 'Add Page'))

class UserProfileRegistrationForm(RegistrationFormUniqueEmail):
    website = forms.CharField(
        required=False)
        
    picture = forms.ImageField(
        required=False)
    
    def clean(self):
        cleaned_data = super(UserProfileRegistrationForm, self).clean()
        website = cleaned_data.get('website')

        #If URLS is not empty and doesn't starts with http://, prepend http://
        if website and not website.startswith('http://'):
            website = 'http://' + website
            cleaned_data['website'] = website

        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super(UserProfileRegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'registration_form'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = 'post'
        self.helper.form_action = '.'
        
        self.helper.add_input(Submit('submit', 'Register'))

class EditUserForm(forms.ModelForm):
    first_name = forms.CharField(
        label='First Name')
    
    last_name = forms.CharField(
        label='Last Name')
    
    email = forms.CharField(
        widget=forms.EmailInput(),
        label='Email')
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
    
    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        
class EditProfileForm(forms.ModelForm):
    website = forms.URLField(
        widget=forms.TextInput(), 
        required=False, 
        label='Website')
    
    picture = forms.ImageField(
        widget=forms.ClearableFileInput(), 
        required=False, 
        label='Profile Picture')
    
    class Meta:
        model = UserProfile
        fields = ['website', 'picture']
    
    def clean(self):
        cleaned_data = super(EditProfileForm, self).clean()
        website = cleaned_data.get('website')

        #If URLS is not empty and doesn't starts with http://, prepend http://
        if website and not website.startswith('http://'):
            website = 'http://' + website
            cleaned_data['website'] = website

        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

#class UserForm(forms.ModelForm):
#    password = forms.CharField(widget=forms.PasswordInput())
#    
#    class Meta:
#        model = User
#        fields = ('username', 'email', 'password')
#
#class UserProfileForm(forms.ModelForm):
#    class Meta:
#        model = UserProfile
#        fields = ('website', 'picture')
