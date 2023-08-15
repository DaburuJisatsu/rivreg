import datetime
import math


class Perks:
    def __init__(self, strength, education, endurance):
        self.strength = strength
        self.education = education
        self.endurance = endurance
        self.perks = {
            'strength': self.strength,
            'education': self.education,
            'endurance': self.endurance
        }
        self.dict = {
            1: strength,
            2: education,
            3: endurance
        }
        self.lowest = LowestPerk(self.dict)


class LowestPerk:
    def __init__(self, perks):
        self.code = min(perks.items(), key=lambda x: x[1])[0]
        self.value = min(perks.items(), key=lambda x: x[1])[1]


class Storage:
    def __init__(
            self,
            oil,
            ore,
            uranium,
            diamonds,
            oxygen,
            helium,
            rivalium,
            antirad,
            energy,
            spacerockets,
            lls,
            tanks,
            aircraft,
            missiles,
            bombers,
            battleships,
            drones,
            moon_tanks,
            stations,
            sumbarines
    ):
        self.oil = oil
        self.ore = ore
        self.uranium = uranium
        self.diamonds = diamonds
        self.oxygen = oxygen
        self.helium = helium
        self.rivalium = rivalium
        self.antirad = antirad
        self.energy = energy
        self.spacerockets = spacerockets
        self.lls = lls
        self.tanks = tanks
        self.aricrafts = aircraft
        self.missiles = missiles
        self.bombers = bombers
        self.battleships = battleships
        self.drones = drones
        self.moon_tanks = moon_tanks
        self.stations = stations
        self.submarines = sumbarines


def time_until_new_day():
    current_time = datetime.datetime.now()
    target_time = datetime.datetime.combine(datetime.date.today(), datetime.time(21, 0))

    time_difference = target_time - current_time
    seconds_left = math.ceil(time_difference.total_seconds())

    return seconds_left


if __name__ == '__main__':
    t = Perks(123, 456, 666)
    print(t.lowest.code)
