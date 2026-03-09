import asyncio
import logging

from playwright.async_api import async_playwright
from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework.views import APIView
from rest_framework import permissions, serializers
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer

from .models import Invoice

logger = logging.getLogger(__name__)


class InvoicePDFAPIView(APIView):
    """
    GET /billings/invoices/<uuid>/pdf/
    Generates a downloadable PDF of an invoice using Playwright (headless Chromium).
    Only the business owner can download their invoices.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(description='PDF file response', response=OpenApiTypes.BINARY),
            404: inline_serializer(
                name='InvoicePdfNotFoundSerializer',
                fields={'detail': serializers.CharField()},
            ),
            500: inline_serializer(
                name='InvoicePdfErrorSerializer',
                fields={'detail': serializers.CharField()},
            ),
        },
    )
    def get(self, request, pk):
        # Fetch invoice, scoped to the current user's businesses
        user_businesses = request.user.businesses.all()
        try:
            invoice = Invoice.objects.select_related(
                'client', 'client__business',
            ).prefetch_related('items', 'milestones').get(
                pk=pk,
                client__business__in=user_businesses,
            )
        except Invoice.DoesNotExist:
            return HttpResponse(
                '{"detail": "Invoice not found."}',
                content_type='application/json',
                status=404,
            )

        # Render the invoice HTML template
        html_content = render_to_string(
            'billings/invoice_pdf.html',
            {
                'invoice': invoice,
                'business': invoice.client.business,
            },
        )

        # Generate PDF using Playwright (sync wrapper around async API)
        try:
            pdf_bytes = asyncio.run(self._generate_pdf(html_content))
        except Exception as e:
            logger.error('PDF generation failed for invoice %s: %s', invoice.invoice_number, e)
            return HttpResponse(
                '{"detail": "PDF generation failed. Please try again."}',
                content_type='application/json',
                status=500,
            )

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
        )
        return response

    @staticmethod
    async def _generate_pdf(html_content):
        """Use headless Chromium to convert HTML → PDF bytes."""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_content(html_content, wait_until='networkidle')
            pdf_bytes = await page.pdf(
                format='A4',
                print_background=True,
                margin={'top': '0.4in', 'bottom': '0.4in', 'left': '0.4in', 'right': '0.4in'},
            )
            await browser.close()
        return pdf_bytes
