from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from orthopedic_dr_dev.models import OrthopedicDr
from core.models import Territory
import os, shutil
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q

# Create your views here.
def delete_image_file(storage, name):
    """
    Delete a stored image and drop its folder when nothing is left in it.

    The upload path is keyed on the doctor name, so renaming a doctor leaves the
    old "<dr_id>-<dr_name>" folder behind once the file inside it is gone.
    """
    try:
        directory = os.path.dirname(storage.path(name))
    except NotImplementedError:
        directory = None

    storage.delete(name)

    if directory and os.path.isdir(directory) and not os.listdir(directory):
        os.rmdir(directory)


def move_image_to_current_path(obj, old_name):
    """
    Keep the stored file in step with the dr_id and dr_name it is named after.

    The upload path is only recomputed when a new file is assigned, so editing
    the id or the name on its own would leave the image in the previous folder.
    """
    new_name = obj.image.field.generate_filename(obj, os.path.basename(old_name))
    if new_name == old_name:
        return

    storage = obj.image.storage
    with storage.open(old_name) as current:
        obj.image.name = storage.save(new_name, current)
    obj.save(update_fields=['image'])
    delete_image_file(storage, old_name)


def redirect_target(pk):
    """
    Field users come from the form itself, the admin arrives with an id in the
    path, so each is sent back to the page they started from.
    """
    return 'orthopedic_dr_dev' if pk else 'odd_form'


@login_required
def anniversary(request, pk=None):
    # With an id in the path the entry is picked by id (admin edit), otherwise
    # it is the single entry belonging to the logged in territory.
    if pk:
        obj = get_object_or_404(OrthopedicDr, pk=pk)
        territory = obj.territory
    else:
        territory = Territory.objects.filter(territory=request.user.username).first()
        obj = OrthopedicDr.objects.filter(territory=territory).first() if territory else None

    if request.method == 'POST':
        if not territory:
            messages.error(request, "No territory found for this user.")
            return redirect(redirect_target(pk))

        dr_name = request.POST.get('dr_name')
        dr_image = request.FILES.get('dr_image')

        # Update the existing entry.
        if obj:
            dr_id = request.POST.get('dr_id')

            if not (dr_id and dr_name):
                messages.error(request, "Doctor RPL ID and name are required.")
                return redirect(redirect_target(pk))

            if OrthopedicDr.objects.filter(dr_id=dr_id).exclude(pk=obj.pk).exists():
                messages.error(request, "This Doctor RPL ID is already used by another entry.")
                return redirect(redirect_target(pk))

            try:
                old_image_name = obj.image.name if obj.image else None
                obj.dr_id = dr_id
                obj.dr_name = dr_name
                if dr_image:
                    obj.image = dr_image
                obj.save()

                if dr_image:
                    if old_image_name and old_image_name != obj.image.name:
                        delete_image_file(obj.image.storage, old_image_name)
                elif old_image_name:
                    move_image_to_current_path(obj, old_image_name)

                messages.success(request, "Orthopedic Dr. Development data updated successfully.")
            except Exception as e:
                messages.error(request, f"Error updating data: {str(e)}")
                print(f"Error updating data: {str(e)}")
            return redirect(redirect_target(pk))

        # Create the first (and only) entry.
        dr_id = request.POST.get('dr_id')

        # Validate the data
        if not (dr_id and dr_name and dr_image):
            messages.error(request, "All fields are required.")
            return redirect('odd_form')

        # Save the data to the database
        try:
            OrthopedicDr.objects.create(
                territory=territory,
                dr_id=dr_id,
                dr_name=dr_name,
                image=dr_image
            )
            messages.success(request, "Orthopedic Dr. Development data saved successfully.")
        except Exception as e:
            messages.error(request, f"Error saving data: {str(e)}")
            print(f"Error saving data: {str(e)}")
        return redirect('odd_form')

    context = {
        "obj": obj,
        "count": 1 if obj else 0,
        "is_admin_edit": bool(pk),
    }
    return render(request, 'odd_form.html', context=context)


@login_required
def delete_orthopedic_dr(request, pk):
    try:
        obj = get_object_or_404(OrthopedicDr, pk=pk)

        if obj.image:
            folder_path = os.path.dirname(obj.image.path)
            safe_root = os.path.join(settings.MEDIA_ROOT, 'orthopedic_dr_development')
            if os.path.commonpath([safe_root]) == os.path.commonpath([safe_root, folder_path]):
                if os.path.isdir(folder_path):
                    shutil.rmtree(folder_path)
                    print(f"Deleted folder: {folder_path}")
                else:
                    print(f"Folder not found: {folder_path}")
            else:
                print(f"Unsafe folder path skipped: {folder_path}")
        obj.delete()
        messages.success(request, "Orthopedic Dr. Development data deleted successfully.")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        print(f"Error deleting data: {str(e)}")
    return redirect('orthopedic_dr_dev')

