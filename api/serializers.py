from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Transaction, Category, TransactionOwed


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email',)
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True}
        }


class OwedUsersSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='owed_by__id')
    username = serializers.CharField(source='owed_by__username')
    amount_owed = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = ('id', 'user', 'budget',)
        read_only_fields = ('id', 'user',)

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user = instance.user
        instance.budget = validated_data.get('budget', instance.budget)
        instance.save()
        user.email = user_data.get('email', user.email)
        user.save()
        return instance


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class TransactionSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    payer = UserSerializer()
    owed_users = serializers.SerializerMethodField()
    date = serializers.DateTimeField(format="%d %h %Y %I:%M %p", required=False)
    created_by = UserSerializer(required=False)

    class Meta:
        model = Transaction
        fields = (
            'id', 'date', 'payer', 'amount', 'category', 'description', 'owed_users', 'created_by', 'payer_owes_split',)
        read_only_fields = ('id', 'date', 'created_by',)

    @staticmethod
    def get_owed_users(obj):
        queryset = obj.owed_users.select_related('owed_by').values('owed_by__id', 'owed_by__username')
        return OwedUsersSerializer(queryset, many=True).data

    def to_internal_value(self, data):
        if self.context['request'].method == 'POST' or self.context['request'].method == 'PUT':
            self.fields['category'] = serializers.IntegerField()
            self.fields['payer'] = serializers.IntegerField()
            self.fields['owed_users'] = serializers.ListField(child=serializers.IntegerField())

        return super().to_internal_value(data)

    def validate(self, data):
        if self.context['request'].method == 'POST' or self.context['request'].method == 'PUT':
            owed_users = data.get('owed_users')
            try:
                Category.objects.get(id=data.get('category'))
            except Category.DoesNotExist:
                raise serializers.ValidationError("Given category does not exist")
            try:
                User.objects.get(id=data.get('payer'))
            except User.DoesNotExist:
                raise serializers.ValidationError("Given payer does not exist")
            for user_id in owed_users:
                try:
                    User.objects.get(id=user_id)
                except User.DoesNotExist:
                    raise serializers.ValidationError(f"User with id {user_id} does not exist")
            if data.get('payer') in owed_users:
                raise serializers.ValidationError('Payer cannot owe to themselves')
        return data

    def create(self, validated_data):
        created_by = self.context['request'].user
        category_id = validated_data.pop('category')
        payer_id = validated_data.pop('payer')
        owed_users = validated_data.pop('owed_users')
        category = Category.objects.get(id=category_id)
        payer = User.objects.get(id=payer_id)
        transaction = Transaction.objects.create(category=category, payer=payer, created_by=created_by,
                                                 **validated_data)
        transaction.save()
        TransactionOwed.objects.bulk_create(
            [TransactionOwed(transaction=transaction, owed_by=User.objects.get(id=user_id)) for user_id in owed_users])

        return transaction

    def update(self, instance, validated_data):
        category_id = validated_data.pop('category')
        payer_id = validated_data.pop('payer')
        updated_owed_users = frozenset(validated_data.pop('owed_users'))
        category = Category.objects.get(id=category_id)
        payer = User.objects.get(id=payer_id)
        instance.category = category
        instance.payer = payer
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        instance.owed_users.exclude(owed_by__id__in=updated_owed_users).delete()

        current_owed_users = frozenset(instance.owed_users.values_list('owed_by__id', flat=True))
        for user_id in updated_owed_users:
            if user_id in current_owed_users:
                continue
            user = User.objects.get(id=user_id)
            transaction_owed = TransactionOwed.objects.create(transaction=instance, owed_by=user)
            transaction_owed.save()

        return instance
