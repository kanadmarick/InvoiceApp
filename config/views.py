from decimal import Decimal

from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from billings.models import Invoice, Milestone


# Helper: returns Tailwind CSS classes for each invoice status badge
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


@login_required(login_url='accounts:login')
def index(request):
    """Dashboard view — aggregates financial stats and recent activity for the logged-in user."""
    # Get only current user's businesses (security: isolates data per user)
    user_businesses = request.user.businesses.all()

    # Get invoices for current user's businesses only
    invoices = list(Invoice.objects.filter(
        client__business__in=user_businesses
    ).prefetch_related("items", "milestones", "client"))

    total_invoices = len(invoices)
    # Accumulators for the summary cards on the dashboard
    paid_amount = Decimal("0")
    pending_amount = Decimal("0")
    overdue_amount = Decimal("0")
    pending_count = 0
    overdue_count = 0

    # Count invoices by status (uses @property on Invoice model)
    for invoice in invoices:
        status = invoice.status

        if status == "OVERDUE":
            overdue_count += 1
        elif status in ("PENDING", "PARTIALLY_PAID"):
            pending_count += 1

    # Sum up monetary amounts from milestones (each milestone has its own
    # PAID/PENDING/OVERDUE status)
    for milestone in Milestone.objects.filter(
            invoice__client__business__in=user_businesses):
        if milestone.status == "PAID":
            paid_amount += milestone.amount
        elif milestone.status == "OVERDUE":
            overdue_amount += milestone.amount
        else:
            pending_amount += milestone.amount

    # Build a combined activity feed from invoices, payments, and businesses
    recent_activity = []

    # Recent invoices for current user
    for invoice in Invoice.objects.filter(
        client__business__in=user_businesses
    ).prefetch_related("items").order_by("-created_at")[:5]:
        recent_activity.append(
            {
                "timestamp": invoice.created_at,
                "title": f"Invoice {
                    invoice.invoice_number} created",
                "url": reverse(
                    "billings:invoice_detail",
                    kwargs={
                        "pk": invoice.pk}),
                "badge_text": invoice.status,
                "badge_is_amount": False,
                "badge_class": _status_badge(
                    invoice.status),
                "icon_class": "fas fa-file-invoice",
                "icon_bg": "bg-blue-100",
                "icon_color": "text-blue-600",
            })

    # Recent payments for current user
    for milestone in (
        Milestone.objects.filter(
            status="PAID",
            invoice__client__business__in=user_businesses
        )
        .select_related("invoice")
        .prefetch_related("invoice__items")
        .order_by("-updated_at")[:5]
    ):
        invoice = milestone.invoice
        recent_activity.append(
            {
                "timestamp": milestone.updated_at,
                "title": f"Payment received for {
                    invoice.invoice_number}",
                "url": reverse(
                    "billings:invoice_detail",
                    kwargs={
                        "pk": invoice.pk}),
                "badge_text": milestone.amount,
                "badge_is_amount": True,
                "badge_class": "bg-blue-100 text-blue-700",
                "icon_class": "fas fa-check-circle",
                    "icon_bg": "bg-green-100",
                    "icon_color": "text-green-600",
            })

    # Recent businesses for current user
    for business in user_businesses.order_by("-created_at")[:5]:
        recent_activity.append(
            {
                "timestamp": business.created_at,
                "title": f"Business \"{
                    business.name}\"",
                "url": reverse(
                    "businesses:business_detail",
                    kwargs={
                        "pk": business.pk}),
                "badge_text": "BUSINESS",
                "badge_is_amount": False,
                "badge_class": "bg-purple-100 text-purple-700",
                "icon_class": "fas fa-building",
                    "icon_bg": "bg-purple-100",
                    "icon_color": "text-purple-600",
            })

    # Sort all activity by timestamp (newest first) and show top 6
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
