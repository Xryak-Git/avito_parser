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
    def __init__(self, avito_id, vc_name, title, description, rating, comments_count, number, last_update, price):
        self.avito_id = avito_id
        self.vc_name = vc_name
        self.title = title
        self.description = description
        self.rating = rating
        self.comments_count = comments_count
        self.number = number
        self.last_update = last_update
        self.price = price


class AvitoParser:
    def __init__(self):
        self.driver = self._create_driver_with_options()
        self.db = DB.DataBase()
        self.db.connect()
        self.db.add_price_column()
        self.today_date = self.db.price_today

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
            else:
                self._update_info_if_needed(ad, i)

    def _update_info_if_needed(self, ad, i):
        avito_id = ad.get_attribute('id')
        last_update = self.db.get_last_update(avito_id)
        if last_update != self.today_date:
            price = self._get_price(ad)
            self.db.update_price(avito_id=avito_id, price=price)

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
        number = self._get_phone_from(ad, i)
        price = self._get_price(ad)

        ad = AD(avito_id=avito_id,
                title=title,
                vc_name=vc_name,
                description=description,
                rating=rating,
                comments_count=comments_count,
                number=number,
                last_update=self.today_date,
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

    def _get_phone_from(self, ad, i):
        number = "Нет"
        try:
            self._open_phone_button(ad)
            number = self._get_photo_and_analise(ad, i)
        except Exception as ex:
            print("#" * 20 + "\nНет номера" + "\n" + "#" * 20)

        return number


    def _get_photo_and_analise(self, ad, i):
        with open(r'Phone_numbers/' + f'{i}.png', 'wb') as file:
            time.sleep(1)
            png = ad.find_element(By.CLASS_NAME, "button-phone-image-LkzoU").screenshot_as_png
            time.sleep(1)
            file.write(png)

        phone = pytesseract.image_to_string(Image.open(f'Phone_numbers/{i}.png'))
        return phone

    def _open_phone_button(self, ad):
        action = ActionChains(self.driver)
        action.move_to_element(ad).perform()

        phone_button = ad.find_element(By.CLASS_NAME, Data.PHONE_BUTTON)
        time.sleep(1)
        phone_button.click()
        time.sleep(2)


def main():

    parser = AvitoParser()

    #parser.get_avito_site()

    parser.parce_avito()



if __name__ == "__main__":
    main()

