from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm

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