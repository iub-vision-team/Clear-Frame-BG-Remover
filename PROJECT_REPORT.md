# ClearFrame AI Project Report

## 1. Project Overview

ClearFrame AI is a Django-based web application for image background removal and image prediction. The system allows users to upload JPG or PNG images, remove the background using an AI segmentation model, download the transparent PNG result, and save processed images in their personal history when they are logged in.

The project also includes a custom Cat/Dog prediction feature. A TensorFlow model is trained separately using a labeled cat/dog dataset and then loaded by the Django application to classify uploaded pet images.

Main features:

- User registration, login, logout, and profile management.
- Image upload with validation.
- Client-side preview before upload.
- AI background removal.
- Cat/Dog image prediction.
- Saved image history for authenticated users.
- Dashboard with total and recent images.
- Download and delete saved images.
- Admin panel support.

## 2. Technologies and Libraries Used

### Django

Django is the main web framework used in this project.

It is used for:

- URL routing.
- Class-based views.
- HTML template rendering.
- Form handling and validation.
- Authentication.
- Session management.
- CSRF protection.
- Database models and ORM.
- Admin panel.

Why Django was used:

- It provides built-in authentication, database handling, forms, and security features.
- It is suitable for a complete web application rather than only an API.
- It reduces the amount of custom code needed for login, registration, file uploads, and admin management.

Why Flask was not used:

- Flask is lighter, but it would require more manual setup for authentication, admin, forms, and database structure.
- This project needed a full web system, so Django was more practical.

Why FastAPI was not used:

- FastAPI is excellent for APIs, but this project is a server-rendered web application with templates, forms, login pages, and dashboards.
- Django is better suited for this style of application.

### Pillow

Pillow is used for image processing in Python.

It is used in:

- `remover/utils.py`
- Saving processed image bytes as PNG files.
- Preserving transparency in the output image.
- Reading basic image information when needed.

Why Pillow was used:

- It is reliable and widely used for image loading, conversion, and saving.
- It works well with Django uploaded image files.

Why only OpenCV was not used for saving:

- OpenCV is mainly used here for model preprocessing.
- Pillow is simpler for saving PNG images with transparency.

### rembg

`rembg` is used for background removal.

It is used in:

- `remove_background()` inside `remover/utils.py`

The function imports:

```python
from rembg import remove
```

Then it passes uploaded image bytes into `remove()` and receives PNG bytes with the background removed.

Why rembg was used:

- It provides a simple interface for background removal.
- It uses strong pre-trained segmentation models such as U2Net.
- It avoids the need to manually train a background-removal model from scratch.

Why a custom segmentation model was not trained:

- Training a high-quality background-removal model requires a large segmentation dataset with pixel-level masks.
- This project focuses on application integration and practical background removal.
- `rembg` gives strong results with much less development time.

### onnxruntime

`onnxruntime` is used indirectly by `rembg`.

It is used for:

- Running the U2Net ONNX model efficiently.
- Performing model inference locally.

Why onnxruntime was used:

- U2Net models used by `rembg` are commonly distributed in ONNX format.
- ONNX Runtime is optimized for inference and works without needing a full training framework.

Why PyTorch was not directly used for background removal:

- The app does not train U2Net.
- `rembg` and ONNX Runtime provide an easier deployment path.
- Using PyTorch directly would require more model loading and preprocessing code.

### TensorFlow

TensorFlow is used for the custom Cat/Dog prediction model.

It is used in:

- `train_cat_dog_model.py`
- `predict_animal_classes()` inside `remover/utils.py`

Main TensorFlow tasks:

- Loading image datasets.
- Building the model.
- Applying data augmentation.
- Using MobileNetV2 as a feature extractor.
- Training the classification head.
- Saving the trained model as `animal_classifier.keras`.
- Loading the saved model during prediction.

Why TensorFlow was used:

- It has strong support for image classification.
- It provides pre-trained MobileNetV2.
- It can save complete models in `.keras` format.
- It integrates well with Python web projects.

Why PyTorch was not used for prediction:

- TensorFlow/Keras gives a simpler high-level model-building API for this small classification task.
- The training script already uses Keras layers, callbacks, and model saving.
- The `.keras` format makes loading the model straightforward.

### OpenCV

OpenCV is used for image decoding and preprocessing before prediction.

It is used in:

- `predict_animal_classes()`
- `predict_image_classes()`

OpenCV steps:

- Convert uploaded file bytes into a NumPy array.
- Decode the image.
- Convert BGR to RGB.
- Resize the image to the expected model size.

Why OpenCV was used:

- It is fast for image decoding and resizing.
- It works well with NumPy arrays and machine learning preprocessing.

Why only Pillow was not used for prediction preprocessing:

- OpenCV is commonly used for computer vision pipelines.
- It gives direct control over decoding, color conversion, and resizing.

### NumPy

NumPy is used for numerical array handling.

It is used for:

- Converting uploaded bytes into arrays.
- Expanding image dimensions into a batch.
- Sorting prediction confidence scores.
- Preparing image arrays for TensorFlow.

Why NumPy was used:

- TensorFlow and OpenCV both work naturally with NumPy arrays.
- It is the standard Python library for numerical image data.

### Bootstrap 5

Bootstrap is used for frontend layout and styling.

It is used for:

- Responsive grid layout.
- Cards.
- Buttons.
- Navbar.
- Alerts.
- Forms.
- Utility classes.

Why Bootstrap was used:

- It speeds up frontend development.
- It gives a clean responsive layout without building every component from zero.
- It works well with server-rendered Django templates.

Why React was not used:

- The app does not need a heavy single-page frontend.
- Django templates are enough for upload forms, result pages, dashboard, and history.
- Using React would add more complexity and build tooling.

### Bootstrap Icons

Bootstrap Icons are used for visual icons in navigation, buttons, upload areas, dashboard cards, and history actions.

Why Bootstrap Icons were used:

- They match Bootstrap styling.
- They are easy to include through CDN.
- They improve the UI without custom image assets.

### SQLite

SQLite is used as the development database.

It stores:

- Users.
- Sessions.
- Processed image records.
- Image metadata such as upload time and prediction fields.

Why SQLite was used:

- It requires no separate database server.
- It is simple for local development and student projects.
- It works directly with Django.

Why PostgreSQL or MySQL were not used:

- They are better for production and high-traffic deployment.
- For a local academic project, SQLite is simpler and sufficient.

## 3. Application Structure

Important files:

- `manage.py`: Django project command runner.
- `ai_bg_remover/settings.py`: project configuration.
- `ai_bg_remover/urls.py`: root URL configuration.
- `remover/urls.py`: app URL routes.
- `remover/views.py`: request handling and page logic.
- `remover/forms.py`: upload, registration, and profile forms.
- `remover/models.py`: database model for saved images.
- `remover/utils.py`: AI processing and prediction helper functions.
- `templates/base.html`: shared layout and JavaScript.
- `remover/templates/remover/home.html`: background removal upload page.
- `remover/templates/remover/predict.html`: prediction page.
- `remover/templates/remover/history.html`: saved image history.
- `train_cat_dog_model.py`: custom model training script.
- `remover/ml_models/animal_classifier.keras`: trained prediction model.
- `remover/ml_models/animal_classes.json`: class names for the trained model.

## 4. Upload Validation

Uploads are validated on both the client side and server side.

Server-side validation is handled by `ImageUploadForm` in `remover/forms.py`.

Allowed image extensions:

- `.jpg`
- `.jpeg`
- `.png`

Maximum file size:

- 5 MB

Why validation is important:

- It prevents unsupported file formats.
- It avoids very large files that could slow down processing.
- It improves security and user experience.

Client-side JavaScript in `templates/base.html` also checks:

- File type.
- File size.
- Preview display before submission.

Server-side validation is still required because client-side checks can be bypassed.

## 5. Background Removal Workflow

The background removal workflow starts on the home page.

Step-by-step process:

1. User opens `/`.
2. `HomeView.get()` displays the upload form.
3. User selects an image.
4. JavaScript displays a preview.
5. User submits the form.
6. `HomeView.post()` validates the uploaded image using `ImageUploadForm`.
7. The uploaded file is passed to `remove_background()`.
8. `remove_background()` reads the image bytes.
9. `rembg.remove()` processes the image using U2Net.
10. The returned PNG bytes are saved using `save_processed_image()`.
11. If the user is logged in, a `ProcessedImage` record is created.
12. The page displays the processed image and download button.

## 6. How Background Removal Works

The project uses `rembg`, which runs U2Net.

U2Net is a deep learning segmentation model designed for salient object detection. Salient object detection means identifying the main foreground object in an image.

Simplified model process:

1. The input image is prepared for the neural network.
2. U2Net analyzes the image at multiple feature scales.
3. The model predicts a foreground probability mask.
4. Each pixel is classified as foreground or background.
5. The background is converted to transparent pixels.
6. The output is returned as a PNG with an alpha channel.

Why PNG is used:

- PNG supports transparency.
- JPG does not support transparent backgrounds.

## 7. Prediction Workflow

The prediction page is available at:

```text
/predict/
```

Step-by-step prediction process:

1. User uploads an image on the prediction page.
2. `PredictView.post()` validates the image using `ImageUploadForm`.
3. The uploaded image is passed to `predict_animal_classes()`.
4. The custom model and class names are loaded from:

```text
remover/ml_models/animal_classifier.keras
remover/ml_models/animal_classes.json
```

5. OpenCV decodes the uploaded image.
6. The image is converted from BGR to RGB.
7. The image is resized to `256 x 256`.
8. The image is converted to `float32`.
9. A batch dimension is added.
10. The TensorFlow model predicts class probabilities.
11. NumPy sorts the probabilities from highest to lowest.
12. The result is returned as labels and confidence percentages.
13. The prediction page displays the uploaded image and prediction results.

The returned prediction format contains:

- `class_id`
- `label`
- `confidence`
- `source`

Example:

```python
{
    "class_id": "cat",
    "label": "Cat",
    "confidence": 96.42,
    "source": "Custom Animal Model"
}
```

## 8. How the Custom Dataset Is Trained

The training script is:

```text
train_cat_dog_model.py
```

Expected dataset structure:

```text
dataset/
  cat_dog/
    image files...
  cat_dog.csv
```

The CSV file contains:

- `image`: image filename.
- `labels`: numeric label.

Class names:

```python
CLASS_NAMES = ["Cat", "Dog"]
```

Label meaning:

- `0`: Cat
- `1`: Dog

Training constants:

```python
IMG_SIZE = (256, 256)
MODEL_IMG_SIZE = (160, 160)
BATCH_SIZE = 32
SEED = 123
MAX_IMAGES_PER_CLASS = 1200
```

Training steps:

1. `load_rows()` reads `cat_dog.csv`.
2. It checks that each image exists in the dataset folder.
3. Images are grouped by class.
4. Up to 1200 images are selected from each class.
5. Selected images are shuffled using a fixed seed.
6. The dataset is split into:

- 80% training data.
- 20% validation data.

7. `make_dataset()` creates a TensorFlow `tf.data.Dataset`.
8. Each image is read, decoded, resized to `256 x 256`, and converted to `float32`.
9. Training data is shuffled, batched, and prefetched.
10. The model is built using `build_model()`.
11. The model is trained for up to 3 epochs.
12. Early stopping monitors validation accuracy.
13. The trained model is saved to:

```text
remover/ml_models/animal_classifier.keras
```

14. Class names are saved to:

```text
remover/ml_models/animal_classes.json
```

## 9. Prediction Model Architecture

The custom prediction model uses transfer learning.

Base model:

```python
MobileNetV2(weights="imagenet", include_top=False)
```

MobileNetV2 is used as a feature extractor. Its original classification head is removed by setting `include_top=False`.

The base model is frozen:

```python
base_model.trainable = False
```

This means the pre-trained MobileNetV2 weights are not updated during training.

Model layers:

1. Input layer: `256 x 256 x 3`
2. Data augmentation:

- Random horizontal flip.
- Small random rotation.
- Small random zoom.

3. Resize to `160 x 160`.
4. MobileNetV2 preprocessing.
5. MobileNetV2 feature extractor.
6. Global average pooling.
7. Dropout with rate `0.25`.
8. Dense output layer with softmax activation.

Output layer:

```python
Dense(2, activation="softmax")
```

Why softmax is used:

- The model predicts one class from multiple possible classes.
- Softmax converts raw scores into probabilities.

Loss function:

```python
sparse_categorical_crossentropy
```

Why this loss is used:

- The labels are integers such as `0` and `1`.
- It is appropriate for multi-class classification with integer labels.

Optimizer:

```python
Adam(learning_rate=0.0003)
```

Why Adam is used:

- It works well for image classification tasks.
- It adapts the learning rate during training.
- It usually converges faster than basic gradient descent.

## 10. Why MobileNetV2 Was Used

MobileNetV2 was selected because:

- It is lightweight.
- It is fast compared with larger models.
- It performs well on image classification tasks.
- It is available pre-trained on ImageNet.
- It is suitable for local development machines.

Why larger models were not used:

- ResNet, EfficientNet, and VGG can be heavier.
- They may take longer to train and run.
- This project only needs Cat/Dog classification, so MobileNetV2 is enough.

Why training from scratch was not used:

- Training from scratch requires more data and time.
- Transfer learning gives better results with smaller datasets.
- MobileNetV2 already knows useful image features such as edges, textures, and shapes.

## 11. Prediction Fallback

The code also includes `predict_image_classes()`, which can use ImageNet MobileNetV2 as a fallback.

However, the current `PredictView` calls:

```python
predict_animal_classes(uploaded_file)
```

So the prediction page is focused on the custom Cat/Dog model.

If the custom model file or class file is missing, `predict_animal_classes()` returns an empty list and the view displays an informational message.

## 12. How History Is Saved

History is saved through the `ProcessedImage` model in `remover/models.py`.

Important fields:

```python
user = models.ForeignKey(User, on_delete=models.CASCADE)
original_image = models.ImageField(upload_to='originals/')
processed_image = models.ImageField(upload_to='processed/', blank=True, null=True)
prediction_label = models.CharField(max_length=120, blank=True)
prediction_confidence = models.FloatField(blank=True, null=True)
predictions = models.JSONField(default=list, blank=True)
uploaded_at = models.DateTimeField(auto_now_add=True)
```

When a logged-in user removes a background:

1. The original uploaded file is saved to:

```text
media/originals/
```

2. The processed transparent PNG is saved to:

```text
media/processed/
```

3. A database record is created in `ProcessedImage`.
4. The record is connected to the current user.
5. The upload time is saved automatically.

The saving logic is in `HomeView.post()`:

```python
if request.user.is_authenticated:
    record = ProcessedImage(user=request.user)
    record.original_image.save(uploaded_file.name, uploaded_file, save=False)
    record.processed_image = relative_path
    record.save()
```

If the user is not logged in:

- The processed image is shown.
- The user can download it.
- It is not saved to personal history.

Important note:

- Background-removal history is saved for logged-in users.
- The standalone prediction page currently shows predictions and the uploaded image, but it does not save prediction-only records to history.
- The model contains prediction fields, so prediction saving can be added later if required.

## 13. Dashboard and History Display

Dashboard URL:

```text
/dashboard/
```

History URL:

```text
/history/
```

Both require login.

The dashboard displays:

- Total saved images.
- Recent images.
- Profile link.
- Full history link.

The history page displays:

- Saved processed images.
- Original filename.
- Upload date and time.
- Prediction label if stored.
- View button.
- Download button.
- Delete button.

Pagination:

- History uses Django `Paginator`.
- It shows 9 images per page.

User isolation:

```python
ProcessedImage.objects.filter(user=request.user)
```

This ensures each user only sees their own image records.

For detail pages and deletion, the app uses:

```python
get_object_or_404(ProcessedImage, pk=pk, user=request.user)
```

This prevents one user from accessing another user's images by changing the URL.

## 14. Download and Delete

Saved image download:

```text
/download/saved/<pk>/
```

Fresh processed image download:

```text
/download/<path:relative_path>/
```

Delete route:

```text
/image/<pk>/delete/
```

When deleting, the app removes:

- The original image file.
- The processed image file.
- The database record.

## 15. Security Features

Security features used in the project:

- Django CSRF protection.
- Server-side file validation.
- Client-side file validation.
- 5 MB upload size limit.
- LoginRequiredMixin on private pages.
- User-specific database filtering.
- Password validation through Django.
- Separate media and static folders.

Private pages:

- Dashboard.
- History.
- Image detail.
- Image delete.
- Profile.
- Saved image download.

## 16. Why This Design Was Chosen

The project separates responsibilities clearly:

- Views handle requests and responses.
- Forms validate user input.
- Models store database records.
- Utils handle AI and image-processing logic.
- Templates display pages.
- Static CSS handles styling.

This makes the project easier to maintain and explain.

Advantages:

- AI logic is not mixed directly into templates.
- Validation is centralized in forms.
- Database records are managed by Django ORM.
- The UI remains simple and responsive.
- The project can be extended later with more prediction classes or saved prediction history.

## 17. Limitations

Current limitations:

- SQLite is suitable for development, not large production usage.
- Background removal depends on the pre-trained `rembg` model.
- Prediction is limited to Cat/Dog classes.
- Prediction-only uploads are displayed but not saved to history yet.
- The model is trained for a small number of epochs.
- Accuracy depends on dataset quality and balance.

## 18. Possible Future Improvements

Future improvements could include:

- Save prediction-only uploads to history.
- Add more animal classes.
- Show model accuracy and validation graphs.
- Add user storage limits.
- Add asynchronous processing for large images.
- Use PostgreSQL for production.
- Add cloud storage for uploaded images.
- Add REST API endpoints.
- Add image cleanup jobs for anonymous processed files.

## 19. Conclusion

ClearFrame AI combines Django web development with practical AI image processing. The system uses `rembg` and U2Net for background removal, TensorFlow and MobileNetV2 for Cat/Dog prediction, and Django ORM for saving user history.

The project demonstrates:

- Full-stack Django development.
- Secure file upload handling.
- AI model integration.
- Transfer learning.
- Image preprocessing.
- User-specific saved history.
- A clean separation between web logic, model logic, and presentation.
