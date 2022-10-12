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

    #@try_exept_wrapper
    def add(self, ad: AD):
        with self._connection.cursor() as cursor:
            add_ad = f"INSERT INTO `videocards` (`avito_id`, `vc_name`, `title`, `description`, `rating`, `comments_count`, `price`) VALUES " \
                     f"('{ad.avito_id}', '{ad.vc_name}', %(title)s, %(descrip)s, '{ad.rating}', '{ad.comments_count}', '{ad.price}')"
            cursor.execute(add_ad, {'title': ad.title, 'descrip': ad.description})

    @try_exept_wrapper
    def check_id(self, avito_id):
        with self._connection.cursor() as cursor:
            does_exists = f'SELECT * FROM `videocards` WHERE avito_id="{avito_id}"'
            cursor.execute(does_exists)
            return cursor.fetchall()

    def close_connection(self):
        self._connection.close()


def main():


    db = DataBase()
    db.connect()

    ad = AD(avito_id='i2481dsada14d171',
                title=r"'dsa",
                vc_name='rtx 3050',
                description=''' dsadq3kjmkcm `;;''""""''''``` ''',
                rating=21,
                comments_count=21,
                price=2000)
    db.add(ad)
    # db.add_price_column()
    # db.add_ad(rtx_3050)
    #db.add_vc("rtx 3070")
    db.close_connection()


if __name__ == "__main__":
    main()
