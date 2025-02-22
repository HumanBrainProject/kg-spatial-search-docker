#!/usr/bin/python

import getopt
import sys
import copy

from util.plot_3d import Fig
from util.solr import Solr


def usage(progname, retval=0):
    print("%s -c <core> -u <url> [(-s|-S)]" % progname)
    print("\t-c <core>          \tCore to use for the queries")
    print("\t-u <url>           \turl to the Solr server")
    print("\t-S                 \tShow universe bounds")
    print("\t-s                 \tHide universe bounds")
    sys.exit(retval)


#############################################################################
# Query utils
def draw_universe(fig):
    if show_universe:
        # Add a box around all the points in the dataset
        universe_mbb = solr.spatial_mbb(core)

        # Draw the box
        fig.plot_mbb(universe_mbb, linecolor='grey', linestyle='dotted')


def draw_query_box(fig, box):
    # Draw the given box
    fig.plot_mbb(box, linecolor='grey', linestyle='dashed')


def average_point(group):
    # FIXME: Most likely not good python code, might even be uber slow
    # FIXME: We arbitrarily take the first point properties for the group of
    #        points. This is most likely not correct in most situations.

    c = len(group)      # Number of points
    n = len(group[0])   # Number of dimensions
    a = copy.deepcopy(group[0])
    for i in range(0, n, 1):
        a['geometry.coordinates_%d___pdouble' % i] = 0.0

    for p in group:
        for i in range(0, n, 1):
            a['geometry.coordinates_%d___pdouble' % i] += \
                p['geometry.coordinates_%d___pdouble' % i]

    for i in range(0, n, 1):
        a['geometry.coordinates_%d___pdouble' % i] = (
                    a['geometry.coordinates_%d___pdouble' % i] / float(c))

    return a


#############################################################################
# Query Examples
def query_oid(oid):
    #########################################################################
    # Find out all the points linked to document oid
    points = solr.query(core, oid, fl=spatial_fields)["response"]["docs"]
    box = solr.spatial_mbb(core, query=solr.label_to_q(oid))

    #########################################################################
    # Create a figure to present the results
    f = Fig(title='Points ID = %s' % oid)

    # Add a box around all the points in the dataset
    draw_universe(f)

    # Add a box containing all the points of the query
    draw_query_box(f, box)

    # Plot each point individually, be careful w.r.t the number of points,
    # as this can be very slow if there are a lots of points
    f.add_points(points)

    f.show()


def query_geometry(geometry):
    #########################################################################
    # Find out all the points at the given position

    # Strictly speaking there might be a mismatch as the following calls are
    # not atomic, between the call to cardinality, the actual query and
    # create_colors.
    num_points = solr.query_cardinality(core, geometry=geometry)
    points = solr.query(core, geometry=geometry,
                        fl=spatial_fields+',properties.id',
                        rows=num_points)["response"]["docs"]
    box = solr.spatial_mbb(core, query='geometry.coordinates:("%s")' %
                                       solr.point_to_str(geometry))

    #########################################################################
    # Create a figure to present the results
    f = Fig(title='Point(%s)' % solr.point_to_str(geometry))

    # Add a box around all the points in the dataset
    draw_universe(f)

    # Add a box containing all the points of the query
    draw_query_box(f, box)

    # Generates multiple colors, one per point
    f.create_colors(num_points)

    # Plot each point individually, be careful w.r.t the number of points,
    # as this can be very slow if there are a lot of points
    for p in points:
        f.add_points([p], label=p['properties.id'][0], color=f.next_color())

    f.show()


def query_mbb(mbb):
    #########################################################################
    # Find out all the points included in the minimum bounding box
    num_points = solr.query_cardinality(core, mbb=mbb)
    print("#Points: %d" % num_points)
    points = solr.query(core, mbb=mbb, rows=num_points)["response"]["docs"]

    #########################################################################
    # Create a figure to present the results
    f = Fig(title='Minimum Bounding Box (%s)' % solr.mbb_to_str(mbb))

    # Add a box around all the points in the dataset
    draw_universe(f)

    # Draw the query box
    f.plot_mbb(mbb, linecolor='red')

    # Generates multiple colors, one per point
    f.create_colors(len(points))

    # Plot each point individually, be careful w.r.t the number of points,
    # as this can be very slow if there are a lots of points
    for p in points:
        f.add_points([p], color=f.next_color())

    f.show()


def query_space(reference_space, bucket_size, page_size):
    # page_size : Max number of rows per query
    # bucket_size: Number of points to group together, per page

    #########################################################################
    # Find out all the points linked to the reference space
    num_points = solr.query_cardinality(core, reference_space=reference_space)
    box = solr.spatial_mbb(core, query='geometry.referenceSpace:%s' %
                                       reference_space)

    #########################################################################
    # Create a figure to present the results
    f = Fig(title='ReferenceSpace %s' % reference_space)

    # Add a box around all the points in the dataset
    draw_universe(f)

    # Generates multiple boxes, as slices along X
    pages = int((num_points / float(page_size)) + 1)

    length = (box[1][0] - box[0][0])
    box_width = length / pages
    pb = box[:][:]
    pb[0][0] = pb[1][0] - box_width

    # Generates multiple colors, one per page (or slice of the dataset)
    f.create_colors(pages)

    page = 0
    while page < pages:
        # Grab the next set of rows of the query
        points = solr.query(core, reference_space=reference_space,
                            fl=spatial_fields, rows=page_size,
                            start=page_size*page)["response"]["docs"]

        color = f.next_color()

        # Skip some points, as a way to display huge datasets
        pp = [average_point(group)
              for group in zip(*[iter(points)] * bucket_size)]
        f.add_points(pp, color=color)

        # Add a box around the current slice of the dataset
        f.plot_mbb(pb, linecolor=color, linestyle="dotted")

        # Compute the next box_width box
        pb[0][0] -= box_width
        pb[1][0] -= box_width

        page += 1

    f.show()


def query_labels(labels):
    #########################################################################
    # Find out all the points linked to each label, per label
    points = {}
    num_points = {}
    for l in labels:
        num_points[l] = solr.query_cardinality(core, labels=[l],
                                               print_timing=True)

        points[l] = solr.query(core, labels=[l], rows=num_points[l],
                               print_timing=True)["response"]["docs"]

    box = solr.spatial_mbb(core, query=solr.labels_to_q(labels))

    #########################################################################
    # Create a figure to present the results
    f = Fig(title='Labels = %s' % [', '.join(labels)])

    # Add a box around all the points in the dataset
    draw_universe(f)

    # Add a box containing all the points of the query
    draw_query_box(f, box)

    # Generates multiple colors, one per label
    f.create_colors(len(labels))

    for l in labels:
        f.add_points(points[l], label=l, color=f.next_color())

    f.show()


#############################################################################
# Manage parameters & global symbols
core = ''
solr = None
url = ''

# Set to true to draw the bounding box of all the points available in Solr
show_universe = False

# comma separated names of spatial fields used in the index:
spatial_fields = \
    'geometry.coordinates_0___pdouble,' \
    'geometry.coordinates_1___pdouble,' \
    'geometry.coordinates_2___pdouble '


def main(argv):
    global core, url, solr, show_universe
    progname = argv[0]

    # url = 'https://nexus-dev.humanbrainproject.org/solr/' # CSCS
    # url = 'http://M64006A327BAE.dyn.epfl.ch:8983/solr'

    try:
        opts, args = getopt.getopt(argv[1:], 'c:u:sS')
    except getopt.GetoptError:
        usage(progname, 1)

    for opt, arg in opts:
        if opt == '-c':
            core = arg
        elif opt == '-u':
            url = arg
        elif opt == '-S':
            show_universe = True
        elif opt == '-s':
            show_universe = False
        elif opt == '-h':
            usage(progname)
        else:
            usage(progname, 1)

    if len(opts) == 0:
        usage(progname, 1)

    assert (core != '')
    assert (url != '')

    solr = Solr(url)

    ####
    # Uncomment below to execute a specific query
    ####

    query_mbb([[0, 0, 0], [0.01, 0.01, 0.01]])
    # query_mbb([[0, 0, 0], [0.5, 0.5, 0.5]])

    # query_oid('2900d3a9-e7cb-4a14-9248-98717f654fc7')

    # Figure out the OIDs available:
    # oids = solr.list_field(core, 'properties.id')
    # Let's hope there is more than point at that location:
    # a_point = solr.query(core, oids[0], fl=spatial_fields)["response"]["docs"][0]
    # position = [a_point["geometry.coordinates_%d___pdouble" % x]
    #            for x in range(0, 3)]
    # query_geometry(position)

    # query_geometry([24.27, 9.84, 17.65])

    # query_mbb([[380, 100, 50], [400, 300, 200]])

    # query_space('MNI', 1, 20)
    # query_space('WHS_SD_rat_v1.01', 100, 20000)

    # query_labels(['75422678_s0152_object'])
    # query_labels(['75422652_s0152_object', '75422676_s0064_object'])
    # query_labels(['75422678_s0152_object', '75422652_s0064_object',
    # '75422676_s0144_object'])

    # Be very very patient to visualise those...
    # query_labels(['metadata/sEEG-spatial-metadata-sample'])
    # query_labels(['Uvula (I)', 'Uvula (II)', 'Uvula (III)', 'Uvula (IV)',
    # 'Uvula (V)', 'Uvula (VI)', 'Uvula (VII)', 'Uvula (VIII)'])


if __name__ == "__main__":
    main(sys.argv)
