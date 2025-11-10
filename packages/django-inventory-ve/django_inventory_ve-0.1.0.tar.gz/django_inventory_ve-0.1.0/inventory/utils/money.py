from decimal import Decimal, ROUND_HALF_UP
Q2 = Decimal("0.01")
Q6 = Decimal("0.000001")


def q2(x):
    return (x or Decimal("0")).quantize(Q2, rounding=ROUND_HALF_UP)


def q6(x):
    return (x or Decimal("0")).quantize(Q6, rounding=ROUND_HALF_UP)