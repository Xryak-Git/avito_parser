from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import undetected_chromedriver as uc
from selenium import webdriver
from PIL import Image
import pytesseract
import pickle
import time
import re

import DataBase as DB

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class Data:
    VIDEOCARDS = "https://www.avito.ru/moskva/tovary_dlya_kompyutera/komplektuyuschie/videokarty-ASgBAgICAkTGB~pm7gmmZw?cd=1&q="
    AVITO = "https://www.avito.ru/"
    VC = ['rtx 3050', 'rx 6600', 'rtx 3070', 'rtx 3060']
    AD_CLASS_NAME = 'iva-item-list-rfgcH'
    PHONE_BUTTON = 'button-button-eBrUW'
    PHONE_IMAGE = "button-phone-image-LkzoU"
    TITLE = 'title-root-zZCwT'
    DESCRIPTION = 'iva-item-description-FDgK4'
    RATING = '//span[@class="desktop-1lslbsi"]'
    COMMENTS = 'desktop-1c71z48'
    PRICE = 'price-text-_YGDY'


class AD:
    def __init__(self, avito_id, vc_name, title, description, rating, comments_count, price):
        self.avito_id = avito_id
        self.vc_name = vc_name
        self.title = title
        self.description = description
        self.rating = rating
        self.comments_count = comments_count
        self.price = price


class AvitoParser:
    def __init__(self):
        self.driver = self._create_driver_with_options()
        self.db = DB.DataBase()
        self.db.connect()



    @staticmethod
    def _create_driver_with_options():
        options = webdriver.ChromeOptions()
        options.add_argument('--window-size=1400,1080')
        options.add_argument(r'--user-data-dir=C:\Users\igser\AppData\Local\Google\Chrome\User Data\Profile_3')
        driver = uc.Chrome(options=options)
        return driver

    def get_avito_site(self):
        self.driver.get(Data.AVITO)
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        self.driver.refresh()

    def parce_avito(self):
        for card in Data.VC:
            page = f'{Data.VIDEOCARDS}{card.replace(" ", "+")}'
            self.driver.get(page)
            ads = self.driver.find_elements(By.CLASS_NAME, Data.AD_CLASS_NAME)

            self._ad_sort(ads, card)

        self.db.close_connection()

    def _ad_sort(self, ads, card):
        for i, ad in enumerate(ads):
            record = self._get_all_info_from_ad(ad, card, i)
            if not (record is None):
                self.db.add(record)

    def _get_all_info_from_ad(self, ad, card, i):
        avito_id = ad.get_attribute('id')

        if self._check_if_already_got(avito_id):
            return None

        title = ad.find_element(By.CLASS_NAME, Data.TITLE).text
        print(title)
        vc_name = card
        description = ad.find_element(By.CLASS_NAME, Data.DESCRIPTION).text

        rating = self._get_rating(ad)
        comments_count = self._get_comments(ad)
        price = self._get_price(ad)

        ad = AD(avito_id=avito_id,
                vc_name=vc_name,
                title=title,
                description=description,
                rating=rating,
                comments_count=comments_count,
                price=price)

        return ad

    def _check_if_already_got(self, ad_id):
        does_exist = len(self.db.check_id(ad_id))
        if does_exist == 0:
            return False
        else:
            return True

    def _get_rating(self, ad):
        rating = 0

        try:
            pattern = r'\d,\d'
            rating = re.findall(pattern, ad.text)[-1]
            rating = rating.replace(',', '.')
            rating = float(rating)
        except Exception as ex:
            print(ex)

        return rating

    def _get_comments(self, ad):
        comments = 0
        try:
            comments = ad.find_element(By.CLASS_NAME, Data.COMMENTS).text.split()[0]
            comments = int(comments)
        except Exception as ex:
            print("\nКомменты не найдены\n")
        return comments

    def _get_price(self, ad):
        price = 0
        try:
            price = ad.find_element(By.CLASS_NAME, Data.PRICE).text
            if price == 'Цена не указана':
                return 0
            price = ''.join(filter(lambda x: x.isdigit(), price))
            price = int(price)
        except Exception as ex:
            print("\nЦена не найдена\n")
        return price


def main():

    parser = AvitoParser()

    #parser.get_avito_site()

    parser.parce_avito()



if __name__ == "__main__":
    main()

