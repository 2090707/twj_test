from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

def index(request):
	category_list = Category.objects.order_by('-likes')[:5]
	context_dict = {'boldmessage': "I am bold font from the context",
					'categories': category_list}

	context_dict['pages_by_views'] = Page.objects.order_by('views')[0:5]
	return render(request, 'rango/index.html', context_dict)

def about(request):
	context_dict = {'aboutinfo': "Rango is a lizard Django"}
	return render(request, 'rango/about.html', context_dict)
	
@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})

def category(request, category_name_slug):
    context_dict = {}
	
    try:
        category = Category.objects.get(slug = category_name_slug)
        context_dict['category_name'] = category.name
		
        pages = Page.objects.filter(category = category)
        context_dict['pages'] = pages
        context_dict['category'] = category
        context_dict['category_name_slug'] = category_name_slug
    except Category.DoesNotExist:
		pass
		
    return render(request, 'rango/category.html', context_dict)

@login_required
def add_category(request):
    # HTTP post?
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        
        # Form valid?
        if form.is_valid():
            # Save new category to DB
            form.save(commit = True)
            
            # User will be shown the home page
            return index(request)
        else:
            print form.errors
    else:
        # request was NOT a post
        form = CategoryForm()
        
    return render(request, 'rango/add_category.html', {'form': form})
    
    
@login_required    
def add_page(request, category_name_slug):
    try:
        cat = Category.objects.get(slug = category_name_slug)
    except Category.DoesNotExist:
        cat = None
        
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit = False)
                page.category = cat
                page.views = 0
                page.save()
            # a redirect here
            return index(request)
        else:
            print form.errors
    else:
        form = PageForm()
        
    return render(request, 'rango/add_page.html', {'form': form, 'category': cat, 'category_name_slug': category_name_slug})
    
@csrf_protect
def register(request):
    # Tell the template if the registration is susccessful
    registered = False
    
    # If POST => we process data
    if request.method == 'POST':
        # Try to grab info from the raw form info
        user_form = UserForm(data = request.POST)
        profile_form = UserProfileForm(data = request.POST)
        
        # If both forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            # Save user form data to DB
            user = user_form.save()
            
            # Hash password with set_password method => update user object
            user.set_password(user.password)
            user.save()
            
            # Sort out the UserProfile instance
            profile = profile_form.save(commit = False)
            profile.user = user
            
            # If user provided a profile pic, deal with it
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            
            profile.save()
            registered = True
            
        # invalid form/s
        else:
            print user_form.errors, profile_form.errors
            
    # not a POST => render with blank ModelForm instances
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
        
    # render template according to context
    return render(request,
            'rango/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def user_login(request):
    # If request is POST => pull out relevant info
    if request.method == 'POST':
        # get username & pass via the form
        username = request.POST['username']
        password = request.POST['password']
        
        # see if name/pass are valid => get user object
        user = authenticate(username=username, password=password)
        
        # if the user was found
        if user:
            # check if account is active
            if user.is_active:
                login(request, user)
                # Redirect doesnt work ?!?
                if request.POST["next"] is not None:
                    return HttpResponseRedirect(request.POST["next"])
                else:
                    return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
            else:
                return HttpResponse("Your Rango account is disabled.")
                
        else:
            # bad login details
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")
            
    # request is NOT an HTTP POST => display login form
    # would most likely be an HTTP GET
    else:
        # no context...
        return render(request,'rango/login.html', {})

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/rango/')





