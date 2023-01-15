from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/register/', views.Register.as_view(), name='register'),
    path('api/authenticate/', views.Authenticate.as_view(), name='authenticate'),
    path('api/users', views.UserList.as_view(), name='user_list'),
    path('api/userprofile', views.UserProfileDetail.as_view(), name='userprofile_detail'),
    path('api/friends', views.FriendsList.as_view(), name='friends_list'),
    path('api/categories', views.CategoriesList.as_view(), name='categories_list'),
    path('api/transactions', views.TransactionsList.as_view(), name='transactions_list'),
    path('api/create_transaction', views.TransactionCreate.as_view(), name='transaction_create'),
    path('api/transaction/<int:pk>', views.TransactionDetail.as_view(), name='transaction_detail'),
    path('api/budget_spending', views.BudgetSpending.as_view(), name='budget_spending'),
    path('api/owed_users', views.OwedUsersList.as_view(), name='owed_users_list'),
    path('api/owes_to_users', views.OwesToUsersList.as_view(), name='owes_to_users_list'),

]
