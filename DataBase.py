from config import host, user, password, db_name
import pymysql.cursors
from datetime import date
from main import AD


def try_exept_wrapper(func):
    def inner(*arg, **kwargs):
        try:
            return func(*arg, **kwargs)
        except Exception as ex:
            print(ex)

    return inner


class DataBase:

    def __init__(self):
        self._connection: pymysql.connections.Connection
        self.price_today = date.today()

    @try_exept_wrapper
    def connect(self):
        self._connection = pymysql.connect(host=host,
                                           user=user,
                                           password=password,
                                           database=db_name,
                                           cursorclass=pymysql.cursors.DictCursor,
                                           autocommit=True)
        print("Succesfull connection!")

    @try_exept_wrapper
    def add_vc(self, naming):
        with self._connection.cursor() as cursor:
            add_videocard = f"INSERT INTO `videocards` (`id`, `name`) VALUES (NULL, '{naming}') "
            cursor.execute(add_videocard)

    @try_exept_wrapper
    def show_vn_namings(self):
        with self._connection.cursor() as cursor:
            show_naming = f"SELECT * FROM `videocards`"
            cursor.execute(show_naming)
            rows = cursor.fetchall()
            for row in rows:
                print(row)

    @try_exept_wrapper
    def _check_if_price_column_exists(self):
        with self._connection.cursor() as cursor:
            get_row = f"SHOW COLUMNS FROM `ads` LIKE '{self.price_today}'"
            cursor.execute(get_row)
            rows = cursor.fetchall()
            if rows:
                return True
            else:
                return False

    @try_exept_wrapper
    def add_price_column(self):
        if not(self._check_if_price_column_exists()):
            with self._connection.cursor() as cursor:
                create_row = f'ALTER TABLE `ads` ADD `{self.price_today}` INT(20) NULL DEFAULT NULL AFTER `last_update`'
                cursor.execute(create_row)

    #@try_exept_wrapper
    def add(self, ad: AD):
        with self._connection.cursor() as cursor:
            add_ad = f"INSERT INTO `ads` (`avito_id`, `vc_name`, `title`, `description`, `rating`, `comments_count`, `number`, `last_update` , `{self.price_today}`) VALUES " \
                     f"('{ad.avito_id}', '{ad.vc_name}', '{ad.title}', '{ad.description}', '{ad.rating}', '{ad.comments_count}', '{ad.number}', '{ad.last_update}' , '{ad.price}')"
            cursor.execute(add_ad)

    @try_exept_wrapper
    def check_id(self, avito_id):
        with self._connection.cursor() as cursor:
            does_exists = f'SELECT * FROM `ads` WHERE avito_id="{avito_id}"'
            cursor.execute(does_exists)
            return cursor.fetchall()

    @try_exept_wrapper
    def get_last_update(self, avito_id):
        with self._connection.cursor() as cursor:
            last_update = f'SELECT `last_update` FROM `ads` WHERE avito_id = "{avito_id}"'
            cursor.execute(last_update)
            ans = cursor.fetchall()[0]
            return ans['last_update']

    @try_exept_wrapper
    def update_price(self, avito_id, price):
        with self._connection.cursor() as cursor:
            update = f'UPDATE `ads` SET ' \
                     f'`last_update` = "{self.price_today}", ' \
                     f'`{self.price_today}` = "{price}" ' \
                     f'WHERE `ads`.`avito_id` = "{avito_id}"'
            cursor.execute(update)

    def insert_date(self, avito_id, date):
        with self._connection.cursor() as cursor:
            update = f'UPDATE `ads` SET `last_update` = "{date}" WHERE `ads`.`avito_id` = "{avito_id}"'
            cursor.execute(update)

    def close_connection(self):
        self._connection.close()


def main():


    db = DataBase()
    db.connect()

    ad = AD(avito_id='i248114d171',
                title='dsa',
                vc_name='rtx 3050',
                description='e2das',
                rating=21,
                comments_count=21,
                number='321312',
                last_update='2022-09-24',
                price=2000)
    db.add(ad)
    # db.add_price_column()
    # db.add_ad(rtx_3050)
    #db.add_vc("rtx 3070")
    db.close_connection()


if __name__ == "__main__":
    main()
