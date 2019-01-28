#!/usr/bin/python

import getopt
import sys

from multiprocessing import Pool

from util.solr import Solr
import util.benchmarks as bench


def usage(progname, retval=0):
    print("%s -c <core> -r <num> -t <num>" % progname)
    print("\t-c <core>          \tCore to use for the queries")
    print("\t-u <url>           \turl to the Solr server")
    print("\t-r <num>           \tnumber of repetition, per query")
    print("\t-t <num>           \tnumber of threads, per query")
    print("")
    print("NOTE: the total number of run per query is defined by -r <R>, which means with\n"
          "      -t <T> threads, each thread will execute R/T times each query.")
    sys.exit(retval)


#############################################################################
# Manage parameters & global symbols
core = ''
solr = None
url = ''


def wrapper(arg):
    f, a = arg
    r, t = bench.timed(lambda: f(*a))
#    print("R {} T {}".format(r, t))
    return t


def repeat(count, threads, query, *args):
    pool = Pool(processes=threads)
    cookies = [(query, args) for _ in range(0, count, 1)]

    query(*args)

    ar = pool.map_async(wrapper, cookies)

    pool.close()
    pool.join()

    return [([""], t) for t in ar.get()]


def run_queries(threads, repetitions):
    # Generate Timing statistics
    oids = bench.list_oids()
    spaceids = bench.list_spaces()
    a_point = bench.query_oid(oids[0])[0]

    qs = []

    print("Stats per queries (%d samples/query, %s core):" %
          (repetitions, core))

    # 1. Query all points with a specific OID
    qs.append(("Q1", repeat(repetitions, threads,
                            bench.query_oid, oids[0])))

    # 2. Query all points at a specific position in space
    position = [a_point["geometry.coordinates_%d___pdouble" % x]
                for x in range(0, 3)]
    qs.append(("Q2", repeat(repetitions, threads,
                            bench.query_geometry, position)))

    # 3. Query all the points in a specific reference space
    qs.append(("Q3", repeat(repetitions, threads,
                            bench.query_space, spaceids[0])))

    # 4. Query all points contained in a specific volume, defined by volume.
    qs.append(("Q4", repeat(repetitions, threads,
                            bench.query_mbb,
                            [[0., 0., 0.], [0.1, 0.1, 0.1]])))
    # 5. Query all points contained in a specific volume, defined by label,
    #    a.k.a OID.
    if len(oids) < 5:
        qs.append(("Q5", repeat(repetitions, threads,
                                bench.query_labels, oids[:])))
    else:
        qs.append(("Q5", repeat(repetitions, threads,
                                bench.query_labels, oids[2:5])))

    #########################################################################
    # Output the selected statistics
    print("Query,counts,timing")
    for q in qs:
        print("%s,%d,%s" %
              (q[0], repetitions,
               ",".join(["%.16f" % v for v in [t for r, t in q[1]]])))


def test_query(threads, repetitions):
    # TESTS TO CHECK QUERY RESULTS
    print("START")
    oids = bench.list_oids()
    # spaceids = bench.list_spaces()

    qr = repeat(repetitions, threads, bench.query_oid, oids[0])
    print(qr)
    print("END")


def main(argv):
    global core, url, solr
    progname = argv[0]
    repetitions = 0
    threads = 0

    try:
        opts, args = getopt.getopt(argv[1:], 'c:r:t:u:')
    except getopt.GetoptError:
        usage(progname, 1)

    for opt, arg in opts:
        if opt == '-c':
            core = arg
        elif opt == '-r':
            repetitions = int(arg)
        elif opt == '-t':
            threads = int(arg)
        elif opt == '-u':
            url = arg
        elif opt == '-h':
            usage(progname)
        else:
            usage(progname, 1)

    if len(opts) == 0:
        usage(progname, 1)

    assert (threads > 0)
    assert (repetitions > 0)
    assert (core != '')
    assert (url != '')

    solr = Solr(url)
    bench.init(solr, core)

    run_queries(threads, repetitions)
    # test_query(threads, repetitions)


if __name__ == "__main__":
    main(sys.argv)
