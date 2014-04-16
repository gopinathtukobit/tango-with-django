from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from rango.models import Category , Page
from rango.forms import CategoryForm




def index(request):
	context = RequestContext(request)
	#return HttpResponse('hello world!')
	category_list=Category.objects.order_by('-likes')[:5]
	context_dict={'categories':category_list}
	for category in category_list:
		category.url=category.name.replace(' ','_')
	return render_to_response('rango/index.html', context_dict, context)


def category(request, category_name_url):
    # Request our context from the request passed to us.
    context = RequestContext(request)

    # Change underscores in the category name to spaces.
    # URLs don't handle spaces well, so we encode them as underscores.
    # We can then simply replace the underscores with spaces again to get the name.
    category_name = category_name_url.replace('_', ' ')

    # Create a context dictionary which we can pass to the template rendering engine.
    # We start by containing the name of the category passed by the user.
    context_dict = {'category_name': category_name}

    try:
        # Can we find a category with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception.
        category = Category.objects.get(name=category_name)

        # Retrieve all of the associated pages.
        # Note that filter returns >= 1 model instance.
        pages = Page.objects.filter(category=category)

        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        context_dict['category'] = category
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything - the template displays the "no category" message for us.
        pass

    # Go render the response and return it to the client.
    return render_to_response('rango/category.html', context_dict, context)






def add_category(request):
	context = RequestContext(request)
	if request.method == 'POST ':
		form = CategoryForm(request.POST)
		if form.is_valid():
			form.save(commit=True)
			return index(request)
		else:
			print form.errors

	else:
		form=CategoryForm()

	return render_to_response('rango/add_category.html',{'from':form},context )

def about(request):
	context= RequestContext(request)
	context_dict={'boldmessage' :"I am  from the context"}
	
	return render_to_response('rango/about.html', context_dict , context)




# Create your views here.
