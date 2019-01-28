#!/usr/bin/python

import getopt
import random
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

# Tasks lists
warm_ups = []
tasks = []


def enqueue(label, count, query, *args):
    # Enqueue the warm up query for this set
    warm_ups.append((label, query, args))

    # Enqueue the set of repeats for this query
    for _ in range(0, count, 1):
        tasks.append((label, query, args))


def wrapper(args):
    rs = []
    for arg in args:
        l, f, a = arg
        r, t = bench.timed(lambda: f(*a))
        rs.append((l, t))
    return rs


def run_threads(threads):
    # Each threads will get a slice of the whole list to execute, evenly
    # distributed among the threads. Each cookie is a list of (label, query,
    # args)

    # We construct separated lists to prevent any kind of lock /
    # synchronization point between the different processes / threads.
    cookies = [[] for _ in range(0, threads, 1)]

    i = 0
    for t in tasks:
        cookies[i].append(t)

        if i < threads - 1:
            i += 1
        else:
            i = 0

    # Warmup queries, they are run sequentially, once. We ignore the return
    # value as the timings are irrelevent
    wrapper(warm_ups)

    # Run the benchmarks, in parallel:
    pool = Pool(processes=threads)
    ar = pool.map_async(wrapper, cookies)
    pool.close()
    pool.join()

    # Flatten the list
    rs = []
    for r in ar.get():
        if r is not None:
            rs = rs + r

    return [(l, [""], t) for l, t in rs]


def run_queries(threads, repetitions):
    # Generate Timing statistics
    oids = bench.list_oids()
    spaceids = bench.list_spaces()
    a_point = bench.query_oid(oids[0])[0]

    print("Stats per queries (%d samples/query, %s core):" %
          (repetitions, core))

    # 1. Query all points with a specific OID
    enqueue("Q1", repetitions, bench.query_oid, oids[0])

    # 2. Query all points at a specific position in space
    position = [a_point["geometry.coordinates_%d___pdouble" % x]
                for x in range(0, 3)]
    enqueue("Q2", repetitions, bench.query_geometry, position)

    # 3. Query all the points in a specific reference space
    enqueue("Q3", repetitions, bench.query_space, spaceids[0])

    # 4. Query all points contained in a specific volume, defined by volume.
    enqueue("Q4", repetitions, bench.query_mbb, [[0., 0., 0.], [0.1, 0.1, 0.1]])

    # 5. Query all points contained in a specific volume, defined by label,
    #    a.k.a OID.
    if len(oids) < 5:
        enqueue("Q5", repetitions, bench.query_labels, oids[:])
    else:
        enqueue("Q5", repetitions, bench.query_labels, oids[2:5])

    random.shuffle(tasks)

    rs = run_threads(threads)

    #########################################################################
    # Output the selected statistics
    # we use a set to deduplicate the values, then we convert back to a list
    # so we can sort the elements
    keys = set([l for l, _, _ in rs])
    keys = list(keys)
    keys.sort()

    print("Query,counts,timing")
    for k in keys:
        print("%s,%d,%s" %
              (k, repetitions,
               ",".join(["%.16f" % t for lp, _, t in rs if lp == k])))


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
