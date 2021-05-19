#!/usr/bin/python3

from tensorflow.keras.utils import to_categorical
from keras import optimizers
from keras.layers import Dense
from keras.models import Sequential
from scipy.signal import stft
from sklearn.metrics import confusion_matrix
import numpy as np
import os
import mne
import matplotlib.pyplot as plt
np.random.seed(5)

save_model = True
plot_on = False
baseDir = os.getcwd()
dataDir = os.path.join(baseDir, "data")
outputDir = os.path.join(baseDir, "model")
recordFile = os.path.join(dataDir, "Records.csv")
event_id = {'A': 1,
            'N': 0}

# define cnn model
def define_model():
    model = Sequential()
    model.add(Dense(2, activation='relu'))
    model.add(Dense(2, activation='tanh'))
    model.add(Dense(2, activation='softmax'))
    model.compile(loss="categorical_crossentropy", optimizer=optimizers.Nadam(), metrics=['accuracy'])
    return model

def load_data():
    global raw_train, annot_train
    raw_train = mne.io.read_raw_edf(os.path.join(dataDir, "a01.edf"))
    annot_train = mne.read_annotations(os.path.join(dataDir, "a01.txt"))
    raw_train.set_annotations(annot_train, emit_warning=False)

def define_tests():
    global raw_test, annot_test
    raw_test = mne.io.read_raw_edf(os.path.join(dataDir, "a02.edf"))
    annot_test = mne.read_annotations(os.path.join(dataDir, "a02.txt"))

    annot_test.crop(annot_test[1]['onset'] - 30 * 60,
                annot_test[-2]['onset'] + 30 * 60)
    raw_test.set_annotations(annot_test, emit_warning=False)

if __name__ == "__main__":
    define_model()
    load_data()
    define_tests()

    model = define_model()
    _,_,SxxTrain = stft(raw_train.get_data(),nperseg=12125)
    _,_,SxxTest = stft(raw_test.get_data(),nperseg=12100)
    # Train
    y_test = np.array([[1] if anno == "A" else [0] for anno in annot_test.description])
    y_test = to_categorical(y_test)

    sTest = SxxTest.reshape(1,528,6051)

    # Same test variables for conversion
    np.savez_compressed(os.path.join(dataDir, "x_test.npz"), sTest[0])
    np.savez_compressed(os.path.join(dataDir, "y_test.npz"), y_test)

    model.fit(sTest[0], y_test,epochs=50, batch_size=32, shuffle=True)
    y_pred_nn = model.predict(sTest[0])
    label_train_pred = [pred.argmax() for pred in y_pred_nn]

    if plot_on:
        cm = confusion_matrix(y_test, label_train_pred)
        plt.matshow(cm, cmap=plt.cm.gray)
        plt.show()

    if save_model:
        if not os.path.isdir(dataDir):
            os.mkdir(outputDir)
        model.save(os.path.join(dataDir, "model", "model.h5"), save_format='h5')
