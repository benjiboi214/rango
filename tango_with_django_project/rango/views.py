from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def index(request):
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by no. likes in descending order.
    # Retrieve the top 5 only - or all if less than 5.
    # Place the list in our context_dict dictionary which will be passed to the template engine.
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}
    
    # Render the response and send it back!
    return render(request, 'rango/index.html', context_dict)

def about(request):
    context_dict = {}
    return render(request, 'rango/about.html', context_dict)

def benweb(request):
    context_dict = {}
    return render(request, 'benweb/index.html', context_dict)

def category(request, category_name_slug):
    #This is our first page generated from stuff pulled from the DB. 
    #See how it pulls the information and stores relevant information in the context dict.
    #Also note the use of try except for if a category doesn't exist.
    #Hint: context dict keys are used in the HTML code to place contextual info. 
    
    #Create a context dictionary which we can pass to the template rendering engine.
    context_dict = {'category_name_slug': category_name_slug}
    
    try:
        #Can we find a category name slug with the given name?
        #If we can't the .get() method raises a DoesNotExist exception.
        #So the .get() method returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        
        #Retrieve all of the associated pages.
        #Note that filter returns >= 1 model instance.
        pages = Page.objects.filter(category=category)
        
        #Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        #We also add the category object form the database to the context dictionary.
        #We'll use this in the template to verify that the category exists.
        context_dict['category'] = category
    except Category.DoesNotExist:
        #We get here if we didn't find the specified category.
        #Don't do anything - the template displays the no category message for us.
        pass
    
    #Go render the response and return it to the client.
    return render(request, 'rango/category.html', context_dict)

@login_required
def add_category(request):
    #HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        
        
        #Have we been provided with a valid form?
        if form.is_valid():
            #save the new category to the db.
            form.save(commit=True)
            
            #then call the index view to return user back to index page.
            return index(request)
        else:
            #The supplied form contained errors, print them to the terminal.
            print form.errors
    else:
        #If the request was not a POST, display the form to enter details.
        form = CategoryForm()
    
    #Bad form (or form details), no form supplied...
    #Render the form with error messages (if any)
    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
    
    try:
        #try getting the slug from the db and assigning to short variable
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        #catch the possibilty the category doesn't exist, assign none so if works later.
        cat = None
    
    #check if it is a post reqest.
    if request.method == 'POST':
        form = PageForm(request.POST)
        #check form is valid, if it is continue saving operation
        if form.is_valid():
            #if category exists, continue saving.
            if cat:
                #save the form
                page = form.save(commit=False)
                page.category = cat #set category field to the slug
                page.views = 0 #set views to zero
                page.save() #save everything.
                #Probably better to use a redirect here
                return category(request, category_name_slug)
        else:
            print form.errors
    
    else:
        form = PageForm()
    
    context_dict = {'form': form, 'category': cat, 'category_name_slug': category_name_slug}
    
    return render(request, 'rango/add_page.html', context_dict)

def register(request):
    
    #A boolean value for telling the template whether the registration was successful.
    #Set to False initially. Code changes value to True when registration succeeds.
    registered = False
    
    #If it's a HTTP POST, we're interested in processing formdata.
    if request.method == 'POST':
        #Attempt to grab information from the raw form information.
        #Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        
        #If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            #Save the user's form data to the db.
            user = user_form.save()
            
            #now we hash the password with the set_password method.
            #Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()
            
            #Now sort out the UserProfile instance.
            #Since we need to set the user attribute ourselves, we set commit=False.
            #This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user
            
            #Did the user provide a profile picture?
            #If so, we need to get it from the input form and put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            
            #Now we save the UserProfile mode instance.
            profile.save()
            
            registered = True
        
        #Invalid form or forms - mistakes or something else?
        #Print problems to the terminal.
        #They'll also be shown to the user.
        else:
            print user_form.errors, profile_form.errors
    
    #Not a HTTP POST, so we render our form using two ModelForm instances.
    #These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    
    #Render the template depending on the context.
    return render(request,
            'rango/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def user_login(request):
    
    #If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        #Gather the username and password provided by the user.
        #This information is obtained from the login form.
            #We use request.POST.get('<variable>') as opposed to request.POST['<variable>'],
            #because the request.POST.get('<variable>') returns None, if the value does not exist,
            #while the request.POST['<variable>'] will raise a key error exception.
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        #Use django's machinery to attempt to see if the username/password
        #combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)
        
        #If we have a User object, the details are correct.
        #If None (Python's way of representing the absence of a value), no user
        #with matching credentials was found.
        if user:
            #Is the account acive? It could have been disabled.
            if user.is_active:
                #If the account is valid and active, we can log the user in.
                #We'll send the user back to the homepage/
                login(request, user)
                return HttpResponseRedirect('/rango/')
            
            else:
                #An inactive account was used - no logging in!
                return HttpResponse('Your Rango account is disabled.')
        
        else:
            #Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse('Invalid login details supplied.')
    
    #The request is not a HTTP POST, so display the login form.
    #This scenario would most likely be a HTTP GET.
    else:
        #No context variables to pass to the template system, hence the
        #blank dictionary object...
        return render(request, 'rango/login.html', {})

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})

@login_required
def user_logout(request):
    #Since we know the user is logged in, we can now just log them out.
    logout(request)
    
    #Take the user back to the homepage.
    return HttpResponseRedirect('/rango/')