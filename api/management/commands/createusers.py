# from django.core.management.base import BaseCommand
# from django.contrib.auth.models import User
#
#
# class Command(BaseCommand):
#     help = 'Create new users'
#
#     def handle(self, *args, **options):
#         # List of Indian names
#         names = ["Rohan Patel", "Priyanka Shah", "Vikram Singh", "Asha Gupta", "Naveen Kumar", "Shruti Sharma",
#                  "Ashok Raj", "Meenakshi Srinivasan", "Rajesh Kaur", "Kamal Narayan"]
#
#         # Create 10 new users
#         for i in range(0, 10):
#             # Split the name into first and last name
#             first_name, last_name = names[i].split(" ")
#             username = first_name.lower() + last_name.lower()
#             email = username + "@example.com"
#             password = username
#             user, created = User.objects.get_or_create(username=username, email=email,
#                                                        defaults={'password': password, 'first_name': first_name,
#                                                                  'last_name': last_name})
#             if created:
#                 user.save()
#                 self.stdout.write(
#                     self.style.SUCCESS(f"Successfully created user {first_name} {last_name} with email {email}"))
#             else:
#                 self.stdout.write(
#                     self.style.WARNING(f"User {first_name} {last_name} with email {email} already exists"))
