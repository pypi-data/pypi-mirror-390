from champsimextract.misc.MetricAggr import MetricAggregator

def geomean(values:list)->float:
    """Calculates the geometric mean of a list of values."""
    product = 1.0
    n = len(values)
    for v in values:
        product *= v
    return product ** (1.0 / n)

GEOMEAN = MetricAggregator(
    name="geomean",
    reducer=geomean
)
AVERAGE = MetricAggregator(
    name="average",
)
