import sourmash
from sourmash.lca import taxlist, LineagePair, lca_utils
import collections

import plotly.graph_objects as go
import seaborn as sns

class GenomeSankeyFlow:
    "Build and track 'flow' of hash/k-mer idents across taxonomic ranks."
    def __init__(self, stop_rank="species", count_item="k=mers"):
        # index for lineages
        self.next_index = 0
        self.index_d = {}

        # src/dest connections for links in sankey diagram
        self.links_d = {}

        # track colors by lineage
        self.default_color = "lightgrey"
        self.colors = {}

        # What items are we counting (changes reporting output)
        self.count_item = count_item # e.g. k-mers, genomes

        # build the set of (rank1, rank2) for all pairs; stop at species.
        taxlist_pairs = []
        for rank in taxlist():
            if rank == 'superkingdom':
                last_rank = rank
                continue
            if last_rank == stop_rank:
                break
            taxlist_pairs.append((last_rank, rank))
            last_rank = rank
        self.taxlist_pairs = tuple(taxlist_pairs)

        # build a lineage w/unassigned at each rank for potential use.
        unassigned_lin = []
        for rank in taxlist():
            if rank == 'species':
                break
            unassigned_lin.append(LineagePair(rank, 'unassigned'))

        self.unassigned_lin = tuple(unassigned_lin)

    def get_index(self, lin):
        "For the given lineage, return or create & return unique index."
        lin = tuple(lin)
        if lin not in self.index_d:
            self.index_d[lin] = self.next_index
            self.next_index += 1
        return self.index_d[lin]

    def make_labels(self):
        "Make the labels in index order."
        linlist = list(self.index_d.items())
        linlist.sort(key = lambda x: x[1])
        return [ lin[-1].name for lin, idx in linlist ]

    def add_link(self, lin, src_rank, dest_rank, count):
        "build a link for lineage from src_rank to dest_rank. Use color/count."
        src_lin = lca_utils.pop_to_rank(lin, src_rank)
        dest_lin = lca_utils.pop_to_rank(lin, dest_rank)

        dest = self.get_index(dest_lin)
        src = self.get_index(src_lin)
        dest_d = self.links_d.get(src, {})

        total_count = dest_d.get(dest, 0)
        total_count += count

        dest_d[dest] = total_count
        self.links_d[src] = dest_d

    def make_links(self, counts, show_unassigned=False):
        "Put all of the links together."
        # collect the set of lineages to display
        # note: could add a filter function to focus in on a specific 'un
        full_lins = set(counts.keys())
        if not show_unassigned:
            if self.unassigned_lin in full_lins:
                full_lins.remove(self.unassigned_lin)

        for lin in full_lins:
            count = counts[lin]
            for last_rank, rank in self.taxlist_pairs:
                self.add_link(lin, last_rank, rank, count)

        self.sum_counts = sum(counts.values())


    def make_lists(self):
        "Construct lists suitable for handing to plotly link."
        src_l = []                        # source of link
        dest_l = []                       # destination link
        cnt_l = []                        # size/count of link
        color_l = []                      # color of link
        label_l = []                      # label for link

        # now, put together set of links.
        for k in sorted(self.links_d):
            for j in sorted(self.links_d[k]):
                # note here that the indices in links_d are indices into
                # labels.
                src_l.append(k)
                dest_l.append(j)

                # retrieve color & counts...
                counts = self.links_d[k][j]
                cnt_l.append(counts)

                # calculate percent of counts.
                if self.sum_counts:
                    pcnt = counts / self.sum_counts * 100
                    #label_l.append(f'{pcnt:.1f}% of total k-mers')
                    label_l.append(f'{pcnt:.1f}% of total {self.count_item}')
                else:
                    label_l.append("no counts")

        # last but not least, put together color for the links.
        linlist = list(self.index_d.items())
        linlist.sort(key = lambda x: x[1])
        idx = 0
        color_l = []
        for k in sorted(self.links_d):
            for j in sorted(self.links_d[k]):
                link_lin = linlist[j][0]
                color = self.default_color


                for color_lin, color_name in self.colors.items():
                    if lca_utils.is_lineage_match(link_lin, color_lin,
                                              link_lin[-1].rank):
                        color = color_name
                        break

                color_l.append(color)
                idx += 1

        return src_l, dest_l, cnt_l, color_l, label_l

