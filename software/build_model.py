#!/usr/bin/python3
from tensorflow.keras.layers import Dense, Input, Conv1D, BatchNormalization, ReLU, GlobalAveragePooling1D
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.utils import to_categorical
from tensorflow.keras import optimizers
from scipy.signal import stft
import numpy as np
import os
import mne
import csv
np.random.seed(5)

save_model = True
plot_on = False
spike_thresh = 0.8
input_segment_length = 6000
num_neurons = 4
value_for_over_thresh = 1
value_for_under_thresh = 0
max_patients = 4
baseDir = os.getcwd()
dataDir = os.path.join(baseDir, "data")
outputDir = os.path.join(baseDir, "model")
testRecordFile = os.path.join(dataDir, "TestRecords.csv")
trainRecordFile = os.path.join(dataDir, "TrainRecords.csv")
event_id = {'A': 1,
            'N': 0}

def define_model():
    model = Sequential()
    model.add(Dense(num_neurons, activation="relu"))
    model.compile(loss='binary_crossentropy', optimizer="adam", metrics=['accuracy'])
    return model

def load_data(data_name):
    global raw_train, annot_test
    raw_train = mne.io.read_raw_edf(os.path.join(dataDir, data_name+".edf"))
    annot_test = mne.read_annotations(os.path.join(dataDir, data_name+".txt"))
    raw_train.set_annotations(annot_test, emit_warning=False)

def define_tests(data_name):
    global raw_test, annot_test
    raw_test = mne.io.read_raw_edf(os.path.join(dataDir, data_name+".edf"))
    annot_test = mne.read_annotations(os.path.join(dataDir, data_name+".txt"))
    annot_test.crop(annot_test[1]['onset'] - 30 * 60,
                    annot_test[-2]['onset'] + 30 * 60)
    raw_test.set_annotations(annot_test, emit_warning=False)

if __name__ == "__main__":
    model = define_model()
    load_data("a01")
    define_tests("a02")

    train_data = raw_train.get_data()
    test_data = raw_test.get_data()
    train_data = np.nan_to_num(train_data)
    test_data = np.nan_to_num(test_data)
    SxxTrain = np.ndarray(shape=(6063,489))
    _,_,SxxTrain[:] = stft(raw_train.get_data(), nperseg=12125)
    _,_,SxxTest = stft(raw_test.get_data(), nperseg=12100)

    y_test = np.array([[1] if anno == "A" else [0] for anno in annot_test.description])
    y_test = to_categorical(y_test, num_classes=4)

    SxxTrain.resize(2958939)
    sTest = SxxTest.reshape(1, 528, 6051)
    sTrain  = SxxTrain.reshape(1, 489, 6051)

    np.savez_compressed(os.path.join(dataDir, "x_norm.npz"), sTrain[0])
    np.savez_compressed(os.path.join(dataDir, "x_test.npz"), sTest[0])
    np.savez_compressed(os.path.join(dataDir, "y_test.npz"), y_test)

    model.fit(sTest[0], y_test, epochs=50, batch_size=32, shuffle=True)
    y_pred_nn = model.predict(sTest[0])
    label_train_pred = [pred.argmax() for pred in y_pred_nn]
    print(model.summary())

    if save_model:
        if not os.path.isdir(dataDir):
            os.mkdir(outputDir)
        model.save(os.path.join(dataDir, "model", "model.h5"), save_format='h5')
        model_json = model.to_json()
        with open(os.path.join(dataDir, "model", "model.json"), "w") as model_file:
            model_file.write(model_json)
