from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from django.views.generic import TemplateView
from django.views import generic
from .models import *
from datetime import datetime
from django.utils import timezone
import pytz # For converting datetime objects from one timezone to another timezone
from django.db.models import Q
# Create your views here.

def get_cur_client(request):
    cur_client = request.META['REMOTE_USER']
    return cur_client

'''
def index(request):
    cur_client = get_cur_client(request)
    return HttpResponse("""
    <!DOCTPYE html>
    <html>

    <head>
        <title>Home Page - Performance Indicator Portal</title>
    </head>

    <body>
        <div>
            <ul>
                <li><a href="/PerInd/about">About</a></li>
                <li><a href="/PerInd/contact">Contact</a></li>
                <li><a href="/PerInd/webgrid">WebGrid - Will remove from this list in prod</a></li>
            </ul>
            <p class="nav navbar-text navbar-right">Hello, {}!</p>
        </div>
    </body>

    </html>
    """.format(cur_client))

def about(request):
    return HttpResponse("This will be the ABOUT page")

def contact(request):
    return HttpResponse("This will be the CONTACT page")

def webgrid(request):
    latest_user_list = Users.objects.order_by('-user_id')[:5]

    context = {
        'latest_user_list': latest_user_list
    }

    return render(request, 'PerInd.template.webgrid.html', context)
'''

def get_user_category_permissions(username):
    try:
        user_permissions_list = UserPermissions.objects.filter(user__login=username)
        return {
            "success": True,
            "pk_list": [x.category.category_id for x in user_permissions_list],
            "err": '',
            "category_names": [x.category.category_name for x in user_permissions_list],
        }
    except Exception as e:
        print("Exception: get_user_category_permissions(): {}".format(e))
        return {
            "success": False,
            "err": "Exception: get_user_category_permissions(): {}".format(e),
            "pk_list": [],
            "category_names": [],
        }

# Given a record id, checks if user has permission to edit the record
def user_has_permission_to_edit(username, record_id):
    try:
        category_info = get_user_category_permissions(username)
        category_id_permission_list = category_info["pk_list"]
        record_category_info = IndicatorData.objects.values('indicator__category__category_id', 'indicator__category__category_name').get(record_id=record_id) # Take a look at https://docs.djangoproject.com/en/3.0/ref/models/querysets/ on "values()" section
        record_category_id = record_category_info["indicator__category__category_id"]
        record_category_name = record_category_info["indicator__category__category_name"]
        if len(category_id_permission_list) != 0:
            if record_category_id in category_id_permission_list:
                return {
                    "success": True,
                    "err": "",
                }
            else:
                print( "Permission denied: '{}' does not have permission to edit {} Category.".format(username, record_category_name) )
                return {
                    "success": False,
                    "err": "Permission denied: '{}' does not have permission to edit {} Category.".format(username, record_category_name),
                }
        elif category_info["success"] == False:
            raise # re-raise the error that happend in get_user_category_permissions(), because ["success"] is only False when an exception happens in get_user_category_permissions()
        else: # Else successful query, but no permissions results found
            return {
                "success": False,
                "err": "Permission denied: '{}' does not have permission to edit {} Category.".format(username, record_category_name),
            }

        return {
            "success": False,
            "err": "Permission denied: '{}' does not have permission to edit {} Category.".format(username, record_category_name),
        }
    except Exception as e:
        print("Exception: user_has_permission_to_edit(): {}".format(e))
        return {
            "success": False,
            "err": 'Exception: user_has_permission_to_edit(): {}'.format(e),
        }

class HomePageView(TemplateView):
    template_name = 'template.home.html'

class AboutPageView(TemplateView):
    template_name = 'template.about.html'
    
class ContactPageView(TemplateView):
    template_name = 'template.contact.html'

# Method Flowchart (the order of execution) for generic.ListView
#     setup()
#     dispatch()
#     http_method_not_allowed()
#     get_template_names()
#     get_queryset()
#     get_context_object_name()
#     get_context_data()
#     get()
#     render_to_response()
class WebGridPageView(generic.ListView):
    template_name = 'PerInd.template.webgrid.html'
    context_object_name = 'indicator_data_entries'

    paginate_by = 12

    req_success = False
    category_permissions = []
    err_msg = ""
    req_sort_dir =  "asc"
    req_sort_by = "indicator__indicator_title"
    
    titles=""
    years=""
    months=""
    
    title_list = []
    yr_list = []
    mn_list = []
    filterStatus = False

    urlParam = ""
    
    def get_queryset(self):
        
        title_list = self.request.GET.get('title_list')
        yr_list = self.request.GET.getlist('yr_list')
        mn_list = self.request.GET.getlist('yr_list')

        tempTitle = self.request.GET.getlist('title_list')
        tempYear = self.request.GET.getlist('yr_list')
        tempMonth = self.request.GET.getlist('mn_list')
        tempSortBy = self.request.GET.getlist('SortBy')
        tempSortDir = self.request.GET.getlist('SortDir')
        tempPage = self.request.GET.getlist('page')
        temp=""
        filt = "&title_list="
        temp2=""
        filt2 = "&yr_list="
        temp3=""
        filt3 = "&mn_list="
        #if (tempSortBy is not None and tempSortBy != '' and tempSortDir is not None and tempSortDir != '' ):
        if(tempSortBy and tempSortDir):
            self.urlParam = self.urlParam+"&SortBy="+str(tempSortBy)+"&SortDir="+str(tempSortDir)
        if(tempTitle): 
            #tempTitle = set(tempTitle)
            for each in range(len(tempTitle)):
                temp = temp + filt + tempTitle[each]
                #self.urlParam=self.urlParam.join("&title_list="+str(each))
            
            #self.urlParam=self.urlParam.join("&title_list="+str(tempTitle))
            self.urlParam=self.urlParam+temp
        if(tempYear): 
            
            for each in range(len(tempYear)):
                temp2 = temp2 + filt2 + tempYear[each]
              
            self.urlParam=self.urlParam+temp2
        if(tempMonth): 
            
            for each in range(len(tempMonth)):
                temp3 = temp3 + filt3 + tempMonth[each]
            self.urlParam=self.urlParam+temp3
        
        

        #urlParam = urlParam+temp
        # Collect GET url parameter info
        temp_sort_dir = self.request.GET.get('SortDir')
        if (temp_sort_dir is not None and temp_sort_dir != '') and (temp_sort_dir == 'asc' or temp_sort_dir == 'desc'):
            self.req_sort_dir = temp_sort_dir

        temp_sort_by = self.request.GET.get('SortBy')
        if (temp_sort_by is not None and temp_sort_by != ''):
            self.req_sort_by = temp_sort_by

        # Get list authorized Categories of Indicator Data, and log the category_permissions
        user_cat_permissions = get_user_category_permissions(self.request.user)
        if user_cat_permissions["success"] == False:
            self.req_success = False
            self.err_msg = "Exception: WebGridPageView(): get_queryset(): {}".format(user_cat_permissions['err'])
            print(self.err_msg)
            return IndicatorData.objects.none()
        category_pk_list = user_cat_permissions["pk_list"]
        self.category_permissions = user_cat_permissions["category_names"]

        try:
            indicator_data_entries = IndicatorData.objects.filter(
                indicator__category__pk__in=category_pk_list, # Filters for authorized Categories
                indicator__active=True, # Filters for active Indicator titles
                year_month__yyyy__gt=timezone.now().year-4, # Filter for only last four year, "yyyy_gt" is "yyyy greater than"
            )
            #add unique titles to the list
            self.titles=indicator_data_entries.order_by('indicator__indicator_title').values('indicator__indicator_title').distinct()
            self.years=indicator_data_entries.order_by('year_month__yyyy').values('year_month__yyyy').distinct()
            self.months=indicator_data_entries.order_by('year_month__mm').values('year_month__mm').distinct()

        except Exception as e:
            self.req_success = False
            self.err_msg = "Exception: WebGridPageView(): get_queryset(): {}".format(e)
            print(self.err_msg)
            return IndicatorData.objects.none()

        # @TODO Filter for only searched indicator title
        yr_list = self.request.GET.getlist('yr_list')
        if len(yr_list) >= 1:
            #filterStatus = True
            try:
            #filter the queryset for each title in the list:
                my_filter_qs1 = Q()
                for i in yr_list:
                    my_filter_qs1 = my_filter_qs1 | Q(year_month__yyyy=i)
                indicator_data_entries = indicator_data_entries.filter(my_filter_qs1)
               # for i in title_list:
                #    indicator_data_entries = indicator_data_entries.filter(indicator__indicator_title=i)
            except Exception as e:
                self.req_success = False
                self.err_msg = "Exception: WebGridPageView(): get_queryset(): yr_list: {}".format(e)
                print(self.err_msg)
                return IndicatorData.objects.none()
        title_list = self.request.GET.getlist('title_list')
        if len(title_list) >= 1:
            #filterStatus = True
            try:
            #filter the queryset for each title in the list:
                my_filter_qs = Q()
                for i in title_list:
                    my_filter_qs = my_filter_qs | Q(indicator__indicator_title=i)
                indicator_data_entries = indicator_data_entries.filter(my_filter_qs)
               # for i in title_list:
                #    indicator_data_entries = indicator_data_entries.filter(indicator__indicator_title=i)
            except Exception as e:
                self.req_success = False
                self.err_msg = "Exception: WebGridPageView(): get_queryset(): title_list: {}".format(e)
                print(self.err_msg)
                return IndicatorData.objects.none()
        
       
        mn_list = self.request.GET.getlist('mn_list')
        if len(mn_list) >= 1:
            
            try:
            
                my_filter_qs2 = Q()
                for i in mn_list:
                    my_filter_qs2 = my_filter_qs2 | Q(year_month__mm=i)
                indicator_data_entries = indicator_data_entries.filter(my_filter_qs2)
               # for i in title_list:
                #    indicator_data_entries = indicator_data_entries.filter(indicator__indicator_title=i)
            except Exception as e:
                self.req_success = False
                self.err_msg = "Exception: WebGridPageView(): get_queryset(): mn_list: {}".format(e)
                print(self.err_msg)
                return IndicatorData.objects.none()

        try:
            if self.req_sort_dir == "asc":
                indicator_data_entries = indicator_data_entries.order_by(self.req_sort_by)
            elif self.req_sort_dir == "desc":
                indicator_data_entries = indicator_data_entries.order_by('-{}'.format(self.req_sort_by))
            else:
                self.req_success = False
                self.err_msg = "Exception: WebGridPageView(): get_queryset(): Unrecognized option for self.req_sort_dir: {}".format(self.req_sort_dir)
                print(self.err_msg)
                return IndicatorData.objects.none()
        except Exception as e:
            self.req_success = False
            self.err_msg = "Exception: WebGridPageView(): get_queryset(): {}".format(e)
            print(self.err_msg)
            return IndicatorData.objects.none()

         #if our list is not empty which means a filter form was filled out
        
      
        self.req_success = True
        return indicator_data_entries

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        
        try:
            context = super().get_context_data(**kwargs)

            # Add my own variables to the context for the front end to shows
            context["title_list"] = self.title_list
            context["yr_list"] = self.yr_list
            context["mn_list"] = self.mn_list
            context["urlParam"] = self.urlParam
            context["filterStatus"] = self.filterStatus
            context["uniq_titles"] = self.titles
            context["uniq_years"] = self.years
            context["uniq_months"] = self.months
            context["sort_dir"] = self.req_sort_dir
            context["sort_by"] = self.req_sort_by
            context["req_success"] = self.req_success
            context["err_msg"] = self.err_msg
            context["category_permissions"] = self.category_permissions
            return context
        except Exception as e:
            self.err_msg = "Exception: get_context_data(): {}".format(e)
            context = super().get_context_data(**kwargs)
            context["uniq_years"] = self.years
            context["mn_list"] = self.mn_list
            context["urlParam"] = self.urlParam
            context["filterStatus"] = self.filterStatus
            context["uniq_months"] = self.months
            context["uniq_titles"] = self.titles
            context["sort_dir"] = self.req_sort_dir
            context["sort_by"] = self.req_sort_by
            context["title_list"] = self.title_list
            context["yr_list"] = self.yr_list
            context["req_success"] = False
            context["err_msg"] = self.err_msg
            context["category_permissions"] = self.category_permissions
            print(self.err_msg)
            return context

def SavePerIndDataApi(request):
    id = request.POST.get('id', '')
    table = request.POST.get('table', '')
    column = request.POST.get('column', '')
    new_value = request.POST.get('new_value', '')

    # Authenticate User
    remote_user = None
    if request.user.is_authenticated:
        remote_user = request.user.username
    else:
        print('Warning: SavePerIndDataApi(): UNAUTHENTICATE USER!')
        return JsonResponse({
            "post_success": False,
            "post_msg": "SavePerIndDataApi():\n\nUNAUTHENTICATE USER!",
        })

    # Authenticate permission for user
    user_perm_chk = user_has_permission_to_edit(remote_user, id)
    if user_perm_chk["success"] == False:
        print("Warning: SavePerIndDataApi(): USER '{}' has no permission to edit record #{}!".format(remote_user, id))
        return JsonResponse({
            "post_success": False,
            "post_msg": "SavePerIndDataApi():\n\nUSER '{}' has no permission to edit record #{}: SavePerIndDataApi(): {}".format(remote_user, id, user_perm_chk["err"]),
        })


    # Make sure new_value is convertable to float
    try:
        new_value = float(new_value)
    except Exception as e:
        print("Warning: SavePerIndDataApi(): Unable to convert new_value '{}' as float type, did not save the value".format(new_value))
        return JsonResponse({
            "post_success": False,
            "post_msg": "Warning: SavePerIndDataApi():\n\nUnable to convert new_value '{}' as float type, did not save the value".format(new_value),
        })

    if table == "IndicatorData":
        row = IndicatorData.objects.get(record_id=id)

        if column=="val":
            try:
                row.val = new_value

                # Update [last updated by] to current remote user, also make sure it's active user
                user_obj = Users.objects.get(login=remote_user, active_user=True) # Will throw exception if no user is found with the criteria: "Users matching query does not exist.""
                row.update_user = user_obj

                # Update [updated date] to current time
                # updated_timestamp = datetime.now() # Give 'naive' local time, which happens to be EDT on my home dev machine
                updated_timestamp = timezone.now() # Give 'time zone awared' datetime, but backend is UTC
                row.updated_date = updated_timestamp

                local_updated_timestamp_str_response = updated_timestamp.astimezone(pytz.timezone('America/New_York')).strftime("%B %d, %Y, %I:%M %p")

                row.save()

                print("Api Log: SavePerIndDataApi(): User '{}' has successfully update '{}' to [{}].[{}] for record id '{}'".format(remote_user, new_value, table, column, id))
                return JsonResponse({
                    "post_success": True,
                    "post_msg": "",
                    "value_saved": "",
                    "updated_timestamp": local_updated_timestamp_str_response,
                    "updated_by": remote_user,
                })
            except Exception as e:
                print("Error: SavePerIndDataApi(): Something went wrong while trying to save to the database: {}".format(e))
                return JsonResponse({
                    "post_success": False,
                    "post_msg": "Error: SavePerIndDataApi():\n\nSomething went wrong while trying to save to the database: {}".format(e),
                })

    print("Warning: SavePerIndDataApi(): Did not know what to do with the request. The request:\n\nid: '{}'\n table: '{}'\n column: '{}'\n new_value: '{}'\n".format(id, table, column, new_value))
    return JsonResponse({
        "post_success": False,
        "post_msg": "Warning: SavePerIndDataApi():\n\nDid not know what to do with the request. The request:\n\nid: '{}'\n table: '{}'\n column: '{}'\n new_value: '{}'\n".format(id, table, column, new_value),
    })