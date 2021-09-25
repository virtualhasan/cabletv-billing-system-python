from typing import Any, Optional
from django.core.management.base import BaseCommand
from catv.utils import monthly_bill_generator


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        monthly_bill_generator()
        print('Generate Finished')
         