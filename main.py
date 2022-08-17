from tensorflow import keras
import streamlit as st
import numpy as np
import pandas as pd
import tensorflow as tf
import re
import json
from urllib import request
import requests
import time
from keras.models import load_model
from tensorflow.keras.preprocessing.text import Tokenizer, tokenizer_from_json
from tensorflow.keras.preprocessing.sequence import pad_sequences
from konlpy.tag import Okt
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from haversine import haversine
from bs4 import BeautifulSoup



MAX_LEN = 30
model_path = 'model/food_review.h5'
model = load_model(model_path)
df = pd.read_csv('data/last_df.csv')
with open('model/tokenizer.json') as f:
    data = json.load(f)
    tokenizer = tokenizer_from_json(data)

okt = Okt()

stopwords = ['의','가','이','은','들','는','좀','잘','걍','과','도','를','으로','자','에','와','한','하다']

loc_button = Button(label="Get Location")
loc_button.js_on_event("button_click", CustomJS(code="""
    navigator.geolocation.getCurrentPosition(
        (loc) => {
            document.dispatchEvent(new CustomEvent("GET_LOCATION", {detail: {lat: loc.coords.latitude, lon: loc.coords.longitude}}))
        }
    )
    """))
result = streamlit_bokeh_events(
    loc_button,
    events="GET_LOCATION",
    key="get_location",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)



def is_positive_sentence(new_sentence):
    new_sentence = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣 ]','', new_sentence)
    new_sentence = okt.morphs(new_sentence, stem=True) # 토큰화
    new_sentence = [word for word in new_sentence if not word in stopwords] # 불용어 제거
    
    encoded = tokenizer.texts_to_sequences([new_sentence]) # 정수 인코딩
    
    pad_new = pad_sequences(encoded, maxlen = MAX_LEN) # 패딩
    score = float(model.predict(pad_new)) # 예측
    if(score > 0.5):
        return True
    else:
        return False

def is_positive_sentences(sentences):
    #test case: ["맛있다", "여기 괜찮네요", "이건 어때요"]
    
    for sentence in sentences:
        sentence = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣 ]','', sentence)
        sentence = okt.morphs(sentence, stem=True) # 토큰화
        sentence = [word for word in sentence if not word in stopwords]
    
    
    encoded = tokenizer.texts_to_sequences(sentences) # 정수 인코딩
    
    pad_new = pad_sequences(encoded, maxlen = MAX_LEN) # 패딩
    score = model.predict(pad_new) # 예측
    return score.round()
    
def blah(place_dict):
    #1. 현재 위치 -> 가장 가까운 5개의 업체 id
    #            -> id로 댓글 목록
    #2. 댓글 목록 -> 댓글의 긍, 부정을 알려주는 nparray
    #3. id -> (2번으로 댓글목록) -> (긍, 부정)
    #   -> list를 pos_list, neg_list 분리
    #   -> 긍정 퍼센테이지 계산
    for place in place_dict:
        st.write(place)
        
    

def get_near_placesummary(df):
    """
        현재 위도, 경도 기반 가장 가까운 5개 업체 정보 받아오는 함수
    """
    origin_lat, origin_lng = result.get("GET_LOCATION")['lat'], result.get("GET_LOCATION")['lon']
    lat_list = df["위도"].tolist()
    lng_list = df["경도"].tolist()
    ds_list = []
    for lat, lng in zip(lat_list, lng_list):
        ds_list.append(distance(origin_lat, origin_lng, lat, lng))
    df['거리'] = pd.DataFrame(ds_list)
    return df.sort_values(by=["거리"]).head(5) 
    
def distance(origin_lat, origin_lng, destination_lat, destination_lng):
    origin = (origin_lat, origin_lng)
    destination = (destination_lat,destination_lng)
    return haversine(origin, destination, unit = 'm')    
    
def make_payload(business_id, display=10, page=1):
    """
        업체 리뷰조회를 위해서 POST 요청시 함께 보낼 payload를 만들어 줌
        params:
            * business_id: 업체 고유번호
            * display: 한번에 불러올 댓글의 갯수 지정
            * page: page 번호
        return_value:
            * dict{"operationName", "query", "variables"}
    """
    if business_id == "--------":
        return {}
    operationName="getVisitorReviews"
    query = "query getVisitorReviews($input: VisitorReviewsInput) {\n  visitorReviews(input: $input) {\n    items {\n      id\n      rating\n      author {\n        id\n        nickname\n        from\n        imageUrl\n        objectId\n        url\n        review {\n          totalCount\n          imageCount\n          avgRating\n          __typename\n        }\n        theme {\n          totalCount\n          __typename\n        }\n        __typename\n      }\n      body\n      thumbnail\n      media {\n        type\n        thumbnail\n        class\n        __typename\n      }\n      tags\n      status\n      visitCount\n      viewCount\n      visited\n      created\n      reply {\n        editUrl\n        body\n        editedBy\n        created\n        replyTitle\n        __typename\n      }\n      originType\n      item {\n        name\n        code\n        options\n        __typename\n      }\n      language\n      highlightOffsets\n      apolloCacheId\n      translatedText\n      businessName\n      showBookingItemName\n      showBookingItemOptions\n      bookingItemName\n      bookingItemOptions\n      votedKeywords {\n        code\n        iconUrl\n        iconCode\n        displayName\n        __typename\n      }\n      userIdno\n      isFollowing\n      followerCount\n      followRequested\n      loginIdno\n      receiptInfoUrl\n      __typename\n    }\n    starDistribution {\n      score\n      count\n      __typename\n    }\n    hideProductSelectBox\n    total\n    showRecommendationSort\n    itemReviewStats {\n      score\n      count\n      itemId\n      starDistribution {\n        score\n        count\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
    variables = {
        "id": business_id,
        "input": {
            "businessId" : business_id,
            #"bookingBusinessId": "390725",
            #"businessType": "restaurant",
            #"cidList": ["220036", "220052", "220576", "221275"],
            "display": display,
            "getUserStats": True,
            "includeContent": True,
            "includeReceiptPhotos": True,
            "isPhotoUsed": False,
            "item": "0",
            "page": page
        }
    }
    return {"operationName": operationName, 
            "query": query,
            "variables": variables}
    
def get_comments(business_id, display=10 page=1):
    """
        업체 리뷰를 가져오는 함수
        params:
            * business_id: 업체 고유번호
            * display: 한번에 불러올 댓글의 갯수 지정
            * page: page 번호
        return_value:
            * list [각 댓글들]
    """
    comments = []
    
    
    try:
        if business_id == "--------":
            raise ValueError
        URL = "https://pcmap-api.place.naver.com/graphql"
        headers = {"Content-Type" : "application/json", 
               "sec-ch-ua":'"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"'}

        response = requests.post(URL, data=json.dumps(make_payload(business_id, display, page)), headers=headers)
        dictData = json.loads(response.text)
        for commentMeta in dictData['data']['visitorReviews']['items']:
            comments.append(commentMeta['body'])
    
    except:
        print('유효하지 않은 입력값')
    
    return comments

def get_comments_5_place(df, display=300, page=1):
    id_list = df["id"].tolist()
    comments_dict = {}
    for id in id_list:
        comments_dict[id] = get_comments(str(id), display, page)
        
    
    return comments_dict


#def blah():
#    origin_df = pd.read_csv('data/origin.csv')
#    summary_df = pd.read_csv('data/df_placesummary.csv')
#    df = pd.concat([origin_df, summary_df], axis=1)
#    return df
    

test_text = st.text_input('긍정/부정 문장 판독', '이거 ')

st.write("hello")


btn_clicked = st.button('결과 보기')
if btn_clicked:
  st.write(is_positive_sentence(test_text))
  st.write(test_text)

    
st.write(blah(get_comments_5_place(get_near_placesummary(df))))
    
    
    
#st.write(get_comments_nearest_5_place(get_near_placesummary(df)))

st.write(is_positive_sentences(get_comments("35395420", 300, 1)))




if result:
    if "GET_LOCATION" in result:
        st.write(result.get("GET_LOCATION"))
        

dis=distance(result.get("GET_LOCATION")['lat'], result.get("GET_LOCATION")['lon'], 37.563953,127.007410)    
st.write(dis)








for x, y in zip(df['위도'], df['경도']):
    dis=distance(result.get("GET_LOCATION")['lat'], result.get("GET_LOCATION")['lon'],x ,y)
    if dis<400000:
        pass
