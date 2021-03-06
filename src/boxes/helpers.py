from datetime import datetime
from math import log
import random

ascii_set = 'abcdefghijklmnopqrstuvwxyABCDEFGHIJKLMNPQRSTUVWXYZ123456789'

def randascii(n):
    return ''.join(random.choice(ascii_set) for _ in range(n)) 

epoch = datetime(1970, 1, 1)

def epoch_seconds(date):
    """Returns the number of seconds from the epoch to date."""
    td = date - epoch
    return td.days * 86400 + td.seconds + (float(td.microseconds) / 1000000)

def hot_score(score, date):
    """The hot formula from reddit"""
    order = log(max(abs(score), 1), 10)
    sign = 1 if score > 0 else -1 if score < 0 else 0
    seconds = epoch_seconds(date) - 1134028003
    return round(order + sign * seconds / 45000, 7)

def color(*seeds):
    """Return a random hue associated with the seed"""
    seed = ''.join(str(seed) for seed in seeds)
    rand = random.Random(seed)
    return int(rand.random()*255)

nothing_messages = [
    "everyone's busy drinking tea",
    'be the first and win nothing!',
    "and it's maybe better this way",
    "I will wait, don't worry",
    "and you know what to do to solve this",
]
