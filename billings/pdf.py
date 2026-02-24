import asyncio
from playwright.async_api import async_playwright
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Invoice

async def generate_invoice_pdf(request, invoice_id):
    invoice = Invoice.objects.get(pk=invoice_id)
    
    # Render the invoice preview component to HTML
    # This assumes you have a way to render the React component to a string
    # Or you could have a separate template for the PDF
    html_content = render_to_string('billings/invoice_pdf.html', {'invoice': invoice})

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html_content)
        pdf_bytes = await page.pdf(format='A4')
        await browser.close()

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
    return response
