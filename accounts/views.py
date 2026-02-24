from django.views.generic import ListView, DetailView
from django.contrib.auth.models import User

class AccountListView(ListView):
    model = User
    template_name = 'accounts/account_list.html'
    context_object_name = 'users'

class AccountDetailView(DetailView):
    model = User
    template_name = 'accounts/account_detail.html'
    context_object_name = 'user'
