from xhtml2pdf import pisa
from django.template.loader import get_template

def generate_pdf(template_name, context, output_path):
    template = get_template(template_name)
    html = template.render(context)

    with open(output_path, "wb") as pdf:
        pisa.CreatePDF(html, dest=pdf)

import os
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa

# def generate_pdf(template_name, context, output_path):
#     # ADD ABSOLUTE PATHS
#     logo_path = os.path.join(settings.BASE_DIR, 'static/images/logo.png')
#     watermark_path = os.path.join(settings.BASE_DIR, 'static/images/watermark.png')

#     # inject into context
#     context['logo_path'] = logo_path
#     context['watermark_path'] = watermark_path

#     template = get_template(template_name)
#     html = template.render(context)

#     with open(output_path, "wb") as pdf:
#         pisa.CreatePDF(html, dest=pdf)


from datetime import datetime
from .models import Bill

def generate_invoice_number():
    year = datetime.now().year

    last_bill = Bill.objects.filter(
        invoice_number__startswith=f"INV-{year}"
    ).order_by("-id").first()

    if last_bill:
        last_number = int(last_bill.invoice_number.split("-")[-1])
        new_number = last_number + 1
    else:
        new_number = 1

    return f"INV-{year}-{str(new_number).zfill(4)}"
