import sqlite3
import os

EMPTY_COOKIES = {'PHPSESSID': 'empty',
                 'rr': 'empty',
                 'rr_add': 'empty',
                 'rr_f': 'empty',
                 'rr_id': 'empty'}


class Account:
    def __init__(self, login, password, user_agent, proxy):
        self.login = login
        self.password = password
        self.user_agent = user_agent
        self.proxy = proxy


class Cookies:
    def __init__(self, login, PHPSESSID, rr, rr_add, rr_f, rr_id):
        self.login = login
        self.PHPSESSID = PHPSESSID
        self.rr = rr
        self.rr_add = rr_add
        self.rr_f = rr_f
        self.rr_id = rr_id
        self.cookies = {
            'PHPSESSID': self.PHPSESSID,
            'rr': self.rr,
            'rr_add': self.rr_add,
            'rr_f': self.rr_f,
            'rr_id': self.rr_id
                        }


class Database:
    def __init__(self):

        path = os.path.join(os.getcwd(), 'db')
        os.makedirs(path, exist_ok=True)
        self.connection = sqlite3.connect(f'{path}/rr_info.db')
        self.cursor = self.connection.cursor()

        cookies_table_query = '''CREATE TABLE IF NOT EXISTS cookies (
            login TEXT UNIQUE,
            PHPSESSID TEXT,
            rr TEXT,
            rr_add TEXT,
            rr_f TEXT,
            rr_id TEXT
            );'''

        data_table_query = '''CREATE TABLE IF NOT EXISTS auth_data (
            login TEXT UNIQUE,
            password TEXT,
            user_agent TEXT,
            proxy TEXT
            );'''

        self.cursor.execute(cookies_table_query)
        self.cursor.execute(data_table_query)

    def find_info(self, login, cookies=True):
        """
        :param login: account login
        :param cookies: set True if you need find cookies, False if auth data
        :return:
        """
        # single database with tables cookies и auth_data
        if cookies:
            # finding data for auth (log/pass/user-agent/proxy or cookies)
            try:
                # find cookies for rr auth
                select_keys = '''PRAGMA table_info('cookies')'''
                select_values = f'''SELECT * FROM cookies WHERE login="{login}"'''

                keys = [x[1] for x in self.cursor.execute(select_keys).fetchall()][1:]
                values = list(self.cursor.execute(select_values).fetchall()[0])[1:]

                return dict(zip(keys, values))
            except IndexError:
                # if no login in table
                print(f'No account "{login}" in db cookies.')
                return False
            except TypeError:
                # idk
                print('Type????//2//22//2')
                return False
        else:
            try:
                select_keys = '''PRAGMA table_info('auth_data')'''
                select_values = f'''SELECT * FROM auth_data WHERE login="{login}"'''

                keys = [x[1] for x in self.cursor.execute(select_keys).fetchall()]
                values = list(self.cursor.execute(select_values).fetchall()[0])

                return dict(zip(keys, values))
            except Exception as ex:
                print(ex)
                return False

    def find_info_gpt(self, login: str, cookies: bool = True):
        table = 'cookies' if cookies else 'auth_data'
        keys_query = f"PRAGMA table_info('{table}')"
        values_query = f"SELECT * FROM {table} WHERE login=?"
        try:
            # keys = [x[1] for x in self.cursor.execute(keys_query).fetchall()][1:]
            values = list(self.cursor.execute(values_query, [login]).fetchall()[0])[1:]
            if cookies:
                return Cookies(login, *values)
            else:
                return Account(login, *values)
        except IndexError:
            print(f'No account "{login}" in db {table}.')
        except Exception as ex:
            print(ex)
        return False

    def insert_info(self, data, cookies=True):
        if cookies:
            key = []
            value = []
            for item in data.items():
                key.append(item[0])
                value.append(item[1])
            insert_query = f'''INSERT OR REPLACE INTO cookies
                            ({key[0]}, {key[1]}, {key[2]}, {key[3]}, {key[4]}, {key[5]})
                            VALUES(?, ?, ?, ?, ?, ?);
                            '''
            self.cursor.execute(insert_query, tuple(value))
            self.connection.commit()
        else:
            keys = []
            values = []
            for item in data.items():
                keys.append(item[0])
                values.append(item[1])
            insert_query = f'''INSERT OR REPLACE INTO auth_data
                            ({keys[0]}, {keys[1]}, {keys[2]}, {keys[3]})
                            VALUES(?, ?, ?, ?);'''
            self.cursor.execute(insert_query, tuple(values))
            self.connection.commit()

            if not self.find_info(login=data['login'], cookies=True):
                print('add empty cookies')
                init_cookies = EMPTY_COOKIES
                init_cookies['login'] = data['login']
                self.insert_info(init_cookies, cookies=True)

    def insert_info_gpt(self, data, cookies=True):
        keys = []
        values = []
        table = 'cookies' if cookies else 'auth_data'

        for item in data.items():
            keys.append(item[0])
            values.append(item[1])

        placeholders = ', '.join('?' * len(keys))
        columns = ', '.join(keys)

        insert_query = f'INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})'

        self.cursor.execute(insert_query, tuple(values))
        self.connection.commit()

        if not cookies and not self.find_info(login=data['login'], cookies=True):
            init_cookies = EMPTY_COOKIES.copy()
            init_cookies['login'] = data['login']
            self.insert_info(init_cookies, cookies=True)


if __name__ == '__main__':
    db = Database()
    a = db.find_info_gpt(login='meidonoraura@gmail.com', cookies=False)
