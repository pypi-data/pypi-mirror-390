from soda.sampler.sample_context import SampleContext
from soda.sampler.sampler import Sampler

from .sample_writer import write_samples

# Create a custom sampler by extending the Sampler class


class CustomSampler(Sampler):
    def __init__(self, output_format, write_all_cols):
        super().__init__()
        self.output_format = output_format
        self.write_all_cols = write_all_cols

    def store_sample(self, sample_context: SampleContext):
        cols = list(map(lambda x: x.name, sample_context.sample.get_schema().columns))
        # Retrieve the rows from the sample for a check
        rows = sample_context.sample.get_rows()
        # Check SampleContext for more details that you can extract
        # This example simply prints the failed row samples
        # print(sample_context.query)
        # print(sample_context.sample.get_schema())

        # For each row, zip the column names and the row values together
        row_dicts = list(map(lambda row: dict(zip(cols, row)), rows))

        col_name = sample_context.column.column_name  # e.g. "state_id"
        table_name = sample_context.column.table.table_name  # e.g. "agencies"

        write_samples(
            table_name, col_name, row_dicts, self.output_format, self.write_all_cols
        )
