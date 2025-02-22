#!/usr/bin/python

import getopt
import sys

from util.solr import Solr
import util.benchmarks as bench


def usage(progname, retval=0):
    print("%s -c <core> -r <num>" % progname)
    print("\t-c <core>          \tCore to use for the queries")
    print("\t-u <url>           \turl to the Solr server")
    print("\t-r <num>           \tnumber of repetition, per query")
    sys.exit(retval)


def repeat(count, query, *args):
    qr = []

    # Warm up query, not timed
    query(*args)

    for i in range(0, count):
        qr.append(bench.timed(lambda: query(*args)))

    return qr


#############################################################################
# Manage parameters & global symbols
core = ''
solr = None
url = ''


def run_queries(repetitions):
    # Generate Timing statistics
    oids = bench.list_oids()
    spaceids = bench.list_spaces()
    a_point = bench.query_oid(oids[0])[0]

    qs = []

    print("Stats per queries (%d samples/query, %s core):" %
          (repetitions, core))

    # 1. Query all points with a specific OID
    qs.append(("Q1", repeat(repetitions, bench.query_oid, oids[0])))

    # 2. Query all points at a specific position in space
    position = [a_point["geometry.coordinates_%d___pdouble" % x]
                for x in range(0, 3)]
    qs.append(("Q2", repeat(repetitions, bench.query_geometry, position)))

    # 3. Query all the points in a specific reference space
    qs.append(("Q3", repeat(repetitions, bench.query_space, spaceids[0])))

    # 4. Query all points contained in a specific volume, defined by volume.
    qs.append(("Q4", repeat(repetitions, bench.query_mbb,
                                  [[0., 0., 0.], [0.1, 0.1, 0.1]])))
    # 5. Query all points contained in a specific volume, defined by label,
    #    a.k.a OID.
    if len(oids) < 5:
        qs.append(("Q5", repeat(repetitions, bench.query_labels, oids[:])))
    else:
        qs.append(("Q5", repeat(repetitions, bench.query_labels, oids[2:5])))

    #########################################################################
    # Output the selected statistics
    print("Query,counts,timing")
    for q in qs:
        print("%s,%d,%s" %
              (q[0], repetitions,
               ",".join(["%.16f" % v for v in [t for r, t in q[1]]])))


def test_query(x=0):
    # TESTS TO CHECK QUERY RESULTS
    oids = bench.list_oids()
    spaceids = bench.list_spaces()

    # 1. Query all points with a specific OID
    r = bench.query_oid(oids[0])

    # 2. Query all points at a specific position in space
    if x == 0:
        a_point = r[0]
        r = bench.query_geometry(
                [a_point["geometry.coordinates_%d___pdouble" % x]
                 for x in range(0, 3)])
    elif x == 1:
        # 3. Query all the points in a specific reference space
        r = bench.query_space(spaceids[0])

    elif x == 2:
        # 4. Query all points contained in a specific volume, defined by volume.
        # FIXME: Double check boundary behavior for points on the surface of the
        #        volume, are they returned or not? Same question if they are on
        #        an edge of the volume?
        r = bench.query_mbb([[0., 0., 0.], [0.1, 0.1, 0.1]])

    elif x == 3:
        # 5. Query all points contained in a specific volume, defined by label,
        #    a.k.a OID.
        if len(oids) < 5:
            r = bench.query_labels(oids[:])
        else:
            r = bench.query_labels(oids[2:5])
    print(r)


def main(argv):
    global core, url, solr
    progname = argv[0]
    repetitions = 0

    try:
        opts, args = getopt.getopt(argv[1:], 'c:r:u:')
    except getopt.GetoptError:
        usage(progname, 1)

    for opt, arg in opts:
        if opt == '-c':
            core = arg
        elif opt == '-r':
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
    bench.init(solr, core)

    run_queries(repetitions)
    # test_query(3)


if __name__ == "__main__":
    main(sys.argv)
