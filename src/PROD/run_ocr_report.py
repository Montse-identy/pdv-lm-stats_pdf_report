import os.path
import random
import time

import pandas as pd
from fpdf import FPDF

import datetime

from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.colors as mcolors
from utils.AWSLambdaHandler import CustomError
from utils import AWSLambdaHandler

# Global Variables
# A4 dimensions
TITLE = "OCR Basic Report"
SUMMARY = "Analyzing data usage reveals trends and customer habits, enabling informed decision-making " \
          "that better aligns with client needs."
WIDTH = 210
HEIGHT = 297

INTERLINE = 5
LEFT_MARGIN = 6
LINE_SECTION_MARGIN = 9
LEFT_MARGIN_SECTION = 11
LEFT_MARGIN_SEPARATOR = 7

ORANGE = '#fae5d3'
BLUE = '#d6eaf8'
GREEN = '#d4efdf'
PURPLE = '#e8daef'

BASE_PATH = '/tmp'

# JPG as improves PDF generation performance by 3
PATH_OCR_SUMMARY_PNG = os.path.join(BASE_PATH, 'summary_ocr.jpg')
PATH_OCR_DOCS_CAPTURED_JPG_TYPE = os.path.join(BASE_PATH, 'captured_documents_type.jpg')
PATH_OCR_DOCS_CAPTURED_JPG_TYPE_SUBTYPE = os.path.join(BASE_PATH, 'captured_documents_type_subtype.jpg')
PATH_OCR_WEEKDAY_USAGE_JPG = os.path.join(BASE_PATH, 'weekday_usage.jpg')
PATH_OCR_TRANSACTIONS_PER_DAY_JPG = os.path.join(BASE_PATH, 'transactions_per_day.jpg')
PATH_OCR_TRANSACTIONS_PER_SDK_JPG = os.path.join(BASE_PATH, 'transactions_per_sdk.jpg')


def override_default_jpg_paths(new_root_path):
    global PATH_OCR_SUMMARY_PNG
    global PATH_OCR_DOCS_CAPTURED_JPG_TYPE
    global PATH_OCR_DOCS_CAPTURED_JPG_TYPE_SUBTYPE
    global PATH_OCR_WEEKDAY_USAGE_JPG
    global PATH_OCR_TRANSACTIONS_PER_DAY_JPG
    global PATH_OCR_TRANSACTIONS_PER_SDK_JPG
    global BASE_PATH

    BASE_PATH = new_root_path
    PATH_OCR_SUMMARY_PNG = os.path.join(BASE_PATH, 'summary_ocr.jpg')
    PATH_OCR_DOCS_CAPTURED_JPG_TYPE = os.path.join(BASE_PATH, 'captured_documents_type.jpg')
    PATH_OCR_DOCS_CAPTURED_JPG_TYPE_SUBTYPE = os.path.join(BASE_PATH, 'captured_documents_type_subtype.jpg')
    PATH_OCR_WEEKDAY_USAGE_JPG = os.path.join(BASE_PATH, 'weekday_usage.jpg')
    PATH_OCR_TRANSACTIONS_PER_DAY_JPG = os.path.join(BASE_PATH, 'transactions_per_day.jpg')
    PATH_OCR_TRANSACTIONS_PER_SDK_JPG = os.path.join(BASE_PATH, 'transactions_per_sdk.jpg')


def create_identy_logo(pdf, WIDTH):
    # IDENTY Logo
    pdf.image("./resources/identy_logo.png", 0, 10, 90, )
    pdf.ln(15)


def create_title(title, subtitle, pdf):
    # Add main title
    pdf.set_font('Helvetica', '', 16)
    pdf.set_text_color(r=30, g=30, b=30)
    pdf.write(10, " " + title)
    pdf.ln(7)

    # Add subtitle
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(r=120, g=120, b=120)
    pdf.write(10, " " + subtitle)

    # Add image on the left
    pdf.image("./resources/separator_title.png", x=LEFT_MARGIN_SEPARATOR, y=25)

    # Add line break
    pdf.ln(12)


def write_to_pdf(pdf, words):
    # Set text colour, font size, and font type
    pdf.set_text_color(r=10, g=10, b=10)
    pdf.set_font('Helvetica', '', 10)

    pdf.write(INTERLINE, words)


def create_section(pdf, section_name, y_pos):
    # Set text colour, font size, and font type
    pdf.set_text_color(r=30, g=30, b=30)
    pdf.set_font('Helvetica', '', 11)

    # pdf.text(x=WIDTH / 2, y=40, txt=section_name.upper())
    pdf.text(x=LEFT_MARGIN_SECTION, y=y_pos - 2, txt=section_name)
    pdf.image("./resources/separator_section.png", x=LINE_SECTION_MARGIN, y=y_pos)

    pdf.ln(10)


def create_subsection_two_plots(pdf, subsection_name_1, image_1, subsection_name_2, image_2, y_pos):
    plot_width = WIDTH * 0.45

    # Set text colour, font size, and font type
    pdf.set_text_color(r=10, g=10, b=10)
    pdf.set_font('Helvetica', '', 11)

    # pdf.text(x=WIDTH / 2, y=40, txt=section_name)
    pdf.text(x=LEFT_MARGIN * 2, y=y_pos + 5, txt=subsection_name_1)
    pdf.text(x=WIDTH / 2 + 10, y=y_pos + 5, txt=subsection_name_2)

    pdf.image("./resources/separator_subsection.png", x=LEFT_MARGIN_SEPARATOR + 1, y=y_pos)
    pdf.image("./resources/separator_subsection.png", x=WIDTH / 2 + LEFT_MARGIN, y=y_pos)

    pdf.image(image_1, x=LEFT_MARGIN, y=y_pos + 10, w=plot_width)
    pdf.image(image_2, x=WIDTH / 2 + LEFT_MARGIN, y=y_pos + 13, w=plot_width)


def create_subsection_one_plot(pdf, subsection_name_1, image_1, y_pos):
    plot_width = WIDTH * 0.80

    # Set text colour, font size, and font type
    pdf.set_text_color(r=10, g=10, b=10)
    pdf.set_font('Helvetica', '', 11)

    # pdf.text(x=WIDTH / 2, y=40, txt=section_name)
    pdf.text(x=LEFT_MARGIN * 2, y=y_pos + 5, txt=subsection_name_1)

    pdf.image("./resources/separator_subsection.png", x=LEFT_MARGIN_SEPARATOR + 1, y=y_pos)

    pdf.image(image_1, x=LEFT_MARGIN_SEPARATOR * 3.3, y=y_pos + 13, w=plot_width)


def create_table(df_in, rel_path_jpg):
    '''
    # We cannot use DFI on AWS python lambdas without installing chrome
    df_styled = df_in.style.hide(axis="index"). \
        hide(axis="columns"). \
        set_properties(**{'text-align': 'left', 'font-size': '14px'}). \
        set_properties(subset=['Metric'], **{'width': '250px'}). \
        set_properties(subset=['Value'], **{'width': '100px'})
    dfi.export(df_styled, rel_path_jpg, dpi=300)
    '''
    # plt.switch_backend('agg')
    fig, ax = plt.subplots()

    cell_text = []
    for row in range(len(df_in)):
        cell_text.append(df_in.iloc[row].tolist())

    table = ax.table(cellText=cell_text, loc='center', cellLoc='left')
    table.auto_set_font_size(False)
    table.set_fontsize(14)

    table.auto_set_column_width(col=list(range(len(df_in.columns))))
    table.scale(1.5, 4.2)

    for row in range(len(cell_text)):
        color = 'white' if row % 2 else '#f2f2f2'
        for col in range(len(df_in.columns)):
            table.get_celld()[(row, col)].set_facecolor(color)  # +1 para ajustar la posición de la fila

    # Eliminar los bordes de las celdas
    for key, cell in table.get_celld().items():
        cell.set_linewidth(0)

    # Ocultar los ejes
    plt.axis('off')

    plt.savefig(rel_path_jpg, bbox_inches='tight', dpi=300)


class PDF(FPDF):

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')


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
    df = pd.read_csv('Santander_examples/Santander-MEX_OCR_ANDROID_2172_2024-01-01_2024-01-25.csv')

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


def create_jpg_ocr_summary_table(df_in, output_path):
    num_transactions = df_in['Transactions'].sum()
    num_valid = df_in.groupby('TransactionType')['Transactions'].sum().get('VALID', 0)
    num_invalid = df_in.groupby('TransactionType')['Transactions'].sum().get('INVALID', 0)
    num_camera = df_in.groupby('CardFrom')['Transactions'].sum().get('CAMERA', 0)
    num_gallery = df_in.groupby('CardFrom')['Transactions'].sum().get('GALLERY', 0)

    if num_valid != 0:
        valid_per = num_valid * 100 / num_transactions
        valid_field = f"{num_valid} ({valid_per:.2f}%)"
    else:
        valid_field = f"{num_valid} ({0:.2f}%)"

    if num_invalid != 0:
        invalid_per = num_invalid * 100 / num_transactions
        invalid_field = f"{num_invalid} ({invalid_per:.2f}%)"
    else:
        invalid_field = f"{num_invalid} ({0:.2f}%)"

    data = {
        'Metric': ['Total Transactions', 'Total Valid', 'Total Invalid', 'Captures from Camera',
                   'Captures from Gallery'],
        'Value': [num_transactions, valid_field, invalid_field, num_camera, num_gallery]
    }

    df_ocr_summary = pd.DataFrame(data)
    create_table(df_ocr_summary, output_path)


def get_pastel_color(color, weight=0.6):
    """ Mix a color with white to obtain a pastel color. """
    rgb = mcolors.to_rgba(color)[:3]
    pastel_rgb = [1 - weight * (1 - c) for c in rgb]
    return mcolors.to_hex(pastel_rgb)


def create_jpg_transactions_per_day(df_in, rel_path):
    fig, ax = plt.subplots()

    df_grouped = df_in.groupby(['Date', 'DocType_DocSubType'])['Transactions'].sum().reset_index().sort_values('Date',
                                                                                                       inplace=False)

    card_from_categories = df_grouped['DocType_DocSubType'].unique()
    if len(card_from_categories) == 1:
        single_category_color = BLUE
        colors = [single_category_color]
    else:
        colors = [get_pastel_color(plt.cm.jet(i / float(len(card_from_categories) - 1))) for i in
                  range(len(card_from_categories))]

    for card_from, color in zip(card_from_categories, colors):
        data_filtered = df_grouped[df_grouped['DocType_DocSubType'] == card_from]
        data_filtered = data_filtered.sort_values('Date')
        ax.plot(data_filtered['Date'], data_filtered['Transactions'], label=card_from, color=color)

    ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
    # Format '15-Jan'
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
    format_plot(ax=ax, x_label='Date', y_label='Transactions', show_legend=True, legend_title='Model\n',
                grid_axis='Y', x_anchor_legend=1.5, y_anchor_legend=1)

    plt.savefig(rel_path, dpi=300, bbox_inches='tight')
    plt.close()


def create_jpg_transactions_per_sdk(df_in, rel_path):
    fig, ax = plt.subplots()

    df_grouped = df_in.groupby(['Date', 'SdkVersion'])['Transactions'].sum().reset_index().sort_values('Date',
                                                                                                       inplace=False)

    card_from_categories = df_grouped['SdkVersion'].unique()
    if len(card_from_categories) == 1:
        single_category_color = BLUE
        colors = [single_category_color]
    else:
        colors = [get_pastel_color(plt.cm.jet(i / float(len(card_from_categories) - 1))) for i in
                  range(len(card_from_categories))]

    for card_from, color in zip(card_from_categories, colors):
        data_filtered = df_grouped[df_grouped['SdkVersion'] == card_from]
        data_filtered = data_filtered.sort_values('Date')
        ax.plot(data_filtered['Date'], data_filtered['Transactions'], label=card_from, color=color)

    ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
    # Format '15-Jan'
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))

    format_plot(ax=ax, x_label='Date', y_label='Transactions', show_legend=True, legend_title='SDK Version\n',
                grid_axis='Y', x_anchor_legend=1.4, y_anchor_legend=1)

    plt.savefig(rel_path, dpi=300, bbox_inches='tight')
    plt.close()


def create_jpg_weekday_usage(df_in, rel_path):
    fig, ax = plt.subplots()

    df_grouped = df_in.groupby(['Weekday', 'Daytime'])['Transactions'].sum().unstack(fill_value=0)
    weekday_categories = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df_grouped = df_grouped.reindex(weekday_categories, fill_value=0)

    color_mapping = {
        '[08 a.m - 2 p.m)': GREEN,
        '[2 p.m - 8 p.m)': ORANGE,
        '[8 p.m - 3 a.m)': PURPLE,
        '[3 a.m - 8 a.m)': BLUE
    }

    daytime_categories = sorted(df_grouped.columns)

    bottom = None
    for daytime in daytime_categories:
        ax.bar(df_grouped.index, df_grouped[daytime], bottom=bottom, label=daytime,
               color=color_mapping.get(daytime, '#000000'))
        bottom = df_grouped[daytime] if bottom is None else bottom + df_grouped[daytime]

    ax.set_xticks(list(range(len(weekday_categories))))
    ax.set_xticklabels(weekday_categories, ha='center', fontsize=7)

    format_plot(ax=ax, x_label='Day of the week', y_label='Transactions', show_legend=True,
                legend_title='Time of the day\n',
                grid_axis='Y', x_anchor_legend=1.4, y_anchor_legend=1)

    plt.savefig(rel_path, dpi=300, bbox_inches='tight')
    plt.close()


def format_plot(ax, x_label, y_label, show_legend, legend_title, grid_axis, x_anchor_legend, y_anchor_legend):
    ax.set_xlabel(x_label, fontsize=10, labelpad=18)
    ax.set_ylabel(y_label, fontsize=10, labelpad=18)

    # ax.set_title('Transactions by Weekday and Daytime', fontsize=11, pad=10)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(True)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)

    if grid_axis == "Y":
        ax.yaxis.grid(True, which='major', color='lightgray', alpha=0.5, zorder=-1)
    if grid_axis == "X":
        ax.xaxis.grid(True, which='major', color='lightgray', alpha=0.5, zorder=-1)

    if show_legend:
        ax.legend(title=legend_title, loc='upper right', bbox_to_anchor=(x_anchor_legend, y_anchor_legend),
                  frameon=False)


def create_jpg_docs_captured_type_subtype(df_in, rel_path):
    df_grouped = df_in.groupby(['DocType_DocSubType', 'CardSide'])['Transactions'].sum().reset_index()
    df_grouped['Percentage'] = (df_grouped['Transactions'] / df_grouped['Transactions'].sum()) * 100
    df_grouped = df_grouped.sort_values(by='Percentage', ascending=False)

    fig, ax = plt.subplots()

    colors = {'FRONT': ORANGE,
              'BACK': GREEN,
              'BOTH': BLUE,
              'NA': BLUE}

    for card_side in df_grouped['CardSide'].unique():
        df_subset = df_grouped[df_grouped['CardSide'] == card_side]
        bars = ax.barh(df_subset['DocType_DocSubType'], df_subset['Percentage'], color=colors[card_side],
                       label=card_side)

    formatter = FuncFormatter(to_percent)
    ax.xaxis.set_major_formatter(formatter)

    ax.tick_params(axis='y', labelsize=7)
    format_plot(ax=ax, x_label='Percentage of Total Transactions', y_label='Document Model', show_legend=True,
                legend_title='Side\n', grid_axis='X', x_anchor_legend=1.3, y_anchor_legend=1)

    plt.xlim(0, 100)
    plt.savefig(rel_path, bbox_inches='tight', dpi=300)

    plt.close()


def to_percent(y, position):
    """ Converts a number into a string with a percentage symbol at the end. """
    return str(y) + '%'


def create_jpg_docs_captured_type(df_in, rel_path):
    df_grouped = df_in.groupby(['CardType', 'SdkVersion'])['Transactions'].sum().reset_index()
    df_grouped['Percentage'] = (df_grouped['Transactions'] / df_grouped['Transactions'].sum()) * 100

    fig, ax = plt.subplots()

    sdks_used = df_grouped['SdkVersion'].unique()
    captured_docs = df_grouped['CardType'].unique()

    if len(sdks_used) == 1:
        single_category_color = BLUE
        colors = [single_category_color]
    else:
        colors = [plt.cm.Pastel2(i / float(len(sdks_used) - 1)) for i in range(len(sdks_used))]

    color_mapping = {sdk: color for sdk, color in zip(sdks_used, colors)}

    bottom = None
    legend_added = {}
    for doc in captured_docs:
        for sdk in sdks_used:
            filtered_data = df_grouped[(df_grouped['SdkVersion'] == sdk) & (df_grouped['CardType'] == doc)]
            if len(filtered_data) == 0:
                percentage_value = 0
            else:
                percentage_value = filtered_data['Percentage'].values[0]

            if sdk not in legend_added:
                ax.bar(doc, percentage_value, bottom=bottom, label=sdk, color=color_mapping.get(sdk, '#000000'))
                legend_added[sdk] = True
            else:
                ax.bar(doc, percentage_value, bottom=bottom, color=color_mapping.get(sdk, '#000000'))

            bottom = percentage_value if bottom is None else bottom + percentage_value
        bottom = None

    ax.set_xticks(list(range(len(captured_docs))))
    ax.set_xticklabels(captured_docs, ha='center', fontsize=7)
    plt.ylim(0, 100)

    format_plot(ax=ax, x_label='Document Type', y_label='Percentage of Total Transactions', show_legend=True,
                legend_title='SDK Version\n', grid_axis='Y', x_anchor_legend=1.3, y_anchor_legend=1)

    plt.savefig(rel_path, bbox_inches='tight', dpi=300)

    plt.close()


def create_jpgs_for_ocr_report(ocr_df, rel_path_summary_jpg, rel_path_docs_captured_type,
                               rel_path_docs_captured_type_subtype,
                               rel_path_weekday_usage, rel_path_trx_per_day,
                               rel_path_trx_per_sdk):
    create_jpg_ocr_summary_table(ocr_df, rel_path_summary_jpg)
    create_jpg_docs_captured_type(ocr_df, rel_path_docs_captured_type)
    create_jpg_docs_captured_type_subtype(ocr_df, rel_path_docs_captured_type_subtype)
    create_jpg_weekday_usage(ocr_df, rel_path_weekday_usage)
    create_jpg_transactions_per_day(ocr_df, rel_path_trx_per_day)
    create_jpg_transactions_per_sdk(ocr_df, rel_path_trx_per_sdk)


def create_ocr_report(ocr_df, license_id, package_id, start_date, end_date, client, platform, output_folder,
                      rel_path_summary_jpg=PATH_OCR_SUMMARY_PNG,
                      rel_path_docs_captured_type=PATH_OCR_DOCS_CAPTURED_JPG_TYPE,
                      rel_path_docs_captured_type_subtype=PATH_OCR_DOCS_CAPTURED_JPG_TYPE_SUBTYPE,
                      rel_path_weekday_usage=PATH_OCR_WEEKDAY_USAGE_JPG,
                      rel_path_trx_per_day=PATH_OCR_TRANSACTIONS_PER_DAY_JPG,
                      rel_path_trx_per_sdk=PATH_OCR_TRANSACTIONS_PER_SDK_JPG):
    ocr_df, has_all_metadata = lm_format_2_report_format(ocr_df)

    # Sometimes LM sends more data than the requested one
    init = pd.to_datetime(start_date, format='%d/%m/%y')
    end = pd.to_datetime(end_date, format='%d/%m/%y')

    ocr_df = ocr_df[(ocr_df['Date'] >= init) & (ocr_df['Date'] <= end)]

    # 1. Create all png used on the PDF report
    create_jpgs_for_ocr_report(ocr_df, rel_path_summary_jpg, rel_path_docs_captured_type,
                               rel_path_docs_captured_type_subtype,
                               rel_path_weekday_usage, rel_path_trx_per_day,
                               rel_path_trx_per_sdk)

    # 2. Generate the PDF
    pdf_filename = create_pdf(license_id, package_id, start_date, end_date, client, platform, output_folder)

    return pdf_filename


def create_pdf(license_id, package_id, start_date, end_date, client, platform, output_folder):
    pdf = PDF(orientation='P', format='A4')  # A4 (210 by 297 mm)

    print(f"create_pdf: Start: {datetime.datetime.now()}")

    # First Page
    pdf.add_page()

    # Add letterhead and title
    create_identy_logo(pdf, WIDTH)
    if len(platform) > 0:
        subtitle = f"Platform: {platform} - License ID: {license_id} - Package ID: {package_id} - Dates: {start_date} - {end_date}"
    else:
        subtitle = f"License ID: {license_id} - Package ID: {package_id} - Dates: {start_date} - {end_date}"
    start_date_str = start_date.replace("/", "")  # YYYYMMDD
    end_date_str = end_date.replace("/", "")  # YYYYMMDD

    filename = f"{license_id}_{package_id}_{start_date_str}_{end_date_str}.pdf"
    if len(client) > 0:
        create_title(TITLE + f": {client}", subtitle, pdf)
    else:
        create_title(TITLE, subtitle, pdf)

    # Add description
    write_to_pdf(pdf, SUMMARY)
    pdf.ln(10)

    create_section(pdf, "SUMMARY", 68)

    create_subsection_two_plots(pdf, "Volumetry", PATH_OCR_SUMMARY_PNG,
                                "Document Types", PATH_OCR_DOCS_CAPTURED_JPG_TYPE, 75)

    create_section(pdf, "CUSTOMER USAGE", 170)
    create_subsection_one_plot(pdf, "Weekday usage", PATH_OCR_WEEKDAY_USAGE_JPG, 177)

    # Second Page
    pdf.add_page()

    create_section(pdf, "PRODUCT USAGE", 20)
    create_subsection_one_plot(pdf, "Document Model Breakdown", PATH_OCR_DOCS_CAPTURED_JPG_TYPE_SUBTYPE, 27)
    create_subsection_one_plot(pdf, "Daily Transactions", PATH_OCR_TRANSACTIONS_PER_DAY_JPG, 155)

    # Third Page
    pdf.add_page()
    create_section(pdf, "SDK", 20)
    create_subsection_one_plot(pdf, "SDK Versions", PATH_OCR_TRANSACTIONS_PER_SDK_JPG, 27)

    # Save PDF
    path_to_pdf = os.path.join(output_folder, filename)
    pdf.output(path_to_pdf)

    print(f"PDF created and archived: {path_to_pdf}")

    return filename


def lambda_handler(event, context):
    st = time.time()
    response = None

    print(f"lambda_handler start: {datetime.datetime.now()}")

    try:
        license_id_str, package_id_str, start_date_str, end_date_str, \
            client_str, platform_str = AWSLambdaHandler.process_http_request(event, '/tmp/data.csv')

        print(f"process_http_request finished: {datetime.datetime.now()}")
        # hardcoded under /tmp as Lambda AWS has read-only rights for everything else
        df_handler = pd.read_csv('/tmp/data.csv')
        pdf_fn = create_ocr_report(df_handler, license_id_str, package_id_str, start_date_str, end_date_str,
                                   client_str, platform_str, "/tmp")

        print(f"create_ocr_report finished: {datetime.datetime.now()}")

        et = time.time()
        et = (et - st) * 1000

        response = AWSLambdaHandler.return_pdf_report(os.path.join(BASE_PATH, pdf_fn), pdf_fn, et)

    except CustomError as e:
        print(f"Error processing http request: {e.code} : {e.description}")
        response = AWSLambdaHandler.return_error(e.code, e.description)
    except Exception as e:
        print(f"Error processing http request: {e}")
        response = AWSLambdaHandler.return_error(500, e)

    return response


def lm_format_2_report_format(df_in):
    df_in.rename(columns={'dt': 'Date',
                          'weekday': 'Weekday',
                          'hr': 'Daytime',
                          'accessinfo': 'Action',
                          'action': 'TransactionType',
                          'cardtype': 'CardType',
                          'cardfrom': 'CardFrom',
                          'docsubtype': 'DocSubType',
                          'sdkversion': 'SdkVersion',
                          'cardside': 'CardSide',
                          'transactions': 'Transactions'
                          }, inplace=True)

    df_in['Daytime'] = df_in['Daytime'].apply(classify_time)
    df_in.fillna({'CardType': 'NA'}, inplace=True)
    df_in.fillna({'CardFrom': 'NA'}, inplace=True)
    df_in.fillna({'DocSubType': 'NA'}, inplace=True)
    df_in.fillna({'CardSide': 'NA'}, inplace=True)

    df_in['DocType_DocSubType'] = df_in['CardType'] + " " + df_in['DocSubType']
    df_in['Date'] = pd.to_datetime(df_in['Date'], format='%d/%m/%y')

    # It´s complete if it has CardFrom, CardSubType
    unique_cardFrom = df_in['CardFrom'].unique()
    unique_cardSide = df_in['CardSide'].unique()
    unique_docSubtype = df_in['DocSubType'].unique()

    if len(unique_cardFrom) == 1 and unique_cardFrom[0] == "" and \
            len(unique_cardSide) == 1 and unique_cardSide[0] == "" and \
            len(unique_docSubtype) == 1 and unique_docSubtype[0] == "":
        has_all_meta = False
    else:
        has_all_meta = True

    return df_in, has_all_meta


if __name__ == '__main__':
    print(f"Main start: {datetime.datetime.now()}")
    start_time = time.time()

    override_default_jpg_paths("tmp")

    # agg_ocr_data_from_raw(-7)

    # df_test = pd.read_csv('PDF_REPORT_SAMPLE_v2.csv')
    # df_test = pd.read_csv('Santander-MEX_OCR_ANDROID_2413_2024-01-01_2024-01-31.csv')
    # df_test = pd.read_csv('Santander_examples/Santander-MEX_OCR_ANDROID_2172_2024-01-01_2024-01-31.csv')
    df_test = pd.read_csv('Santander_examples/agg_ocr_2172_from_2.14.2.csv')

    create_ocr_report(df_test, "2172", "mx.bancosantander.supermovil", "01/01/24", "01/03/24", "Santander-MEX",
                      "ANDROID", "tmp",
                      rel_path_summary_jpg=PATH_OCR_SUMMARY_PNG,
                      rel_path_docs_captured_type=PATH_OCR_DOCS_CAPTURED_JPG_TYPE,
                      rel_path_docs_captured_type_subtype=PATH_OCR_DOCS_CAPTURED_JPG_TYPE_SUBTYPE,
                      rel_path_weekday_usage=PATH_OCR_WEEKDAY_USAGE_JPG,
                      rel_path_trx_per_day=PATH_OCR_TRANSACTIONS_PER_DAY_JPG,
                      rel_path_trx_per_sdk=PATH_OCR_TRANSACTIONS_PER_SDK_JPG)

    end_time = time.time()
    elapsed_time_ms = (end_time - start_time) * 1000

    print(f'Total execution time in ms: {elapsed_time_ms}')
