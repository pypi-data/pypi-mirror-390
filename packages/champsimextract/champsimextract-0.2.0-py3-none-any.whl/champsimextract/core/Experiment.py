from dataclasses import dataclass
from champsimextract.core.ChampsimLog import ChampsimLogCollection
from champsimextract.core.metrics import Metric
from champsimextract.plotting import plotter,tableGen
from champsimextract.misc.MetricAggr import MetricAggregator 

@dataclass
class Configuration:
    """
    Represents a single configuration in an experiment, holding its name and associated log collection.
    """
    name: str
    logCollection: ChampsimLogCollection

    def __init__(self, name: str, logdir: str,get_workload_name_from_log_filename, get_simpoint_from_log_filename):
        """
        Initializes the Configuration with a name and a directory containing Champsim logs.
        Args:
            name (str): The name of the configuration.
            logdir (str): The directory containing Champsim logs for this configuration.
            get_workload_name_from_log_filename (function): Function to extract workload name from log path. Example if filename is sssp-10.txt, this function should return sssp. Customize as per your filename structure.
            get_simpoint_from_log_filename (function): Function to extract simpoint from log path. Example if filename is sssp-10.txt, this function should return 10. Customize as per your filename structure.
        """
        self.name = name
        self.logCollection = ChampsimLogCollection(log_dir=logdir)
        self.get_workload_name_from_log_filename = get_workload_name_from_log_filename
        self.get_simpoint_from_log_filename = get_simpoint_from_log_filename
    def get_data_dict(self, metric: Metric) -> dict:
        """ Format: data[workload][simpoint] = value
            Args:
                metric (Metric): The metric object used to extract values from a log file. 
            Returns:
                dict: A nested dictionary with workload names as keys, each containing another dictionary with simpoints as keys and metric values as values.
        """
        data = {}
        for log in self.logCollection.logs:
            if self.get_workload_name_from_log_filename(log.path) not in data:
                data[self.get_workload_name_from_log_filename(log.path)] = {}
            if self.get_simpoint_from_log_filename(log.path) not in data:
                data[self.get_workload_name_from_log_filename(log.path)][self.get_simpoint_from_log_filename(log.path)] = None
            data[self.get_workload_name_from_log_filename(log.path)][self.get_simpoint_from_log_filename(log.path)] = metric.get_val(log)
        return data

@dataclass
class Experiment:
    """
    Represents an experiment consisting of multiple configurations.
    Capable of plotting metrics across configurations and generating tables."""
    name: str
    configurations: list[Configuration]

    def __init__(self, name: str, configurations: dict[str, str],get_workload_name_from_log_filename, get_simpoint_from_log_filename):
        """
        Initializes the Experiment with a name and multiple configurations.
        Args:
            name (str): The name of the experiment.
            configurations (dict): A dictionary mapping configuration names to their respective log directories.
            get_workload_name_from_log_filename (function): Function to extract workload name from log path.
            get_simpoint_from_log_filename (function): Function to extract simpoint from log path.
        """
        self.name = name
        self.configurations = []
        for config_name, logdir in configurations.items():
            config = Configuration(name=config_name, logdir=logdir, get_workload_name_from_log_filename=get_workload_name_from_log_filename, get_simpoint_from_log_filename=get_simpoint_from_log_filename)
            self.configurations.append(config)
    
    def get_data_dict(self,metric:Metric) -> dict:
        """ Format: data[config][workload] = value
            Args:
                metric (Metric): The metric object used to extract values from log files across configurations.
            Returns:
                dict: A nested dictionary with configuration names as keys, each containing another dictionary with workload names as keys and metric values as values.
        """
        data = {}
        for config in self.configurations:
            data[config.name] = config.get_data_dict(metric)

        return data
    
    def get_reduced_data_dict(self, metric: Metric, aggregator: MetricAggregator) -> dict:
        """ Format: data[config][workload] = reduced_value
            Collapses multiple simpoints per workload using the provided aggregator. 
            For example if sssp has 4 simpoints and the aggregator uses geomean it will compute geomean across those 4 simpoints and assign that to sssp.
            Args:
                metric (Metric): The metric object used to extract values from log files across configurations.
                aggregator (MetricAggregator): The aggregator object used to reduce metric values.
            Returns:
                dict: A nested dictionary with configuration names as keys, each containing another dictionary with workload names as keys and reduced metric values as values.
        """
        data = self.get_data_dict(metric)
        data = aggregator.reduce_data(data)
        return data

    def get_reduced_data_dict_with_avg(self,metric: Metric, aggregator: MetricAggregator) -> dict:
        """ Format: data[config][workload] = reduced_value
            Collapses multiple simpoints per workload using the provided aggregator and adds an average entry.
            For example if sssp has 4 simpoints and the aggregator uses geomean it will compute geomean across those 4 simpoints and assign that to sssp.
            Additionally, it will compute the average across all workloads using the same aggregator and add it as a special entry.
            Args:
                metric (Metric): The metric object used to extract values from log files across configurations.
                aggregator (MetricAggregator): The aggregator object used to reduce metric values.
            Returns:
                dict: A nested dictionary with configuration names as keys, each containing another dictionary with workload names as keys and reduced metric values as values, including an average entry.
        """
        data = self.get_data_dict(metric)
        data = aggregator.add_avg(data)
        return data
    
    def plot(self, metric: Metric, aggregator: MetricAggregator,savepath:str="", plot_type: str="bar",**plot_kwargs):
        """ Plot the given metric across configurations using the specified plot type.
            Args:
                metric (Metric): The metric object used to extract values from log files across configurations.
                aggregator (MetricAggregator): The aggregator object used to reduce metric values.
                savepath (str): The file path to save the generated plot. If empty, the plot will be displayed instead of saved.
                plot_type (str): The type of plot to generate. Options are "bar", "stacked", or "line".
                **plot_kwargs: Additional keyword arguments to pass to the Plotter class. Some important ones include:
                    base_color (str): Base color for the plot.
                    ylabel (str): Label for the y-axis.
                    round_to (float): Rounding factor for y-axis limits.
                    delta_round (float): Delta rounding factor for y-axis ticks.
                    delta_factor (float): Delta scaling factor for y-axis ticks.
                    tune_yticks (bool): Whether to print y-ticks params to allow you to experiment and adjust to get a good figure.
        """

        data = self.get_reduced_data_dict_with_avg(metric, aggregator)
        plot = plotter.Plotter(data,plot_type,avg_key=aggregator.name, **plot_kwargs)
        plot.plot(savepath=savepath)

    
    def print_table(self, metric: Metric, aggregator: MetricAggregator,latex:bool=False) -> str:
        """ Generate a table of the given metric across configurations.
            Args:
                metric (Metric): The metric object used to extract values from log files across configurations.
                aggregator (MetricAggregator): The aggregator object used to reduce metric values.
                latex (bool): If True, generates the table in LaTeX format. Otherwise, generates a plain text table.
            Returns:
                str: The generated table as a string.
        """
        data = self.get_reduced_data_dict_with_avg(metric, aggregator)
        table = tableGen.tableGen(data)
        if latex:
            return table.generate_latex()
        return table.generate_table()
    
    def __str__(self) -> str:
        return f"Experiment(name={self.name}, num_configurations={len(self.configurations)})"

