from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Student, Attendance, Expense
from .forms import StudentForm, AttendanceForm, ExpenseForm
from datetime import date, datetime

import csv
from django.http import HttpResponse
from datetime import date, timedelta, datetime


from datetime import date, timedelta
from django.utils import timezone


from django.contrib.auth.decorators import login_required, user_passes_test

def staff_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)



from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
# (these imports may already be there, keep only one copy)


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Option A: auto-login after register
            # auth_login(request, user)
            # return redirect("tracker:dashboard")

            # Option B: go to login page after register
            return redirect("login")
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    total_students = Student.objects.count()
    total_attendance = Attendance.objects.count()
    total_present = Attendance.objects.filter(status='P').count()
    total_absent = Attendance.objects.filter(status='A').count()
    total_expense = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'total_students': total_students,
        'total_attendance': total_attendance,
        'total_present': total_present,
        'total_absent': total_absent,
        'total_expense': total_expense,
    }
    return render(request, 'tracker/dashboard.html', context)


@login_required
def student_list(request):
    students = Student.objects.all().order_by('name')
    return render(request, 'tracker/student_list.html', {'students': students})


@login_required
def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tracker:student_list')
    else:
        form = StudentForm()
    return render(request, 'tracker/student_form.html', {'form': form})


@login_required
def attendance_list(request):
    records = Attendance.objects.select_related('student').order_by('-date')

    # ---- FILTERS ----
    period = request.GET.get('period')           # today / week / month / custom
    start_date = request.GET.get('start_date')   # yyyy-mm-dd
    end_date = request.GET.get('end_date')       # yyyy-mm-dd

    today = date.today()

    if period == 'today':
        records = records.filter(date=today)

    elif period == 'week':
        # Monday as start of week
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        records = records.filter(date__range=[start, end])

    elif period == 'month':
        start = today.replace(day=1)
        if start.month == 12:
            next_month = start.replace(year=start.year + 1, month=1, day=1)
        else:
            next_month = start.replace(month=start.month + 1, day=1)
        end = next_month - timedelta(days=1)
        records = records.filter(date__range=[start, end])

    # Custom date range (overrides period if both given)
    if start_date and end_date:
        try:
            from datetime import datetime
            s = date.fromisoformat(start_date)
            e = date.fromisoformat(end_date)
            records = records.filter(date__range=[s, e])
        except ValueError:
            pass  # ignore invalid dates

    context = {
        'records': records,
        'period': period or '',
        'start_date': start_date or '',
        'end_date': end_date or '',
    }
    return render(request, 'tracker/attendance_list.html', context)


@login_required
def attendance_create(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tracker:attendance_list')
    else:
        form = AttendanceForm()
    return render(request, 'tracker/attendance_form.html', {'form': form})

@login_required
def expense_list(request):
    expenses, period, start_date, end_date = filter_expenses(request)

    from django.db.models import Sum
    total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    category_summary = (
        expenses.values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    context = {
        'expenses': expenses,
        'total_expense': total_expense,
        'category_summary': category_summary,
        'period': period or '',
        'start_date': start_date or '',
        'end_date': end_date or '',
    }
    return render(request, 'tracker/expense_list.html', context)




@login_required
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tracker:expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'tracker/expense_form.html', {'form': form})

@login_required
def attendance_mark_day(request):
    # If no date selected, use today
    selected_date_str = request.POST.get('date') or request.GET.get('date')
    if selected_date_str:
        selected_date = date.fromisoformat(selected_date_str)
    else:
        selected_date = date.today()
        selected_date_str = selected_date.isoformat()

    students = Student.objects.all().order_by('name')

    if request.method == 'POST':
        for student in students:
            status = request.POST.get(f'status_{student.id}')
            in_time_str = request.POST.get(f'in_time_{student.id}') or None
            out_time_str = request.POST.get(f'out_time_{student.id}') or None
            remarks = request.POST.get(f'remarks_{student.id}') or ''

            if not status:
                # Skip students you didn't touch
                continue

            in_time = None
            out_time = None
            if in_time_str:
                in_time = datetime.strptime(in_time_str, "%H:%M").time()
            if out_time_str:
                out_time = datetime.strptime(out_time_str, "%H:%M").time()

            Attendance.objects.update_or_create(
                student=student,
                date=selected_date,
                defaults={
                    'status': status,
                    'in_time': in_time,
                    'out_time': out_time,
                    'remarks': remarks,
                }
            )

        # After save, reload same page
        return redirect(f"{request.path}?date={selected_date_str}")

    context = {
        'students': students,
        'selected_date': selected_date_str,
    }
    return render(request, 'tracker/attendance_mark_day.html', context)

def filter_expenses(request):
    expenses = Expense.objects.order_by('-date')

    period = request.GET.get('period')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    today = date.today()

    if period == 'today':
        expenses = expenses.filter(date=today)

    elif period == 'week':
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        expenses = expenses.filter(date__range=[start, end])

    elif period == 'month':
        start = today.replace(day=1)
        if start.month == 12:
            next_month = start.replace(year=start.year + 1, month=1, day=1)
        else:
            next_month = start.replace(month=start.month + 1, day=1)
        end = next_month - timedelta(days=1)
        expenses = expenses.filter(date__range=[start, end])

    if start_date and end_date:
        try:
            s = date.fromisoformat(start_date)
            e = date.fromisoformat(end_date)
            expenses = expenses.filter(date__range=[s, e])
        except ValueError:
            pass

    return expenses, period, start_date, end_date


@login_required
def expense_export_csv(request):
    expenses, _, _, _ = filter_expenses(request)

    # Create the HttpResponse object with CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'

    writer = csv.writer(response)
    # Header row
    writer.writerow(["Date", "Category", "Description", "Amount", "Payment Mode", "Notes"])

    for e in expenses:
        writer.writerow([
            e.date,
            e.category,
            e.description,
            float(e.amount),   # convert Decimal to float
            e.payment_mode,
            e.notes or "",
        ])

    return response


