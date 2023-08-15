from xy_login import RRsession as Rr
import threading
import time

import account_unit

em1 = 'canje0469@gmail.com'
em2 = 'randze738@gmail.com'
em3 = 'meidonoraura@gmail.com'
em4 = 'raurabodevuihhi5@gmail.com'

def perks(login):
    while True:
        acc = Rr(login=login)
        if acc.endurance < 100:
            t = int(acc.learn_perks(perk=3, speed=1))
        else:
            t = int(acc.learn_perks(perk=1, speed=1))
        print(f'time remaining: {t}')
        time.sleep(t + 1)

def alive():
    acc1 = threading.Thread(target=perks, args=(em1,))
    acc2 = threading.Thread(target=perks, args=(em2,))
    acc3 = threading.Thread(target=perks, args=(em3,))
    acc4 = threading.Thread(target=perks, args=(em4,))

    acc1.start()
    acc2.start()
    acc3.start()
    acc4.start()


def main():
    print('init')
    alive()


if __name__ == '__main__':
    main()
