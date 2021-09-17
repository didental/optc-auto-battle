import time
from typing import List, Union
from appium import webdriver
from timeit import default_timer
from time import sleep
import cv2
import os
import numpy as np


DEVICE_NAME = 'R3CM707WG4N'
PACKAGE_NAME = 'com.namcobandaigames.spmoja010E'
ACTIVITY_NAME = '.kizakura'

desired_caps = {}

desired_caps['platformName'] = 'Android'
desired_caps['deviceName'] = DEVICE_NAME
desired_caps['appPackage'] = PACKAGE_NAME
desired_caps['appActivity'] = ACTIVITY_NAME
desired_caps['dontStopAppOnReset'] = True
desired_caps['noReset'] = True


driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
driver.update_settings({
    'imageMatchThreshold': 0.7
})

# directory = '%s/' % os.getcwd()
# file_name = 'screenshot.png'
# driver.save_screenshot(directory + file_name)


# img_rgb = cv2.imread('screenshot.png')
# template = cv2.imread('images/auto.png')
# w, h = template.shape[:-1]

# res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
# threshold = .8
# loc = np.where(res >= threshold)
# for pt in zip(*loc[::-1]):  # Switch collumns and rows
#     cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)

# cv2.imwrite('result.png', img_rgb)


retry_count = 300
count = 0
step = 0


ok_path = ['images/ok_2.png', 'images/ok_1.png']

def click_until_indisplayed(driver: webdriver.Remote, path: Union[List[str], str], timeout: int = 5):
    obj = []
    start_time = default_timer()
    while default_timer() - start_time < timeout:
        try:
            if isinstance(path, List):
                for p in path:
                    obj = driver.find_elements_by_image(p)
                    if obj:
                        path_clicked = p
                        break
            else:
                obj = driver.find_elements_by_image(path)
                path_clicked = path
            
            if obj:
                obj[0].click()
                print(f'object clicked: {path_clicked}')
                sleep(1)
                if not driver.find_elements_by_image(path_clicked):
                    print(f'object disappeared: {path_clicked}')
                    return True
        except:
            continue
    else:
        return False


def click_auto(driver: webdriver.Remote):
    print('자동 전투 버튼 확인')
    start_time = default_timer()
    while default_timer() - start_time < 30:
        if click_until_indisplayed(driver, 'images/auto.png', 2):
            sleep(1)
        if driver.find_elements_by_image('images/auto_check.png'):
            print('자동 전투 중 상태')
            return
        else:
            sleep(1)
        

def wait_until_battle_finish(driver: webdriver.Remote):
    start_time = default_timer()        
    battle_finished = False
    while default_timer() - start_time < 300:
        if click_until_indisplayed(driver, ok_path):
            print('전투 종료')
            start_time_inner = default_timer()
            while default_timer() - start_time_inner < 10:
                exp = driver.find_elements_by_image('images/finish_exp.png')
                if exp:
                    print('전투 종료 화면 출력')
                    battle_finished = True
                    break
            else:
                print("전투 종료 화면 출력 확인 실패")
        elif battle_finished:
            return
        elif driver.find_elements_by_image('images/finish_exp.png'):
            return
        else:
            click_until_indisplayed(driver, 'images/auto.png', 3)
            sleep(5)


def retry_battle(driver: webdriver.Remote):
    start_time = default_timer()
    while default_timer() - start_time < 60:
        if click_until_indisplayed(driver, 'images/finish_exp.png', 1):
            continue
        elif click_until_indisplayed(driver, 'images/retry.png', 1):
            print('전투 다시 도전')
            sleep(1)

            # 고기 부족 체크
            refill_stamina = driver.find_elements_by_image('images/yes.png')
            if refill_stamina:
                refill_stamina[0].click()
                if click_until_indisplayed(driver, 'images/ok.png'):
                    print('고기 충전 후 다시 도전하기 버튼 선택 완료')
                    return
            else:
                print('다시 도전하기 버튼 선택 완료')
                return
        elif click_until_indisplayed(driver, ok_path, 3):
            continue


while count < retry_count:
    battle_start_time = default_timer()
    # 자동전투 버튼 확인
    click_auto(driver)

    # 전투 종료 대기
    wait_until_battle_finish(driver)

    # 전투 종료 화면 확인
    retry_battle(driver)
    count += 1

    time_spend = default_timer() - battle_start_time
    print(f'전투 완료: {count} / 소요 시간: {int(time_spend / 60)}분 {int(time_spend % 60)}초')

driver.quit()