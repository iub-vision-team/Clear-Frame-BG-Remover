# Animal Classifier Model

Place the trained Kaggle animal classifier here:

- `animal_classifier.keras`
- `animal_classes.json`

The Django app will use this custom model automatically when both files exist.
If the model file is missing or invalid, the app falls back to the built-in
ImageNet prediction path so background removal keeps working.
