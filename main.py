from tensorflow import keras
import numpy as np
import tensorflow as tf


model_path = 'model/best_model_1.h5'
model = keras.models.load_model(model_path)


#def getPN(text):
#  return model.predict([text])

test_text = st.text_input('Movie title', 'Life of Brian')

st.write(result_string)
btn = st.button('결과 보기')
