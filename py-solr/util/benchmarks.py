from functools import reduce
import operator
import time


solr = None
core = None


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


def flatten(lists):
    return reduce(operator.concat, lists)


#############################################################################
# Query utils

# Figure out the OIDs available:
def list_oids():
    return solr.list_field(core, 'properties.id')


# Figure out the reference spaces available:
def list_spaces():
    return solr.list_field(core, 'geometry.referenceSpace')


def init(solr_, core_):
    global solr, core
    assert (solr_ is not None)
    assert (core_ is not None)

    solr = solr_
    core = core_


###########################################################################
# Typical queries
def query_oid(oid):
    # Find out all the points linked to document oid
    num_points = solr.query_cardinality(core, oid=oid)
    points = solr.query(core, oid, indent='off',
                        rows=num_points)["response"]["docs"]
    return points


def query_geometry(geometry):
    # Find out all the points at the given position
    num_points = solr.query_cardinality(core, geometry=geometry)
    points = solr.query(core, geometry=geometry, indent='off',
                        rows=num_points)["response"]["docs"]
    return points


def query_mbb(mbb):
    # Find out all the points included in the minimum bounding box
    num_points = solr.query_cardinality(core, mbb=mbb)
    points = solr.query(core, mbb=mbb, indent='off',
                        rows=num_points)["response"]["docs"]
    return points


def query_space(reference_space):
    # Find out all the points linked to the reference space
    num_points = solr.query_cardinality(
        core, reference_space=reference_space)
    points = solr.query(core, reference_space=reference_space,
                        indent='off',
                        rows=num_points)["response"]["docs"]
    return points


def query_labels(labels):
    # Find out all the points linked to each label, per label
    points = {}
    # retrieve total number of points stored
    num_points = solr.query_cardinality(core)

    for l in labels:
        points[l] = \
            solr.query(core, labels=[l], q="properties.id:%s" % l,
                       indent='off',
                       rows=num_points)["response"]["docs"]

    return flatten(points)
