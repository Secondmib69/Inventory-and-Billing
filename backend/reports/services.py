from datetime import timedelta
from invoices.models import Invoice
from django.db.models import Sum, Value, BigIntegerField
from django.db.models.functions import TruncDate, Coalesce



def get_sales_by_day(start_date, end_date):
    qs = Invoice.objects.filter(
    created_at__date__gte=start_date,
    created_at__date__lte=end_date
)

    data = qs.annotate(day=TruncDate("created_at")) \
        .values("day") \
        .annotate(
            revenue=Coalesce(
                Sum("total_amount"),
                Value(0),
                output_field=BigIntegerField()
            )
        ).order_by("day")

    revenue_by_day = {item["day"]: item["revenue"] for item in data}

    day = start_date
    results = []

    while day <= end_date:
        results.append({
            "day": day,
            "revenue": revenue_by_day.get(day, 0)
        })
        day += timedelta(days=1)
    return results