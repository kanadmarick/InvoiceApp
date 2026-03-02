from playwright.async_api import async_playwright
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Invoice


async def generate_invoice_pdf(request, invoice_id):
    """
    Generates a downloadable PDF of an invoice using Playwright (headless Chromium).
    Renders the invoice HTML template, then converts it to a PDF.
    Requires: pip install playwright && playwright install chromium
    """
    invoice = Invoice.objects.get(pk=invoice_id)

    # Render the Django template to an HTML string
    html_content = render_to_string(
        'billings/invoice_pdf.html', {'invoice': invoice})

    # Use headless Chromium to convert HTML → PDF
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html_content)
        pdf_bytes = await page.pdf(format='A4')  # A4 paper size
        await browser.close()

    # Return the PDF as a downloadable file
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{
        invoice.invoice_number}.pdf"'
    return response
