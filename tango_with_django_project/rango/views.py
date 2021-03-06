from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, EditUserForm, EditProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    
    context_dict = {'categories': category_list, 'pages': page_list}
    
    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False
    
    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
        
        if (datetime.now() - last_visit_time).seconds > 0:
            #...reassign the value of the cookie to +1 of what it was before...
            visits += 1
            #... and update the last visit cookie too.
            reset_last_visit_time = True
    else:
        #Cookie last_visit doesn't exist, so create it to the current date/time.
        reset_last_visit_time = True
    
    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits
    
    response = render(request, 'rango/index.html', context_dict)
    return response

def about(request):
    #Note that this logic increments visits on the index page, and presents here.
    visits = request.session.get('visits')
    context_dict = {'visits': visits}
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
        pages = Page.objects.filter(category=category).order_by('-views')
        
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

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})

@login_required
def profile_view(request):
    user = request.user
    profile = UserProfile.objects.get(user=request.user)
    user_initial = {
        'first_name':user.first_name, 
        'last_name':user.last_name, 
        'email':user.email}
    profile_initial = {
        'website':profile.website, 
        'picture':profile.picture}
    
    if request.method == 'POST':
        userform = EditUserForm(data=request.POST, initial=user_initial)
        profileform = EditProfileForm(request.POST, request.FILES, initial=profile_initial)
        if userform.is_valid() and profileform.is_valid():
            user.first_name = userform.cleaned_data['first_name']
            user.last_name = userform.cleaned_data['last_name']
            user.email = userform.cleaned_data['email']
            user.save()
            
            profile.website = profileform.cleaned_data['website']
            if 'picture' in request.FILES:
                profile.picture = profileform.cleaned_data['picture']
            profile.save()
            
            return HttpResponseRedirect('/rango/profile')
    
    else:
        userform = EditUserForm(initial=user_initial)
        profileform = EditProfileForm(initial=profile_initial)

    context = {
        "userform": userform,
        "profileform": profileform}
    
    return render(request, 'registration/profile.html', context)

def track_url(request):
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views += 1
                page.save()
                url = page.url
            except:
                pass
    
    return redirect(url)

@login_required
def like_category(request):
    category_id = None
    likes = 0
    if request.method == 'GET':
        if 'category_id' in request.GET:
            category_id = request.GET['category_id']
            try:
                category = Category.objects.get(id=int(category_id))
                likes = category.likes + 1
                category.likes = likes
                category.save()
            except:
                pass
    return HttpResponse(likes)

def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)
    
    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]
    
    return cat_list

def suggest_category(request):
    cat_list = []
    starts_with = ''
    if request.method == 'GET':
        starts_with = request.GET['suggestion']
    
    cat_list = get_category_list(8, starts_with)
    
    return render(request, 'rango/category_list.html', {'cat_list': cat_list})



#################################################
#Registration Graveyard below. Replaced by Redux#
#################################################

#def user_login(request):
#    
#    #If the request is a HTTP POST, try to pull out the relevant information.
#    if request.method == 'POST':
#        #Gather the username and password provided by the user.
#        #This information is obtained from the login form.
#            #We use request.POST.get('<variable>') as opposed to request.POST['<variable>'],
#            #because the request.POST.get('<variable>') returns None, if the value does not exist,
#            #while the request.POST['<variable>'] will raise a key error exception.
#        username = request.POST.get('username')
#        password = request.POST.get('password')
#        
#        #Use django's machinery to attempt to see if the username/password
#        #combination is valid - a User object is returned if it is.
#        user = authenticate(username=username, password=password)
#        
#        #If we have a User object, the details are correct.
#        #If None (Python's way of representing the absence of a value), no user
#        #with matching credentials was found.
#        if user:
#            #Is the account acive? It could have been disabled.
#            if user.is_active:
#                #If the account is valid and active, we can log the user in.
#                #We'll send the user back to the homepage/
#                login(request, user)
#                return HttpResponseRedirect('/rango/')
#            
#            else:
#                #An inactive account was used - no logging in!
#                return HttpResponse('Your Rango account is disabled.')
#        
#        else:
#            #Bad login details were provided. So we can't log the user in.
#            print "Invalid login details: {0}, {1}".format(username, password)
#            return HttpResponse('Invalid login details supplied.')
#    
#    #The request is not a HTTP POST, so display the login form.
#    #This scenario would most likely be a HTTP GET.
#    else:
#        #No context variables to pass to the template system, hence the
#        #blank dictionary object...
#        return render(request, 'rango/login.html', {})

#def register(request):
#    #A boolean value for telling the template whether the registration was successful.
#    #Set to False initially. Code changes value to True when registration succeeds.
#    registered = False
#    
#    #If it's a HTTP POST, we're interested in processing formdata.
#    if request.method == 'POST':
#        #Attempt to grab information from the raw form information.
#        #Note that we make use of both UserForm and UserProfileForm.
#        user_form = UserForm(data=request.POST)
#        profile_form = UserProfileForm(data=request.POST)
#        
#        #If the two forms are valid...
#        if user_form.is_valid() and profile_form.is_valid():
#            #Save the user's form data to the db.
#            user = user_form.save()
#            
#            #now we hash the password with the set_password method.
#            #Once hashed, we can update the user object.
#            user.set_password(user.password)
#            user.save()
#            
#            #Now sort out the UserProfile instance.
#            #Since we need to set the user attribute ourselves, we set commit=False.
#            #This delays saving the model until we're ready to avoid integrity problems.
#            profile = profile_form.save(commit=False)
#            profile.user = user
#            
#            #Did the user provide a profile picture?
#            #If so, we need to get it from the input form and put it in the UserProfile model.
#            if 'picture' in request.FILES:
#                profile.picture = request.FILES['picture']
#            
#            #Now we save the UserProfile mode instance.
#            profile.save()
#            
#            registered = True
#        
#        #Invalid form or forms - mistakes or something else?
#       #Print problems to the terminal.
#        #They'll also be shown to the user.
#        else:
#            print user_form.errors, profile_form.errors
#    
#    #Not a HTTP POST, so we render our form using two ModelForm instances.
#    #These forms will be blank, ready for user input.
#    else:
#        user_form = UserForm()
#        profile_form = UserProfileForm()
#    
#    #Render the template depending on the context.
#    return render(request,
#            'rango/register.html',
#            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

#@login_required
#def user_logout(request):
#    #Since we know the user is logged in, we can now just log them out.
#    logout(request)
#    
#    #Take the user back to the homepage.
#    return HttpResponseRedirect('/rango/')


#COOKIE INDEX EXAMPLES BELOW#
# def index(request): #Hashed out is client side cookie example see below for session example.
#    # Query the database for a list of ALL categories currently stored.
    # Order the categories by no. likes in descending order.
    # Retrieve the top 5 only - or all if less than 5.
    # Place the list in our context_dict dictionary which will be passed to the template engine.
#    category_list = Category.objects.all()
#    page_list = Page.objects.order_by('-views')[:5]
#    context_dict = {'categories': category_list, 'pages': page_list}
#    
#    #Get the number of visits to the site.
    #We use the COOKIES.get() function to obtain the visits cookie.
    #If the cookie exists, the value returned is casted to an integer.
    #If the cookie doesn't exist, we default to zero and cast that.
#    visits = int(request.COOKIES.get('visits', '1'))
#    
#    #Set the reset last visit to time a False default
#    reset_last_visit_time = False
#    response = render(request, 'rango/index.html', context_dict)
#    #Does the cookie last_visit exist?
#    if 'last_visit' in request.COOKIES:
#        # Yes it does! Get the cookie's value.
#        last_visit = request.COOKIES['last_visit']
#        #Cast the value to a Python date/time value.
#        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
#        
#        #If it's been more than a day since the last visit...
#        if (datetime.now() - last_visit_time).days > 0:
#            visits += 1
#            #And flag that the cookie last visit needs to be updated.
#            reset_last_visit_time = True
#    else:
#        #Cookie last_visit doesn't exist, so flag that it should be set.
#        reset_last_visit_time = True
#        
#        context_dict['visits'] = visits
#        
#        #Obtain our response object early so we can add cookie information.
#        response = render(request, 'rango/index.html', context_dict)
#    
#    if reset_last_visit_time:
#        response.set_cookie('last_visit', datetime.now())
#        response.set_cookie('visits', visits)
#    
#    #Return response back to the user, updating any cookies that eed to be changed.
#    return response

#OLD SEARCH VIEW#
#def search(request):
#    result_list = []
#    
#    if request.method == 'POST':
#        query = request.POST['query'].strip()
#        
#        if query:
#            #Run our Bing functions
#            result_list = run_query(query)
#    
#    return render(request, 'rango/search.html', {'result_list': result_list})