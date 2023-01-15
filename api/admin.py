from django.contrib import admin
from .models import UserProfile, Friendship, Transaction, Category, TransactionOwed


class TransactionOwedInline(admin.TabularInline):
    model = TransactionOwed
    extra = 1


class TransactionAdmin(admin.ModelAdmin):
    inlines = (TransactionOwedInline,)
    list_display = ('id', 'amount', 'category', 'date', 'description', 'payer',)
    list_filter = ('category', 'payer', 'date',)
    search_fields = ('description',)


admin.site.register(UserProfile)
admin.site.register(Friendship)
admin.site.register(Category)
admin.site.register(TransactionOwed)
admin.site.register(Transaction, TransactionAdmin)
