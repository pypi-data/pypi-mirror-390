import math

__all__ = ["round_half_up"]


def round_half_up(n, places=0):
    multiplier = 10**places
    return math.floor(n * multiplier + 0.5) / multiplier
