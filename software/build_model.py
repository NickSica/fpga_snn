#!/usr/bin/python3

from tensorflow.keras.layers import Dense, Input, Conv1D, BatchNormalization, ReLU, GlobalAveragePooling1D
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import EarlyStopping
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
    model.add(Input((input_segment_length, 1)))
    model.add(Conv1D(filters=64, kernel_size=3, padding="same"))
    model.add(BatchNormalization())
    model.add(ReLU())
    model.add(GlobalAveragePooling1D())
    model.add(Dense(num_neurons, activation="relu"))
    model.add(Dense(2, activation="softmax"))
    model.compile(loss='sparse_categorical_crossentropy', metrics=['sparse_categorical_accuracy'])
    return model

def load_all_data(train_or_test):
    # Determine which designations are for testing and for training
    if train_or_test == "train":
        with open(trainRecordFile, newline='') as train_csv:
            records = [entry[0] for entry in list(csv.reader(train_csv))][1:]
    elif train_or_test == "test":
        with open(testRecordFile, newline='') as test_csv:
            records = [entry[0] for entry in list(csv.reader(test_csv))][1:]
    else:
        return
    # Load all data from records and convert to 60-second spike features
    all_data = []
    spike_sequences = []
    for record in records:
        if len(spike_sequences) > max_patients-1:
            break
        loaded_data = load_data(record)
        all_data.append(loaded_data)
        spike_sequences.append(spike_convert(loaded_data))
    # Collapse records
    all_sequences = []
    for sequence in spike_sequences:
        for spikes in sequence:
            all_sequences.append(spikes)
    # Make sure all annotations are corrected
    labels = []
    for edf in all_data:
        annotations = edf.annotations.description
        binarized_annotations = [[1] if anno == "A" else [0] for anno in annotations]
        for label in binarized_annotations:
            labels.append(label)
    # A bit of reformatting
    labels = np.array(labels)
    reformatted_spikes = np.asarray(all_sequences) .astype('float32')
    reformatted_spikes = reformatted_spikes.reshape(reformatted_spikes.shape[0], reformatted_spikes.shape[1], 1)
    return [all_data, reformatted_spikes, labels]
        
def load_data(data_name):
    raw_data = mne.io.read_raw_edf(os.path.join(dataDir, data_name+".edf"))
    annotations = mne.read_annotations(os.path.join(dataDir, data_name+".txt"))
    raw_data.set_annotations(annotations, emit_warning=False)
    return raw_data

def spike_convert(raw_edf):
    edf_data = raw_edf.get_data()[0]
    edf_max = max(edf_data)
    # Convert to spikes (1 when below threshold, 0 when above)
    converted_spikes = [value_for_under_thresh if value < spike_thresh*edf_max else value_for_over_thresh for value in edf_data]
    annotation_times = raw_edf.annotations.onset
    num_segments = len(annotation_times)
    data_times = raw_edf.times
    segmented_spikes = []
    this_segment = []
    counter = 0
    # Split up train into labeled/annotated segments
    for idx in range(len(edf_data)):
        if idx == 0:
            continue
        this_segment.append(converted_spikes[idx])
        if data_times[idx] >= annotation_times[counter+1]:
            segmented_spikes.append(this_segment)
            this_segment = []
            counter = counter + 1
        if counter + 1 >= num_segments:
            counter = idx
            break
    segmented_spikes.append(converted_spikes[counter:counter+input_segment_length])
    # One more pass through all segments to ensure padding
    for segment in segmented_spikes:
        while len(segment) < input_segment_length:
            segment.append(value_for_under_thresh)
        while len(segment) > input_segment_length:
            segment.pop()
    return segmented_spikes

if __name__ == "__main__":
    model = define_model()
    all_edf_train, data_train, train_labels = load_all_data("train")
    all_edf_test, data_test, test_labels = load_all_data("test")

    np.savez_compressed(os.path.join(dataDir, "x_test.npz"), data_train)
    np.savez_compressed(os.path.join(dataDir, "y_test.npz"), train_labels)

    print(data_train.shape)
    print(train_labels.shape)
    history = model.fit(data_train, train_labels, epochs=1, batch_size=64,
        shuffle=True, callbacks=[EarlyStopping(monitor='sparse_categorical_crossentropy', patience=3)])
    print(model.summary())

    if save_model:
        if not os.path.isdir(dataDir):
            os.mkdir(outputDir)
        model.save(os.path.join(dataDir, "model", "model.h5"), save_format='h5')
