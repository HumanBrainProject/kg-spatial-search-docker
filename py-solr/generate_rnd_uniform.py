#!/usr/bin/python

import random
import sys
import getopt


def usage(progname, retval=0):
    print("%s -o <num> -p <num>" % progname)
    print("\t-o <num>           \tNumber of OIDs to generate in the space")
    print("\t-p <num>           \tNumber of spatial points to generate per OID")
    sys.exit(retval)


def print_point(oid, reference_space, point, end):
    """ Generate a single data point with the properties provided. """

    (x0, x1, x2) = point
    point_str = '{{"type":"Feature","geometry":'
    point_str += '{{"type":"Point","referenceSpace":"{}",'
    point_str += '"coordinates":["{},{},{}"]}},'
    point_str += '"properties":{{"id":"{}"}}}}'
    point_str += end

    print(point_str.format(reference_space, x0, x1, x2, oid))


def print_oid(reference_space, oid, num, end):
    """ Generate a point ID with `num` random spatial points linked to it.
    """

    for k in range(num):
        coordinates = (random.random(), random.random(), random.random())
        print_point(oid, reference_space, coordinates, end)


def print_space(reference_space, oids_per_space, points_per_oid):
    """ Generate a space ID with `oids_per_space` different OIDs, and 
        `points_per_oid` spatial records per OID.
    """
    for k in range(oids_per_space - 1):
        oid = random.random()
        print_oid("space{}".format(reference_space), "oid{}".format(oid),
                  points_per_oid, ",")

    oid = random.random()
    print_oid("space{}".format(reference_space), "oid{}".format(oid),
              points_per_oid-1, ",")
    print_oid("space{}".format(reference_space), "oid{}".format(oid), 1, "")


def generate_file(points_per_oid, oids_per_space):
    print("[")
    reference_space = random.random()
    print_space(reference_space, oids_per_space, points_per_oid)
    print("]")


def main(argv):
    progname = argv[0]
    points_per_oid = 0
    oids_per_space = 0

    try:
        opts, args = getopt.getopt(argv[1:], 'o:p:')
    except getopt.GetoptError:
        usage(progname, 1)

    for opt, arg in opts:
        if opt == '-o':
            points_per_oid = int(arg)
        elif opt == '-p':
            oids_per_space = int(arg)
        elif opt == '-h':
            usage(progname)
        else:
            usage(progname, 1)

    if len(opts) == 0:
        usage(progname, 1)

    assert(points_per_oid > 0)
    assert(oids_per_space > 0)

    generate_file(points_per_oid, oids_per_space)


if __name__ == "__main__":
    main(sys.argv)
