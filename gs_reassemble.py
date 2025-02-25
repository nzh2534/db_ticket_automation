import pandas as pd
from df2gspread import df2gspread as d2g

def google_sheet_clean(df_criteria,gs_creds,sheet_name_results,client, upload_id):
    """
    Cleans and updates a Google Sheet based on the provided criteria DataFrame.

    Parameters:
    df_criteria (DataFrame): DataFrame containing the criteria for cleaning and updating the Google Sheet.
    gs_creds (Credentials): Google Sheets API credentials.
    sheet_name_results (str): Name of the Google Sheet to update.
    client (gspread.Client): Authenticated gspread client.
    upload_id (str): ID of the Google Sheet to upload the cleaned data to.

    Returns:
    None
    """
    replace_blanks = []
    for i in df_criteria["Select a Country This Opportunity Applies To"]:
        if i == "":
            replace_blanks.append("nan")
        else:
            replace_blanks.append(i)
    df_criteria["Select a Country This Opportunity Applies To"] = replace_blanks
    df_criteria = df_criteria[df_criteria["Select a Country This Opportunity Applies To"] != 'nan']
    df_criteria.reset_index(drop=True, inplace=True)

    sheet_2 = client.open(sheet_name_results)
    sheet_2.values_clear("'Sheet 1'!A1:J10000")
    d2g.upload(df_criteria, upload_id, "Sheet 1", credentials=gs_creds, row_names=True)

    all_countries_var = []
    countries_list = []
    base_list = []
    for v in df_criteria["Are all of the countries selected above currently moving forward with the opportunity?"]:
        all_countries_var.append(v)
    for countries in df_criteria["Check all of the FH countries that this opportunity applies to"]:
        countries_list.append(countries.split(", ")[0])
    for base in df_criteria["Select a Country This Opportunity Applies To"]:
        base_list.append(base)

    index = 0
    for v in all_countries_var:
        if v == "No":
            all_countries_var[index] = countries_list[index]
        index += 1

    index = 0
    for v in all_countries_var:
        if v != "Yes" and v != "":
            base_list[index] = all_countries_var[index]
        index += 1

    #df_criteria["Select a Country This Opportunity Applies To"] = base_list
    df_criteria.__setitem__("Select a Country This Opportunity Applies To", base_list)

    single_select = []
    multi_select = []
    for s in df_criteria["Select a Country This Opportunity Applies To"]:
        single_select.append(s)
    for m in df_criteria["Check all of the FH countries that this opportunity applies to"]:
        multi_select.append(m)

    index = 0 
    for entry in single_select:
        if entry == 'More than one country/TBD':
            single_select[index] = multi_select[index]
            index += 1
        else:
            index += 1

    #df_criteria["Select a Country This Opportunity Applies To"] = single_select
    df_criteria.__setitem__("Select a Country This Opportunity Applies To", single_select)

    new_gs_rows = []
    new_row_count = []
    for c in df_criteria["Select a Country This Opportunity Applies To"]:
        each_country = c.split(", ")
        rows_needed = 0
        for i in each_country:
            new_gs_rows.append(i)
            rows_needed += 1
        new_row_count.append(rows_needed)

    df_criteria_clean = pd.DataFrame()

    index = 0
    for row in new_row_count:
        row = int(row)
        while row > 0:
            df_criteria_clean = df_criteria_clean.append(df_criteria.iloc[index])
            row -= 1
        index += 1

    #df_criteria_clean["Select a Country This Opportunity Applies To"] = new_gs_rows
    df_criteria_clean.__setitem__("Select a Country This Opportunity Applies To", new_gs_rows)
    df_criteria = df_criteria_clean
    df_criteria.reset_index(drop=True, inplace=True)

    d2g.upload(df_criteria, upload_id, "Sheet 1", credentials=gs_creds, row_names=True)