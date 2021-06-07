import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QTransform
from PyQt5.QtCore import *
import os
import glob
import shutil
import random
import pandas as pd
from win32api import GetSystemMetrics


main_form_class = uic.loadUiType("main.ui")[0]
photo_smartphone_form_class = uic.loadUiType("photo_smartphone.ui")[0]
photo_monitor_form_class = uic.loadUiType("photo_monitor.ui")[0]
photo_without_form_class = uic.loadUiType("photo_without_sur.ui")[0]
end_form_class = uic.loadUiType("end_widget.ui")[0]

# 총 설문 수
global total_sur
total_sur = 11

class mainWindow(QMainWindow, main_form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.start_test_btn.clicked.connect(self.start_test_btn_func)

    def start_test_btn_func(self):
        self.hide()
        global part_num
        part_num = self.input_part_num.toPlainText()

        if self.cond_radioButton1.isChecked():
            self.photo_monitor_Window = Photo_Smartphone_Window()
            self.photo_monitor_Window.exec()            
        elif self.cond_radioButton2.isChecked():
            self.photo_monitor_Window = Photo_Monitor_Window()
            self.photo_monitor_Window.exec()
        elif self.cond_radioButton3.isChecked():
            self.photoWithoutWindow = Photo_Withdout_Window()
            self.photoWithoutWindow.exec()
        self.show()

class Photo_Smartphone_Window(QtWidgets.QDialog, photo_smartphone_form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.showFullScreen()  # 전체화면으로 위젯 열기

        # 결과 폴더 만들기
        self.dir_path = os.path.join("./result/%s" % part_num)
        os.makedirs(self.dir_path, exist_ok=True)
        self.result_path = os.path.join(
            self.dir_path+"/%s_result.csv" % part_num)

       # 이미지 갯수 체크
        self.imgfiles = glob.glob(os.path.join('./img/Galaxy', '*.jpg'))
        print(len(self.imgfiles))

        # 이미지 순서 파일 경로
        self.image_order_path = os.path.join(
            self.dir_path+"/%s_order.csv" % part_num)
        # 이미지 순서 파일이 없으면 만들기
        if not os.path.exists(self.image_order_path):
            save_partifipant_img_order = []
            temp_order = list(range(1, len(self.imgfiles)+1))
            random.shuffle(temp_order)

            # 디바이스 순서 섞기
            for i in range(1, len(self.imgfiles)+1):
                temp_device = [1, 2]
                random.shuffle(temp_device)
                if temp_device[0] == 1:
                    save_partifipant_img_order.append(
                        {"img_order": i, "img_number": temp_order[i-1], "left": temp_device[0], "right": temp_device[1], "Mobile_A":"GG", "Mobile_B":"GI", "Mobile_C":"IG", "Mobile_D": "II"})
                if temp_device[0] == 2:
                    save_partifipant_img_order.append(
                        {"img_order": i, "img_number": temp_order[i-1], "left": temp_device[0], "right": temp_device[1], "Mobile_A":"IG", "Mobile_B":"II", "Mobile_C":"GG", "Mobile_D": "GI"})

            save_part_img_order_pd = pd.DataFrame(
                save_partifipant_img_order)
            save_part_img_order_pd.to_csv(
                self.image_order_path, index=False, mode="w", encoding="utf-8-sig")

        # 이미지 순서 파일 읽어오기
        self.image_order = pd.read_csv(
            self.image_order_path, engine='python', encoding='utf-8')

        # 이미지 이동 코드
        # A,C: S21 B,D:12pm
        dst_A = os.path.join(self.dir_path + "/A")
        os.makedirs(dst_A, exist_ok=True)
        dst_B = os.path.join(self.dir_path + "/B")
        os.makedirs(dst_B, exist_ok=True)
        dst_C = os.path.join(self.dir_path + "/C")
        os.makedirs(dst_C, exist_ok=True)
        dst_D = os.path.join(self.dir_path + "/D")
        os.makedirs(dst_D, exist_ok=True)

        #이미지 파일로 복사
        for i in range(len(self.image_order)):
            src_gal = os.path.join('./img/galaxy/%d.jpg'%self.image_order.loc[i][1])
            src_ipn = os.path.join('./img/iphone/%d.jpg'%self.image_order.loc[i][1])
            if self.image_order.loc[i][2] == 1:
                shutil.copy2(src_gal, dst_A+"/%d.jpg"%self.image_order.loc[i][0])
                shutil.copy2(src_gal, dst_B+"/%d.jpg"%self.image_order.loc[i][0])
                shutil.copy2(src_ipn, dst_C+"/%d.jpg"%self.image_order.loc[i][0])
                shutil.copy2(src_ipn, dst_D+"/%d.jpg"%self.image_order.loc[i][0])
            elif self.image_order.loc[i][2] == 2:
                shutil.copy2(src_ipn, dst_A+"/%d.jpg"%self.image_order.loc[i][0])
                shutil.copy2(src_ipn, dst_B+"/%d.jpg"%self.image_order.loc[i][0])
                shutil.copy2(src_gal, dst_C+"/%d.jpg"%self.image_order.loc[i][0])
                shutil.copy2(src_gal, dst_D+"/%d.jpg"%self.image_order.loc[i][0])  
        
        #시작
        self.i = 0
        self.change_img(1)  # 첫번째 사진 틀기
        
        # 이전 다음 버튼 누르면 함수실행 # 인자를 받으려면 람다함수 써야함
        self.nextBtn.clicked.connect(lambda: self.change_img(1))
        self.preBtn.clicked.connect(lambda: self.change_img(-1))

        # 슬라이더 값을 받아오고 업데이트 하기
        for i in range(total_sur):
            slider_sur_a = self.findChild(
                QSlider, "slider_sur_a_{}".format(i+1))
            slider_sur_a.valueChanged.connect(
                lambda: self.update_value(1))

            slider_sur_b = self.findChild(
                QSlider, "slider_sur_b_{}".format(i+1))
            slider_sur_b.valueChanged.connect(
                lambda: self.update_value(2))
            
            slider_sur_c = self.findChild(
                QSlider, "slider_sur_c_{}".format(i+1))
            slider_sur_c.valueChanged.connect(
                lambda: self.update_value(3))

            slider_sur_d = self.findChild(
                QSlider, "slider_sur_d_{}".format(i+1))
            slider_sur_d.valueChanged.connect(
                lambda: self.update_value(4))

    # 슬라이더 움직이면 라벨 값 업데이트하는 함수
    def update_value(self, col):
        if col == 1:
            for i in range(total_sur):
                a_value_sur = self.findChild(
                    QLabel, "a_value_sur_{}".format(i+1))
                slider_sur_a = self.findChild(
                    QSlider, "slider_sur_a_{}".format(i+1))
                slider_value = slider_sur_a.value()
                if i < 5:
                    a_value_sur.setText("%s점" % slider_value)
                elif i == 5:
                    if slider_value == 1:
                        a_value_sur.setText("매우 화려하다")
                    elif slider_value == 2:
                        a_value_sur.setText("화려하다")
                    elif slider_value == 3:
                        a_value_sur.setText("조금 화려하다")
                    elif slider_value == 4:
                        a_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        a_value_sur.setText("조금 평범하다")
                    elif slider_value == 6:
                        a_value_sur.setText("평범하다")
                    elif slider_value == 7:
                        a_value_sur.setText("매우 평범하다")
                elif i == 6:
                    if slider_value == 1:
                        a_value_sur.setText("매우 세련되었다")
                    elif slider_value == 2:
                        a_value_sur.setText("세련되었다")
                    elif slider_value == 3:
                        a_value_sur.setText("조금 세련되었다")
                    elif slider_value == 4:
                        a_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        a_value_sur.setText("조금 촌스럽다")
                    elif slider_value == 6:
                        a_value_sur.setText("촌스럽다")
                    elif slider_value == 7:
                        a_value_sur.setText("매우 촌스럽다")
                elif i == 7:
                    if slider_value == 1:
                        a_value_sur.setText("매우 자연스럽다")
                    elif slider_value == 2:
                        a_value_sur.setText("자연스럽다")
                    elif slider_value == 3:
                        a_value_sur.setText("조금 자연스럽다")
                    elif slider_value == 4:
                        a_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        a_value_sur.setText("조금 부자연스럽다")
                    elif slider_value == 6:
                        a_value_sur.setText("부자연스럽다")
                    elif slider_value == 7:
                        a_value_sur.setText("매우 부자연스럽다")   
                elif i == 8:
                    if slider_value == 1:
                        a_value_sur.setText("매우 밝다")
                    elif slider_value == 2:
                        a_value_sur.setText("밝다")
                    elif slider_value == 3:
                        a_value_sur.setText("조금 밝다")
                    elif slider_value == 4:
                        a_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        a_value_sur.setText("조금 어둡다")
                    elif slider_value == 6:
                        a_value_sur.setText("어둡다")
                    elif slider_value == 7:
                        a_value_sur.setText("매우 어둡다")      
                elif i == 9:
                    if slider_value == 1:
                        a_value_sur.setText("매우 따뜻하다")
                    elif slider_value == 2:
                        a_value_sur.setText("따뜻하다")
                    elif slider_value == 3:
                        a_value_sur.setText("조금 따뜻하다")
                    elif slider_value == 4:
                        a_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        a_value_sur.setText("조금 차갑다")
                    elif slider_value == 6:
                        a_value_sur.setText("차갑다")
                    elif slider_value == 7:
                        a_value_sur.setText("매우 차갑다")
                elif i == 10:
                    if slider_value == 1:
                        a_value_sur.setText("매우 푸르다")
                    elif slider_value == 2:
                        a_value_sur.setText("푸르다")
                    elif slider_value == 3:
                        a_value_sur.setText("조금 푸르다")
                    elif slider_value == 4:
                        a_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        a_value_sur.setText("조금 푸르지 않다")
                    elif slider_value == 6:
                        a_value_sur.setText("푸르지 않다")
                    elif slider_value == 7:
                        a_value_sur.setText("매우 푸르지 않다")
                else:
                    pass
   
        elif col == 2:
            for i in range(total_sur):
                b_value_sur = self.findChild(
                    QLabel, "b_value_sur_{}".format(i+1))
                slider_sur_b = self.findChild(
                    QSlider, "slider_sur_b_{}".format(i+1))
                slider_value = slider_sur_b.value()    
                if i < 5:
                    b_value_sur.setText("%s점" % slider_value)
                elif i == 5:
                    if slider_value == 1:
                        b_value_sur.setText("매우 화려하다")
                    elif slider_value == 2:
                        b_value_sur.setText("화려하다")
                    elif slider_value == 3:
                        b_value_sur.setText("조금 화려하다")
                    elif slider_value == 4:
                        b_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        b_value_sur.setText("조금 평범하다")
                    elif slider_value == 6:
                        b_value_sur.setText("평범하다")
                    elif slider_value == 7:
                        b_value_sur.setText("매우 평범하다")
                elif i == 6:
                    if slider_value == 1:
                        b_value_sur.setText("매우 세련되었다")
                    elif slider_value == 2:
                        b_value_sur.setText("세련되었다")
                    elif slider_value == 3:
                        b_value_sur.setText("조금 세련되었다")
                    elif slider_value == 4:
                        b_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        b_value_sur.setText("조금 촌스럽다")
                    elif slider_value == 6:
                        b_value_sur.setText("촌스럽다")
                    elif slider_value == 7:
                        b_value_sur.setText("매우 촌스럽다")
                elif i == 7:
                    if slider_value == 1:
                        b_value_sur.setText("매우 자연스럽다")
                    elif slider_value == 2:
                        b_value_sur.setText("자연스럽다")
                    elif slider_value == 3:
                        b_value_sur.setText("조금 자연스럽다")
                    elif slider_value == 4:
                        b_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        b_value_sur.setText("조금 부자연스럽다")
                    elif slider_value == 6:
                        b_value_sur.setText("부자연스럽다")
                    elif slider_value == 7:
                        b_value_sur.setText("매우 부자연스럽다")   
                elif i == 8:
                    if slider_value == 1:
                        b_value_sur.setText("매우 밝다")
                    elif slider_value == 2:
                        b_value_sur.setText("밝다")
                    elif slider_value == 3:
                        b_value_sur.setText("조금 밝다")
                    elif slider_value == 4:
                        b_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        b_value_sur.setText("조금 어둡다")
                    elif slider_value == 6:
                        b_value_sur.setText("어둡다")
                    elif slider_value == 7:
                        b_value_sur.setText("매우 어둡다")      
                elif i == 9:
                    if slider_value == 1:
                        b_value_sur.setText("매우 따뜻하다")
                    elif slider_value == 2:
                        b_value_sur.setText("따뜻하다")
                    elif slider_value == 3:
                        b_value_sur.setText("조금 따뜻하다")
                    elif slider_value == 4:
                        b_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        b_value_sur.setText("조금 차갑다")
                    elif slider_value == 6:
                        b_value_sur.setText("차갑다")
                    elif slider_value == 7:
                        b_value_sur.setText("매우 차갑다")
                elif i == 10:
                    if slider_value == 1:
                        b_value_sur.setText("매우 푸르다")
                    elif slider_value == 2:
                        b_value_sur.setText("푸르다")
                    elif slider_value == 3:
                        b_value_sur.setText("조금 푸르다")
                    elif slider_value == 4:
                        b_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        b_value_sur.setText("조금 푸르지 않다")
                    elif slider_value == 6:
                        b_value_sur.setText("푸르지 않다")
                    elif slider_value == 7:
                        b_value_sur.setText("매우 푸르지 않다")
                else:
                    pass
        elif col == 3:
            for i in range(total_sur):
                c_value_sur = self.findChild(
                    QLabel, "c_value_sur_{}".format(i+1))
                slider_sur_c = self.findChild(
                    QSlider, "slider_sur_c_{}".format(i+1))
                slider_value = slider_sur_c.value()
                if i < 5:
                    c_value_sur.setText("%s점" % slider_value)
                elif i == 5:
                    if slider_value == 1:
                        c_value_sur.setText("매우 화려하다")
                    elif slider_value == 2:
                        c_value_sur.setText("화려하다")
                    elif slider_value == 3:
                        c_value_sur.setText("조금 화려하다")
                    elif slider_value == 4:
                        c_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        c_value_sur.setText("조금 평범하다")
                    elif slider_value == 6:
                        c_value_sur.setText("평범하다")
                    elif slider_value == 7:
                        c_value_sur.setText("매우 평범하다")
                elif i == 6:
                    if slider_value == 1:
                        c_value_sur.setText("매우 세련되었다")
                    elif slider_value == 2:
                        c_value_sur.setText("세련되었다")
                    elif slider_value == 3:
                        c_value_sur.setText("조금 세련되었다")
                    elif slider_value == 4:
                        c_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        c_value_sur.setText("조금 촌스럽다")
                    elif slider_value == 6:
                        c_value_sur.setText("촌스럽다")
                    elif slider_value == 7:
                        c_value_sur.setText("매우 촌스럽다")
                elif i == 7:
                    if slider_value == 1:
                        c_value_sur.setText("매우 자연스럽다")
                    elif slider_value == 2:
                        c_value_sur.setText("자연스럽다")
                    elif slider_value == 3:
                        c_value_sur.setText("조금 자연스럽다")
                    elif slider_value == 4:
                        c_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        c_value_sur.setText("조금 부자연스럽다")
                    elif slider_value == 6:
                        c_value_sur.setText("부자연스럽다")
                    elif slider_value == 7:
                        c_value_sur.setText("매우 부자연스럽다")   
                elif i == 8:
                    if slider_value == 1:
                        c_value_sur.setText("매우 밝다")
                    elif slider_value == 2:
                        c_value_sur.setText("밝다")
                    elif slider_value == 3:
                        c_value_sur.setText("조금 밝다")
                    elif slider_value == 4:
                        c_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        c_value_sur.setText("조금 어둡다")
                    elif slider_value == 6:
                        c_value_sur.setText("어둡다")
                    elif slider_value == 7:
                        c_value_sur.setText("매우 어둡다")      
                elif i == 9:
                    if slider_value == 1:
                        c_value_sur.setText("매우 따뜻하다")
                    elif slider_value == 2:
                        c_value_sur.setText("따뜻하다")
                    elif slider_value == 3:
                        c_value_sur.setText("조금 따뜻하다")
                    elif slider_value == 4:
                        c_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        c_value_sur.setText("조금 차갑다")
                    elif slider_value == 6:
                        c_value_sur.setText("차갑다")
                    elif slider_value == 7:
                        c_value_sur.setText("매우 차갑다")
                elif i == 10:
                    if slider_value == 1:
                        c_value_sur.setText("매우 푸르다")
                    elif slider_value == 2:
                        c_value_sur.setText("푸르다")
                    elif slider_value == 3:
                        c_value_sur.setText("조금 푸르다")
                    elif slider_value == 4:
                        c_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        c_value_sur.setText("조금 푸르지 않다")
                    elif slider_value == 6:
                        c_value_sur.setText("푸르지 않다")
                    elif slider_value == 7:
                        c_value_sur.setText("매우 푸르지 않다")
                else:
                    pass

        elif col == 4:
            for i in range(total_sur):
                d_value_sur = self.findChild(
                    QLabel, "d_value_sur_{}".format(i+1))
                slider_sur_d = self.findChild(
                    QSlider, "slider_sur_d_{}".format(i+1))
                slider_value = slider_sur_d.value()
                if i < 5:
                    d_value_sur.setText("%s점" % slider_value)
                elif i == 5:
                    if slider_value == 1:
                        d_value_sur.setText("매우 화려하다")
                    elif slider_value == 2:
                        d_value_sur.setText("화려하다")
                    elif slider_value == 3:
                        d_value_sur.setText("조금 화려하다")
                    elif slider_value == 4:
                        d_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        d_value_sur.setText("조금 평범하다")
                    elif slider_value == 6:
                        d_value_sur.setText("평범하다")
                    elif slider_value == 7:
                        d_value_sur.setText("매우 평범하다")
                elif i == 6:
                    if slider_value == 1:
                        d_value_sur.setText("매우 세련되었다")
                    elif slider_value == 2:
                        d_value_sur.setText("세련되었다")
                    elif slider_value == 3:
                        d_value_sur.setText("조금 세련되었다")
                    elif slider_value == 4:
                        d_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        d_value_sur.setText("조금 촌스럽다")
                    elif slider_value == 6:
                        d_value_sur.setText("촌스럽다")
                    elif slider_value == 7:
                        d_value_sur.setText("매우 촌스럽다")
                elif i == 7:
                    if slider_value == 1:
                        d_value_sur.setText("매우 자연스럽다")
                    elif slider_value == 2:
                        d_value_sur.setText("자연스럽다")
                    elif slider_value == 3:
                        d_value_sur.setText("조금 자연스럽다")
                    elif slider_value == 4:
                        d_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        d_value_sur.setText("조금 부자연스럽다")
                    elif slider_value == 6:
                        d_value_sur.setText("부자연스럽다")
                    elif slider_value == 7:
                        d_value_sur.setText("매우 부자연스럽다")   
                elif i == 8:
                    if slider_value == 1:
                        d_value_sur.setText("매우 밝다")
                    elif slider_value == 2:
                        d_value_sur.setText("밝다")
                    elif slider_value == 3:
                        d_value_sur.setText("조금 밝다")
                    elif slider_value == 4:
                        d_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        d_value_sur.setText("조금 어둡다")
                    elif slider_value == 6:
                        d_value_sur.setText("어둡다")
                    elif slider_value == 7:
                        d_value_sur.setText("매우 어둡다")      
                elif i == 9:
                    if slider_value == 1:
                        d_value_sur.setText("매우 따뜻하다")
                    elif slider_value == 2:
                        d_value_sur.setText("따뜻하다")
                    elif slider_value == 3:
                        d_value_sur.setText("조금 따뜻하다")
                    elif slider_value == 4:
                        d_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        d_value_sur.setText("조금 차갑다")
                    elif slider_value == 6:
                        d_value_sur.setText("차갑다")
                    elif slider_value == 7:
                        d_value_sur.setText("매우 차갑다")
                elif i == 10:
                    if slider_value == 1:
                        d_value_sur.setText("매우 푸르다")
                    elif slider_value == 2:
                        d_value_sur.setText("푸르다")
                    elif slider_value == 3:
                        d_value_sur.setText("조금 푸르다")
                    elif slider_value == 4:
                        d_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        d_value_sur.setText("조금 푸르지 않다")
                    elif slider_value == 6:
                        d_value_sur.setText("푸르지 않다")
                    elif slider_value == 7:
                        d_value_sur.setText("매우 푸르지 않다")
                else:
                    pass
                
    # 데이터 저장하는 함수
    def save_data(self):
        # ABCD 사진 설문값 저장용 리스트
        survey_result = []

        # abcd 사진 저장용 리스트
        temp_dic_a = {}
        temp_dic_b = {}
        temp_dic_c = {}
        temp_dic_d = {}

        #abcd 기기별 데이터 기록
        temp_dic_a['p_number'] = part_num
        temp_dic_b['p_number'] = part_num
        temp_dic_c['p_number'] = part_num
        temp_dic_d['p_number'] = part_num

        temp_dic_a['img_order_num'] = self.i
        temp_dic_b['img_order_num'] = self.i
        temp_dic_c['img_order_num'] = self.i
        temp_dic_d['img_order_num'] = self.i

        temp_dic_a['img_num'] = self.image_order.loc[self.i-1][1]
        temp_dic_b['img_num'] = self.image_order.loc[self.i-1][1]
        temp_dic_c['img_num'] = self.image_order.loc[self.i-1][1]
        temp_dic_d['img_num'] = self.image_order.loc[self.i-1][1]

        temp_dic_a['img_num'] = self.image_order.loc[self.i-1][1]
        temp_dic_b['img_num'] = self.image_order.loc[self.i-1][1]
        temp_dic_c['img_num'] = self.image_order.loc[self.i-1][1]
        temp_dic_d['img_num'] = self.image_order.loc[self.i-1][1]        
        
        # image_order에 left가 1이면 GGII 2이면 IIGG
        if self.image_order.loc[self.i-1][2] == 1:
            temp_dic_a['src_device'] = 'G'
            temp_dic_b['src_device'] = 'G'
            temp_dic_c['src_device'] = 'I'
            temp_dic_d['src_device'] = 'I'
        elif self.image_order.loc[self.i-1][2] == 2:
            temp_dic_a['src_device'] = 'I'
            temp_dic_b['src_device'] = 'I'
            temp_dic_c['src_device'] = 'G'
            temp_dic_d['src_device'] = 'G'

        # 재생 디바이스는 GIGI 고정
        temp_dic_a['dis_device'] = 'G'
        temp_dic_b['dis_device'] = 'I'
        temp_dic_c['dis_device'] = 'G'
        temp_dic_d['dis_device'] = 'I'
        

        # 설문+번호 열에 슬라이더 값 저장
        for l in range(total_sur):
            param_name = "sur_%d" % (l+1)
            slider_sur_a = self.findChild(
                QSlider, "slider_sur_a_{}".format(l+1))
            slider_sur_b = self.findChild(
                QSlider, "slider_sur_b_{}".format(l+1))            
            slider_sur_c = self.findChild(
                QSlider, "slider_sur_c_{}".format(l+1))
            slider_sur_d = self.findChild(
                QSlider, "slider_sur_d_{}".format(l+1))
            try:
                temp_dic_a[param_name] = int(slider_sur_a.value())
            except:
                temp_dic_a[param_name] = None

            try:
                temp_dic_b[param_name] = int(slider_sur_b.value())
            except:
                temp_dic_b[param_name] = None

            try:
                temp_dic_c[param_name] = int(slider_sur_c.value())
            except:
                temp_dic_c[param_name] = None

            try:
                temp_dic_d[param_name] = int(slider_sur_d.value())
            except:
                temp_dic_d[param_name] = None


        # 하나로 리스트 합치기
        survey_result.append(temp_dic_a)
        survey_result.append(temp_dic_b)
        survey_result.append(temp_dic_c)
        survey_result.append(temp_dic_d)


        # 세이브 부분, 기존에 파일 없으면 바로생성
        if not os.path.exists(self.result_path):
            survey_result_pd = pd.DataFrame(survey_result)
            survey_result_pd.to_csv(
                self.result_path, index=False, mode="w", encoding='utf-8')
        # 기존파일이 있으면 중복확인해서 새 데이터로 기록
        else:
            temp_pd = pd.DataFrame(survey_result)
            previous_data = pd.read_csv(
                self.result_path, engine='python', encoding='utf-8')
            temp2_pd = pd.concat([temp_pd, previous_data]
                                 )  # 기존 값과 새로운 값 pd 합치기
            survey_result_pd = temp2_pd.drop_duplicates(
                ['img_num', 'src_device', 'dis_device'], keep='first')  # pd 중복 확인해서 제거하는 코드 first는 위에 있는 자료 남기고 삭제
            survey_result_pd.to_csv(
                self.result_path, index=False, mode="w", encoding='utf-8')

    # 이전 데이터 체크
    def prev_data_check(self):
        # 결과 데이터가 있는지 확인
        if os.path.exists(self.result_path):
            result_data = pd.read_csv(
                self.result_path, engine='python', encoding='utf-8')
            # ABCD 데이터 검색
            if self.image_order.loc[self.i-1][2] == 1:
                previous_data_a = result_data[(result_data['img_num'] == self.image_order.loc[self.i-1][1]) & (
                    result_data['src_device'] == 'G') & (result_data['dis_device'] == 'G')]
                previous_data_b = result_data[(result_data['img_num'] == self.image_order.loc[self.i-1][1]) & (
                    result_data['src_device'] == 'G') & (result_data['dis_device'] == 'I')]
                previous_data_c = result_data[(result_data['img_num'] == self.image_order.loc[self.i-1][1]) & (
                    result_data['src_device'] == 'I') & (result_data['dis_device'] == 'G')]
                previous_data_d = result_data[(result_data['img_num'] == self.image_order.loc[self.i-1][1]) & (
                    result_data['src_device'] == 'I') & (result_data['dis_device'] == 'I')]
            elif self.image_order.loc[self.i-1][2] == 2:
                previous_data_a = result_data[(result_data['img_num'] == self.image_order.loc[self.i-1][1]) & (
                    result_data['src_device'] == 'I') & (result_data['dis_device'] == 'G')]
                previous_data_b = result_data[(result_data['img_num'] == self.image_order.loc[self.i-1][1]) & (
                    result_data['src_device'] == 'I') & (result_data['dis_device'] == 'I')]
                previous_data_c = result_data[(result_data['img_num'] == self.image_order.loc[self.i-1][1]) & (
                    result_data['src_device'] == 'G') & (result_data['dis_device'] == 'G')]
                previous_data_d = result_data[(result_data['img_num'] == self.image_order.loc[self.i-1][1]) & (
                    result_data['src_device'] == 'G') & (result_data['dis_device'] == 'I')]

            print(previous_data_a, previous_data_b, previous_data_c, previous_data_d)

            # 설문마다 데이터 입력 (문항 이름 정하는 곳이 여기니 변경하고 싶으면 여기서 변경하면 됨)
            # 설문문항마다 열 이름 다르게 하고 싶을때
            # sur_title = ["설문명1", "설문명2", ----]
            # for i in range(0, len(sur_title)):
            # param_name = sur_title[i]
            # 아래 두줄을 빼고 위에 세줄을 넣으면 설문명마다 열이름 다르게 가능
            for i in range(0, total_sur):
                param_name = "sur_{}".format(i+1)
                previous_sur_a = list(previous_data_a[param_name])
                previous_sur_b = list(previous_data_b[param_name])
                previous_sur_c = list(previous_data_c[param_name])
                previous_sur_d = list(previous_data_d[param_name])

                # print(previous_sur_a, previous_sur_b)
                slider_sur_a = self.findChild(
                    QSlider, "slider_sur_a_{}".format(i+1))
                slider_sur_b = self.findChild(
                    QSlider, "slider_sur_b_{}".format(i+1))
                slider_sur_c = self.findChild(
                    QSlider, "slider_sur_c_{}".format(i+1))
                slider_sur_d = self.findChild(
                    QSlider, "slider_sur_d_{}".format(i+1))

                # 값이 있으면 넣고 없으면 0으로 세팅하는 코드
                try:
                    slider_sur_a.setValue(int(previous_sur_a[0]))
                except:
                    if i<5:
                        slider_sur_a.setValue(0)
                    else:
                        slider_sur_a.setValue(4)
                try:
                    slider_sur_b.setValue(int(previous_sur_b[0]))
                except:
                    if i<5:
                        slider_sur_b.setValue(0)
                    else:
                        slider_sur_b.setValue(4)
                try:
                    slider_sur_c.setValue(int(previous_sur_c[0]))
                except:
                    if i<5:
                        slider_sur_c.setValue(0)
                    else:
                        slider_sur_c.setValue(4)
                try:
                    slider_sur_d.setValue(int(previous_sur_d[0]))
                except:
                    if i<5:
                        slider_sur_d.setValue(0)
                    else:
                        slider_sur_d.setValue(4)           

        # 슬라이더 라벨값 업데이트
        self.update_value(1)
        self.update_value(2)
        self.update_value(3)
        self.update_value(4)

    # 다음이나 이전 버튼 누를시 사진 교체하는 함수
    def change_img(self, count):
        # 처음사진이면 이전사진 없게
        if self.i == 1:
            if count == -1:
                pass
            else:
                self.save_data()
                self.i = self.i + count
        # 마지막 사진이면 이후 사진없이 종료
        elif self.i == len(self.imgfiles):
            self.save_data()
            if count == 1:
                self.end_widget_call()
            else:
                self.i = self.i + count
        elif self.i == 0:
            self.i = self.i + count
        else:
            self.save_data()
            self.i = self.i + count
        # 그림 이미지 객체생성
        qPximapVar_a = QPixmap()
        qPximapVar_b = QPixmap()

        # 객체 이미지 불러오기(순서 맞춰서 좌우 바꿔줌)
        if self.image_order.loc[self.i-1][2] == 1:
            qPximapVar_a.load(os.path.join("./img/galaxy/%d.jpg" %
                              self.image_order.loc[self.i-1][1]))
            qPximapVar_b.load(os.path.join("./img/iphone/%d.jpg" %
                              self.image_order.loc[self.i-1][1]))
        else:
            qPximapVar_a.load(os.path.join("./img/iphone/%d.jpg" %
                              self.image_order.loc[self.i-1][1]))
            qPximapVar_b.load(os.path.join("./img/galaxy/%d.jpg" %
                              self.image_order.loc[self.i-1][1]))

        # 이미지 크기 조절
        qPximapVar_a = qPximapVar_a.scaledToWidth(1000)
        qPximapVar_b = qPximapVar_b.scaledToWidth(1000)

        # 이미지 회전
        img_transform = QTransform()
        img_transform.rotate(90)
        qPximapVar_a = qPximapVar_a.transformed(img_transform)
        qPximapVar_b = qPximapVar_b.transformed(img_transform)

        # 이미지 객체를 라벨에 넣기
        self.image_1.setPixmap(qPximapVar_a)
        self.image_2.setPixmap(qPximapVar_b)
        self.image_number.setText("%d"%self.i+" 번째 사진 ("+ "%d"%self.i + " / %d)"% len(self.imgfiles))

        # # 이전 데이터 확인 및 업데이트
        self.prev_data_check()


    #마지막 사진 이후 종료 위젯 실행 함수
    def end_widget_call(self):
        self.close()
        self.endWindow = EndWindow()
        self.endWindow.exec()


class Photo_Monitor_Window(QtWidgets.QDialog, photo_monitor_form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.test_frame.setAlignment(Qt.AlignCenter)
        self.photo_frame.setAlignment(Qt.AlignCenter)
        self.showFullScreen()  # 전체화면으로 위젯 열기

        # 결과 폴더 만들기
        self.dir_path = os.path.join("./result/%s" % part_num)
        os.makedirs(self.dir_path, exist_ok=True)
        self.result_path = os.path.join(
            self.dir_path+"/%s_result.csv" % part_num)

        # 이미지 갯수 체크
        self.imgfiles = glob.glob(os.path.join('./img/Galaxy', '*.jpg'))
        print(len(self.imgfiles))

        # 이미지 순서 파일 경로
        self.image_order_path = os.path.join(
            self.dir_path+"/%s_order.csv" % part_num)
        # 이미지 순서 파일이 없으면 만들기
        if not os.path.exists(self.image_order_path):
            save_partifipant_img_order = []
            temp_order = list(range(1, len(self.imgfiles)+1))
            random.shuffle(temp_order)

            # 디바이스 순서 섞기
            for i in range(1, len(self.imgfiles)+1):
                temp_device = [1, 2]
                random.shuffle(temp_device)
                if temp_device[0] == 1:
                    save_partifipant_img_order.append(
                        {"img_order": i, "img_number": temp_order[i-1], "left": temp_device[0], "right": temp_device[1], "Mobile_A":"GG", "Mobile_B":"GI", "Mobile_C":"IG", "Mobile_D": "II"})
                if temp_device[0] == 2:
                    save_partifipant_img_order.append(
                        {"img_order": i, "img_number": temp_order[i-1], "left": temp_device[0], "right": temp_device[1], "Mobile_A":"IG", "Mobile_B":"II", "Mobile_C":"GG", "Mobile_D": "GI"})

            save_part_img_order_pd = pd.DataFrame(
                save_partifipant_img_order)
            save_part_img_order_pd.to_csv(
                self.image_order_path, index=False, mode="w", encoding="utf-8-sig")

        # 이미지 순서 파일 읽어오기
        self.image_order = pd.read_csv(
            self.image_order_path, engine='python', encoding='utf-8')

        # 이미지 이동 코드
        # A,C: S21 B,D:12pm
        dst_A = os.path.join(self.dir_path + "/A")
        os.makedirs(dst_A, exist_ok=True)
        dst_B = os.path.join(self.dir_path + "/B")
        os.makedirs(dst_B, exist_ok=True)
        dst_C = os.path.join(self.dir_path + "/C")
        os.makedirs(dst_C, exist_ok=True)
        dst_D = os.path.join(self.dir_path + "/D")
        os.makedirs(dst_D, exist_ok=True)

        #이미지 파일로 복사
        for i in range(len(self.image_order)):
            src_gal = os.path.join('./img/galaxy/%d.jpg'%self.image_order.loc[i][1])
            src_ipn = os.path.join('./img/iphone/%d.jpg'%self.image_order.loc[i][1])
            if self.image_order.loc[i][2] == 1:
                shutil.copy2(src_gal, dst_A+"/%d.jpg"%self.image_order.loc[i][0])
                shutil.copy2(src_gal, dst_B+"/%d.jpg"%self.image_order.loc[i][0])
                shutil.copy2(src_ipn, dst_C+"/%d.jpg"%self.image_order.loc[i][0])
                shutil.copy2(src_ipn, dst_D+"/%d.jpg"%self.image_order.loc[i][0])
            elif self.image_order.loc[i][2] == 2:
                shutil.copy2(src_ipn, dst_A+"/%d.jpg"%self.image_order.loc[i][0])
                shutil.copy2(src_ipn, dst_B+"/%d.jpg"%self.image_order.loc[i][0])
                shutil.copy2(src_gal, dst_C+"/%d.jpg"%self.image_order.loc[i][0])
                shutil.copy2(src_gal, dst_D+"/%d.jpg"%self.image_order.loc[i][0])  
        
        #시작
        self.i = 0
        self.change_img(1)  # 첫번째 사진 틀기

        # 이전 다음 버튼 누르면 함수실행 # 인자를 받으려면 람다함수 써야함
        self.nextBtn.clicked.connect(lambda: self.change_img(1))
        self.preBtn.clicked.connect(lambda: self.change_img(-1))

        # 슬라이더 값을 받아오고 업데이트 하기
        for i in range(total_sur):
            slider_sur_a = self.findChild(
                QSlider, "slider_sur_a_{}".format(i+1))
            slider_sur_a.valueChanged.connect(
                lambda: self.update_value(1))

            slider_sur_b = self.findChild(
                QSlider, "slider_sur_b_{}".format(i+1))
            slider_sur_b.valueChanged.connect(
                lambda: self.update_value(2))

    # 슬라이더 움직이면 라벨 값 업데이트하는 함수
    def update_value(self, col):
        if col == 1:
            for i in range(total_sur):
                a_value_sur = self.findChild(
                    QLabel, "a_value_sur_{}".format(i+1))
                slider_sur_a = self.findChild(
                    QSlider, "slider_sur_a_{}".format(i+1))
                slider_value = slider_sur_a.value()
                if i < 5:
                    a_value_sur.setText("%s점" % slider_value)
                elif i == 5:
                    if slider_value == 1:
                        a_value_sur.setText("매우 화려하다")
                    elif slider_value == 2:
                        a_value_sur.setText("화려하다")
                    elif slider_value == 3:
                        a_value_sur.setText("조금 화려하다")
                    elif slider_value == 4:
                        a_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        a_value_sur.setText("조금 평범하다")
                    elif slider_value == 6:
                        a_value_sur.setText("평범하다")
                    elif slider_value == 7:
                        a_value_sur.setText("매우 평범하다")
                elif i == 6:
                    if slider_value == 1:
                        a_value_sur.setText("매우 세련되었다")
                    elif slider_value == 2:
                        a_value_sur.setText("세련되었다")
                    elif slider_value == 3:
                        a_value_sur.setText("조금 세련되었다")
                    elif slider_value == 4:
                        a_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        a_value_sur.setText("조금 촌스럽다")
                    elif slider_value == 6:
                        a_value_sur.setText("촌스럽다")
                    elif slider_value == 7:
                        a_value_sur.setText("매우 촌스럽다")
                elif i == 7:
                    if slider_value == 1:
                        a_value_sur.setText("매우 자연스럽다")
                    elif slider_value == 2:
                        a_value_sur.setText("자연스럽다")
                    elif slider_value == 3:
                        a_value_sur.setText("조금 자연스럽다")
                    elif slider_value == 4:
                        a_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        a_value_sur.setText("조금 부자연스럽다")
                    elif slider_value == 6:
                        a_value_sur.setText("부자연스럽다")
                    elif slider_value == 7:
                        a_value_sur.setText("매우 부자연스럽다")   
                elif i == 8:
                    if slider_value == 1:
                        a_value_sur.setText("매우 밝다")
                    elif slider_value == 2:
                        a_value_sur.setText("밝다")
                    elif slider_value == 3:
                        a_value_sur.setText("조금 밝다")
                    elif slider_value == 4:
                        a_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        a_value_sur.setText("조금 어둡다")
                    elif slider_value == 6:
                        a_value_sur.setText("어둡다")
                    elif slider_value == 7:
                        a_value_sur.setText("매우 어둡다")      
                elif i == 9:
                    if slider_value == 1:
                        a_value_sur.setText("매우 따뜻하다")
                    elif slider_value == 2:
                        a_value_sur.setText("따뜻하다")
                    elif slider_value == 3:
                        a_value_sur.setText("조금 따뜻하다")
                    elif slider_value == 4:
                        a_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        a_value_sur.setText("조금 차갑다")
                    elif slider_value == 6:
                        a_value_sur.setText("차갑다")
                    elif slider_value == 7:
                        a_value_sur.setText("매우 차갑다")
                elif i == 10:
                    if slider_value == 1:
                        a_value_sur.setText("매우 푸르다")
                    elif slider_value == 2:
                        a_value_sur.setText("푸르다")
                    elif slider_value == 3:
                        a_value_sur.setText("조금 푸르다")
                    elif slider_value == 4:
                        a_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        a_value_sur.setText("조금 푸르지 않다")
                    elif slider_value == 6:
                        a_value_sur.setText("푸르지 않다")
                    elif slider_value == 7:
                        a_value_sur.setText("매우 푸르지 않다")
                else:
                    pass
   

        elif col == 2:
            for i in range(total_sur):
                b_value_sur = self.findChild(
                    QLabel, "b_value_sur_{}".format(i+1))
                slider_sur_b = self.findChild(
                    QSlider, "slider_sur_b_{}".format(i+1))
                slider_value = slider_sur_b.value()    
                if i < 5:
                    b_value_sur.setText("%s점" % slider_value)
                elif i == 5:
                    if slider_value == 1:
                        b_value_sur.setText("매우 화려하다")
                    elif slider_value == 2:
                        b_value_sur.setText("화려하다")
                    elif slider_value == 3:
                        b_value_sur.setText("조금 화려하다")
                    elif slider_value == 4:
                        b_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        b_value_sur.setText("조금 평범하다")
                    elif slider_value == 6:
                        b_value_sur.setText("평범하다")
                    elif slider_value == 7:
                        b_value_sur.setText("매우 평범하다")
                elif i == 6:
                    if slider_value == 1:
                        b_value_sur.setText("매우 세련되었다")
                    elif slider_value == 2:
                        b_value_sur.setText("세련되었다")
                    elif slider_value == 3:
                        b_value_sur.setText("조금 세련되었다")
                    elif slider_value == 4:
                        b_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        b_value_sur.setText("조금 촌스럽다")
                    elif slider_value == 6:
                        b_value_sur.setText("촌스럽다")
                    elif slider_value == 7:
                        b_value_sur.setText("매우 촌스럽다")
                elif i == 7:
                    if slider_value == 1:
                        b_value_sur.setText("매우 자연스럽다")
                    elif slider_value == 2:
                        b_value_sur.setText("자연스럽다")
                    elif slider_value == 3:
                        b_value_sur.setText("조금 자연스럽다")
                    elif slider_value == 4:
                        b_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        b_value_sur.setText("조금 부자연스럽다")
                    elif slider_value == 6:
                        b_value_sur.setText("부자연스럽다")
                    elif slider_value == 7:
                        b_value_sur.setText("매우 부자연스럽다")   
                elif i == 8:
                    if slider_value == 1:
                        b_value_sur.setText("매우 밝다")
                    elif slider_value == 2:
                        b_value_sur.setText("밝다")
                    elif slider_value == 3:
                        b_value_sur.setText("조금 밝다")
                    elif slider_value == 4:
                        b_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        b_value_sur.setText("조금 어둡다")
                    elif slider_value == 6:
                        b_value_sur.setText("어둡다")
                    elif slider_value == 7:
                        b_value_sur.setText("매우 어둡다")      
                elif i == 9:
                    if slider_value == 1:
                        b_value_sur.setText("매우 따뜻하다")
                    elif slider_value == 2:
                        b_value_sur.setText("따뜻하다")
                    elif slider_value == 3:
                        b_value_sur.setText("조금 따뜻하다")
                    elif slider_value == 4:
                        b_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        b_value_sur.setText("조금 차갑다")
                    elif slider_value == 6:
                        b_value_sur.setText("차갑다")
                    elif slider_value == 7:
                        b_value_sur.setText("매우 차갑다")
                elif i == 10:
                    if slider_value == 1:
                        b_value_sur.setText("매우 푸르다")
                    elif slider_value == 2:
                        b_value_sur.setText("푸르다")
                    elif slider_value == 3:
                        b_value_sur.setText("조금 푸르다")
                    elif slider_value == 4:
                        b_value_sur.setText("보통이다")
                    elif slider_value == 5:
                        b_value_sur.setText("조금 푸르지 않다")
                    elif slider_value == 6:
                        b_value_sur.setText("푸르지 않다")
                    elif slider_value == 7:
                        b_value_sur.setText("매우 푸르지 않다")
                else:
                    pass

    # 다음이나 이전 버튼 누를시 사진 교체하는 함수
    def change_img(self, count):
        # 처음사진이면 이전사진 없게
        if self.i == 1:
            if count == -1:
                pass
            else:
                self.save_data()
                self.i = self.i + count
        # 마지막 사진이면 이후 사진없이 종료
        elif self.i == len(self.imgfiles):
            self.save_data()
            if count == 1:
                self.end_widget_call()
            else:
                self.i = self.i + count
        elif self.i == 0:
            self.i = self.i + count
        else:
            self.save_data()
            self.i = self.i + count
        # 그림 이미지 객체생성
        qPximapVar_a = QPixmap()
        qPximapVar_b = QPixmap()

        # 객체 이미지 불러오기(순서 맞춰서 좌우 바꿔줌)
        if self.image_order.loc[self.i-1][2] == 1:
            qPximapVar_a.load(os.path.join("./img/galaxy/%d.jpg" %
                              self.image_order.loc[self.i-1][1]))
            qPximapVar_b.load(os.path.join("./img/iphone/%d.jpg" %
                              self.image_order.loc[self.i-1][1]))
        else:
            qPximapVar_a.load(os.path.join("./img/iphone/%d.jpg" %
                              self.image_order.loc[self.i-1][1]))
            qPximapVar_b.load(os.path.join("./img/galaxy/%d.jpg" %
                              self.image_order.loc[self.i-1][1]))

        # 이미지 크기 조절
        qPximapVar_a = qPximapVar_a.scaledToWidth(GetSystemMetrics(1)-200)
        qPximapVar_b = qPximapVar_b.scaledToWidth(GetSystemMetrics(1)-200)

        # 이미지 회전
        img_transform = QTransform()
        img_transform.rotate(90)
        qPximapVar_a = qPximapVar_a.transformed(img_transform)
        qPximapVar_b = qPximapVar_b.transformed(img_transform)

        # 이미지 객체를 라벨에 넣기
        self.image_a.setPixmap(qPximapVar_a)
        self.image_b.setPixmap(qPximapVar_b)

        # 이전 데이터 확인 및 업데이트
        self.prev_data_check()

    # 데이터 저장하는 함수
    def save_data(self):
        # 좌우 사진 설문값 저장용 리스트
        survey_result = []

        # 좌 사진 저장용 리스트
        temp_dic1 = {}
        temp_dic2 = {}

        temp_dic1['p_number'] = part_num
        temp_dic2['p_number'] = part_num

        temp_dic1['img_order_num'] = self.i
        temp_dic2['img_order_num'] = self.i
        # loc는 pd 줄 번호로 검색하고 0부터 시작
        temp_dic1['img_num'] = self.image_order.loc[self.i-1][1]
        temp_dic2['img_num'] = self.image_order.loc[self.i-1][1]

        if self.image_order.loc[self.i-1][2] == 1:
            temp_dic1['src_device'] = "G"
            temp_dic2['src_device'] = "I"
        elif self.image_order.loc[self.i-1][2] == 2:
            temp_dic1['src_device'] = "I"
            temp_dic2['src_device'] = "G"            

        temp_dic1['dis_device'] = "M"
        temp_dic2['dis_device'] = "M"

        # 설문+번호 열에 슬라이더 값 저장
        for l in range(total_sur):
            param_name = "sur_%d" % (l+1)
            slider_sur_a = self.findChild(
                QSlider, "slider_sur_a_{}".format(l+1))
            slider_sur_b = self.findChild(
                QSlider, "slider_sur_b_{}".format(l+1))

            try:
                temp_dic1[param_name] = int(slider_sur_a.value())
            except:
                temp_dic1[param_name] = None
            try:
                temp_dic2[param_name] = int(slider_sur_b.value())
            except:
                temp_dic2[param_name] = None

        # 하나로 리스트 합치기
        survey_result.append(temp_dic1)
        survey_result.append(temp_dic2)

        # 세이브 부분, 기존에 파일 없으면 바로생성
        if not os.path.exists(self.result_path):
            survey_result_pd = pd.DataFrame(survey_result)
            survey_result_pd.to_csv(
                self.result_path, index=False, mode="w", encoding='utf-8')
        # 기존파일이 있으면 중복확인해서 새 데이터로 기록
        else:
            temp_pd = pd.DataFrame(survey_result)
            previous_data = pd.read_csv(
                self.result_path, engine='python', encoding='utf-8')
            temp2_pd = pd.concat([temp_pd, previous_data]
                                 )  # 기존 값과 새로운 값 pd 합치기
            survey_result_pd = temp2_pd.drop_duplicates(
                ['img_num', 'src_device', 'dis_device'], keep='first')  # pd 중복 확인해서 제거하는 코드 first는 위에 있는 자료 남기고 삭제
            survey_result_pd.to_csv(
                self.result_path, index=False, mode="w", encoding='utf-8')

    # 이전 데이터 체크
    def prev_data_check(self):
        # 결과 데이터가 있는지 확인
        if os.path.exists(self.result_path):
            result_data = pd.read_csv(
                self.result_path, engine='python', encoding='utf-8')
            if self.image_order.loc[self.i-1][2] == 1:
                previous_data1 = result_data[(result_data['img_num'] == self.image_order.loc[self.i-1][1]) & (
                    result_data['src_device'] == 'G') & (result_data['dis_device'] == 'M')]
                previous_data2 = result_data[(result_data['img_num'] == self.image_order.loc[self.i-1][1]) & (
                    result_data['src_device'] == 'I') & (result_data['dis_device'] == 'M')]
            elif self.image_order.loc[self.i-1][2] == 2:
                previous_data1 = result_data[(result_data['img_num'] == self.image_order.loc[self.i-1][1]) & (
                    result_data['src_device'] == 'G') & (result_data['dis_device'] == 'M')]
                previous_data2 = result_data[(result_data['img_num'] == self.image_order.loc[self.i-1][1]) & (
                    result_data['src_device'] == 'I') & (result_data['dis_device'] == 'M')] 
            print(previous_data1, previous_data2)

            # 설문마다 데이터 입력 (문항 이름 정하는 곳이 여기니 변경하고 싶으면 여기서 변경하면 됨)
            # 설문문항마다 열 이름 다르게 하고 싶을때
            # sur_title = ["설문명1", "설문명2", ----]
            # for i in range(0, len(sur_title)):
            # param_name = sur_title[i]
            # 아래 두줄을 빼고 위에 세줄을 넣으면 설문명마다 열이름 다르게 가능
            for i in range(0, total_sur):
                param_name = "sur_{}".format(i+1)
                previous_sur_a = list(previous_data1[param_name])
                previous_sur_b = list(previous_data2[param_name])
                # print(previous_sur_a, previous_sur_b)
                slider_sur_a = self.findChild(
                    QSlider, "slider_sur_a_{}".format(i+1))
                slider_sur_b = self.findChild(
                    QSlider, "slider_sur_b_{}".format(i+1))

                # 값이 있으면 넣고 없으면 0으로 세팅하는 코드
                try:
                    slider_sur_a.setValue(int(previous_sur_a[0]))
                except:
                    if i<5:
                        slider_sur_a.setValue(0)
                    else:
                        slider_sur_a.setValue(4)
                try:
                    slider_sur_b.setValue(int(previous_sur_b[0]))
                except:
                    if i<5:
                        slider_sur_b.setValue(0)
                    else:
                        slider_sur_b.setValue(4)


        # 슬라이더 라벨값 업데이트
        self.update_value(1)
        self.update_value(2)

    def end_widget_call(self):
        self.close()
        self.endWindow = EndWindow()
        self.endWindow.exec()


class Photo_Withdout_Window(QtWidgets.QDialog, photo_without_form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.test_frame.setAlignment(Qt.AlignCenter)
        self.photo_frame.setAlignment(Qt.AlignCenter)
        self.showFullScreen()  # 전체화면으로 위젯 열기

        # 결과 폴더 만들기
        self.dir_path = os.path.join("./result/%s" % part_num)
        os.makedirs(self.dir_path, exist_ok=True)
        self.result_path = os.path.join(
            self.dir_path+"/%s_result.csv" % part_num)

        # 이미지 갯수 체크
        self.imgfiles = glob.glob(os.path.join('./img/Galaxy', '*.jpg'))
        print(len(self.imgfiles))

        # 이미지 순서 파일 경로
        self.image_order_path = os.path.join(
            self.dir_path+"/%s_order.csv" % part_num)

        # 이미지 순서 파일이 없으면 만들기
        if not os.path.exists(self.image_order_path):
            save_partifipant_img_order = []
            temp_order = list(range(1, len(self.imgfiles)+1))
            random.shuffle(temp_order)

            # 디바이스 순서 섞기
            for i in temp_order:
                temp_device = [1, 2]
                random.shuffle(temp_device)
                save_partifipant_img_order.append(
                    {"img_number": i, "left": temp_device[0], "right": temp_device[1]})

            save_part_img_order_pd = pd.DataFrame(
                save_partifipant_img_order)
            save_part_img_order_pd.to_csv(
                self.image_order_path, index=False, mode="w", encoding="utf-8-sig")

        # 이미지 순서 파일 읽어오기
        self.image_order = pd.read_csv(
            self.image_order_path, engine='python', encoding='utf-8')

        self.i = 0
        self.change_img(1)  # 첫번째 사진 틀기

        # 이전 다음 버튼 누르면 함수실행 # 인자를 받으려면 람다함수 써야함
        self.nextBtn.clicked.connect(lambda: self.change_img(1))
        self.preBtn.clicked.connect(lambda: self.change_img(-1))

    # 다음이나 이전 버튼 누를시 사진 교체하는 함수

    def change_img(self, count):
        # 처음사진이면 이전사진 없게
        if self.i == 1:
            if count == -1:
                pass
            else:
                self.i = self.i + count
        # 마지막 사진이면 이후 사진없이 종료
        elif self.i == len(self.imgfiles):
            if count == 1:
                self.end_widget_call()
            else:
                self.i = self.i + count
        elif self.i == 0:
            self.i = self.i + count
        else:
            self.i = self.i + count
        # 그림 이미지 객체생성
        qPximapVar_a = QPixmap()
        qPximapVar_b = QPixmap()

        # 객체 이미지 불러오기(순서 맞춰서 좌우 바꿔줌)
        if self.image_order.loc[self.i-1][2] == 1:
            qPximapVar_a.load(os.path.join("./img/galaxy/%d.jpg" %
                              self.image_order.loc[self.i-1][1]))
            qPximapVar_b.load(os.path.join("./img/iphone/%d.jpg" %
                              self.image_order.loc[self.i-1][1]))
        else:
            qPximapVar_a.load(os.path.join("./img/iphone/%d.jpg" %
                              self.image_order.loc[self.i-1][1]))
            qPximapVar_b.load(os.path.join("./img/galaxy/%d.jpg" %
                              self.image_order.loc[self.i-1][1]))

        # 이미지 크기 조절
        qPximapVar_a = qPximapVar_a.scaledToWidth(GetSystemMetrics(1)-100)
        qPximapVar_b = qPximapVar_b.scaledToWidth(GetSystemMetrics(1)-100)

        # 이미지 회전
        img_transform = QTransform()
        img_transform.rotate(90)
        qPximapVar_a = qPximapVar_a.transformed(img_transform)
        qPximapVar_b = qPximapVar_b.transformed(img_transform)

        # 이미지 객체를 라벨에 넣기
        self.image_a.setPixmap(qPximapVar_a)
        self.image_b.setPixmap(qPximapVar_b)

    def end_widget_call(self):
        self.close()
        self.endWindow = EndWindow()
        self.endWindow.exec()


# 실험 종료 위젯
class EndWindow(QtWidgets.QDialog, end_form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.center_frame.setAlignment(Qt.AlignCenter)
        self.showFullScreen()  # 전체화면으로 위젯 열기


if __name__ == "__main__":
    # QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    # WindowClass의 인스턴스 생성
    myWindow = mainWindow()

    # 프로그램 화면을 보여주는 코드
    myWindow.show()

    # 프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
