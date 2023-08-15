# import cloudscraper
# import functools
import user_agents
import requests
import datetime
import random
import math
import time
import re

from db import Database
from utils import Perks, Storage

"""
нужно переработать базу данных, в данный момент она сделана крайне криво и имеет лишние методы
добавить cloudscraper если cloudflare начинает блокировать подключение, актуально для сервера, с локалки всё ок
"""

LANGUAGE_DICT = {
    'be': {'profile': 'Профіль', 'expired': 'мінае', 'penalty': 'км, урон:', 'level': 'Узровень',
           'strength': 'Моц', 'education': 'Веды', 'endurance': 'Трываласць'},
    'ru': {'profile': 'Профиль', 'expired': 'истекает', 'penalty': 'км, урон:', 'level': 'Уровень',
           'strength': 'Сила', 'education': 'Знания', 'endurance': 'Выносливость'},
    'en': {'profile': 'Profile', 'expired': 'expires', 'penalty': 'km, damage:', 'level': 'Level',
           'strength': 'Strength', 'education': 'Education', 'endurance': 'Endurance'}
}


class Req:
    def __init__(self, login, timedelay=None):
        self.login = login
        self.timedelay = timedelay or random.randint(1, 3)
        self.account_info = Database().find_info_gpt(self.login, cookies=False)
        self.session = self.make_session()

    def set_headers(self, params=None):
        headers = {
            'User-Agent': self.account_info.user_agent,
            'Sec-Ch-Ua-Platform': str(user_agents.parse(self.account_info.user_agent).os.family),
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ja-RU,ja;q=0.9,ru-RU;q=0.8,ru;q=0.7,en-US;q=0.6,en;q=0.5',  # refactor
            # наличие этих двух заголовков при сборе сессии не позволяет использовать сохранённые куки и
            # вызывает cloudflare
            # 'Host': 'rivalregions.com',
            # 'Referer': 'https://rivalregions.com/',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
        }
        if params:
            headers.update(
                {
                    'Content-Length': str(
                        len(bytes(str(params.replace(' ', '').replace("'", '').replace('"', '')), 'utf-8'))),
                    'Origin': 'https://rivalregions.com',
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
            )
        return headers

    def get(self, link, data=None, params=None):
        # требуется тестирование этих заголовков
        # self.session.headers = self.set_headers()
        time.sleep(random.randint(0, self.timedelay))
        try:
            response = self.session.get(link, data=data, params=params)
            return response
        except requests.RequestException as e:
            print(f"An error occurred during GET request: {str(e)}")
            return None

    def post(self, link, data=None, params=None):
        # need test
        # self.session.headers = self.set_headers(params)
        time.sleep(random.randint(0, self.timedelay))
        # useless?
        #        self.session.headers = self.set_headers()
        try:
            response = self.session.post(link, data=data, params=params)
            return response
        except requests.RequestException as e:
            print(f"An error occurred during POST request: {str(e)}")
            return None

    def check_auth(self):
        pass

    def make_session(self):
        # добавить обработку моментов, когда cloudflare блокирует создание новой сессии для обновления куков
        session = requests.Session()
        db = Database()

        auth_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image'
                      '/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ja-RU,ja;q=0.9',
            'Cache-Control': 'max-age=0',
            'Content-Length': '0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://rivalregions.com',
            'Referer': 'https://rivalregions.com/',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': str(user_agents.parse(self.account_info.user_agent).os.family),
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.account_info.user_agent
        }

        # session.headers = auth_headers

        if self.account_info.proxy != 'None':
            session.proxies = {'https': f'https://{self.account_info.proxy}',
                               'http': f'http://{self.account_info.proxy}'}

        session.cookies.update(Database().find_info_gpt(self.login, cookies=True).cookies)
        session.headers = self.set_headers()
        print('init headers:\n', session.headers)
        print('init cookies:\n', session.cookies)

        # session = cloudscraper.create_scraper(sess=session)

        def login_check():
            time.sleep(1)
            tmp = session.get('https://rivalregions.com/').text
            if 'Attention Required!' in tmp:
                print('cloud')
                return False
            if 'sa_sn float_left imp vkvk' in tmp:
                print('bad cookies or some rnd shit')
                return False
            print('is ok')
            return True

        if login_check():
            return session

        # session = cloudscraper.create_scraper()
        session = requests.Session()
        session.headers = auth_headers

        data = {'mail': self.login, 'p': self.account_info.password, 's': 'Войти'}  # ログイン

        session.get('https://rivalregions.com')
        time.sleep(2)
        auth_data = session.post('https://rivalregions.com/rival/pass', data=data).text
        # try: except:
        _viewer_id = auth_data.split('name="viewer_id" value="')[1].split('"')[0]
        _id = auth_data.split('name="id" value="')[1].split('"')[0]
        _access_token = auth_data.split('name="access_token" value="')[1].split('"')[0]
        _hash = auth_data.split('name="hash" value="')[1].split('"')[0]
        _tmz = False
        _wdt = False
        url = f'https://rivalregions.com/?id={_viewer_id}&id={_id}&gl_number=ru&gl_photo=&gl_photo_medium=' \
              f'&gl_photo_big=&tmz_sent=3&wdt_sent=741&register_locale=ru&stateshow=&access_token=' \
              f'{_access_token}&hash={_hash}'
        # add parse tmz_sent, wdt_sent and locale
        time.sleep(2)
        print('pre t cook', session.cookies)
        session.get(url)
        cookies = session.cookies.get_dict(domain='rivalregions.com')

        cookies['login'] = self.login
        db.insert_info(cookies, cookies=True)

        return session


class RRsession:
    def __init__(self, login: str, timedelay: int = None):
        self.session = Req(login=login, timedelay=timedelay)

        self.c_html = None
        self.rr_id = None
        self.language = LANGUAGE_DICT[re.search(r"var all_locales = \['(.+)'];", self.session.get(
            'https://rivalregions.com/#overview', data={'c': self.c_html}).text).group(1)]
        self.perks = None
        self.level = None
        self.gold = None
        self.money = None
        self.residency_region = None
        self.current_region = None
        self.current_state = None
        self.current_party = None
        self.storage = None

        # self.moe = False
        # self.mf = False
        # self.leader = None
        # self.state_type = None

    def get_profile(self):
        profile_page = self.session.get(f'https://rivalregions.com/slide/profile/').text
        self.c_html = re.search("c_html = '(.+)'", profile_page).group(1)
        self.rr_id = re.search(r"slide_header\('slide/profile/(.+)'\);", profile_page).group(1)
        self.level = int(re.search(r'center;">' + self.language['level'] + r': (.+) \(', profile_page).group(1))
        self.perks = Perks(
            strength=int(re.search(self.language['strength'] + r'" class="slide_karma tip pointer">(\d+)'
                                                               r'</span> / <span action', profile_page).group(1)),
            education=int(re.search(self.language['education'] + r'" class="slide_karma tip pointer">(\d+)</span> /'
                                                                 r' <span action', profile_page).group(1)),
            endurance=int(re.search(self.language['endurance'] + r'" class="slide_karma tip pointer">(\d+)'
                                                                 r'</span>', profile_page).group(1))
        )
        self.current_region = int(re.search('map/details/(.+)" class="header_buttons_hover', profile_page).group(1))
        self.residency_region = int(re.search('action="map/details/(.+)" class="tip header_buttons_hover',
                                              profile_page).group(1))
        self.current_state = int(re.search('map/state_details/(.+)/in', profile_page).group(1))
        self.current_party = int(re.search(r"add_party\('0', (.+)\);", profile_page).group(1))
        self.gold = int(re.search(r"new_g\('(.+)'\);", profile_page).group(1).replace('.', ''))
        self.money = int(re.search(r"new_m\('(.+)'\);", profile_page).group(1).replace('.', ''))

    def get_storage(self):
        storage_data = re.findall('class="storage_number_change">(.+)</span>',
                                  self.session.get('https://rivalregions.com/storage', params={'c': self.c_html}).text)
        storage_data = [int(x.replace('.', '')) for x in storage_data]
        self.storage = Storage(*storage_data)


class Account(RRsession):
    def __init__(self, login: str, timedelay: int = None):
        super().__init__(login, timedelay)

    """
    main methods
    """

    def auto_work(self, factory: int = 0) -> None:
        data = params = {'c': self.c_html}
        if self.perks.endurance >= 50:
            factory_now = re.search('<span class="dot hov2 factory_slide" action="factory/index/(.+)">',
                                    self.session.get(f'https://rivalregions.com/work',
                                                     data=data, params=params).text).group(1)
            if not factory:
                self.session.get(f'https://rivalregions.com/factory/search/{self.current_region}?c={self.c_html}',
                                 data=data)
                region_factories = self.session.get(f'https://rivalregions.com/factory/search/'
                                                    f'{self.current_region}/0/6', data=data, params=params).text
                factory = re.search('<td action="factory/index/(.+)" class', region_factories).group(1)

            if factory != factory_now:
                self.session.post('https://rivalregions.com/factory/resign', data=data)

            self.session.get(f'https://rivalregions.com/factory/index/{factory}', data=data, params=params)
            self.session.post('https://rivalregions.com/factory/assign',
                              data={'factory': factory, 'c_html': self.c_html})
            f_type = re.search(f'], factory: {factory}, type: (.+), lim: 0',
                               self.session.get('https://rivalregions.com/work',
                                                data=data, params=params).text).group(1)
            data.update({'mentor': 0, 'factory': factory, 'type': f_type, 'lim': 0})
            self.session.post('https://rivalregions.com/work/autoset/', data=data)

    def auto_war(self):
        pass

    def departments(self, dep: int):
        if self.perks.education >= 100:
            data = {'c': self.c_html}
            deps = self.session.get(f'https://rivalregions.com/map/state_details/{self.current_state}/in',
                                    data={'c': self.c_html})
            if "count_mainst').countdown({until" not in deps:
                dict_dep = {"state": f"{self.current_state}"}
                dict_dep.update({f"w{i}": "0" for i in range(1, 12)})
                dict_dep.update({f"w{dep}": "10"})
                data.update({'what': str(dict_dep).replace("'", '"')})
                self.session.post('https://rivalregions.com/rival/instwork/', data=data)

    def military_academy(self):
        data = params = {'c': self.c_html}
        if self.current_region == self.residency_region:
            academy = self.session.get(
                f'https://rivalregions.com/slide/academy/{self.residency_region}', data=data, params=params).text
            if 'until' not in academy:
                self.session.post(f'https://rivalregions.com/slide/academy_do/', data=data)

    def learn_perks(self, perk: int, speed: int) -> int:
        # perk: {1: str, 2: edu, 3: end}
        # speed: {1: money, 2: gold}
        data = params = {'c': self.c_html}
        perk_time_remaining = 0

        main_data = self.session.get(f'https://rivalregions.com/main/content', data=data, params=params).text

        for i in range(1, 4):
            p_time = main_data.split(f"$('#perk_counter_{i}').countdown(" + "{until: ")
            if len(p_time) == 2:
                perk_time_remaining = int(p_time[1].split(",")[0])
                return perk_time_remaining

        if not perk_time_remaining:
            self.session.post(f'https://rivalregions.com/perks/up/{perk}/{speed}', data=data)
            return self.learn_perks(perk=perk, speed=speed)

    def move_to_region(self):
        pass

    """
    major methods
    """

    def request_residency(self, reg_id):
        data = params = {'c': self.c_html}
        self.session.get(f'https://rivalregions.com/map/details/{reg_id}', data=data, params=params)
        data.update({'post': 'post'})
        self.session.post(f'https://rivalregions.com/map/add_request/{reg_id}', data=data)

    def produce(self):  # отделить крафт энергии в отдельный метод?
        pass

    def enter_party(self):
        pass

    def leave_party(self):
        pass

    def work_permit(self):
        pass

    def move_exp(self):
        pass

    def donate_player(self):
        pass

    def donate_state(self):
        pass

    def start_revolution(self):
        pass

    """
    minor methods
    """

    def change_flag(self, flag):
        data = {'toggle': 1, 'nation': flag, 'c': self.c_html}
        self.session.post('https://rivalregions.com/slide/nation_toggle', data=data)

    def change_about(self, text):
        data = {'c': self.c_html, 'm': text}
        self.session.post('https://rivalregions.com/rival/about', data=data)

    def change_locale(self, loc):
        self.session.get(f'https://rivalregions.com/slide/toggle_locale/{loc}')

    """
    votes
    """

    def vote_leader(self):
        pass

    def vote_parliament(self):
        # primaries
        pass

    def vote_party(self):
        pass

    def article_vote(self):
        pass


if __name__ == '__main__':
    t = Account(login='rr.ruri002@gmail.com')
    t.get_profile()
    t.military_academy()
