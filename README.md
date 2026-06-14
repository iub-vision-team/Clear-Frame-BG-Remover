# AI Background Remover System

A fully-featured Django web application that uses the **U2Net deep learning model** (via `rembg`) to automatically remove image backgrounds. Built with Django 4.2, class-based views, Bootstrap 5, and SQLite.

---

## Features

| Feature                       | Details                                                                        |
| ----------------------------- | ------------------------------------------------------------------------------ |
| **AI Background Removal**     | U2Net model via rembg; no manual selection required                            |
| **User Registration & Login** | Complete authentication system with a custom registration form                 |
| **Image History**             | Saved per user and paginated (9 images per page)                               |
| **Image Preview**             | Client-side image preview before upload                                        |
| **Download**                  | Download transparent PNG images with one click                                 |
| **User Profile**              | View statistics and edit name/email                                            |
| **Admin Panel**               | `/admin` with thumbnail previews                                               |
| **Guest Mode**                | Remove backgrounds without logging in (history is not saved)                   |
| **Security**                  | CSRF protection, file validation, 5 MB upload limit, and login-required access |

---

## Project Structure

```text
ai_bg_remover/
├── ai_bg_remover/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── remover/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── utils.py
│   ├── urls.py
│   ├── static/remover/css/
│   │   └── styles.css
│   └── templates/remover/
│       ├── home.html
│       ├── register.html
│       ├── login.html
│       ├── dashboard.html
│       ├── history.html
│       ├── image_detail.html
│       └── profile.html
├── templates/
│   └── base.html
├── media/
├── manage.py
├── requirements.txt
└── README.md
```

---

## Installation Guide

### Prerequisites

* Python 3.10 or higher
* `pip` installed
* Internet connection for downloading the U2Net model weights (~170 MB on first use)

---

### Step 1 — Clone or Download the Project

```bash
git clone https://github.com/yourusername/ai-bg-remover.git
cd ai-bg-remover
```

Alternatively, download the ZIP file, extract it, and open a terminal in the project folder.

---

### Step 2 — Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

---

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `rembg` automatically downloads the U2Net model weights (~170 MB) the first time an image is processed. This download happens only once and is stored in your home directory.

---

### Step 4 — Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### Step 5 — Create a Superuser

```bash
python manage.py createsuperuser
```

Enter your username, email, and password when prompted.

---

### Step 6 — Run the Development Server

```bash
python manage.py runserver
```

Open your browser and visit:

* Application: `http://127.0.0.1:8000`
* Admin Panel: `http://127.0.0.1:8000/admin`

---

## URL Reference

| URL                     | View                   | Description                                          |
| ----------------------- | ---------------------- | ---------------------------------------------------- |
| `/`                     | HomeView               | Upload and remove image backgrounds                  |
| `/register/`            | RegisterView           | Create an account                                    |
| `/login/`               | CustomLoginView        | Sign in                                              |
| `/logout/`              | CustomLogoutView       | Sign out                                             |
| `/dashboard/`           | DashboardView          | View statistics and recent images (login required)   |
| `/history/`             | HistoryView            | View paginated image history (login required)        |
| `/image/<pk>/`          | ImageDetailView        | View a single image (login required)                 |
| `/image/<pk>/delete/`   | ImageDeleteView        | Delete an image (login required)                     |
| `/profile/`             | ProfileView            | View and update profile information (login required) |
| `/download/<path>/`     | DownloadImageView      | Download a processed PNG                             |
| `/download/saved/<pk>/` | DownloadSavedImageView | Download a saved PNG (login required)                |
| `/admin/`               | Django Admin           | Manage users and images                              |

---

## Database Model

```python
class ProcessedImage(models.Model):
    user = ForeignKey(User, on_delete=CASCADE)
    original_image = ImageField(upload_to='originals/')
    processed_image = ImageField(upload_to='processed/')
    uploaded_at = DateTimeField(auto_now_add=True)
```

---

## Media Configuration

```python
# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png']
```

---

## Security Features

* CSRF protection through `{% csrf_token %}`
* Server-side and client-side file type validation
* 5 MB upload limit enforced in `ImageUploadForm.clean_image()`
* `LoginRequiredMixin` protects restricted pages
* User isolation using:

```python
get_object_or_404(
    ProcessedImage,
    pk=pk,
    user=request.user
)
```

This ensures users can access only their own images.

---

## How the AI Model Works (Viva Explanation)

### What is U2Net?

**U2Net (U-squared Network)** is a deep learning model designed for **Salient Object Detection**, which identifies the most visually important object in an image.

### Step-by-Step AI Process

```text
Input Image
    |
    v
1. Pre-processing
   - Resize to 320 × 320 pixels
   - Normalize pixel values to [0,1]

    |
    v
2. U2Net Forward Pass
   - Six nested U-Net encoder-decoder stages
   - Uses Residual U-blocks (RSU blocks)
   - Extracts features at multiple scales:
       • Fine edges and textures
       • High-level semantic information
   - Combines side outputs for better accuracy

    |
    v
3. Saliency Map Generation
   - Each pixel receives a probability score:
       0.0 → Background
       1.0 → Foreground

    |
    v
4. Alpha Mask Application
   - rembg thresholds the saliency map
   - Foreground pixels: alpha = 255
   - Background pixels: alpha = 0

    |
    v
Output: PNG image with a transparent background
```

---

## Key Viva Questions

| Question                                 | Answer                                                   |
| ---------------------------------------- | -------------------------------------------------------- |
| What model is used?                      | U2Net (U-squared Network)                                |
| What library is used?                    | `rembg`                                                  |
| What is the output format?               | PNG with an alpha transparency channel                   |
| Is the model supervised or unsupervised? | Supervised                                               |
| What dataset was used?                   | DUTS-TR (10,553 labeled images)                          |
| What task does it solve?                 | Salient Object Detection / Foreground Segmentation       |
| Why use U2Net instead of U-Net?          | RSU blocks capture multi-scale features more effectively |
| Where is the AI logic located?           | `remover/utils.py`                                       |
| How is it integrated?                    | `from rembg import remove`                               |

---

## Viva Analogy

> "Think of U2Net as a team of artists examining the same painting through different perspectives. Some focus on tiny details such as edges, while others observe the overall subject and context. Together, they determine which pixels belong to the foreground, creating an accurate mask that separates the subject from the background."

---

## Dependencies

| Package     | Purpose                                     |
| ----------- | ------------------------------------------- |
| Django 4.2  | Web framework                               |
| Pillow      | Image processing                            |
| rembg       | Background removal using U2Net              |
| onnxruntime | Efficient execution of the U2Net ONNX model |

---

## GitHub Submission Checklist

* [x] All source files included
* [x] `requirements.txt` included
* [x] `README.md` contains installation instructions
* [x] `.gitignore` recommended entries included
* [x] No secret keys hardcoded
* [x] Database file (`db.sqlite3`) included or excluded as preferred
* [x] User-uploaded media excluded from version control

### Recommended `.gitignore`

```text
venv/
__pycache__/
*.pyc
db.sqlite3
media/originals/
media/processed/
staticfiles/
.env
*.log
```
