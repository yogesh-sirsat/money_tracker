from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=1000)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)
    payer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paid_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateTimeField(auto_now_add=True)
    payer_owes_split = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='created_transactions')

    def __str__(self):
        return self.description

    def get_owed_users_count(self):
        return self.owed_users.count() + (1 if self.payer_owes_split else 0)

    def delete(self, using=None, keep_parents=False):
        self.payer.userprofile.budget += self.amount
        self.payer.userprofile.save()
        super().delete(using, keep_parents)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.pk is None:
            self.payer.userprofile.budget -= self.amount
        else:
            old_transaction = Transaction.objects.only('payer', 'amount').get(pk=self.pk)
            if old_transaction.payer != self.payer:
                old_transaction.payer.userprofile.budget += old_transaction.amount
                old_transaction.payer.userprofile.save()
                self.payer.userprofile.budget -= self.amount
            else:
                self.payer.userprofile.budget += old_transaction.amount - self.amount

        self.payer.userprofile.save()
        return super().save(force_insert, force_update, using, update_fields)


class TransactionOwed(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='owed_users')
    owed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owed_transactions')

    def __str__(self):
        return f"{self.transaction} owed by {self.owed_by.username}"


class Friendship(models.Model):
    requested = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_friendship')
    accepted = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accepted_friendship')
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('requested', 'accepted')

    def __str__(self):
        return f"{self.requested.username} - {self.accepted.username}"
