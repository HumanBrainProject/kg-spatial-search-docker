#!/usr/bin/python

import getopt
import sys

from util.solr import Solr
import util.benchmarks as bench


def usage(progname, retval=0):
    print("%s -c <core> -n <num>" % progname)
    print("\t-c <core>          \tCore to use for the queries")
    print("\t-u <url>           \turl to the Solr server")
    sys.exit(retval)


#############################################################################
# Query utils

# Figure out the OIDs available:
def list_oids():
    return solr.list_field(core, 'properties.id')


# Figure out the reference spaces available:
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

    return bench.flatten(points)


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

    print("Stats per queries (%d samples/query, %s core):" %
          (repetitions, core))

    # 1. Query all points with a specific OID
    qs.append(("Q1", bench.repeat(repetitions, query_oid, oids[0])))

    # 2. Query all points at a specific position in space
    position = [a_point["geometry.coordinates_%d___pdouble" % x]
                for x in range(0, 3)]
    qs.append(("Q2", bench.repeat(repetitions, query_geometry, position)))

    # 3. Query all the points in a specific reference space
    qs.append(("Q3", bench.repeat(repetitions, query_space, spaceids[0])))

    # 4. Query all points contained in a specific volume, defined by volume.
    qs.append(("Q4", bench.repeat(repetitions, query_mbb,
                                  [[0., 0., 0.], [0.1, 0.1, 0.1]])))
    # 5. Query all points contained in a specific volume, defined by label,
    #    a.k.a OID.
    if len(oids) < 5:
        qs.append(("Q5", bench.repeat(repetitions, query_labels, oids[:])))
    else:
        qs.append(("Q5", bench.repeat(repetitions, query_labels, oids[2:5])))

    #########################################################################
    # Output the selected statistics
    print("Query,counts,timing")
    for q in qs:
        print("%s,%d,%s" %
              (q[0], repetitions,
               ",".join(["%.16f" % v for v in [t for r, t in q[1]]])))


def test_query(x=0):
    # TESTS TO CHECK QUERY RESULTS
    oids = list_oids()
    spaceids = list_spaces()

    # 1. Query all points with a specific OID
    r = query_oid(oids[2])

    # 2. Query all points at a specific position in space
    if x == 0:
        a_point = r[0]
        r = query_geometry([a_point["geometry.coordinates_%d___pdouble" % x]
                            for x in range(0, 3)])
    elif x == 1:
        # 3. Query all the points in a specific reference space
        r = query_space(spaceids[0])

    elif x == 2:
        # 4. Query all points contained in a specific volume, defined by volume.
        # FIXME: Double check boundary behavior for points on the surface of the
        #        volume, are they returned or not? Same question if they are on
        #        an edge of the volume?
        r = query_mbb([[0., 0., 0.], [0.1, 0.1, 0.1]])

    elif x == 2:
        # 5. Query all points contained in a specific volume, defined by label,
        #    a.k.a OID.
        r = query_labels(oids[2:5])
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
    # test_query()


if __name__ == "__main__":
    main(sys.argv)
