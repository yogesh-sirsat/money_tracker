from collections import defaultdict
from decimal import Decimal

from django.contrib.auth.models import User
from django.db.models import Q, F, Count, DecimalField, Sum, Prefetch, ExpressionWrapper
from django.http import HttpResponse
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Transaction, Category, TransactionOwed
from .serializers import UserSerializer, UserProfileSerializer, TransactionSerializer, CategorySerializer, \
    OwedUsersSerializer

SPLIT_AMOUNT_EXPRESSION = ExpressionWrapper(
    F('transaction__amount') / Count('transaction__owed_users') +
    F('transaction__payer_owes_split'),
    output_field=DecimalField())


def index(request):
    # print('loading...') payer = User.objects.get(username='dummy1') queries = TransactionOwed.objects.filter(
    # transaction__payer=payer, transaction__owed_users__isnull=False).annotate( amount_owed=F('transaction__amount')
    # / Count('transaction__owed_users') + Case( When(transaction__payer_owes_split=True, then=1), default=0,
    # output_field=DecimalField())).values('owed_by__username', 'amount_owed')
    #
    # execution_time = timeit.timeit(lambda: queries.all(), number=100000)
    #
    # print('Execution time:', execution_time)
    return HttpResponse('<h1 style="text-align: center">Hello World! You are at Money Tracker backend.</h1>')


class Register(APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def post(request):
        user_serializer = UserSerializer(
            data=request.data, context={'request': request})
        if user_serializer.is_valid():
            user = user_serializer.save()
            if user:
                token = Token.objects.create(user=user)
                return Response({'message': 'You registered successfully!', 'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Authenticate(APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def post(request, *args, **kwargs):
        username = request.data.get('username', None)
        password = request.data.get('password', None)
        if username is None or password is None:
            return Response({'message': 'Please provide both email and password.'},
                            status=400)
        user = User.objects.filter(username=username).first()
        if user is None:
            return Response({'message': 'User does not exists.'},
                            status=404)
        if not user.check_password(password):
            return Response({'message': 'Incorrect Password.'},
                            status=401)

        token, created = Token.objects.get_or_create(user=user)
        if created:
            token.save()
        return Response({'message': 'Authentication successful!', 'token': token.key}, status=status.HTTP_200_OK)


class UserList(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.only('id', 'username')


class FriendsList(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        user_friends = User.objects.filter(Q(requested_friendship__accepted=user) |
                                           Q(accepted_friendship__requested=user)).only('id', 'username', 'email')
        return user_friends


class UserProfileDetail(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer

    @staticmethod
    def get(request, *args, **kwargs):
        user = request.user
        serializer = UserProfileSerializer(user.userprofile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def put(request, *args, **kwargs):
        user = request.user
        serializer = UserProfileSerializer(user.userprofile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile updated successfully!'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoriesList(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TransactionCreate(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = TransactionSerializer

    @staticmethod
    def post(request, *args, **kwargs):
        serializer = TransactionSerializer(
            context={'request': request}, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Transaction created successfully!'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionDetail(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = TransactionSerializer

    @staticmethod
    def get(request, pk, *args, **kwargs):
        try:
            transaction = Transaction.objects.get(pk=pk)
        except Transaction.DoesNotExist:
            return Response({'message': 'Transaction does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def put(request, pk, *args, **kwargs):
        try:
            transaction = Transaction.objects.get(pk=pk)
        except Transaction.DoesNotExist:
            return Response({'message': 'Transaction does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        if transaction.created_by != request.user:
            return Response({'message': 'You do not have permission to edit this transaction.'},
                            status=status.HTTP_401_UNAUTHORIZED)
        serializer = TransactionSerializer(
            transaction, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Transaction updated successfully!'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, pk, *args, **kwargs):
        try:
            transaction = Transaction.objects.get(pk=pk)
        except Transaction.DoesNotExist:
            return Response({'message': 'Transaction does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        if transaction.created_by != request.user:
            return Response({'message': 'You do not have permission to delete this transaction.'},
                            status=status.HTTP_403_FORBIDDEN)

        transaction.delete()
        return Response({'message': 'Transaction deleted successfully!'}, status=status.HTTP_200_OK)


class TransactionsList(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


def default_dict_to_list(default_dict):
    return [{'owed_by__id': k, 'owed_by__username': v['username'], 'amount_owed': v['amount_owed']} for k, v in
            default_dict.items()]


class OwedUsersList(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = OwedUsersSerializer

    def get_queryset(self):
        payer = self.request.user
        owed_instances = (TransactionOwed.objects
                          .prefetch_related(
                              Prefetch('transaction',
                                       queryset=Transaction.objects.only('amount', 'payer_owes_split')),
                              Prefetch('owed_by',
                                       queryset=User.objects.only('id', 'username')))
                          .filter(transaction__payer=payer)
                          .exclude(transaction__owed_users__isnull=True)
                          .values('owed_by__id', 'owed_by__username')
                          .annotate(amount_owed=SPLIT_AMOUNT_EXPRESSION)
                          .order_by('-amount_owed'))

        combined_owed_instances = defaultdict(
            lambda: defaultdict(Decimal, amount_owed=Decimal(0)))
        for owed in owed_instances:
            combined_owed_instances[owed['owed_by__id']
                                    ]['username'] = owed['owed_by__username']
            combined_owed_instances[owed['owed_by__id']
                                    ]['amount_owed'] += owed['amount_owed']

        return default_dict_to_list(combined_owed_instances)


class OwesToUsersList(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = OwedUsersSerializer

    def get_queryset(self):
        user = self.request.user

        user_owes_to = (user.owed_transactions
                        .exclude(transaction__owed_users__isnull=True)
                        .prefetch_related(
                            Prefetch('transaction',
                                     queryset=Transaction.objects.only('payer', 'amount', 'payer_owes_split')),
                            Prefetch('transaction__payer', queryset=User.objects.only('id', 'username')))
                        .values('transaction__payer__id', 'transaction__payer__username')
                        .annotate(amount_user_owes=SPLIT_AMOUNT_EXPRESSION)
                        .order_by('-amount_user_owes'))
        combine_amount_user_owes = defaultdict(
            lambda: defaultdict(Decimal, amount_owed=Decimal(0)))
        for user in user_owes_to:
            combine_amount_user_owes[user['transaction__payer__id']
                                     ]['username'] = user['transaction__payer__username']
            combine_amount_user_owes[user['transaction__payer__id']
                                     ]['amount_owed'] += user['amount_user_owes']

        return default_dict_to_list(combine_amount_user_owes)


class BudgetSpending(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def get(request, *args, **kwargs):
        user = request.user
        total_spending = user.paid_transactions.aggregate(
            total_spent=Sum('amount'))['total_spent']
        budget = user.userprofile.budget
        data = {'spending': total_spending, 'budget': budget}
        return Response(data, status=status.HTTP_200_OK)
