#!/usr/bin/python

import getopt
import matplotlib.pyplot as plt
import ntpath
import sys

import util.data as data
import util.stat as stat
import util.plot as plot


def usage(progname, retval=0):
    print("%s [-h] [-vV] [-o graph.pdf] <input files>" % progname)
    print("\t-o graph.pdf  \tSpecify the PDF filename, by default 'graph.pdf'.")
    print("\t-v            \tEnable print of the statistics gathered.")
    print("\t-h            \tThis help message.")
    sys.exit(retval)


def main(argv):
    progname = argv[0]
    plot_file = ""
    verbose = False

    try:
        opts, args = getopt.getopt(argv[1:], 'o:hvV')
    except getopt.GetoptError:
        usage(progname, 1)

    for opt, arg in opts:
        if opt == '-o':
            plot_file = arg
        elif opt == '-v':
            verbose = True
        elif opt == '-h':
            usage(progname)
        else:
            usage(progname, 1)

    if len(args) < 1:
        usage(progname, 1)

    converter = (str, int,
                 float, float, float, float, float,
                 float, float, float, float, float,
                 float, float, float, float, float,
                 float, float, float, float, float)

    labels = {
        "Q1": "id", "Q2": "coord", "Q4": "mbb", "Q3": "space id", "Q5": "labels"
    }
    x = {
        "Q1": [], "Q2": [], "Q3": [], "Q4": [], "Q5": []
    }
    y = {
        "Q1": [], "Q2": [], "Q3": [], "Q4": [], "Q5": []
    }
    lo = {
        "Q1": [], "Q2": [], "Q3": [], "Q4": [], "Q5": []
    }
    up = {
        "Q1": [], "Q2": [], "Q3": [], "Q4": [], "Q5": []
    }

    results = []
    skipped = []

    # Load the data form the files
    data.load_csv(args, converter, results, skipped)

    # Compute statistics per data series
    for dataset in results:
        dataset_size = int(ntpath.basename(dataset[0])[:-1])*1000

        if verbose:
            print("-"*78)
            print("Core %d" % dataset_size)

        for query in dataset[1]:
            query_name = query[0]
            values = query[2:]

            t_min = min(values)
            t_max = max(values)
            t_mean = stat.mean(values)
            t_median = stat.median(values)
            # t_stddev = stat.stddev(values)

            x[query_name].append(dataset_size)
            y[query_name].append(t_mean)
            lo[query_name].append(-(t_min-t_median))
            up[query_name].append(t_max-t_median)

            if verbose:
                print("  Query %s : repeats %s" % (query[0], query[1]))
                print("    Timings: %s" %
                      (":".join(["%.16f" % v for v in values])))
                print("    %f [%f;%f]" % (t_median, t_min, t_max))

    # Plot for PowerPoint
    plot.plot_presentation(x, y, lo, up, labels,
                           ["Q1", "Q2", "Q3", "Q4", "Q5"], "upper left",
                           xscale='log', yscale='log', show_grid=False,
                           figsize=(14, 7), dpi=200,
                           concept_graph=False
                           )

    # Customize this specific plot
    plt.xlabel("Dataset Size [# points]")
    plt.ylabel("Timing [seconds]")

    plt.xlim(5E2, 1E7)
    plt.ylim(3E-3, 1E3)

    # plt.hlines(1, 0, 1E9, linestyle="-", color="navy", label="1 sec")
    # plt.hlines(10, 0, 1E9, linestyle="-", color="navy", label="10 sec")
    # plt.hlines(600, 0, 1E9, linestyle="-", color="navy", label="10 min")

    if not plot_file == '':
        plt.savefig(plot_file, facecolor='white', edgecolor='none',
                    bbox_inches='tight', dpi=200)
    else:
        plt.show()


if __name__ == "__main__":
    main(sys.argv)
