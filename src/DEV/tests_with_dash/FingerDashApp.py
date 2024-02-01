import sys
from datetime import datetime

import dash
import pandas as pd
from dash import html
from dash import dcc

from dash.dependencies import Input, Output

from src.DEV.pages import overview
from utils import classify_time


class FingerDashApp:

    def __init__(self, csv_df, license_id, package_id, start_date, end_date, utc_offset):
        self.csv_df = csv_df
        self.license_id = license_id
        self.package_id = package_id
        self.start_date = start_date
        self.end_date = end_date
        self.utc_offset = utc_offset

        self.df_trx_summary = pd.DataFrame()
        self.df_detection_modes = pd.DataFrame()
        self.df_agg_trx_weekdays = pd.DataFrame()
        self.df_agg_trx_over_time = pd.DataFrame()

        # Dash App
        self.app = dash.Dash(__name__)
        self.app.title = "PRODUCT ACTIVITY OVERVIEW"
        self.server = self.app.server

        # Describe the layout/ UI of the app
        self.app.layout = html.Div(
            [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
        )

        # Update page
        @self.app.callback(Output("page-content", "children"), [Input("url", "pathname")])
        def display_page(path):
            return overview.create_layout(self.app, self.license_id, self.package_id, self.start_date, self.end_date,
                                          self.df_trx_summary, self.df_detection_modes, self.df_agg_trx_weekdays,
                                          self.df_agg_trx_over_time)

    def generate_csv(self):
        # 1. Generate df_trx_summary
        num_rows = len(self.csv_df)
        # For debugging
        # spoofs = df[df['Spoof'] == 'Y'].shape[0]
        # no_spoofs = df[df['Spoof'] == 'N'].shape[0]
        spoof_percentage = f"{(self.csv_df[self.csv_df['Spoof'] == 'N'].shape[0] / num_rows * 100):.2f}%"

        # For debugging
        # invalid = df[df['TransactionType'] == 'INVALID'].shape[0]
        # valid = df[df['TransactionType'] == 'VALID'].shape[0]
        invalid_percentage = f"{(self.csv_df[self.csv_df['TransactionType'] == 'INVALID'].shape[0] / num_rows * 100):.2f}%"

        unique_device_ids = self.csv_df['UniqueDeviceId'].nunique()
        num_capture = self.csv_df[self.csv_df['Action'] == 'CAPTURE'].shape[0]
        num_enroll = self.csv_df[self.csv_df['Action'] == 'ENROLL'].shape[0]
        num_verify = self.csv_df[self.csv_df['Action'] == 'VERIFY'].shape[0]
        data = {
            'A': ['Total Transactions', 'Spoof Rate', 'Capture Error Rate', ' Unique Devices', '',
                  'Capture Transactions', 'Enroll Transactions', 'Verify Transactions'],
            # 'Spoof', 'NoSpoof', 'Invalid', 'Valid'
            'B': [num_rows, spoof_percentage, invalid_percentage, unique_device_ids, '',
                  num_capture, num_enroll, num_verify]
            # spoofs, no_spoofs, invalid, valid,
        }

        self.df_trx_summary = pd.DataFrame(data)

        # 2. Generate df_detection_mode
        self.df_detection_modes = self.csv_df.groupby(['DetectionMode', 'SdkVersion']).agg(
            {'TransactionId': 'count'}).reset_index()
        self.df_detection_modes.columns = ['DetectionMode', 'SdkVersion', 'Total']

        # 3. Generate df_agg_trx_over_time and df_agg_trx_weekdays
        self.csv_df['TransactionTimeinUTC'] = pd.to_datetime(self.csv_df['TransactionTimeinUTC'],
                                                             format='%d/%m/%y %H:%M')
        offset_timedelta = pd.Timedelta(hours=self.utc_offset)
        self.csv_df['TransactionTimeAdjusted'] = self.csv_df['TransactionTimeinUTC'] + offset_timedelta
        self.csv_df['Weekday'] = self.csv_df['TransactionTimeAdjusted'].dt.strftime('%A')
        self.csv_df['Daytime'] = self.csv_df['TransactionTimeAdjusted'].dt.hour.apply(classify_time)
        self.csv_df['Date'] = self.csv_df['TransactionTimeAdjusted'].dt.date

        self.df_agg_trx_over_time = self.csv_df.groupby(['Date', 'Action', 'Spoof', 'SdkVersion']).size().reset_index(
            name='Transactions')
        start_date_q = datetime.strptime(self.start_date, "%d/%m/%y").date()
        self.df_agg_trx_over_time = self.df_agg_trx_over_time[self.df_agg_trx_over_time['Date'] >= start_date_q]

        # df_agg_trx_over_time.to_csv('test.csv')
        self.df_agg_trx_weekdays = self.csv_df.groupby(['Weekday', 'Daytime']).size().reset_index(name='Total')

    def run_finger_dash(self):
        self.generate_csv()
        self.app.run_server(debug=True, dev_tools_hot_reload=False, dev_tools_prune_errors=False)
        # self.app.run_server(debug=True)


if __name__ == '__main__':
    csv_path_str = sys.argv[1]
    license_id_str = sys.argv[2]
    package_id_str = sys.argv[3]
    start_date_str = sys.argv[4]
    end_date_str = sys.argv[5]
    utc_offset_int = int(sys.argv[6])

    df = pd.read_csv(csv_path_str, sep=',')
    finger_dash_app = FingerDashApp(df, license_id_str, package_id_str, start_date_str, end_date_str,
                                    utc_offset_int)
    finger_dash_app.run_finger_dash()
