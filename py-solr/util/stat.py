from math import sqrt


#############################################################################
# Statistical functions
def mean(values):
    # Cast everything to float before summing / dividing to improve accuracy
    return sum([float(x) for x in values]) / float(len(values))


def percentile(values, percent):
    s = list(values[:])  # Copy, to make sure we do not change the inputs
    s.sort()
    i = len(values) * (float(percent) / 100.0)
    return s[int(i)]


def median(values):
    return percentile(values, 50)


def stddev(values):
    mn = mean(values)
    v = sum([(float(x) - mn)**2 for x in values]) / (len(values) - 1.0)
    return sqrt(v)
