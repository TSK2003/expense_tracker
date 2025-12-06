from django import forms
from .models import Student, Attendance, Expense


class BaseStyledModelForm(forms.ModelForm):
    """Base form to add Bootstrap classes to all fields."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget

            # Common style
            if isinstance(widget, (forms.TextInput, forms.DateInput, forms.TimeInput,
                                   forms.NumberInput, forms.EmailInput, forms.Textarea)):
                widget.attrs.setdefault("class", "form-control")
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault("class", "form-select")
            elif isinstance(widget, forms.RadioSelect):
                widget.attrs.setdefault("class", "form-check-input")

            # Optional: add placeholder = label
            if not widget.attrs.get("placeholder") and not isinstance(widget, forms.Select):
                widget.attrs["placeholder"] = field.label


class StudentForm(BaseStyledModelForm):
    class Meta:
        model = Student
        fields = ['name', 'phone', 'course', 'join_date']
        widgets = {
            'join_date': forms.DateInput(attrs={'type': 'date'}),
        }


class AttendanceForm(BaseStyledModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'date', 'status', 'in_time', 'out_time', 'remarks']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'in_time': forms.TimeInput(attrs={'type': 'time'}),
            'out_time': forms.TimeInput(attrs={'type': 'time'}),
        }


class ExpenseForm(BaseStyledModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'category', 'description', 'amount', 'payment_mode', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
