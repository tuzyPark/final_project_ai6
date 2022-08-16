from tensorflow import keras
import streamlit as st
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from konlpy.tag import Okt


MAX_LEN = 30
model_path = 'model/best_model_1.h5'
model = keras.models.load_model(model_path)
okt = Okt()


def sentiment_predict(new_sentence):
    new_sentence = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣 ]','', new_sentence)
    new_sentence = okt.morphs(new_sentence, stem=True) # 토큰화
    new_sentence = [word for word in new_sentence if not word in stopwords] # 불용어 제거
    encoded = tokenizer.texts_to_sequences([new_sentence]) # 정수 인코딩
    pad_new = pad_sequences(encoded, maxlen = MAX_LEN) # 패딩
    score = float(loaded_model.predict(pad_new)) # 예측
    if(score > 0.5):
        print("긍정 리뷰입니다.\n".format(score * 100))
    else:
        print("부정 리뷰입니다.\n".format((1 - score) * 100))

def getPN(text):
  return model.predict([text])

test_text = st.text_input('Movie title', 'Life of Brian')

st.write("hello")


btn_clicked = st.button('결과 보기')
if btn_clicked:
  st.write("Clicked")
else:
  st.write("not Clicked")
