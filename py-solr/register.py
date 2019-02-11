#!/usr/bin/python

import sys
import getopt
from util.solr import Solr


def usage(progname, retval=0):
    print("%s -c <core> -u <url to solr> [-f <data_file.json> [-l]]" % progname)
    print("\t-c <core>          \tcreate a new core, named <core>")
    print("\t-u <url>           \turl to the Solr server")
    print("\t-f <data_file.json>\tload data from <data_file.json> after "
          "registering the core")
    print("\t-l                 \tload data only")
    sys.exit(retval)


def main(argv):
    progname = argv[0]
    core = ''
    url = ''
    data_file = ''
    register = True

    try:
        opts, args = getopt.getopt(argv[1:], 'c:f:hlu:')
    except getopt.GetoptError:
        usage(progname, 1)

    for opt, arg in opts:
        if opt == '-c':
            core = arg
        elif opt == '-f':
            data_file = arg
        elif opt == '-l':
            register = False
        elif opt == '-u':
            url = arg
        elif opt == '-h':
            usage(progname)
        else:
            usage(progname, 1)

    if len(opts) == 0:
        usage(progname, 1)

    assert(core != '')
    assert(url != '')

    solr = Solr(url)

    if register:
        # 1. Create collection with *default_* schema configs
        if [True for c in solr.cores() if c == core]:
            print('Core "%s" exists, skipping...' % core)
            exit(1)
        solr.core_load(core)

        # 2. Define Types
        solr.create_kd_double_point_type(core, "Point3D", 3)

        # 3. Add geometry fields
        solr.field_add(core, 'geometry.type', 'string', stored='true',
                       indexed='true', doc_values='true')
        solr.field_add(core, 'geometry.referenceSpace', 'string', stored='true',
                       indexed='true', doc_values='true')
        solr.field_add(core, 'geometry.coordinates', 'Point3D',
                       stored='true', indexed="true",
                       multi='true')

        # 4. Add attributes
        solr.field_add(core, 'type', 'string', stored='true',
                       indexed='true', doc_values='true')
        solr.field_add(core, 'properties.id', 'string', stored='true',
                       indexed='true', doc_values='true')

    if not [True for c in solr.cores() if c == core]:
        print('Core "%s" does not exist, skipping...' % core)
        exit(1)

    # Load data, if a file was provided
    if data_file != '':
        solr.index_spatial_json(data_file, core, True, True)


if __name__ == "__main__":
    main(sys.argv)
