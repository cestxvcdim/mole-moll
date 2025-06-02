from django.core.management import BaseCommand
from config.settings import CSU_PHONE_NUMBER, CSU_PASSWORD, CSU_FIRST_NAME, CSU_LAST_NAME

from users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        if not User.objects.filter(phone_number=CSU_PHONE_NUMBER).exists():
            user = User.objects.create(
                phone_number=CSU_PHONE_NUMBER,
                first_name=CSU_FIRST_NAME,
                last_name=CSU_LAST_NAME,
                is_staff=True,
                is_superuser=True,
            )

            user.set_password(CSU_PASSWORD)
            user.save()
