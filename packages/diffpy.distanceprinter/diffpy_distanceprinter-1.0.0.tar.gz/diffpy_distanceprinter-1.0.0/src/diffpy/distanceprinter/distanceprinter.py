#!/usr/bin/env python
##############################################################################
#
# (c) 2013-2025 The Trustees of Columbia University in the City of New York.
# All rights reserved.
#
# File coded by: Xiaohao Yang and Billinge Group members
#
# See GitHub contributions for a more detailed list of contributors.
# https://github.com/diffpy/diffpy.distanceprinter/graphs/contributors
# noqa: E501
#
# See LICENSE.rst for license information.
#
##############################################################################

import sys

import numpy as np

from diffpy.pdffit2 import PdfFit
from diffpy.structure import PDFFitStructure


def calDistance(strufile, atomi, atomj, lb, ub, complete):

    stru = PDFFitStructure(filename=strufile)
    pdffit = PdfFit()
    pdffit.add_structure(stru)
    ele = stru.element

    rv = pdffit.bond_length_types(atomi, atomj, lb, ub)
    dij = np.around(rv["dij"], 6)
    ddij = np.around(rv["ddij"], 10)
    rv["all0ddij"] = np.all(ddij == 0)
    ij0 = rv["ij0"]

    chardtype = "S8" if complete else "S4"
    dtypec = [
        ("distance", float),
        ("dd", float),
        ("i", chardtype),
        ("j", chardtype),
    ]
    distlist = np.zeros(len(dij), dtype=dtypec)

    if not complete:
        for i, dist, dd, ij in zip(range(len(dij)), dij, ddij, ij0):
            if ij[0] > ij[1]:
                distlist[i] = (dist, dd, ele[ij[1]], ele[ij[0]])
            else:
                distlist[i] = (dist, dd, ele[ij[0]], ele[ij[1]])
        distlist = np.unique(distlist)
    else:
        for i, dist, dd, ij in zip(range(len(dij)), dij, ddij, ij0):
            distlist[i] = (
                dist,
                dd,
                "%s.%i" % (ele[ij[0]], ij[0]),
                "%s.%i" % (ele[ij[1]], ij[1]),
            )

    distlist.sort(order="distance")
    rv["distlist"] = distlist
    rv["atomi"] = atomi
    rv["atomj"] = atomj
    rv["lb"] = lb
    rv["ub"] = ub
    rv["complete"] = complete
    rv["stru"] = stru
    rv["strufile"] = strufile
    return rv


def formatResults(stru, distlist, complete, all0ddij, **kw):
    """Format the distlist to string."""
    lines = []
    # header
    lines.append("# Structure file: %s" % kw["strufile"])
    lines.append("# ")
    strustr = stru.__str__().splitlines()
    lines.append("# " + strustr[0])
    for i in range(1, len(strustr)):
        lines.append("# %2i " % (i - 1) + strustr[i])
    lines.append("# ")
    lines.append(
        "# Inter-atomic distance of (%s, %s) in (%2.2f, %2.2f) A"
        % (kw["atomi"], kw["atomj"], kw["lb"], kw["ub"])
    )
    lines.append("")

    if complete:
        for dist in distlist:
            try:
                lines.append(
                    "%s-%s:\t%2.6f"
                    % (
                        dist[2].decode("utf-8"),
                        dist[3].decode("utf-8"),
                        dist[0],
                    )
                )
            except AttributeError:
                lines.append("%s-%s:\t%2.6f" % (dist[2], dist[3], dist[0]))
    else:
        for dist in distlist:
            try:
                lines.append(
                    "%s-%s:\t%2.6f (%1.1e)"
                    % (
                        dist[2].decode("utf-8"),
                        dist[3].decode("utf-8"),
                        dist[0],
                        dist[1],
                    )
                )
            except AttributeError:
                lines.append(
                    "%s-%s:\t%2.6f (%1.1e)"
                    % (dist[2], dist[3], dist[0], dist[1])
                )
    rv = "\n".join(lines)
    return rv


def writeToFile(filename, rv):
    f = open(filename, "w", encoding="utf-8")
    try:
        rv = rv.decode("utf-8")
        f.write(rv)
        f.close()
    except AttributeError:
        # No need to decode in python 3
        f.write(rv)
        f.close()
        pass


def main():
    sysargv = sys.argv[1:]
    strufile, atomi, atomj, lb, ub, complete, filename = sysargv
    lb = float(lb)
    ub = float(ub)
    complete = "1" == complete
    rv = calDistance(strufile, atomi, atomj, lb, ub, complete)
    strv = formatResults(**rv)
    writeToFile(filename, strv)
    return


if __name__ == "__main__":
    main()
