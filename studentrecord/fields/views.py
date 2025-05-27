from django.shortcuts import render, redirect, get_object_or_404
from .models import Fields
from rest_framework import viewsets
from rest_framework import filters as drf_filters  # Renamed to avoid conflict
from .serializers import FieldsSerializer

# For Window functions (Django 2.0+)
from django.db.models import F, Window
from django.db.models.functions import RowNumber

# For deleting old files (optional but good practice)
import os
from django.conf import settings


# DRF ViewSet for API access
class FieldsViewSet(viewsets.ModelViewSet):
    queryset = Fields.objects.all()
    serializer_class = FieldsSerializer
    filter_backends = [drf_filters.SearchFilter, drf_filters.OrderingFilter]
    search_fields = ['name', 'classname']
    ordering_fields = ['name', 'id', 'age', 'marks']


# Function-Based Views for Web

def field_list(request):
    fields_queryset = Fields.objects.all()
    name_query = request.GET.get('name_filter')
    class_query = request.GET.get('class_filter')
    min_marks_query = request.GET.get('min_marks_filter')

    if name_query:
        fields_queryset = fields_queryset.filter(name__icontains=name_query)
    if class_query and class_query.strip():
        fields_queryset = fields_queryset.filter(classname__icontains=class_query)
    if min_marks_query:
        try:
            min_marks = int(min_marks_query)
            fields_queryset = fields_queryset.filter(marks__gte=min_marks)
        except ValueError:
            pass

    annotated_queryset = fields_queryset.annotate(
        row_num=Window(
            expression=RowNumber(),
            partition_by=[F('name'), F('classname')],
            order_by=F('marks').desc()
        )
    )
    ids_to_keep = annotated_queryset.filter(row_num=1).values_list('id', flat=True)
    final_queryset = fields_queryset.filter(id__in=list(ids_to_keep))
    final_queryset = final_queryset.order_by('name', 'classname', '-marks')

    context = {'fields': final_queryset}
    return render(request, 'fields/field_list.html', context)


def field_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        age_str = request.POST.get('age')
        classname = request.POST.get('classname')
        marks_str = request.POST.get('marks')
        profile_pic_file = request.FILES.get('profile_pic')  # Get uploaded file

        try:
            age = int(age_str) if age_str else None
            marks = int(marks_str) if marks_str else None

            if name:
                new_field = Fields(
                    name=name,
                    age=age,
                    classname=classname if classname else None,
                    marks=marks
                )
                if profile_pic_file:
                    new_field.profile_pic = profile_pic_file
                new_field.save()  # Save to get ID and handle file
                return redirect('fields:field_list')
            else:
                pass  # Handle error: name is required
        except ValueError:
            pass  # Handle error: age or marks not valid

    return render(request, 'fields/field_create.html')


def field_update(request, field_id):
    field_instance = get_object_or_404(Fields, id=field_id)
    old_pic_path = field_instance.profile_pic.path if field_instance.profile_pic else None

    if request.method == 'POST':
        field_instance.name = request.POST.get('name')
        age_str = request.POST.get('age')
        field_instance.classname = request.POST.get('classname')
        marks_str = request.POST.get('marks')
        profile_pic_file = request.FILES.get('profile_pic')

        try:
            field_instance.age = int(age_str) if age_str else field_instance.age
            field_instance.marks = int(marks_str) if marks_str else field_instance.marks

            if profile_pic_file:
                # If a new picture is uploaded, assign it.
                # The old picture will be automatically handled by ImageField if default behavior is used
                #  you can manually delete the old_pic_path if it exists and is different.
                if old_pic_path and os.path.exists(
                        old_pic_path) and field_instance.profile_pic.name != "profile_pics/default.png":
                    # Don't delete the default image if it was the old one
                    if profile_pic_file.name != os.path.basename(old_pic_path):  # if new file is different
                        try:
                            os.remove(old_pic_path)
                        except OSError:
                            pass  # Handle error if file cannot be removed
                field_instance.profile_pic = profile_pic_file
            elif 'clear_profile_pic' in request.POST:  # Add a checkbox in form with name="clear_profile_pic"
                if old_pic_path and os.path.exists(
                        old_pic_path) and field_instance.profile_pic.name != "profile_pics/default.png":
                    try:
                        os.remove(old_pic_path)
                    except OSError:
                        pass
                field_instance.profile_pic = 'profile_pics/default.png'  # Reset to default

            if field_instance.name:
                field_instance.save()
                return redirect('fields:field_list')
            else:
                pass  # Handle error: name is required
        except ValueError:
            pass  # Handle error: age or marks not valid

    return render(request, 'fields/field_update.html', {'field': field_instance})


def field_delete(request, field_id):
    field_instance = get_object_or_404(Fields, id=field_id)
    if request.method == 'POST':
        # Optionally delete the profile picture file from storage
        if field_instance.profile_pic and field_instance.profile_pic.name != 'profile_pics/default.png':
            if os.path.exists(field_instance.profile_pic.path):
                try:
                    os.remove(field_instance.profile_pic.path)
                except OSError:
                    pass  # Handle error if file cannot be removed
        field_instance.delete()
        return redirect('fields:field_list')
    return render(request, 'fields/field_delete.html', {'field': field_instance})