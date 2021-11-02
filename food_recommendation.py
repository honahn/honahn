#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings('ignore')

from sklearn.metrics.pairwise import cosine_similarity

food_df=pd.read_csv('food_df.csv', index_col=0)
menu_db=pd.read_excel('최종DB(라벨링,위경도포함).xlsx', index_col=0)



# 클래스 생성

class FoodInfo:
    def __init__(self, calorie, first_nut, second_nut):
        self.calorie = calorie
        self.first_nut = first_nut
        self.second_nut = second_nut
        
        self.sorted_food = food_df.loc[food_df['에너지(㎉)'] < self.calorie]
        
        # 선호하는 1순위 영양소(first_nut)와 2순위 영양소(second_nut)를 입력
        # 1: 탄수화물   2: 단백질   3: 지방
        if first_nut == 1:
            if second_nut == 2:
                self.sorted_food = self.sorted_food[(self.sorted_food['탄수화물(g)'] > self.sorted_food['단백질(g)'])
                                                    & (self.sorted_food['단백질(g)'] > self.sorted_food['지방(g)'])]
            elif second_nut == 3:
                self.sorted_food = self.sorted_food[(self.sorted_food['탄수화물(g)'] > self.sorted_food['지방(g)'])
                                                    & (self.sorted_food['지방(g)'] > self.sorted_food['단백질(g)'])]
        if first_nut == 2:
            if second_nut == 1:
                self.sorted_food = self.sorted_food[(self.sorted_food['단백질(g)'] > self.sorted_food['탄수화물(g)'])
                                                    & (self.sorted_food['탄수화물(g)'] > self.sorted_food['지방(g)'])]
            elif second_nut == 3:
                self.sorted_food = self.sorted_food[(self.sorted_food['단백질(g)'] > self.sorted_food['지방(g)'])
                                                    & (self.sorted_food['지방(g)'] > self.sorted_food['탄수화물(g)'])]
        if first_nut == 3:
            if second_nut == 1:
                self.sorted_food = self.sorted_food[(self.sorted_food['지방(g)'] > self.sorted_food['탄수화물(g)'])
                                                    & (self.sorted_food['탄수화물(g)'] > self.sorted_food['단백질(g)'])]
            elif second_nut == 2:
                self.sorted_food = self.sorted_food[(self.sorted_food['지방(g)'] > self.sorted_food['단백질(g)'])
                                                    & (self.sorted_food['단백질(g)'] > self.sorted_food['탄수화물(g)'])]                
    
    def get_info(self):
        return self.sorted_food
    
    def set_kwd(self, kwd):
        self.kwd = kwd
        
    def get_market(self):
        '''
        #1
        key word와 매칭되는 메뉴를 가진 음식점의 정보 제공
        화면에 보여줄 때 영양정보, cid는 제외한 '음식점 정보와 가게 메뉴'만 제공
        '''
        self.market = menu_db.loc[menu_db['정답']==self.kwd]
        return self.market.iloc[:, 1:9].drop(columns = 'cid')
    
    def get_similar_food(self):
        '''
        #2
        사용자가 선택한 음식과 유사한 음식의 영양 정보를 제공
        '영양 구성'이 비슷한 음식을 매칭
        '''
        # 칼로리로 필터링 된 음식들의 영양 정보만 피처벡터화 하여 코사인 유사도 계산
        cosine_sim = cosine_similarity(self.sorted_food.loc[:,['에너지(㎉)','탄수화물(g)','단백질(g)','지방(g)','나트륨(㎎)']])
        self.cosine_sim_df = pd.DataFrame(cosine_sim, index = self.sorted_food['식품명'], columns = self.sorted_food['식품명'])
                                     
        # 코사인 유사도 값(0~1 사이의 값)이 높은 순으로 정렬
        # 가장높은 1은 소비자가 처음 선택한 음식이므로 제외, 상위 10개의 음식명을 유사한 음식으로 판단, 리스트로 저장
        self.similar_menu = self.cosine_sim_df[self.kwd].sort_values(ascending = False)[1:11].index.tolist()
        
        self.similar_menu_info = pd.DataFrame()

        for i in range(len(self.sorted_food)):
            if self.sorted_food.iloc[i]['식품명'] in self.similar_menu:
                self.similar_menu_info = self.similar_menu_info.append(pd.DataFrame([self.sorted_food.iloc[i]]))
                                     
        return self.similar_menu_info
        


# 인스턴스 생성

sample=FoodInfo(200, 2, 1)
sample.get_info()

sample.set_kwd('닭곰탕')

sample.get_market()

sample.get_similar_food()

print(sample.similar_menu)
