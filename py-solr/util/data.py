import re


#############################################################################
# Data helpers
def parse_results(fd, converter):
    converter_len = len(converter)

    results = []
    skipped = []
    for line in fd:
        if line not in ['\n', '\r\n']:
            fields = re.split(r',', line.strip())
            length = len(fields)
            if length == converter_len:
                record = tuple(
                    [converter[i](fields[i]) for i in xrange(length)])
                results.append(record)
            else:
                skipped.append(fields)

    return results, skipped


def load_csv(files, converter, results, skipped):
    for f in files:
        try:
            with open(f, 'r') as data:
                r, s = parse_results(data, converter)

            # Remove the anything after the last point
            name = "%s" % (".".join(f.split(".")[:-1]))

            results.append((name, r))
            skipped.append((name, s))
        except IOError:
            pass
