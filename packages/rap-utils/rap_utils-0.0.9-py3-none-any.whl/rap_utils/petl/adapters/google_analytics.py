import petl as etl
import numpy as np
from google.analytics.data_v1beta import BetaAnalyticsDataClient


class GoogleAnalytics4(object):
    """Class encapsulating access to GA4 reports"""

    def __init__(self):
        self.client = BetaAnalyticsDataClient()

    def run_report(self, request):
        """Runs a simple report on a Google Analytics 4 property."""
        response = self.client.run_report(request)
        header = [c.name for c in response.dimension_headers] + \
            [c.name for c in response.metric_headers]
        data = np.transpose([[c.value for c in row.dimension_values] +
                            [c.value for c in row.metric_values] for row in response.rows])

        return etl.fromcolumns(data, header=header)
