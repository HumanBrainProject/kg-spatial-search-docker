from functools import reduce
import operator
import time


#############################################################################
# benchmarking utils
def timed(f, store_results=False):
    ret = [""]

    start = time.time()
    if store_results:
        ret = f()
    else:
        f()
    elapsed = time.time() - start

    return ret, elapsed


def repeat(count, query, *args):
    qr = []
    query(*args)

    for i in range(0, count):
        qr.append(timed(lambda: query(*args)))

    return qr


def flatten(lists):
    return reduce(operator.concat, lists)
