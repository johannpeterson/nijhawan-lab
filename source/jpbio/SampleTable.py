# jpbio.SampleTable

import re
import csv

class SampleTable:
    """Class to read and manage tables of samples, and map from primer pairs to sample names."""

# example samples.tsv:
# oVK026	oVK38	oVK39	oVK40	oVK41	oVK42	oVK43	oVK44	oVK45	oVK46	oVK47	oVK48
# oVK025	1557	1558	1559	1560	1561	1562	1563	1564	1565	1566	1567	1568
# oVK031	1569	1570	1571	1572	1573	1574	1575	1576	1577	1615	1616	1629
# oVK032	1630	1631	1701	1646	1647	1648	1649	1650	1651	1652	1653	1654
# oVK033	1655	1656	1657	1658	1659	1660	1661	1662	1663	1664	1665	1666
# oVK034	1667	1668	1669	1670	1671	1672	1673	1674	1675	1676	1677	1678
# oVK035	1679	1680	1681	1682	245	289	431	water				
# oVK036												
# oVK037												

    primer_name_regex = re.compile(r"(oVK)(\d{1,3})")

    def pad_primer_name(s):
        m = SampleTable.primer_name_regex.match(s)
        return m.group(1) + m.group(2).rjust(3, '0')

    def __init__(self):
        self.sample_dict = {}

    def readSampleFile(self, filename):
        with open(filename, "r") as f:
            csvraw = list(csv.reader(f, delimiter='\t'))
        col_headers = [SampleTable.pad_primer_name(h) for h in csvraw[0][1:]]
        row_headers = [SampleTable.pad_primer_name(row[0]) for row in csvraw[1:]]
        data = [row[1:] for row in csvraw[1:]]
        # sample_list = [s for sublist in data for s in sublist if s != '']
        self.sample_dict = {row_headers[r]:{col_headers[c]:data[r][c] for c in range(len(col_headers))} for r in range(0, len(row_headers))}

    def lookupSampleByPrimers(self, fwd, rev):
        try:
            sample = self.sample_dict[fwd][rev]
        except KeyError:
            sample = None
        return sample

