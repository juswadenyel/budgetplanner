from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import date, timedelta
import json

from .models import Transaction

CATEGORY_ICONS = {
    'Salary': {'icon': '💼', 'color': '#22c55e', 'bg': '#dcfce7'},
    'Allowance': {'icon': '🎓', 'color': '#22c55e', 'bg': '#dcfce7'},
    'Business': {'icon': '🏢', 'color': '#22c55e', 'bg': '#dcfce7'},
    'Freelance': {'icon': '💻', 'color': '#22c55e', 'bg': '#dcfce7'},
    'Food': {'icon': '🍔', 'color': '#f97316', 'bg': '#ffedd5'},
    'Transportation': {'icon': '🚗', 'color': '#8b5cf6', 'bg': '#ede9fe'},
    'Bills': {'icon': '📄', 'color': '#ef4444', 'bg': '#fee2e2'},
    'Utilities': {'icon': '⚡', 'color': '#f59e0b', 'bg': '#fef3c7'},
    'Entertainment': {'icon': '🎬', 'color': '#ec4899', 'bg': '#fce7f3'},
    'Health': {'icon': '❤️', 'color': '#ef4444', 'bg': '#fee2e2'},
    'Education': {'icon': '📚', 'color': '#3b82f6', 'bg': '#dbeafe'},
    'Groceries': {'icon': '🛒', 'color': '#f97316', 'bg': '#ffedd5'},
    'Dining Out': {'icon': '🍽️', 'color': '#6366f1', 'bg': '#e0e7ff'},
    'Others': {'icon': '📌', 'color': '#6b7280', 'bg': '#f3f4f6'},
}

ALL_CATEGORIES = [
    'Salary', 'Allowance', 'Business', 'Freelance',
    'Food', 'Transportation', 'Bills', 'Utilities',
    'Entertainment', 'Health', 'Education', 'Groceries', 'Dining Out', 'Others'
]

ITEMS_PER_PAGE = 5


def home(request):
    # Date range filter
    date_range = request.GET.get('date_range', 'this_month')
    category_filter = request.GET.get('category', '')

    today = date.today()
    if date_range == 'this_month':
        start_date = today.replace(day=1)
        end_date = today
    elif date_range == 'last_month':
        first_this = today.replace(day=1)
        end_date = first_this - timedelta(days=1)
        start_date = end_date.replace(day=1)
    elif date_range == 'this_year':
        start_date = today.replace(month=1, day=1)
        end_date = today
    elif date_range == 'last_7':
        start_date = today - timedelta(days=7)
        end_date = today
    elif date_range == 'last_30':
        start_date = today - timedelta(days=30)
        end_date = today
    else:
        start_date = today.replace(day=1)
        end_date = today

    transactions = Transaction.objects.filter(date__gte=start_date, date__lte=end_date)

    if category_filter:
        transactions = transactions.filter(category=category_filter)

    # Summary calculations (always based on date range, not category filter)
    all_in_range = Transaction.objects.filter(date__gte=start_date, date__lte=end_date)
    total_income = all_in_range.filter(transaction_type='Income').aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = all_in_range.filter(transaction_type='Expense').aggregate(total=Sum('amount'))['total'] or 0
    remaining = total_income - total_expenses

    # Pagination
    page = int(request.GET.get('page', 1))
    total_count = transactions.count()
    total_pages = max(1, (total_count + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
    page = max(1, min(page, total_pages))
    offset = (page - 1) * ITEMS_PER_PAGE
    paginated = transactions[offset:offset + ITEMS_PER_PAGE]

    # Attach icon info
    transactions_display = []
    for t in paginated:
        icon_data = CATEGORY_ICONS.get(t.category, CATEGORY_ICONS['Others'])
        transactions_display.append({
            'id': t.id,
            'date': t.date.strftime('%B %d, %Y'),
            'category': t.category,
            'icon': icon_data['icon'],
            'icon_color': icon_data['color'],
            'icon_bg': icon_data['bg'],
            'amount': t.amount,
            'transaction_type': t.transaction_type,
            'description': t.description or '',
        })

    # Page range for pagination display
    page_range = list(range(1, total_pages + 1))

    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'remaining': remaining,
        'transactions': transactions_display,
        'date_range': date_range,
        'category_filter': category_filter,
        'all_categories': ALL_CATEGORIES,
        'current_page': page,
        'total_pages': total_pages,
        'page_range': page_range,
        'has_prev': page > 1,
        'has_next': page < total_pages,
    }
    return render(request, 'home.html', context)


@require_http_methods(["POST"])
def add_transaction(request):
    try:
        data = json.loads(request.body)
        amount = float(data.get('amount', 0))
        if amount <= 0:
            return JsonResponse({'success': False, 'error': 'Amount must be greater than 0'})

        transaction_type = data.get('transaction_type')
        category = data.get('category')
        trans_date = data.get('date')
        description = data.get('description', '')

        if not all([transaction_type, category, trans_date]):
            return JsonResponse({'success': False, 'error': 'Required fields missing'})

        if transaction_type not in ['Income', 'Expense']:
            return JsonResponse({'success': False, 'error': 'Invalid transaction type'})

        if category not in ALL_CATEGORIES:
            return JsonResponse({'success': False, 'error': 'Invalid category'})

        t = Transaction.objects.create(
            transaction_type=transaction_type,
            category=category,
            amount=amount,
            date=trans_date,
            description=description,
        )
        return JsonResponse({'success': True, 'id': t.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["POST"])
def edit_transaction(request, pk):
    try:
        t = get_object_or_404(Transaction, pk=pk)
        data = json.loads(request.body)
        amount = float(data.get('amount', 0))
        if amount <= 0:
            return JsonResponse({'success': False, 'error': 'Amount must be greater than 0'})

        t.transaction_type = data.get('transaction_type', t.transaction_type)
        t.category = data.get('category', t.category)
        t.amount = amount
        t.date = data.get('date', str(t.date))
        t.description = data.get('description', t.description)
        t.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["POST"])
def delete_transaction(request, pk):
    try:
        t = get_object_or_404(Transaction, pk=pk)
        t.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def get_transaction(request, pk):
    try:
        t = get_object_or_404(Transaction, pk=pk)
        return JsonResponse({
            'success': True,
            'id': t.id,
            'transaction_type': t.transaction_type,
            'category': t.category,
            'amount': str(t.amount),
            'date': str(t.date),
            'description': t.description or '',
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})