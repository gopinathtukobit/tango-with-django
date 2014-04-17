from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse ,HttpResponseRedirect
from rango.models import Category , Page 
from rango.forms import CategoryForm , PageForm , UserProfileForm , UserForm 
from django.contrib.auth import  authenticate , login , logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.bing_search import run_query
from django.contrib.auth.models import User


def category(request, category_name_url):
    # Request our context from the request passed to us.
    context = RequestContext(request)

    # Change underscores in the category name to spaces.
    # URLs don't handle spaces well, so we encode them as underscores.
    # We can then simply replace the underscores with spaces again to get the name.
    category_name = category_name_url.replace('_', ' ')

    # Create a context dictionary which we can pass to the template rendering engine.
    # We start by containing the name of the category passed by the user.
    context_dict = {'category_name': category_name,
     'category_name_url': category_name_url}

    cat_list = get_category_list()
    context_dict['cat_list'] = cat_list 

    try:
        # Can we find a category with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception.
        category = Category.objects.get(name__iexact=category_name)
        context_dict['category'] = category

        # Retrieve all of the associated pages.
        # Note that filter returns >= 1 model instance.
        pages = Page.objects.filter(category=category).order_by('-views')

        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything - the template displays the "no category" message for us.
        pass
    if request.method == POST:
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)
            context_dict['result_list'] = result_list

    # Go render the response and return it to the client.
    return render_to_response('rango/category.html', context_dict, context)


def add_category(request):
    # Get the context from the request.
    context = RequestContext(request)

    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = CategoryForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render_to_response('rango/add_category.html', {'form': form}, context)    

def add_page(request,category_name_url):

    context = RequestContext(request)

    category_name = (category_name_url).replace('_',' ')

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():

            page =form.save(commit=False)


            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat 
            except Category.DoesNotExist:


                return render_to_response('rango/add_category.html', {} , context)

            page.views = 0

            page.save()

            return category(request, category_name_url)
        else:
            print form.errors
    else:
        form = PageForm()

    return render_to_response('rango/add_page.html' ,
        {'category_name_url' : category_name_url ,
        'category_name': category_name,'form' : form},
        context) 





'''


def add_category(request):
    context = RequestContext(request)
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:

            print form.errors

    else:

        form=CategoryForm()

    return render_to_response('rango/add_category.html',{'from':form},context ) '''



def register(request):
    if request.session.test_cookie_worked():
        print ">>>> TEST COOKIE WORKED!"
        request.session.delete_test_cookie()

    context = RequestContext(request)

    registered = False
    if request.method == 'POST':

        user_form = UserForm (data = request.POST)
        profile_form = UserProfileForm(data= request.POST)


        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()

            registered = True
        else:
            print user_form.errors , profile_form.errors

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render_to_response(
        'rango/register.html',{'user_form':user_form ,'profile_form':profile_form , 'registered': registered},
        context)

def user_login(request):
    context = RequestContext(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']


        user = authenticate (username= username, password = password )


        if user is not None:

            if user.is_active:

                login(request , user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponse("Your rango account is disabled. ")
        else:

            print "Invalid login details: {0},{1}".format(username,password)
            return HttpResponse("Invalid login detail supplied.")

    else:

        return render_to_response('rango/login.html' , {} , context) 

def some_view(request):
    if not request.user.is_authenticated():
        return HttpResponse("Your logged in")
    else:
        return HttpResponse("Your not logged in")
# Create your views here.
@login_required
def restricted(request):
    return HttpResponse("Since you're logged in , you can see this text !")

@login_required
def user_logout(request):
    logout(request)
    return HttpResponse('/rango/')

def index(request):
    context = RequestContext(request)
    
    

    category_list = Category.objects.all()
    context_dict = {'categories': category_list}
    cat_list = get_category_list()
    context_dict['cat_list'] = cat_list

    for category in category_list:
        category.url = category.name.replace('_',' ')

    page_list = Page.objects.order_by('-views')[:5]
    context_dict['pages'] = page_list

     #### NEW CODE ####
    # Obtain our Response object early so we can add cookie information.
    response = render_to_response('rango/index.html', context_dict, context)

    # Get the number of visits to the site.
    # We use the COOKIES.get() function to obtain the visits cookie.
    # If the cookie exists, the value returned is casted to an integer.
    # If the cookie doesn't exist, we default to zero and cast that.
    visits = int(request.COOKIES.get('visits', '0'))

    # Does the cookie last_visit exist?
    if request.COOKIES.has_key('last_visit'):
        # Yes it does! Get the cookie's value.
        last_visit = request.COOKIES['last_visit']
        # Cast the value to a Python date/time object.
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        # If it's been more than a day since the last visit...
        if (datetime.now() - last_visit_time).days > 0:
            # ...reassign the value of the cookie to +1 of what it was before...
            response.set_cookie('visits', visits+1)
            # ...and update the last visit cookie, too.
            response.set_cookie('last_visit', datetime.now())
    else:
        # Cookie last_visit doesn't exist, so create it to the current date/time.
        response.set_cookie('last_visit', datetime.now())

    # Return response back to the user, updating any cookies that need changed.

    #### END NEW CODE ####

    #### NEW CODE ####
    if request.session.get('last_visit'):
        # The session has a value for the last visit
        last_visit_time = request.session.get('last_visit')
        visits = request.session.get('visits', 0)

        if (datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).days > 0:
            request.session['visits'] = visits + 1
            request.session['last_visit'] = str(datetime.now())
    else:
        # The get returns None, and the session does not have a value for the last visit.
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = 1
    #### END NEW CODE ####

    # Render and return the rendered response back to the user.
    return response

def about(request):
    context = RequestContext(request)
    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0
    return render_to_response('rango/about.html' , {'visits':count} , context)



def search (request):
    context =  RequestContext(request)
    result_list = []
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list =  run_query(query)
    return render_to_response('rango/search.html',{'result_list': result_list} , context)

def get_category_list():
    cat_list =  Category.objects.all()
    for cat in cat_list:
        cat.url= cat.name.replace(' ','_')
    return cat_list
@login_required
def profile(request):
    context = RequestContext(request)
    cat_list = get_category_list()
    context_dict = {'cat_list':cat_list}
    u = User.objects.get(user=u)

    try:
        up = UserProfile.objects.get(user=u)
    except:
        up = None

    context_dict['user'] = u 
    context_dict['userprofile'] = up
    return render_to_response('rango/profile.html',context_dict, context)





'''
def about(request):
    context= RequestContext(request)
    if request.session.get('visits'):
    count = request.session.get('visits')


    count = 0
  
    
    return render_to_response('rango/about.html', {} , context) '''
