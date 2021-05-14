import itertools
import pickle
import sys

from keras import optimizers
from keras.layers import Conv1D, MaxPooling1D, Flatten, Dense, Dropout
from keras.optimizers import SGD
from mne.time_frequency import psd_welch
from scipy.signal import medfilt, stft, spectrogram, welch
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer
from tqdm import tqdm
import numpy as np
import wfdb
import os
import pandas as pd
import mne
import matplotlib.pyplot as plt
import snntoolbox
from keras.models import Sequential
np.random.seed(5)
# define cnn model
def define_model():
    model = Sequential()
    model.add(Dense(2, activation='relu'))
    model.add(Dense(2, activation='tanh'))
    model.add(Dense(2, activation='softmax'))
    model.compile(loss="sparse_categorical_crossentropy", optimizer=optimizers.nadam(), metrics=['accuracy'])
    return model


baseDir = r"C:\Users\Drifter\Documents\TEST\Test"
recordFile = os.path.join(baseDir, "Records.csv")

raw_train = mne.io.read_raw_edf(r"C:\Users\Drifter\Documents\TEST\Test\a01.edf")
annot_train = mne.read_annotations(r"C:\Users\Drifter\Documents\TEST\Test\a01.txt")

raw_train.set_annotations(annot_train, emit_warning=False)

annotation_desc_2_event_id = {'A': 1,
                              'N': 0}

raw_train.set_annotations(annot_train, emit_warning=False)

events_train, _ = mne.events_from_annotations(
    raw_train, event_id=annotation_desc_2_event_id, chunk_duration=30.)

event_id = {'A': 1,'N': 0}

tmax = 30. - 1. / raw_train.info['sfreq']

epochs_train = mne.Epochs(raw=raw_train, events=events_train,
                          event_id=event_id, tmin=0., tmax=tmax, baseline=None)

raw_test = mne.io.read_raw_edf(r"C:\Users\Drifter\Documents\TEST\Test\a02.edf")
annot_test = mne.read_annotations(r"C:\Users\Drifter\Documents\TEST\Test\a02.txt")

annot_test.crop(annot_test[1]['onset'] - 30 * 60,
                annot_test[-2]['onset'] + 30 * 60)
raw_test.set_annotations(annot_test, emit_warning=False)
events_test, _ = mne.events_from_annotations(
    raw_test, event_id=annotation_desc_2_event_id, chunk_duration=30.)
epochs_test = mne.Epochs(raw=raw_test, events=events_test, event_id=event_id,
                         tmin=0., tmax=tmax, baseline=None)

model = define_model()

_,_,SxxTrain = stft(raw_train.get_data(),nperseg=12125)
_,_,SxxTest = stft(raw_test.get_data(),nperseg=12100)
# Train
y_train = np.array([[1] if anno == "A" else [0] for anno in annot_train.description])
y_test = np.array([[1] if anno == "A" else [0] for anno in annot_test.description])

sTest = SxxTest.reshape(1,528,6051)
sTrain = SxxTrain.reshape(1,489,6063)

model.fit(sTest[0], y_test,epochs=50, batch_size=32, shuffle=True)
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix
y_pred_nn = model.predict(sTest[0])
label_train_pred = [pred.argmax() for pred in y_pred_nn]
cm = confusion_matrix(y_test, label_train_pred)

plt.matshow(cm, cmap=plt.cm.gray)
plt.show()
















#1D convolution
#Short Time Fourier Transform or spectogram, frequency components


#or could use raw signals for RNN