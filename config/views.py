from decimal import Decimal

from django.shortcuts import render
from django.urls import reverse

from billings.models import Invoice, Milestone
from businesses.models import Business


def _status_badge(status):
    status = status or "DRAFT"
    badge_map = {
        "PAID": "bg-green-100 text-green-700",
        "PENDING": "bg-yellow-100 text-yellow-800",
        "OVERDUE": "bg-red-100 text-red-700",
        "PARTIALLY_PAID": "bg-blue-100 text-blue-700",
        "DRAFT": "bg-gray-100 text-gray-800",
    }
    return badge_map.get(status, "bg-gray-100 text-gray-800")


def index(request):
    invoices = list(Invoice.objects.prefetch_related("items", "milestones", "client"))

    total_invoices = len(invoices)
    paid_amount = Decimal("0")
    pending_amount = Decimal("0")
    overdue_amount = Decimal("0")
    pending_count = 0
    overdue_count = 0

    for invoice in invoices:
        status = invoice.status

        if status == "OVERDUE":
            overdue_count += 1
        elif status in ("PENDING", "PARTIALLY_PAID"):
            pending_count += 1

    for milestone in Milestone.objects.all():
        if milestone.status == "PAID":
            paid_amount += milestone.amount
        elif milestone.status == "OVERDUE":
            overdue_amount += milestone.amount
        else:
            pending_amount += milestone.amount

    recent_activity = []

    for invoice in Invoice.objects.prefetch_related("items").order_by("-created_at")[:5]:
        recent_activity.append(
            {
                "timestamp": invoice.created_at,
                "title": f"Invoice {invoice.invoice_number} created",
                "url": reverse("billings:invoice_detail", kwargs={"pk": invoice.pk}),
                "badge_text": invoice.status,
                "badge_is_amount": False,
                "badge_class": _status_badge(invoice.status),
                "icon_class": "fas fa-file-invoice",
                "icon_bg": "bg-blue-100",
                "icon_color": "text-blue-600",
            }
        )

    for milestone in (
        Milestone.objects.filter(status="PAID")
        .select_related("invoice")
        .prefetch_related("invoice__items")
        .order_by("-updated_at")[:5]
    ):
        invoice = milestone.invoice
        recent_activity.append(
            {
                "timestamp": milestone.updated_at,
                "title": f"Payment received for {invoice.invoice_number}",
                "url": reverse("billings:invoice_detail", kwargs={"pk": invoice.pk}),
                "badge_text": milestone.amount,
                "badge_is_amount": True,
                "badge_class": "bg-blue-100 text-blue-700",
                "icon_class": "fas fa-check-circle",
                "icon_bg": "bg-green-100",
                "icon_color": "text-green-600",
            }
        )

    for business in Business.objects.order_by("-created_at")[:5]:
        recent_activity.append(
            {
                "timestamp": business.created_at,
                "title": f"New business \"{business.name}\" added",
                "url": reverse("businesses:business_detail", kwargs={"pk": business.pk}),
                "badge_text": "NEW",
                "badge_is_amount": False,
                "badge_class": "bg-purple-100 text-purple-700",
                "icon_class": "fas fa-building",
                "icon_bg": "bg-purple-100",
                "icon_color": "text-purple-600",
            }
        )

    recent_activity = sorted(
        recent_activity, key=lambda item: item["timestamp"], reverse=True
    )[:6]

    context = {
        "total_invoices": total_invoices,
        "paid_amount": paid_amount,
        "pending_amount": pending_amount,
        "overdue_amount": overdue_amount,
        "pending_count": pending_count,
        "overdue_count": overdue_count,
        "recent_activity": recent_activity,
    }

    return render(request, "index.html", context)
