import pandas as pd
import random


def classify_time(hour):
    if 8 <= hour < 14:
        return '[08 a.m - 2 p.m)'
    elif 14 <= hour < 20:
        return '[2 p.m - 8 p.m)'
    elif 20 <= hour < 3:
        return '[8 p.m - 3 a.m)'
    else:
        return '[3 a.m - 8 a.m)'


def agg_ocr_data_from_raw(utc_offset):
    df = pd.read_csv('../../PROD/Santander_examples/Santander-MEX_OCR_ANDROID_2172_2024-01-01_2024-01-25.csv')

    offset_timedelta = pd.Timedelta(hours=utc_offset)
    # Leo, be aware of respecting the same date format across modalities and SDK versions.
    # I believe finger is not the same format.
    df['TransactionTimeinUTC'] = pd.to_datetime(df['TransactionTimeinUTC'],
                                                format='%Y-%m-%d %H:%M:%S')  # 2024-01-23 06:24:53
    df['TransactionTimeAdjusted'] = df['TransactionTimeinUTC'] + offset_timedelta
    df['Weekday'] = df['TransactionTimeAdjusted'].dt.strftime('%A')
    df['Daytime'] = df['TransactionTimeAdjusted'].dt.hour.apply(classify_time)
    df['Date'] = df['TransactionTimeAdjusted'].dt.date

    df['CardFrom'].fillna("NA", inplace=True)
    df['DocSubType'].fillna("NA", inplace=True)
    df['CardSide'].fillna("NA", inplace=True)

    df_grouped = df.groupby(['Date', 'Weekday', 'Daytime', 'Action', 'TransactionType', 'CardFrom', 'CardType',
                             'DocSubType', 'SdkVersion', 'CardSide']).size().reset_index(name='Transactions')

    df_grouped.to_csv('agg_ocr_2172_before_2.14.2.csv')

    card_from = ["CAMERA", "GALLERY"]
    front_weights = [0.75, 0.25]
    card_subtypes = ["C", "D", "E", "F", "G", "H"]
    subtypes_weights = [0.1, 0.35, 0.15, 0.17, 0.07, 0.1]
    card_side = ["FRONT", "BACK", "BOTH"]
    side_weights = [0.14, 0.12, 0.74]

    df['CardFrom'] = df.apply(
        lambda row: random.choices(card_from, front_weights)[0] if row['CardFrom'] == 'NA' else row['CardFrom'], axis=1)
    df['DocSubType'] = df.apply(lambda row: random.choices(card_subtypes, subtypes_weights)[0] if row[
                                                                                                      'CardType'] == 'MEX_NATIONAL_ID' else "NA",
                                axis=1)
    df['CardSide'] = df.apply(
        lambda row: random.choices(card_side, side_weights)[0] if row['CardType'] == 'MEX_NATIONAL_ID' else "FRONT",
        axis=1)

    df_grouped = df.groupby(['Date', 'Weekday', 'Daytime', 'Action', 'TransactionType', 'CardFrom', 'CardType',
                             'DocSubType', 'SdkVersion', 'CardSide']).size().reset_index(name='Transactions')

    df_grouped.to_csv('agg_ocr_2172_from_2.14.2.csv')


if __name__ == '__main__':
    agg_ocr_data_from_raw(-7)
