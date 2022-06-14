import os

import tensorflow
from tensorflow.keras.applications import (
    MobileNetV2,
    VGG16,
    MobileNetV3Large,
    ResNet50,
    ResNet50V2,
    DenseNet121,
)

# from classification_models.tfkeras import Classifiers
from tensorflow.keras.callbacks import CSVLogger
from tensorflow.keras.applications.efficientnet import EfficientNetB0
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.layers import (
    Input,
    Flatten,
    Dense,
    Dropout,
    Permute,
    Reshape,
    GlobalAveragePooling2D,
    AveragePooling2D,
    BatchNormalization,
    Activation,
)
from tensorflow.keras.models import Model
import numpy as np
from imutils import paths
import matplotlib.pyplot as plt
from tensorflow.keras.optimizers import SGD, Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.utils import class_weight

MODEL_NAME = "resnet"
CASE_NAME = "rice_newdata"

if not os.path.isdir(
    os.path.join("model", CASE_NAME + "\\" + MODEL_NAME)
) or not os.path.isdir(os.path.join("saved_model", CASE_NAME + "\\" + MODEL_NAME)):
    os.makedirs(os.path.join("model", CASE_NAME + "\\" + MODEL_NAME))
    os.makedirs(os.path.join("saved_model", CASE_NAME + "\\" + MODEL_NAME))


def plot_training(H, N, plotPath):
    plt.style.use("ggplot")
    plt.figure()
    plt.plot(np.arange(0, N), H.history["loss"], label="train_loss")
    plt.plot(np.arange(0, N), H.history["val_loss"], label="val_loss")
    plt.plot(np.arange(0, N), H.history["accuracy"], label="train_acc")
    plt.plot(np.arange(0, N), H.history["val_accuracy"], label="val_acc")
    plt.title("Training Loss and Accuracy")
    plt.xlabel("Epoch #")
    plt.ylabel("Loss/Accuracy")
    plt.legend(loc="lower left")
    plt.savefig(plotPath)


trainPath = r"C:\Users\Quang\Downloads\RiceLeafs\train"
valPath = r"C:\Users\Quang\Downloads\RiceLeafs\validation"

totalTrain = len(list(paths.list_images(trainPath)))
totalVal = len(list(paths.list_images(valPath)))

trainAug = ImageDataGenerator(
    rotation_range=30,
    zoom_range=0.15,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.15,
    horizontal_flip=True,
    fill_mode="nearest",
)
valAug = ImageDataGenerator()

mean = np.array([123.68, 116.779, 103.939], dtype="float32")
# mean = np.array([0, 0, 0], dtype="float32")
trainAug.mean = mean
valAug.mean = mean

batchSize = 32

trainGen = trainAug.flow_from_directory(
    trainPath,
    class_mode="categorical",
    target_size=(224, 224),
    color_mode="rgb",
    shuffle=True,
    batch_size=batchSize,
)

label_map = trainGen.class_indices
print(label_map)

my_class_weights = class_weight.compute_class_weight(
    "balanced", np.unique(trainGen.classes), trainGen.classes
)

my_class_weights = {l: c for l, c in zip(np.unique(trainGen.classes), my_class_weights)}

print(my_class_weights)

valGen = valAug.flow_from_directory(
    valPath,
    class_mode="categorical",
    target_size=(224, 224),
    color_mode="rgb",
    shuffle=False,
    batch_size=batchSize,
)

baseModel = DenseNet121(
    weights="imagenet", include_top=False, input_tensor=Input(shape=(224, 224, 3))
)

# baseModel = ResNet50(weights="imagenet", include_top=False, input_tensor=Input(shape=(224, 224, 3)))

headModel = baseModel.output

feed_x = GlobalAveragePooling2D()(headModel)
feed_x = BatchNormalization()(feed_x)
feed_x = Dropout(0.5)(feed_x)
feed_x = Dense(1024, activation="relu")(feed_x)
feed_x = Dense(512, activation="relu")(feed_x)
feed_x = BatchNormalization()(feed_x)
feed_x = Dropout(0.5)(feed_x)

preds = Dense(4, activation="softmax")(feed_x)  # FC-layer

# headModel = baseModel.output
# # headModel = BatchNormalization(headModel)
# # headModel = Activation('relu')(headModel)
# headModel = AveragePooling2D((2, 2), padding='same')(headModel)
# headModel = Flatten(name="flatten")(headModel)
# headModel = Dense(512, activation="relu")(headModel)
# headModel = Dense(2, activation="softmax")(headModel)

model = Model(inputs=baseModel.input, outputs=preds)


# train only head
for layer in baseModel.layers:
    layer.trainable = False

model.summary()

# model.load_weights("model/falldown_best.h5")

print("[INFO] compiling model...")
opt = Adam()

model.compile(loss="categorical_crossentropy", optimizer=opt, metrics=["accuracy"])

checkpointer = ModelCheckpoint(
    monitor="val_accuracy",
    filepath=os.path.join(
        os.path.join("model", CASE_NAME + "\\" + MODEL_NAME), CASE_NAME + "_prebest.h5"
    ),
    verbose=1,
    save_best_only=True,
)

reduce_LR = ReduceLROnPlateau(
    monitor="val_accuracy", factor=0.5, patience=5, verbose=1, min_lr=1e-3
)
earlystop = EarlyStopping(monitor="accuracy", patience=10)
csv_logger = CSVLogger(
    "model/" + CASE_NAME + "\\" + MODEL_NAME + "_head.csv", append=True
)

print("[INFO] training head...")
H = model.fit(
    x=trainGen,
    steps_per_epoch=totalTrain // batchSize,
    validation_data=valGen,
    validation_steps=totalVal // batchSize,
    epochs=50,
    callbacks=[checkpointer, csv_logger, reduce_LR],
    class_weight=my_class_weights,
)

# plot_training(H, 50, "image/1.png")
print("[INFO] serializing network...")
model.save("model/" + CASE_NAME + "\\" + MODEL_NAME + "_pre", save_format="h5")
# model.save("saved_model/"+CASE_NAME+"\\"+MODEL_NAME)

trainGen.reset()
valGen.reset()
model.load_weights(
    os.path.join(
        os.path.join("model", CASE_NAME + "\\" + MODEL_NAME), CASE_NAME + "_prebest.h5"
    )
)
# train all
for layer in model.layers:
    layer.trainable = True

# for layer in model.layers:
#     print("{}: {}".format(layer, layer.trainable))

model.summary()

print("[INFO] re-compiling model...")
opt = Adam()
model.compile(loss="categorical_crossentropy", optimizer=opt, metrics=["accuracy"])

checkpointer = ModelCheckpoint(
    monitor="val_accuracy",
    # monitor="accuracy",
    filepath=os.path.join(
        os.path.join("model", CASE_NAME + "\\" + MODEL_NAME), CASE_NAME + "_best.h5"
    ),
    verbose=1,
    save_best_only=True,
)
csv_logger = CSVLogger("model/" + CASE_NAME + "\\" + MODEL_NAME + ".csv", append=True)

H = model.fit(
    x=trainGen,
    steps_per_epoch=totalTrain // batchSize,
    validation_data=valGen,
    validation_steps=totalVal // batchSize,
    epochs=30,
    callbacks=[checkpointer, csv_logger],
    class_weight=my_class_weights,
)

# plot_training(H, 5, "image/2.png")

print("[INFO] serializing network...")
model.save("model/" + CASE_NAME + "\\" + MODEL_NAME + "_end", save_format="h5")
# model.save("saved_model/"+CASE_NAME+"\\"+MODEL_NAME)
