import numpy as np
import keras
from keras import layers

def feedForwardNN(inputShape, numClasses):
  model = keras.Sequential(
    [
        keras.Input(shape=inputShape),
        layers.Dense(64,activation='sigmoid'),
        layers.Dense(numClasses,activation='softmax'),
    ]
  )
  return model
