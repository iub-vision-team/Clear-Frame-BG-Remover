"""
views.py — AI Background Remover Views
========================================
All views are class-based (CBV) following Django best practices.
"""

import os
import logging
import base64

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import FileResponse, Http404
from django.conf import settings

from .forms import ImageUploadForm, CustomUserCreationForm, UserProfileForm
from .models import ProcessedImage
from .utils import predict_animal_classes, remove_background, save_processed_image

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Home / Index
# ─────────────────────────────────────────────

class HomeView(View):
    """Landing page — shows upload form and handles image processing."""

    template_name = 'remover/home.html'

    def get(self, request):
        form = ImageUploadForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = ImageUploadForm(request.POST, request.FILES)

        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        uploaded_file = request.FILES['image']

        try:
            # ── AI Processing ──────────────────────────────────
            output_bytes = remove_background(uploaded_file)

            processed_dir = os.path.join(settings.MEDIA_ROOT, 'processed')
            relative_path = save_processed_image(output_bytes, processed_dir)
            processed_url = settings.MEDIA_URL + relative_path

            # ── Save to DB (only if logged in) ─────────────────
            if request.user.is_authenticated:
                record = ProcessedImage(user=request.user)
                record.original_image.save(uploaded_file.name, uploaded_file, save=False)
                record.processed_image = relative_path
                record.save()
                messages.success(request, 'Background removed and saved to your history!')
            else:
                messages.info(request, 'Background removed! Log in to save your history.')

            return render(request, self.template_name, {
                'form': ImageUploadForm(),
                'processed_url': processed_url,
                'processed_path': relative_path,
                'original_name': uploaded_file.name,
            })

        except RuntimeError as exc:
            logger.error("Processing error: %s", exc)
            messages.error(request, f'Error processing image: {exc}')
            return render(request, self.template_name, {'form': form})


class PredictView(View):
    """Separate image classification feature."""

    template_name = 'remover/predict.html'

    def get(self, request):
        return render(request, self.template_name, {'form': ImageUploadForm()})

    def post(self, request):
        form = ImageUploadForm(request.POST, request.FILES)

        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        uploaded_file = request.FILES['image']
        predictions = predict_animal_classes(uploaded_file)
        uploaded_file.seek(0)
        image_data = base64.b64encode(uploaded_file.read()).decode('ascii')
        uploaded_file.seek(0)
        predicted_image_url = f"data:{uploaded_file.content_type};base64,{image_data}"

        if not predictions:
            messages.info(
                request,
                'Custom animal model is not ready yet. Train it first to create remover/ml_models/animal_classifier.keras.'
            )
        elif predictions[0].get('confidence', 0) < 20:
            messages.warning(
                request,
                'This is a low-confidence prediction, so the labels may be inaccurate.'
            )

        return render(request, self.template_name, {
            'form': ImageUploadForm(),
            'predictions': predictions,
            'original_name': uploaded_file.name,
            'predicted_image_url': predicted_image_url,
        })


# ─────────────────────────────────────────────
# Authentication
# ─────────────────────────────────────────────

class RegisterView(View):
    """User registration."""

    template_name = 'remover/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = CustomUserCreationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}! Your account has been created.')
            return redirect('home')
        return render(request, self.template_name, {'form': form})


class CustomLoginView(LoginView):
    """Custom login view with Bootstrap-styled template."""

    template_name = 'remover/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Welcome back, {self.request.user.first_name or self.request.user.username}!')
        return response


class CustomLogoutView(View):
    """Logout then redirect to home."""

    def post(self, request):
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('home')

    # Allow GET logout too (for simplicity in dev)
    def get(self, request):
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('home')


# ─────────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────────

class DashboardView(LoginRequiredMixin, View):
    """User dashboard showing stats and recent images."""

    template_name = 'remover/dashboard.html'

    def get(self, request):
        images = ProcessedImage.objects.filter(user=request.user)
        total_count = images.count()
        recent_images = images[:6]

        context = {
            'total_count': total_count,
            'recent_images': recent_images,
        }
        return render(request, self.template_name, context)


# ─────────────────────────────────────────────
# History (with pagination)
# ─────────────────────────────────────────────

class HistoryView(LoginRequiredMixin, View):
    """Full image history for the logged-in user, paginated."""

    template_name = 'remover/history.html'
    paginate_by = 9

    def get(self, request):
        all_images = ProcessedImage.objects.filter(user=request.user)
        paginator = Paginator(all_images, self.paginate_by)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj,
            'total_count': all_images.count(),
        }
        return render(request, self.template_name, context)


# ─────────────────────────────────────────────
# Image Detail
# ─────────────────────────────────────────────

class ImageDetailView(LoginRequiredMixin, View):
    """Shows a single processed image with download options."""

    template_name = 'remover/image_detail.html'

    def get(self, request, pk):
        image = get_object_or_404(ProcessedImage, pk=pk, user=request.user)
        return render(request, self.template_name, {'image': image})


# ─────────────────────────────────────────────
# Image Delete
# ─────────────────────────────────────────────

class ImageDeleteView(LoginRequiredMixin, View):
    """Delete a processed image record (and physical files)."""


    def post(self, request, pk):
        image = get_object_or_404(ProcessedImage, pk=pk, user=request.user)

        # Delete physical files from disk
        if image.original_image and os.path.isfile(image.original_image.path):
            os.remove(image.original_image.path)
        if image.processed_image and os.path.isfile(image.processed_image.path):
            os.remove(image.processed_image.path)

        image.delete()
        messages.success(request, 'Image deleted successfully.')
        return redirect('history')


# ─────────────────────────────────────────────
# Profile
# ─────────────────────────────────────────────

class ProfileView(LoginRequiredMixin, View):
    """User profile page — view & update name/email."""

    template_name = 'remover/profile.html'

    def get(self, request):
        form = UserProfileForm(instance=request.user)
        image_count = ProcessedImage.objects.filter(user=request.user).count()
        return render(request, self.template_name, {'form': form, 'image_count': image_count})

    def post(self, request):
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        image_count = ProcessedImage.objects.filter(user=request.user).count()
        return render(request, self.template_name, {'form': form, 'image_count': image_count})


# ─────────────────────────────────────────────
# Download processed image
# ─────────────────────────────────────────────

class DownloadImageView(View):
    """
    Serve a processed image as a file download.
    Authenticated users can download their own saved images.
    Anonymous users can download a freshly processed image by relative path.
    """

    def get(self, request, relative_path=None):
        if relative_path:
            # Anonymous or quick download — path passed directly
            abs_path = os.path.join(settings.MEDIA_ROOT, relative_path)
        else:
            raise Http404

        if not os.path.isfile(abs_path):
            raise Http404('Processed image not found.')

        response = FileResponse(open(abs_path, 'rb'), content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="bg_removed.png"'
        return response


class DownloadSavedImageView(LoginRequiredMixin, View):
    """Download a saved processed image (by DB record id)."""


    def get(self, request, pk):
        record = get_object_or_404(ProcessedImage, pk=pk, user=request.user)
        abs_path = record.processed_image.path

        if not os.path.isfile(abs_path):
            raise Http404('Processed image file not found on disk.')

        response = FileResponse(open(abs_path, 'rb'), content_type='image/png')
        response['Content-Disposition'] = 'attachment; filename="bg_removed.png"'
        return response
