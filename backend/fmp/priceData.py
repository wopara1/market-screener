import pandas as pd

class PriceData:
    def __init__(self, data):
        self.data = self.validate_and_prepare_data(data)

    def validate_and_prepare_data(self, data):
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Input data must be a pandas DataFrame.")

        if 'date' in data.columns:
            data.rename(columns={'date': 'timestamp'}, inplace=True)

        required_columns = ['timestamp', 'symbol', 'exchange', 'open', 'high', 'low', 'close', 'volume', 'timeframe']
        if not all(col in data.columns for col in required_columns):
            missing_cols = [col for col in required_columns if col not in data.columns]
            raise ValueError(f"Missing required columns: {missing_cols}")

        try:
            data['timestamp'] = pd.to_datetime(data['timestamp'])
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid timestamp format: {e}")

        for col in ['open', 'high', 'low', 'close', 'volume']:
            data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0) 

        return data.set_index('timestamp')

    def __str__(self):
        if self.data is None:
            return "No data to display."

        header = ["Timestamp", "Symbol", "Exchange", "Open", "High", "Low", "Close", "Volume", "Timeframe"]
        data_list = []
        for index, row in self.data.reset_index().iterrows():
            data_list.append([
                str(row['timestamp']),
                row['symbol'],
                row['exchange'],
                row['open'],
                row['high'],
                row['low'],
                row['close'],
                row['volume'],
                row['timeframe']
            ])

        max_lengths = [max(len(str(item)) for item in col) for col in zip(*([header] + data_list))]
        formatted_header = " | ".join(name.ljust(length) for name, length in zip(header, max_lengths))
        formatted_rows = [" | ".join(str(item).ljust(length) for item, length in zip(row, max_lengths)) for row in data_list]

        return "\n".join([formatted_header] + formatted_rows)

    def iterrows(self):
        for index, row in self.data.iterrows():
            yield {
                'timestamp': index,
                'symbol': row['symbol'],
                'exchange': row['exchange'],
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'close': row['close'],
                'volume': row['volume'],
                'timeframe': row['timeframe']
            }