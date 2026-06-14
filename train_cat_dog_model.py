import csv
import json
from pathlib import Path

import tensorflow as tf
from tensorflow.keras import layers


BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "dataset" / "cat_dog"
CSV_PATH = BASE_DIR / "dataset" / "cat_dog.csv"
MODEL_DIR = BASE_DIR / "remover" / "ml_models"
MODEL_PATH = MODEL_DIR / "animal_classifier.keras"
CLASSES_PATH = MODEL_DIR / "animal_classes.json"

CLASS_NAMES = ["Cat", "Dog"]
IMG_SIZE = (256, 256)
MODEL_IMG_SIZE = (160, 160)
BATCH_SIZE = 32
SEED = 123
MAX_IMAGES_PER_CLASS = 1200


def load_rows():
    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            image_path = DATASET_DIR / row["image"]
            if image_path.exists():
                rows.append((str(image_path), int(row["labels"])))
    return rows


def make_dataset(paths, labels, training=False):
    path_ds = tf.data.Dataset.from_tensor_slices((paths, labels))

    def load_image(path, label):
        image = tf.io.read_file(path)
        image = tf.io.decode_image(image, channels=3, expand_animations=False)
        image = tf.image.resize(image, IMG_SIZE)
        image = tf.cast(image, tf.float32)
        return image, label

    ds = path_ds.map(load_image, num_parallel_calls=tf.data.AUTOTUNE)
    if training:
        ds = ds.shuffle(2048, seed=SEED)
    return ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)


def build_model():
    data_augmentation = tf.keras.Sequential(
        [
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(0.04),
            layers.RandomZoom(0.08),
        ],
        name="augmentation",
    )

    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(160, 160, 3),
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False

    inputs = tf.keras.Input(shape=(256, 256, 3))
    x = data_augmentation(inputs)
    x = layers.Resizing(*MODEL_IMG_SIZE)(x)
    x = tf.keras.applications.mobilenet_v2.preprocess_input(x)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.25)(x)
    outputs = layers.Dense(len(CLASS_NAMES), activation="softmax")(x)

    model = tf.keras.Model(inputs, outputs)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0003),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def main():
    rows = load_rows()
    if not rows:
        raise RuntimeError(f"No training images found in {DATASET_DIR}")

    by_class = {0: [], 1: []}
    for path, label in rows:
        if label in by_class:
            by_class[label].append(path)

    selected_rows = []
    for label, class_paths in by_class.items():
        shuffled_indexes = tf.random.shuffle(tf.range(len(class_paths)), seed=SEED + label).numpy().tolist()
        selected_paths = [class_paths[i] for i in shuffled_indexes[:MAX_IMAGES_PER_CLASS]]
        selected_rows.extend((path, label) for path in selected_paths)

    shuffled = tf.random.shuffle(tf.range(len(selected_rows)), seed=SEED).numpy().tolist()
    selected_rows = [selected_rows[i] for i in shuffled]
    paths = [path for path, _ in selected_rows]
    labels = [label for _, label in selected_rows]

    split_at = int(len(paths) * 0.8)
    train_ds = make_dataset(paths[:split_at], labels[:split_at], training=True)
    val_ds = make_dataset(paths[split_at:], labels[split_at:])

    print(f"Training images: {split_at}")
    print(f"Validation images: {len(paths) - split_at}")
    print(f"Classes: {CLASS_NAMES}")

    model = build_model()
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy",
            patience=2,
            restore_best_weights=True,
        )
    ]
    model.fit(train_ds, validation_data=val_ds, epochs=3, callbacks=callbacks)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model.save(MODEL_PATH)
    with open(CLASSES_PATH, "w", encoding="utf-8") as class_file:
        json.dump(CLASS_NAMES, class_file, indent=2)

    print(f"Saved model: {MODEL_PATH}")
    print(f"Saved classes: {CLASSES_PATH}")


if __name__ == "__main__":
    main()
