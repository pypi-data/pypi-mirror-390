from typing import Dict, List, Optional
class tableGen:
    """ Generate tables from data dictionaries.
        Data format: data[config][workload] = value
    """
    def __init__(
        self,
        data: Dict[str, Dict[str, float]]):
        self.data = data
    def generate_table(self) -> str:
        """ Generate a plain text table from the given data dictionary.
            Table format: 
            ## Metric Name ##
            | Benchmark | Config1 | Config2 | ... |
            |---------|---------|---------|-----|
            | wl1     | val1    | val2    | ... |
        """
        table_str = "## Metric Table ##\n"
        # Header
        header = "| Benchmark | " + " | ".join(self.data.keys()) + " |\n"
        separator = "|---------|" + "---------|" * len(self.data) + "\n"
        table_str += header
        table_str += separator
        # Rows
        workloads = list(next(iter(self.data.values())).keys())
        for wl in workloads:
            row = f"| {wl} | " + " | ".join(f"{self.data[conf][wl]:.2f}" for conf in self.data) + " |\n"
            table_str += row
        return table_str
    
    def generate_latex(self)->str:
        r""" Generate a LaTeX table from the given data dictionary.
            Table format: 
            \begin{tabular}{|c|c|c|...|}
            \hline
            Benchmark & Config1 & Config2 & ... \\
            \hline
            wl1 & val1 & val2 & ... \\
            ...
            \hline
            \end{tabular}
        """
        table_str = "\\begin{tabular}{|" + "c|" * (len(self.data) + 1) + "}\n\\hline\n"
        # Header
        header = "Benchmark & " + " & ".join(self.data.keys()) + " \\\\\n\\hline\n"
        table_str += header
        # Rows
        workloads = list(next(iter(self.data.values())).keys())
        for wl in workloads:
            row = f"{wl} & " + " & ".join(f"{self.data[conf][wl]:.2f}" for conf in self.data) + " \\\\\n\\hline\n"
            table_str += row
        table_str += "\\end{tabular}\n"
        return table_str