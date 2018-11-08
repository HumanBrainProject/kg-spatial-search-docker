#!/usr/bin/python

from functools import reduce
import getopt
import operator
from math import sqrt
import sys
import time


from solr import Solr


def usage(progname, retval=0):
    print("%s -c <core> -n <num>" % progname)
    print("\t-c <core>          \tCore to use for the queries")
    print(
        "\t-n <num>           \tNumber of times to run each query of the query "
        "set.")
    print("\t-u <url>           \turl to the Solr server")
    sys.exit(retval)


def flatten(lists):
    return reduce(operator.concat, lists)


#############################################################################
# Timing statistics utils
def mean(values):
    # Cast everything to float before summing / dividing to improve accuracy
    return sum([float(x) for x in values]) / float(len(values))


def percentile(values, percent):
    s = values[:]  # Copy, to make sure we do not change the inputs
    s.sort()
    i = len(values) * (float(percent) / 100.0)
    return s[int(i)]


def stddev(values):
    mn = mean(values)
    v = sum([(float(x) - mn)**2 for x in values]) / (len(values) - 1.0)
    return sqrt(v)


def timed(f):
    start = time.time()
    ret = f()
    elapsed = time.time() - start
    return ret, elapsed


def repeat(count, query, *args):
    qr = []
    query(*args)

    for i in range(0, count):
        qr.append(timed(lambda: query(*args)))

    return qr


def stats(timings):
    m = mean(timings)
    p = percentile(timings, 50)
    s = stddev(timings)
    return m, s, p


#############################################################################
# Query utils

# Figure out the OIDs available:
def list_oids():
    return solr.list_field(core, 'properties.id')


# Figure out the OIDs available:
def list_spaces():
    return solr.list_field(core, 'geometry.referenceSpace')


#############################################################################
# Typical queries
def query_oid(oid):
    # Find out all the points linked to document oid
    num_points = solr.query_cardinality(core, oid=oid)
    points = solr.query(core, oid, rows=num_points)["response"]["docs"]
    return points


def query_geometry(geometry):
    # Find out all the points at the given position
    num_points = solr.query_cardinality(core, geometry=geometry)
    points = solr.query(core, geometry=geometry,
                        rows=num_points)["response"]["docs"]
    return points


def query_mbb(mbb):
    # Find out all the points included in the minimum bounding box
    num_points = solr.query_cardinality(core, mbb=mbb)
    points = solr.query(core, mbb=mbb, rows=num_points)["response"]["docs"]
    return points


def query_space(reference_space):
    # Find out all the points linked to the reference space
    num_points = solr.query_cardinality(core, reference_space=reference_space)
    points = solr.query(core, reference_space=reference_space,
                        rows=num_points)["response"]["docs"]
    return points


def query_labels(labels):
    # Find out all the points linked to each label, per label
    points = {}
    # retrieve total number of points stored
    num_points = solr.query_cardinality(core)

    for l in labels:
        points[l] = \
            solr.query(core, labels=[l],
                       q="properties.id:%s" % l,
                       rows=num_points)["response"]["docs"]

    return flatten(points)


#############################################################################
# Manage parameters & global symbols
core = ''
solr = None
url = ''

# comma separated names of spatial fields used in the index:
spatial_fields = \
    'geometry.coordinates_0___pdouble,' \
    'geometry.coordinates_1___pdouble,' \
    'geometry.coordinates_2___pdouble '


def run_queries(repetitions):
    # Generate Timing statistics
    oids = list_oids()
    spaceids = list_spaces()
    a_point = query_oid(oids[0])[0]

    qs = []

    # 1. Query all points with a specific OID
    qs.append(("Q1", repeat(repetitions, query_oid, oids[0])))

    # 2. Query all points at a specific position in space
    qs.append(("Q2", repeat(repetitions, query_geometry,
                            [a_point["geometry.coordinates_%d___pdouble" % x]
                                for x in range(0, 3)])))

    # 3. Query all the points in a specific reference space
    qs.append(("Q3", repeat(repetitions, query_space, spaceids[0])))

    # 4. Query all points contained in a specific volume, defined by volume.
    qs.append(("Q4", repeat(repetitions, query_mbb,
                            [[0., 0., 0.], [0.1, 0.1, 0.1]])))
    # 5. Query all points contained in a specific volume, defined by label,
    #    a.k.a OID.
    if len(oids) < 5:
        qs.append(("Q5", repeat(repetitions, query_labels, oids[:])))
    else:
        qs.append(("Q5", repeat(repetitions, query_labels, oids[2:5])))

    #########################################################################
    # Output the selected statistics
    print("Stats per queries (%d samples/query, %s core):" %
          (repetitions, core))
    print("Query,mean,stddev,median,counts")
    for q in qs:
        print("%s,%s,%s" %
              (q[0],
               ",".join(["%f" % v for v in stats([t for r, t in q[1]])]),
               [len(r) for r, t in q[1]]
               ))


def test_queries():
    # TESTS TO CHECK QUERY RESULTS
    oids = list_oids()
    spaceids = list_spaces()

    # 1. Query all points with a specific OID
    r = query_oid(oids[2])
    a_point = r[0]

    # 2. Query all points at a specific position in space
    # r = query_geometry([a_point["geometry.coordinates_%d___pdouble" % x]
    #                    for x in range(0, 3)])

    # 3. Query all the points in a specific reference space
    # r = query_space(spaceids[0])

    # 4. Query all points contained in a specific volume, defined by volume.
    # FIXME: Double check boundary behavior for points on the surface of the
    #        volume, are they returned or not? Same question if they are on
    #        an edge of the volume?
    # r = query_mbb([[0., 0., 0.], [0.1, 0.1, 0.1]])

    # 5. Query all points contained in a specific volume, defined by label,
    #    a.k.a OID.
    r = query_labels(oids[2:5])
    # OK*************
    print(r)


def main(argv):
    global core, url, solr
    progname = argv[0]
    repetitions = 0

    try:
        opts, args = getopt.getopt(argv[1:], 'c:n:u:')
    except getopt.GetoptError:
        usage(progname, 1)

    for opt, arg in opts:
        if opt == '-c':
            core = arg
        elif opt == '-n':
            repetitions = int(arg)
        elif opt == '-u':
            url = arg
        elif opt == '-h':
            usage(progname)
        else:
            usage(progname, 1)

    if len(opts) == 0:
        usage(progname, 1)

    assert (repetitions > 0)
    assert (core != '')
    assert (url != '')

    solr = Solr(url)

    run_queries(repetitions)
    # test_queries()


if __name__ == "__main__":
    main(sys.argv)
