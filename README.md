# ðŸŽ¨ AI Background Remover System

A fully-featured Django web application that uses the **U2Net deep learning model** (via `rembg`) to automatically remove image backgrounds. Built with Django 4.2, class-based views, Bootstrap 5, and SQLite.

---

## ðŸ“¸ Features

| Feature | Details |
|---|---|
| **AI Background Removal** | U2Net model via rembg, no manual selection needed |
| **User Registration & Login** | Full auth system with custom registration form |
| **Image History** | Saved per-user, paginated (9 per page) |
| **Image Preview** | Client-side preview before upload |
| **Download** | Download transparent PNG with one click |
| **User Profile** | View stats, edit name/email |
| **Admin Panel** | `/admin` with thumbnail previews |
| **Guest Mode** | Remove backgrounds without logging in (no history saved) |
| **Security** | CSRF, file type validation, size limit (5 MB), login-required decorators |

---

## ðŸ“ Project Structure

```
ai_bg_remover/
├── ai_bg_remover/             # Django project package
│   ├── settings.py            # Project settings
│   ├── urls.py                # Root URL routing
│   └── wsgi.py
├── remover/                   # Main Django app
│   ├── models.py              # ProcessedImage model
│   ├── views.py               # Class-based views
│   ├── forms.py               # Upload, registration, profile forms
│   ├── utils.py               # rembg/U2Net logic
│   ├── urls.py                # App URL patterns
│   ├── static/remover/css/
│   │   └── styles.css         # App stylesheet
│   └── templates/remover/     # App templates
│       ├── home.html
│       ├── register.html
│       ├── login.html
│       ├── dashboard.html
│       ├── history.html
│       ├── image_detail.html
│       └── profile.html
├── templates/
│   └── base.html              # Master template, loads styles.css
├── media/                     # User uploads
├── manage.py
├── requirements.txt
└── README.md
```

---

## âš¡ Installation Guide (Step by Step)

### Prerequisites
- Python 3.10+ installed
- `pip` available
- Internet connection (to download the U2Net model weights ~170 MB on first run)

---

### Step 1 â€” Clone / Download the Project

```bash
git clone https://github.com/yourusername/ai-bg-remover.git
cd ai-bg-remover
```

Or if you have the zip, extract it and open a terminal inside the folder.

---

### Step 2 â€” Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

---

### Step 3 â€” Install Dependencies

```bash
pip install -r requirements.txt
```

> âš ï¸ **Note:** `rembg` will automatically download the U2Net model weights (~170 MB) the **first time** you process an image. This is a one-time download stored in your home directory.

---

### Step 4 â€” Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### Step 5 â€” Create a Superuser (for Admin Panel)

```bash
python manage.py createsuperuser
# Enter: username, email, password
```

---

### Step 6 â€” Run the Development Server

```bash
python manage.py runserver
```

Open your browser and go to: **http://127.0.0.1:8000**

Admin panel: **http://127.0.0.1:8000/admin**

---

## ðŸ”— URL Reference

| URL | View | Description |
|---|---|---|
| `/` | HomeView | Upload & remove background |
| `/register/` | RegisterView | Create account |
| `/login/` | CustomLoginView | Sign in |
| `/logout/` | CustomLogoutView | Sign out |
| `/dashboard/` | DashboardView | Stats & recent images *(login required)* |
| `/history/` | HistoryView | Paginated history *(login required)* |
| `/image/<pk>/` | ImageDetailView | View single image *(login required)* |
| `/image/<pk>/delete/` | ImageDeleteView | Delete image *(login required)* |
| `/profile/` | ProfileView | View/edit profile *(login required)* |
| `/download/<path>/` | DownloadImageView | Download processed PNG |
| `/download/saved/<pk>/` | DownloadSavedImageView | Download saved PNG *(login required)* |
| `/admin/` | Django Admin | Manage users & images |

---

## ðŸ—„ï¸ Database Model

```python
class ProcessedImage(models.Model):
    user           = ForeignKey(User, on_delete=CASCADE)
    original_image = ImageField(upload_to='originals/')
    processed_image = ImageField(upload_to='processed/')
    uploaded_at    = DateTimeField(auto_now_add=True)
```

---

## âš™ï¸ Settings â€” Media Configuration

```python
# settings.py
MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

MAX_UPLOAD_SIZE = 5 * 1024 * 1024          # 5 MB
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png']
```

---

## ðŸ” Security Features

- **CSRF protection** â€” all POST forms include `{% csrf_token %}`
- **File type validation** â€” server-side (forms.py) + client-side (JavaScript)
- **File size limit** â€” 5 MB enforced in `ImageUploadForm.clean_image()`
- **LoginRequiredMixin** â€” history, dashboard, profile, delete are protected
- **User isolation** â€” `get_object_or_404(ProcessedImage, pk=pk, user=request.user)` ensures users can only access their own images

---

## ðŸ¤– How the AI Model Works (Viva Explanation)

### What is U2Net?

**U2Net** stands for **U-squared Network**. It is a deep learning model designed for **Salient Object Detection** â€” detecting the most visually prominent object (foreground) in an image.

### Step-by-Step AI Process

```
Input Image
    â”‚
    â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  1. Pre-processing                       â”‚
â”‚     â€¢ Resize to 320Ã—320 pixels           â”‚
â”‚     â€¢ Normalise pixel values to [0, 1]   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â”‚
                     â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  2. U2Net Forward Pass                   â”‚
â”‚     â€¢ 6 nested U-Net encoderâ€“decoder    â”‚
â”‚       stages (RSU blocks)               â”‚
â”‚     â€¢ Each stage extracts features at   â”‚
â”‚       a different scale:                â”‚
â”‚       â€“ Stage 1: Fine edges & textures  â”‚
â”‚       â€“ Stage 6: High-level semantics   â”‚
â”‚     â€¢ Feature maps fused via side outputâ”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â”‚
                     â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  3. Saliency Map Output                  â”‚
â”‚     â€¢ Each pixel gets a probability     â”‚
â”‚       value 0.0 (background) â†’ 1.0      â”‚
â”‚       (foreground)                      â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â”‚
                     â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  4. Alpha Mask Application               â”‚
â”‚     â€¢ rembg thresholds the map          â”‚
â”‚     â€¢ Foreground pixels: alpha = 255    â”‚
â”‚     â€¢ Background pixels: alpha = 0      â”‚
â”‚       (fully transparent)               â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â”‚
                     â–¼
           Output: PNG with
           transparent background
```

### Key Points for Viva

| Question | Answer |
|---|---|
| What model is used? | U2Net (U-squared Network) |
| What library? | `rembg` â€” wraps U2Net with a simple Python API |
| What format is the output? | PNG with alpha transparency channel |
| Is it supervised/unsupervised? | Supervised â€” trained on DUTS-TR (10,553 labelled images) |
| What task does it solve? | Salient Object Detection / Foreground Segmentation |
| Why U2Net over U-Net? | Nested residual U-blocks capture features at multiple scales simultaneously |
| Where is the AI logic? | In `remover/utils.py` â€” separated from views (good design) |
| How is it integrated? | `from rembg import remove` â€” single function call |

### Analogy for Viva
> *"Think of U2Net like a team of artists looking at the same painting through different lenses â€” some look at tiny details (edges), others at the big picture (subject vs background). They all vote on each pixel, and the result is a precise mask that separates the subject from the background."*

---

## ðŸ“¦ Dependencies

| Package | Purpose |
|---|---|
| Django 4.2 | Web framework |
| Pillow | Image processing in Python |
| rembg | Background removal using U2Net |
| onnxruntime | Runs the U2Net ONNX model efficiently |

---

## ðŸš€ GitHub Submission Checklist

- [x] All source files included
- [x] `requirements.txt` present
- [x] `README.md` with installation steps
- [x] `.gitignore` recommended entries below
- [x] No secret keys hardcoded (change `SECRET_KEY` for production)
- [x] Database (`db.sqlite3`) â€” commit or exclude per your preference
- [x] `media/` folder â€” **do not commit** user uploads

### Recommended `.gitignore`

```
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
