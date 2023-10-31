# import gspread
# from oauth2client.service_account import ServiceAccountCredentials

# import pandas as pd

import requests
import datetime

# # ----------------------- For Testing ----------------------------------
# creds_json = "googlesheets.json"
# sheet_name_results = "FH OPP FORM RESULTS" #For Form Results Used to Filter Staff List
# sheet_name_staff = "FH STAFF FOR TICKETS"

# scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
# creds = ServiceAccountCredentials.from_json_keyfile_name(creds_json,scope)
# client = gspread.authorize(creds)

# #Data Frame for Criteria that will filter Staff
# sheet = client.open(sheet_name_results).sheet1
# criteria_list = sheet.get_all_records()
# df_criteria = pd.DataFrame(criteria_list)

# #Data Frame for Staff
# sheet = client.open(sheet_name_staff).sheet1
# staff_list = sheet.get_all_records()
# df_staff = pd.DataFrame(staff_list)

import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

JITBIT_USER_ID = os.environ.get("JITBIT_USER_ID")
DEVELOPMENT_CAT = os.environ.get("DEVELOPMENT_CAT")
APPROVALS_CAT = os.environ.get("APPROVALS_CAT")
SUBMITTED_CAT = os.environ.get("SUBMITTED_CAT")
WHISPER_CAT = os.environ.get("WHISPER_CAT")
DEVELOPMENT_STA = os.environ.get("DEVELOPMENT_STA")
APPROVALS_STA = os.environ.get("APPROVALS_STA")
SUBMITTED_STA = os.environ.get("SUBMITTED_STA")
WHISPER_STA = os.environ.get("WHISPER_STA")


def create_tickets(df_criteria,y,df_staff,donor_abbr,for_testing, auth_user, auth_pass):

    country_abbr = {
        'Bangladesh':'BAN',
        'Bolivia':'BOL',
        'Burundi':'BDI',
        'Cambodia':'CAM',
        'Democratic Republic of the Congo':'DRC',
        'Dominican Republic':'DOM',
        'Ethiopia':'ETH',
        'Guatemala':'GUA',
        'Haiti':'HAI',
        'Indonesia':'INA',
        'Kenya':'KEN',
        'Mozambique':'MOZ',
        'Nicaragua':'NCA',
        'Peru':'PER',
        'Philippines':'PHI',
        'Rwanda':'RWA',
        'South Sudan':'SSD',
        'Uganda':'UGA',
        'United States': 'USA',
        'TBD': 'TBD'
        }

    categoryID_dict = {
        "Development": int(DEVELOPMENT_CAT), #has approvals
        "Approvals": int(APPROVALS_CAT),
        "Submitted": int(SUBMITTED_CAT), #has approvals
        "Whisper": int(WHISPER_CAT)
    }

    statusID_dict = {
        "Development": int(DEVELOPMENT_STA), #GTO - Development
        "Approvals": int(APPROVALS_STA), #GTO - Approvals Needed
        "Submitted": int(SUBMITTED_STA), #GTO - Submitted
        "Whisper": int(WHISPER_STA) #GTO - In Consideration
    }

    submitted_status = df_criteria["Has the opportunity already been submitted?"][y]
    whisper_status = df_criteria["Is this opportunity a Whisper? (Meaning there is no active RFA/RFP; The donor is not actively soliciting for the opportunity currently, but may in the future?)"][y]
    country = str(df_criteria["Select a Country This Opportunity Applies To"][y])
    if df_criteria["Are all of the countries selected above currently moving forward with the opportunity?"][y] == "No":
        country = "TBD"
    if donor_abbr == "":
        donor = df_criteria["Please list the donor"][y]
    else:
        donor = donor_abbr
    opp_name = df_criteria["Please list the opportunity/project's anticipated name"][y]
    sectors = str(df_criteria["What Sectors Will This Opportunity Incorporate?"][y])
    type_var = str(df_criteria["Is This Opportunity Primarily for Relief or Development? (Only Select One)"][y])
    opp_type_var = df_criteria["Will FH be submitting a Concept Note, Full Proposal, or for a Cost Extension? Or is this unknown?"][y]
    due_date = df_criteria["When is the opportunity due (or if the opportunity has been submitted, what was the date of submission)?"][y]
    due_date = datetime.datetime.strptime(due_date, '%m/%d/%Y')

    today = datetime.datetime.now()
    d = datetime.timedelta(days = 3)
    due_date_approvals = today + d #datetime.datetime.strptime((today + d), '%m/%d/%Y')

    budget_tag = int(df_criteria["Estimated Budget of the Project (Type in Numbers Only AND in US Dollar Amounts)"][y])
    if (budget_tag < 100_000) and (budget_tag > 0):
        budget_tag = ",less than $100k"
    else:
        budget_tag = ""

    #Add RFI to ticket name if opp is an RFI
    if opp_type_var == 'Request for Information (RFI)':
        opp_type_var = " RFI"
    else: 
        opp_type_var = ""

    ticket_subject = country_abbr[country] + " " + donor + " " + opp_name + opp_type_var
    approval_suffix = " [GSC APPROVED]"

    status = "Development"
    if whisper_status == "Yes":
        status = "Whisper"
        approval_suffix = ""
    if submitted_status == "Yes":
        status = "Submitted"

    url =  os.environ.get("JITBIT_URL")
    endpoint_create = os.environ.get("ENDPOINT_TICKET")
    endpoint_update = os.environ.get("ENPOINT_UPDATE_TICKET")
    endpoint_postsus = os.environ.get("ENDPOINT_POSTSUS")
    endpoint_getuser = os.environ.get("ENDPOINT_GETUSER")
    endpoint_link = os.environ.get("ENDPOINT_LINK")

    payload = {
            "categoryId": categoryID_dict[status], #  int	Category ID
            "body": "Grants Ticket from API", #string	Ticket body
            "subject": ticket_subject + approval_suffix, #string	Ticket subject
            "priorityId": 0,
            "userId": int(JITBIT_USER_ID), #for nhaglund@fh.org
            "tags": sectors + "," + type_var.lower() + budget_tag,
        }
    response = requests.post(f"{url}{endpoint_create}",auth=(auth_user, auth_pass), data=payload)

    coordination_id = response.content.decode('utf-8')
    approvals_id = ""

    payload_update = {
            "id": int(coordination_id),
            "dueDate": due_date,
            "statusId": statusID_dict[status]
        }
    requests.post(f"{url}{endpoint_update}",auth=(auth_user, auth_pass), data=payload_update)

    #If TBD & if countries selected aren't all moving forward "No" then skips the approvals ticket
    prelim_ticket = df_criteria["Are all of the countries selected above currently moving forward with the opportunity?"][y]
    if prelim_ticket == "No":
        status = "Whisper"


    approvals_id_list = []

    if status != "Whisper":
        payload_approvals = {
            "categoryId": categoryID_dict["Approvals"],
            "body": "Grants Ticket from API",
            "subject": "APPROVALS " + ticket_subject,
            "priorityId": 0,
            "userId": int(JITBIT_USER_ID),
            "tags": sectors + "," + type_var.lower() + budget_tag,
        }
        response = requests.post(f"{url}{endpoint_create}",auth=(auth_user, auth_pass), data=payload_approvals)
        approvals_id = response.content.decode('utf-8')

        payload_update = {
            "id": int(approvals_id),
            "dueDate": due_date_approvals,
            "statusId": statusID_dict["Approvals"]
        }
        requests.post(f"{url}{endpoint_update}",auth=(auth_user, auth_pass), data=payload_update)

        #List for adding subs to approvals ticket
        approval_subs_list = []
        #Add Country Director to approvals ticket
        if country != 'United States':
            cd_row = df_staff[(df_staff['Approvals Ticket Details'] == "Country Director") & (df_staff['Country'] == df_criteria['Select a Country This Opportunity Applies To'][0])]
            cd_dict = (cd_row.reset_index()).to_dict('index')
            approval_subs_list.append(cd_dict[0]['Email'])
        #Add main approvers and other subs to ticket
        approvals_staff_main = df_staff[(df_staff['Approvals Ticket Details'] == "Approvals") & (df_staff['Everything?'] == "Yes")] #RHA and Region and BDD
        approvals_staff_main = approvals_staff_main.reset_index()
        for email in approvals_staff_main['Email']:
            approval_subs_list.append(email)
        #Make a dataframe for approvals subs that needs filtered
        approvals_staff_sub = df_staff[(df_staff['Approvals Ticket Details'] == "Approvals") & (df_staff['Everything?'] == "No")] #RHA and Region and BDD
        approvals_staff_sub = approvals_staff_sub.reset_index()

        #Add RD/BDDs to approvals
        for index, row in approvals_staff_sub.iterrows():
            if row['Country'] != "":
                if df_criteria['Select a Country This Opportunity Applies To'][y] in row['Country'].split(', '):
                    approval_subs_list.append(row['Email'])

        #Add RHA staff to approvals
        if df_criteria["Is This Opportunity Primarily for Relief or Development? (Only Select One)"][y] == "Relief":
            approvals_staff_sub_relief = approvals_staff_sub[(approvals_staff_sub['Type'] == "Relief")]
            for email in approvals_staff_sub_relief['Email']:
                approval_subs_list.append(email)

        #Add Special staff to approvals
        if "Food for the Hungry Canada" in df_criteria["Please Select All of the Following Stakeholders or Components that this Opportunity Involves:"][y].split(', '):
            approvals_staff_sub_fhc = approvals_staff_sub[(approvals_staff_sub['Category'] == "FHC")]
            for email in approvals_staff_sub_fhc['Email']:
                approval_subs_list.append(email)

        #Takes emails from FH staff and finds their corresponding Helpdesk ID
        for email in approval_subs_list:
            payload_user = {
                "Email": email
            }
            response = requests.get(f"{url}{endpoint_getuser}",auth=(auth_user, auth_pass), params=payload_user)
            data = response.json()

            approvals_id_list.append(data['UserID'])

        payload_link = {
            "id": int(approvals_id),
            "id2": int(coordination_id)
        }
        requests.post(f"{url}{endpoint_link}",auth=(auth_user, auth_pass), data=payload_link)

    return [coordination_id,approvals_id,approvals_id_list]
