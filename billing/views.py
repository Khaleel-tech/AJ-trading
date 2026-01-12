from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from .models import Item, Bill, BillItem
from decimal import Decimal
from django.conf import settings
import os
import json
from .utils import generate_pdf, generate_invoice_number

from decimal import Decimal
from django.shortcuts import render, redirect
from .models import Item, Bill, BillItem
import json
import os
from django.conf import settings
from .utils import generate_invoice_number, generate_pdf

@login_required
def create_bill(request):
    items = Item.objects.all()

    if request.method == "POST":
        customer_name = request.POST.get("customer_name")
        customer_mobile = request.POST.get("customer_mobile")
        customer_address = request.POST.get("customer_address")

        # Extra charges
        labour = Decimal(request.POST.get("labour", 0) or 0)
        vehicle = Decimal(request.POST.get("vehicle", 0) or 0)
        railway = Decimal(request.POST.get("railway", 0) or 0)
        tray = Decimal(request.POST.get("tray", 0) or 0)
        advance = Decimal(request.POST.get("advance", 0) or 0)

        invoice_number = generate_invoice_number()
        subtotal = Decimal("0.00")

        # Create bill first
        bill = Bill.objects.create(
            invoice_number=invoice_number,
            customer_name=customer_name,
            customer_mobile=customer_mobile,
            customer_address=customer_address,

            labour_charges=labour,
            vehicle_rent=vehicle,
            railway_charges=railway,
            tray_amount=tray,
            advance_amount=advance,

            subtotal=Decimal("0.00"),
            total_amount=Decimal("0.00")
        )

        # Process each item
        for item in items:
            qty = request.POST.get(f"qty_{item.id}")
            suit = request.POST.get(f"suit_{item.id}")

            if qty and Decimal(qty) > 0:
                qty = Decimal(qty)
                suit = Decimal(suit or 0)

                # 🔥 CORRECT FORMULA
                net_weight = qty - ((qty * suit) / Decimal("1000"))
                if net_weight < 0:
                    net_weight = Decimal("0.000")

                row_total = net_weight * item.price
                subtotal += row_total

                BillItem.objects.create(
                    bill=bill,
                    item=item,
                    quantity=qty,
                    suit=suit,
                    net_weight=net_weight,
                    price=item.price,
                    total=row_total
                )

        # Final grand total calculation
        grand_total = subtotal + labour + vehicle + railway + tray - advance

        bill.subtotal = subtotal
        bill.total_amount = grand_total
        bill.save()

        # Generate PDF
        # pdf_name = f"bill_{bill.id}.pdf"
        # pdf_path = os.path.join(settings.MEDIA_ROOT, "bills", pdf_name)
        # os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

        # generate_pdf(
        #     "billing/bill_pdf.html",
        #     {
        #         "bill": bill,
        #         "logo_path": os.path.join(settings.MEDIA_ROOT, "logo.png"),
        #         "watermark_path": os.path.join(settings.MEDIA_ROOT, "watermark.png"),
        #     },
        #     pdf_path
        # )

        # bill.pdf = f"bills/{pdf_name}"
        # bill.save()

        # return redirect("create_bill")

    from django.http import HttpResponse
    from io import BytesIO
    from xhtml2pdf import pisa
    from django.template.loader import get_template

    template = get_template("billing/bill_pdf.html")
    html = template.render({
        "bill": bill,
        "logo_path": os.path.join(settings.BASE_DIR, "billing/static/images/logo.png"),
        "watermark_path": os.path.join(settings.BASE_DIR, "billing/static/images/watermark.png"),
    })

    result = BytesIO()
    pisa.CreatePDF(html, dest=result)

    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="bill_{bill.id}.pdf"'
    return response


    # GET request
    return render(
        request,
        "billing/create_bill.html",
        {
            "items": items,
            "items_json": json.dumps([
                {"id": i.id, "name": i.name, "price": float(i.price)}
                for i in items
            ])
        }
    )

from django.shortcuts import render
from .models import Bill
@login_required

# def bill_list(request):
#     bills = Bill.objects.all().order_by('-created_at')

#     invoice = request.GET.get('invoice')
#     customer = request.GET.get('customer')
#     date = request.GET.get('date')

#     if invoice:
#         bills = bills.filter(invoice_number__icontains=invoice)

#     if customer:
#         bills = bills.filter(customer_name__icontains=customer)

#     if date:
#         bills = bills.filter(created_at__date=date)

#     context = {
#         'bills': bills
#     }
#     return render(request, 'billing/bill_list.html', context)

def bill_list(request):
    bills = Bill.objects.filter(is_removed=False).order_by('-created_at')

    invoice = request.GET.get('invoice')
    customer = request.GET.get('customer')
    date = request.GET.get('date')

    if invoice:
        bills = bills.filter(invoice_number__icontains=invoice)

    if customer:
        bills = bills.filter(customer_name__icontains=customer)

    if date:
        bills = bills.filter(created_at__date=date)

    context = {
        'bills': bills
    }
    return render(request, 'billing/bill_list.html', context)

from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    return render(request, "billing/dashboard.html")

# def logout_view(request):
#     return redirect("login")

@login_required
def add_item(request):
    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")

        Item.objects.create(name=name, price=price)
        return redirect("items_list")

    return render(request, "billing/add_item.html")

# @login_required
# def item_list(request):
#     items = Item.objects.all()
#     return render(request, "billing/item_list.html", {"items": items})



import json
from django.http import JsonResponse
from .models import Item

@login_required
def update_item(request, id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            item = Item.objects.get(id=id)

            item.name = data.get("name")
            item.price = data.get("price")
            item.save()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False})


@login_required
def items_list(request):
    items = Item.objects.all()
    return render(request, "billing/item_list.html", {"items": items})


from .models import Item, RemovedItem
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


from .models import Item, RemovedItem
from django.http import JsonResponse
@login_required
@csrf_exempt
def remove_item(request, id):
    if request.method == "POST":
        try:
            item = Item.objects.get(id=id)

            # Save in removed items table
            RemovedItem.objects.create(
                item_name=item.name,
                removed_price=item.price
            )

            # Now delete from main items table
            item.delete()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False})



from .models import RemovedItem, Item
from django.http import JsonResponse
from django.shortcuts import render, redirect

@login_required
def removed_items_list(request):
    removed_items = RemovedItem.objects.all().order_by('-removed_at')
    return render(request, "billing/removed_items.html", {"removed_items": removed_items})


@login_required
def restore_item(request, id):
    try:
        removed_item = RemovedItem.objects.get(id=id)

        # Restore to Item table
        Item.objects.create(
            name=removed_item.item.name,
            price=removed_item.removed_price
        )

        # Delete from RemovedItem table
        removed_item.delete()

        return redirect("removed_items_list")
    except Exception as e:
        return redirect("removed_items_list")



from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect

def remove_bill(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    bill.is_removed = True
    bill.removed_at = timezone.now()
    bill.save()
    return redirect('bill_list')



def removed_bills(request):
    bills = Bill.objects.filter(is_removed=True).order_by('-removed_at')
    return render(request, 'billing/removed_bills.html', {'bills': bills})



def restore_bill(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    bill.is_removed = False
    bill.removed_at = None
    bill.save()
    return redirect('removed_bills')



def permanent_delete_bill(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    bill.delete()
    return redirect('removed_bills')


from django.db.models import Count
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from django.http import JsonResponse
from .models import Bill

def bills_per_day(request):
    data = (
        Bill.objects.filter(is_removed=False)
        .annotate(day=TruncDay('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    labels = [item['day'].strftime('%d %b') for item in data]
    counts = [item['count'] for item in data]

    return JsonResponse({'labels': labels, 'counts': counts})

def bills_per_month(request):
    data = (
        Bill.objects.filter(is_removed=False)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    labels = [item['month'].strftime('%b %Y') for item in data]
    counts = [item['count'] for item in data]

    return JsonResponse({'labels': labels, 'counts': counts})


def bills_per_year(request):
    data = (
        Bill.objects.filter(is_removed=False)
        .annotate(year=TruncYear('created_at'))
        .values('year')
        .annotate(count=Count('id'))
        .order_by('year')
    )

    labels = [item['year'].strftime('%Y') for item in data]
    counts = [item['count'] for item in data]

    return JsonResponse({'labels': labels, 'counts': counts})


def analytics_dashboard(request):
    return render(request, 'billing/analytics.html')


from django.db.models import Sum
from django.http import JsonResponse
from .models import BillItem

def top_items_by_quantity(request):
    data = (
        BillItem.objects
        .filter(bill__is_removed=False)
        .values('item__name')
        .annotate(total_qty=Sum('quantity'))
        .order_by('-total_qty')[:10]
    )

    labels = [i['item__name'] for i in data]
    values = [i['total_qty'] for i in data]

    return JsonResponse({'labels': labels, 'values': values})


def top_items_by_weight(request):
    data = (
        BillItem.objects
        .filter(bill__is_removed=False)
        .values('item__name')
        .annotate(total_weight=Sum('net_weight'))
        .order_by('-total_weight')[:10]
    )

    labels = [i['item__name'] for i in data]
    values = [float(i['total_weight']) for i in data]

    return JsonResponse({'labels': labels, 'values': values})

def top_items_by_revenue(request):
    data = (
        BillItem.objects
        .filter(bill__is_removed=False)
        .values('item__name')
        .annotate(total_amount=Sum('total'))
        .order_by('-total_amount')[:10]
    )

    labels = [i['item__name'] for i in data]
    values = [float(i['total_amount']) for i in data]

    return JsonResponse({'labels': labels, 'values': values})


@login_required
def sales_analytics(request):
    return render(request, 'billing/sales_analytics.html')


@login_required
def fruits_analytics(request):
    return render(request, 'billing/fruits_analytics.html')


from django.db.models import Count
from django.db.models.functions import TruncDay, TruncMonth
from django.http import JsonResponse
from .models import Bill
from datetime import datetime


def bills_per_day_in_month(request):
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))

    data = (
        Bill.objects.filter(
            is_removed=False,
            created_at__year=year,
            created_at__month=month
        )
        .annotate(day=TruncDay('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    labels = [item['day'].strftime('%d %b') for item in data]
    counts = [item['count'] for item in data]

    return JsonResponse({'labels': labels, 'counts': counts})


def bills_per_month_in_year(request):
    year = int(request.GET.get('year', datetime.now().year))

    data = (
        Bill.objects.filter(
            is_removed=False,
            created_at__year=year
        )
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    labels = [item['month'].strftime('%b') for item in data]
    counts = [item['count'] for item in data]

    return JsonResponse({'labels': labels, 'counts': counts})


from django.db.models import Sum
from django.http import JsonResponse
from datetime import datetime
from .models import BillItem
def revenue_by_fruit_range(request):
    from_month = int(request.GET.get('from_month'))
    from_year = int(request.GET.get('from_year'))
    to_month = int(request.GET.get('to_month'))
    to_year = int(request.GET.get('to_year'))

    start_date = datetime(from_year, from_month, 1)
    end_date = datetime(to_year, to_month, 28, 23, 59, 59)

    data = (
        BillItem.objects
        .filter(
            bill__is_removed=False,
            bill__created_at__range=[start_date, end_date]
        )
        .values('item__name')
        .annotate(total_revenue=Sum('total'))
        .order_by('-total_revenue')
    )

    labels = [i['item__name'] for i in data]
    values = [float(i['total_revenue']) for i in data]

    return JsonResponse({'labels': labels, 'values': values})


@login_required
def revenue_analytics(request):
    return render(request, 'billing/revenue_analytics.html')


from django.db.models import Sum
from django.http import JsonResponse
from .models import BillItem

def fruit_revenue_share(request):
    data = (
        BillItem.objects
        .filter(bill__is_removed=False)
        .values('item__name')
        .annotate(total_revenue=Sum('total'))
        .order_by('-total_revenue')
    )

    labels = [i['item__name'] for i in data]
    values = [float(i['total_revenue']) for i in data]

    return JsonResponse({'labels': labels, 'values': values})
