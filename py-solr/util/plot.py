import matplotlib.pyplot as plt


#############################################################################
# Plotting helpers
def plot_presentation(x, y, lo, up, labels, skeys, loc=None,
                      xscale=None, yscale=None, show_grid=False,
                      error_area=False, concept_graph=False, figsize=None,
                      dpi=None):
    plt.figure(1, figsize=figsize, dpi=dpi)

    plt.rcParams.update({'font.size': 22})

    if concept_graph:
        plt.xkcd(scale=1, length=100, randomness=2)

    if yscale is not None:
        plt.yscale(yscale, nonposy='clip')
    if xscale is not None:
        plt.xscale(xscale, nonposx='clip')

    if yscale == 'log' and xscale == 'log':
        plt.loglog(basex=10, basey=10)
    elif yscale == 'log' and not xscale == 'log':
        plt.semilogy(basey=10)
    elif not yscale == 'log' and xscale == 'log':
        plt.semilogx(basex=10)

    plt.minorticks_on()

    if show_grid:
        plt.grid(b=True, which='major', color='lightgrey', linestyle='-')
        plt.grid(b=True, which='minor', color='whitesmoke', linestyle='-')

    # Draw a point plot to show pulse as a function of three categorical factors

    for s in skeys:
        # plt.plot(x[s], y[s], marker="x", linestyle="-", label=s)
        # plt.plot(x[s], lo[s], marker="*", linestyle="-", label="%s-min" %s)
        # plt.plot(x[s], up[s], marker="+", linestyle="-", label="%s-max" %s)

        plt.errorbar(x[s], y[s], yerr=[lo[s], up[s]], fmt='x-', label=labels[s],
                     elinewidth=1, capsize=4)
        if error_area:
            plt.fill_between(x[s],
                             [-v+t for v, t in zip(lo[s], y[s])],
                             [v+t for v, t in zip(up[s], y[s])], alpha=0.5)

    plt.legend(loc=loc)
