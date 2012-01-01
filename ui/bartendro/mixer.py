# -*- coding: utf-8 -*-
from time import sleep
from sqlalchemy.orm import mapper, relationship, backref
from bartendro.model.drink import Drink
from bartendro.model.dispenser import Dispenser
from bartendro.model import drink_booze
from bartendro.model import booze

ML_PER_FL_OZ = 29.57
MS_PER_ML = 50

class Mixer(object):
    '''This is where the magic happens!'''

    def __init__(self, driver):
        self.driver = driver
        self.err = ""

    def get_error(self):
        #self.driver.get_error()
        return self.err

    def make_drink(self, id, size, strength):
        drink = Drink.query.filter_by(id=int(id)).first()
        dispensers = Dispenser.query.order_by(Dispenser.id).all()
        print "make ", drink
        print "dispensers ", dispensers

        disp_count = 8
        recipe = []
        for db in drink.drink_boozes:
            r = None
            for i in xrange(disp_count):
                disp = dispensers[i]
                if db.booze_id == disp.booze_id:
                    print "drink_booze %d is in dispenser %d" % (db.booze_id, disp.id)
                    r = {}
                    r['dispenser'] = disp.id
                    r['booze'] = db.booze_id
                    r['booze_name'] = db.booze.name
                    r['part'] = db.value
                    break
            if not r:
                print "Fail to make drink"
                self.err = "Cannot make drink. I don't have the required booze: %s" % db.booze.name
                return 1
            recipe.append(r)

        total_parts = 0
        for r in recipe:
            total_parts += r['part']

        dur = 0
        for r in recipe:
            r['ml'] = r['part'] * size * ML_PER_FL_OZ / total_parts
            r['ms'] = r['ml'] * MS_PER_ML
            print "disp %d %d" % (r['dispenser'] - 1, int(r['ms']))
            self.driver.send("disp %d %d" % (r['dispenser'] - 1, int(r['ms'])))
            sleep(.01)

            if r['ms'] > dur: dur = r['ms']

        self.driver.send("go");
        sleep(dur / 1000)

        return 0 