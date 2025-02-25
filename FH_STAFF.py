#Initial Message
print("\nNow Running....\n")

from json import JSONDecodeError, loads
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import pandas as pd

import requests

from datetime import date
import datetime

import csv

from pathlib import Path
file_path = str(Path.home() / "Downloads") + "\\"

from file_and_sf import file_and_update
from upload_attachments import upload_attachments
from create_tickets import create_tickets
from gs_reassemble import google_sheet_clean
from opp_prioritization_fxn import opp_prioritization_fxn

import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

AUTH_USER = os.environ.get("AUTH_USER")
AUTH_PASS = os.environ.get("AUTH_PASS")

url = os.environ.get("JITBIT_URL")
endpoint_getuser = os.environ.get("ENDPOINT_GETUSER")
endpoint_postsus = os.environ.get("ENDPOINT_POSTSUS")
endpoint_comment = os.environ.get("ENDPOINT_COMMENT")
endpoint_update_ticket = os.environ.get("ENPOINT_UPDATE_TICKET")
endpoint_attach = os.environ.get("ENDPOINT_ATTACH")

creds_json = "googlesheets.json"
sheet_name_staff = os.environ.get("SHEET_NAME_STAFF")
sheet_name_results = os.environ.get("SHEET_NAME_RESULTS")

scope = [os.environ.get("SCOPE_1"), os.environ.get("SCOPE_2"), os.environ.get("SCOPE_3"), os.environ.get("SCOPE_4")]
creds = ServiceAccountCredentials.from_json_keyfile_name(creds_json,scope)
client = gspread.authorize(creds)

#Data Frame for Staff
sheet = client.open(sheet_name_staff).sheet1
staff_list = sheet.get_all_records()
df_staff = pd.DataFrame(staff_list)
df_staff_original = df_staff

#Data Frame for Criteria that will filter Staff
sheet = client.open(sheet_name_results).sheet1
criteria_list = sheet.get_all_records()
df_criteria = pd.DataFrame(criteria_list)

#For comparing the updated to the original, bc if the updated remains blank (aka == the original) then it will not be printed
region_string_original = "Region: "
field_string_original = "Country: "
programs_string_original = "Programs: "
mss_string_original = "MSS: "
mel_string_original = "MEL: "
rha_string_original = "RHA: "
grants_string_original = "Grants: "
affairs_string_original = "External Affairs/Marketing: "
fhuk_string_original = "FHUK: "
fhc_string_original = "FHC: "

original_dict = {
    'Region':region_string_original,
    'Field':field_string_original,
    'Programs':programs_string_original,
    'MSS':mss_string_original,
    'MEL':mel_string_original,
    'RHA':rha_string_original,
    'Grants': grants_string_original,
    'External Affairs/Marketing':affairs_string_original,
    'FHUK':fhuk_string_original,
    'FHC':fhc_string_original
}

#Ask User if they would like the sheet reformatted (remove blank rows)
google_user = input("What is your Email?: ")
google_pass = input("What is your Password?: ")
reformat_sheet = input("\nReformat Sheet? y for yes, otherwise press enter to run the program: ")
if reformat_sheet == "y":
    google_sheet_clean(df_criteria,creds,sheet_name_results,client, os.environ.get("UPLOAD_ID"))
    input("\nThe sheet has been reformatted, press Enter to begin...")

y = 0 # Variable used to iterate through FH OPP FORM RESULTS, y changes row
df_results_length = int(len(df_criteria.index))
while y < (df_results_length):

    #If global df_staff was redefined, return it to normal
    df_staff = df_staff_original

    #This may never be needed?
    countries_orig = df_criteria["Select a Country This Opportunity Applies To"][y]
    if countries_orig == "More than one country/TBD":
        print("\nColumn B (the country column) in the managed Google Sheet is not a single FH country."\
            "Please change each line to a single FH counry, then re-run the program")
        quit()

    opp_name = df_criteria["Please list the opportunity/project's anticipated name"][y]
    print("\nNow running for " + opp_name + "\n")
    for_testing = input("**For Testing Purposes** Do you want subscribers to be added to the tickets? Press Enter if so, otherwise input n and then press enter: ")
    for_testing_sf = input("**For Testing Purposes** Do you want to run the Salesforce and Google Folder portion of the program? Press Enter if so, otherwise input n and then press enter: ")
    opp_abbr = input("\nDoes the Opportunity have an abbreviation for the file name? Press Enter to Skip, otheriwse input: ")
    donor_abbr = input("Does the Donor have an abbreviation for the file name? Press Enter to Skip, otheriwse input: ")

    region_string = "Region: "
    field_string = "Country: "
    programs_string = "Programs: "
    mss_string = "MSS: "
    mel_string = "MEL: "
    rha_string = "RHA: "
    grants_string = "Grants: "
    affairs_string = "External Affairs/Marketing: "
    fhuk_string = "FHUK: "
    fhc_string = "FHC: "

    emails_list = []

    category_dict = {
        'Region':region_string,
        'Field':field_string,
        'Programs':programs_string,
        'MSS':mss_string,
        'MEL':mel_string,
        'RHA':rha_string,
        'Grants': grants_string,
        'External Affairs/Marketing':affairs_string,
        'FHUK':fhuk_string,
        'FHC':fhc_string
    }

    #Check if TBD row needs a preliminary ticket, removing field & regional staff (non approvals staff)
    if df_criteria["Are all of the countries selected above currently moving forward with the opportunity?"][0] == "No":
            values = ["Approvals"]
            df_staff = df_staff[df_staff["Approvals Ticket Details"].isin(values) == True]
            df_staff.reset_index(drop=True, inplace=True)

            regions_list = []

            regions_dict = {
                "Burundi":"Africa","Democratic Republic of the Congo":"Africa","Ethiopia":"Africa","Kenya":"Africa","Mozambique":"Africa","Rwanda":"Africa","South Sudan":"Africa","Uganda":"Africa",
                "Bangladesh":"Asia","Cambodia":"Asia","Indonesia":"Asia","Philippines":"Asia",
                "Bolivia":"LAC","Dominican Republic":"LAC","Guatemala":"LAC","Haiti":"LAC","Nicaragua":"LAC","Peru":"LAC"
            }

            # A Local FH Staff List for prelim tickets
            f = open('needed_per_region.json')
            needed_per_region = loads(f)

            for c in df_criteria["Check all of the FH countries that this opportunity applies to"][y].split(", "):
                    regions_list.append(regions_dict[c])

            first_region = regions_dict[df_criteria["Select a Country This Opportunity Applies To"][y]]

            other_needed_regions = []

            if "Africa" in regions_list:
                    other_needed_regions.append("Africa")
            if "Asia" in regions_list:
                    other_needed_regions.append("Asia")
            if "LAC" in regions_list:
                    other_needed_regions.append("LAC")

            other_needed_regions.remove(first_region)

            additional_emails = []

            for r in other_needed_regions:
                    for e in needed_per_region[r]:
                            if e not in additional_emails:
                                additional_emails.append(e)

            for pair in additional_emails:
                for key in pair:
                     region_string += key + ", "
                     emails_list.append(pair[key])

    #----------------- Set Priority of Ticket (int 2 = Tier 1; 1 = Tier 2; 0 = Tier 3; -1 = Tier 4) ---------------------
    incumbent = df_criteria["Is Food for the Hungry an Incumbent or partnering with an incumbent?"][y]
    follow_on = df_criteria["Is this a follow on opportunity?"][y]
    donor_exp = df_criteria["Does the country office have experience working with the donor?"][y]
    models = df_criteria["Do we have evidence based approaches and models for this opportunity?"][y]
    sector_priorities = df_criteria["Does the opportunity align with country office sector and sub sector priorities?"][y]
    length = df_criteria["Please list the anticipated length of the project in months"][y]
    budget_orig = df_criteria["Estimated Budget of the Project (Type in Numbers Only AND in US Dollar Amounts)"][y]
    opp_type_var = df_criteria["Will FH be submitting a Concept Note, Full Proposal, or for a Cost Extension? Or is this unknown?"][y]

    priority = opp_prioritization_fxn(incumbent,follow_on,donor_exp,length,budget_orig,models,sector_priorities,opp_type_var)

    #Create Tickets
    ids_list = create_tickets(df_criteria,y,df_staff,donor_abbr,for_testing, AUTH_USER, AUTH_PASS)
    ticket_id = int(ids_list[0])
    if ids_list[1] != "":
        approvals_id = int(ids_list[1])
    else:
        approvals_id = ""
    
    approvals_id_list = ids_list[2]

    # -------------------- From Google Sheet for Tickets/Helpdesk ---------------------
    countries_orig = df_criteria["Select a Country This Opportunity Applies To"][y]
    sectors = df_criteria["What Sectors Will This Opportunity Incorporate?"][y].split(", ")
    sectors_orig = df_criteria["Select ONLY ONE sector from the list below that is the strongest focus of this opportunity"][y].split(", ")
    type_var_orig = df_criteria["Is This Opportunity Primarily for Relief or Development? (Only Select One)"][y]
    dollar_amount = '${:,.2f}'.format(budget_orig)
    gng_document = (df_criteria["Is the Go/No Go document included in the relevant attachments on this form (see previous question)."][y])
    whisper = df_criteria["Is this opportunity a Whisper? (Meaning there is no active RFA/RFP; The donor is not actively soliciting for the opportunity currently, but may in the future?)"][y]

    gng_comm_for_approvals = ""
    if gng_document == "Yes":
        gng_document = ""
    elif whisper == "Yes":
        gng_document = ""
    else:
        gng_document = "Please upload the Go/No Go document to the ticket when you are able."
        gng_comm_for_approvals = " after the Go/No Go document has been uploaded to the ticket "

    if budget_orig == 0:
        dollar_amount = "to be determined"

    donor = df_criteria["Please list the donor"][y]
    project_length_orig = df_criteria["Please list the anticipated length of the project in months"][y]
    project_length = df_criteria["Please list the anticipated length of the project in months"][y]
    due_date_orig = df_criteria["When is the opportunity due (or if the opportunity has been submitted, what was the date of submission)?"][y]
    submitted_var = df_criteria["Has the opportunity already been submitted?"][y]

    if project_length == 0:
        project_length = "to be determined"
    else:
        project_length = str(project_length) + " months"

    if submitted_var == 'Yes':
        due_date = "The opportunity was submiited on " + due_date_orig
    else:
        due_date = "The opportunity due date is " + due_date_orig

    first_name = df_criteria["What is your first name?"][y]
    submitter_email = df_criteria["What is your email?"][y]
    opp_desc = df_criteria["Please briefly describe the opportunity/project in no more than 5 sentences."][y]
    match = df_criteria["Is match required?"][y]
    opp_link = df_criteria["Please link the grant opportunity (RFA, CFP, etc)"][y]
    if opp_link != "":
        opp_link = "Link to opportunity/relevant information: " + opp_link
    submitted_documents = df_criteria["List the names of the documents attached above separate by a comma (EX: Go/No Go File, the RFA, Proposal Template, and a Budget)"][y]
    if submitted_documents != "":
        submitted_documents = "Additionally, find attached to the ticket the following documents: " + submitted_documents

    # -------------------- For SF Create and google_file.py ---------------------
    whisper_or_development = "Development"
    coordination_var = "coordination"
    if whisper == 'Yes':
        whisper_or_development = "In Consideration"
        coordination_var = "whisper"
    if submitted_var == 'Yes':
        whisper_or_development = "Submitted"

    #---------------------- For File name Abbreviations --------------------------
    if donor_abbr == "":
        donor_abbr = donor 
    opp_abbr = "_" + opp_abbr

    # -------------------- For SF Create ----------------------------
    today = date.today()
    identified_at_level = df_criteria["Did the Region, Field, GSC, or an Affiliate identify this opportunity?"][y]

    # ------------------- For SF Update ----------------------------
    funding_type = df_criteria["What is the funding type?"][y]
    resilience_check = df_criteria["Does the opportunity incorporate resilience? In other words, as a part of the RFA/RFP, does the donor use words such as 'resilience', 'risks', 'scenario', 'adaptive', 'crisis', or 'crises' when describing the funding opportunity?"][y]
    budget_ceiling = df_criteria["What is the estimated budget ceiling?"][y]
    start_date = df_criteria["What is the estimated start date of the project (please insert the best estimate if unknown)?"][y]
    fh_role = df_criteria["For this opportunity, will FH be Prime, a Sub, or a solo recipient if awarded?"][y]
    funding_office = df_criteria["Select which FH Office will receive the funding directly from the donor."][y]
    award_type = df_criteria["What type of award is this opportunity?"][y]

    if funding_office == "FHUS - All USG funding and other US donors provide funding through FHUS":
        funding_office = "FH US"
    elif funding_office == "FHUK":
        funding_office = "FH UK"
    elif funding_office == "FH Canada":
        funding_office = "FH Canada"
    elif funding_office == "JIFH (Japan FH)":
        funding_office = "JIFH"
    elif funding_office == "KFHI (Korean FH)":
        funding_office = "KFHI"
    elif funding_office == "FH Swiss":
        funding_office = "FH Swiss"
    else:
        funding_office = "FHA"

    #Reformat dates to match SF date input requirement
    due_date_orig = datetime.datetime.strptime(due_date_orig, '%m/%d/%Y').strftime("%Y-%m-%d")
    start_date = datetime.datetime.strptime(start_date, '%m/%d/%Y').strftime("%Y-%m-%d")

    if for_testing_sf != "n":
        list_of_links = file_and_update(google_user,google_pass,opp_name,identified_at_level,countries_orig,whisper_or_development,today.strftime("%Y-%m-%d"),donor,budget_orig,opp_desc,funding_type,funding_office,opp_type_var,\
        ticket_id,approvals_id,resilience_check,due_date_orig,match,submitted_var,project_length_orig,budget_ceiling,\
        start_date,fh_role,type_var_orig,sectors_orig,donor_abbr,opp_abbr,priority,award_type,sectors)
    else:
        list_of_links = ["###","###"]

    google_file_string = list_of_links[0]
    SF_entry_string = list_of_links[1]

    #-----------------Reference created tickets and insert links in the body-----------------------
    #Coordination Update and Post Comment
    payload_update = {
            "id": ticket_id,
            "priority": priority,
            "body": google_file_string + "\n" + SF_entry_string
        }
    response = requests.post(f"{url}{endpoint_update_ticket}",auth=(AUTH_USER, AUTH_PASS), data=payload_update)

    #Approvals Comment and Post Update
    if approvals_id != "":
        payload_update_approvals = {
                "id": approvals_id,
                "priority": priority,
                "body": google_file_string + "\n" + SF_entry_string
            }
        response = requests.post(f"{url}{endpoint_update_ticket}",auth=(AUTH_USER, AUTH_PASS), data=payload_update_approvals)
    
    #-----------------Add attachments to Coordination/Main Ticket ---------------------------------
    attachments = df_criteria["Please upload relevant attachments"][y]

    if attachments != "":
        upload_attachments(ticket_id, attachments,file_path,approvals_id, AUTH_USER, AUTH_PASS, url, endpoint_attach)

    x = 0 # Variable used to iterate through FH STAFF FOR TICKETS, x changes row
    df_staff_length = int(len(df_staff.index))
    while x < (df_staff_length):

        #These variable, minus threshold, need to stay in this subloop to change them back from integers to their strings
        #Otherwise there will be an error saying 'countries int isn't iterable, etc
        unique_id = df_criteria["Timestamp"][y]
        countries = df_criteria["Select a Country This Opportunity Applies To"][y].split(", ")
        budget = (df_criteria["Estimated Budget of the Project (Type in Numbers Only AND in US Dollar Amounts)"][y]).item()
        sectors = df_criteria["What Sectors Will This Opportunity Incorporate?"][y].split(", ")
        type_var = df_criteria["Is This Opportunity Primarily for Relief or Development? (Only Select One)"][y].split(", ")
        special = df_criteria["Please Select All of the Following Stakeholders or Components that this Opportunity Involves:"][y].split(", ") + funding_type.split(", ")

        if df_staff.loc[x]["Everything?"] == "Yes":
            category_dict[df_staff.loc[x]["Category"]] = category_dict[df_staff.loc[x]["Category"]] + df_staff.loc[x]["First Name"] + ', '
            emails_list.append(df_staff.loc[x]["Email"])

        elif df_staff.loc[x]["Everything?"] == "No":
            criteria_dict = {
                'Country': df_staff.loc[x]["Country"].split(", "),
                'Budget Threshold': df_staff.loc[x]["Budget Threshold"],
                'Sector': df_staff.loc[x]["Sector"].split(", "),
                'Type': df_staff.loc[x]["Type"].split(", "),
                'Special': df_staff.loc[x]["Special"].split(", ")
            }

            if criteria_dict['Country'][0] == '':
                countries = 1
            elif criteria_dict['Country'][0] != '': 
                for c in countries:
                    if c in criteria_dict['Country']:
                        countries = 1
                        break
                    if c not in criteria_dict['Country']:
                        countries = 0

            try:
                if budget >= criteria_dict['Budget Threshold']:
                    budget = 1
                elif budget < criteria_dict['Budget Threshold']:
                    budget = 0
            except TypeError:
                budget = 1

            if criteria_dict['Sector'][0] == '':
                sectors = 1
            elif criteria_dict['Sector'][0] != '': 
                for s in sectors:
                    if s in criteria_dict['Sector']:
                        sectors = 1
                        break
                    if s not in criteria_dict['Sector']:
                        sectors = 0

            if criteria_dict['Type'][0] == '':
                type_var = 1
            elif criteria_dict['Type'][0] != '': 
                for t in type_var:
                    if t in criteria_dict['Type']:
                        type_var = 1
                        break
                    if t not in criteria_dict['Type']:
                        type_var = 0
            
            if criteria_dict['Special'][0] == '':
                special = 1
            elif criteria_dict['Special'][0] != '': 
                for sp in special:
                    if sp in criteria_dict['Special']:
                        special = 1
                        break
                    if sp not in criteria_dict['Special']:
                        special = 0

            score = countries + budget + sectors + type_var + special

            if score == 5:
                category_dict[df_staff.loc[x]["Category"]] = category_dict[df_staff.loc[x]["Category"]] + df_staff.loc[x]["First Name"] + ', '
                emails_list.append(df_staff.loc[x]["Email"])

        x += 1

    user_id_list = []
    emails_list.append(submitter_email)
    comment_orig = ""

    #Compares the new dict to the original one, excluding lines that are the same (Ex if RHA: == RHA:  )
    for i in category_dict:
        category_dict[i] = category_dict[i].removesuffix(", ")
        if category_dict[i] != original_dict[i]:
            comment_orig = comment_orig + ("\n" + category_dict[i])

    comment = "\nHi everyone,\n\nI am opening this " + coordination_var + " ticket for a " + type_var_orig.lower() + " opportunity, " + opp_name + \
        ", that " + countries_orig + " is pursuing with " + donor + ". The project budget is " + str(dollar_amount) +\
         " and the estimated project length is " + str(project_length) + ". " + due_date + ". "\
        + match + "\n\nAs per " + first_name + ": " + opp_desc + "\n\n" + submitted_documents + "\n\nI'm adding the following people to the ticket. Everyone, please\
         add others to the ticket as needed or contact me if help is needed doing this.\n" + comment_orig +"\n\n\n" + first_name +",\n\n" + "Thank you for bringing\
         this opportunity to FH's attention. " + gng_document + "\n\nIf there is any change or update to the opportunity's due date, budget, or length\
         (from what was initially indicated in the submission of this ticket), please let us know here in the ticket.\n\n"\
        + opp_link + "\n\nBest,\nNoah"

    #Changes comment to match 
    if df_criteria["Are all of the countries selected above currently moving forward with the opportunity?"][y] == "No":

        possible_countries = df_criteria["Check all of the FH countries that this opportunity applies to"][y]

        comment = "\nHi everyone,\n\nI am opening this preliminary coordination ticket for a " + type_var_orig.lower() + " opportunity, " + opp_name + \
        ", that the following countries are able to pursue with " + donor + ": " + possible_countries + ". The project budget is " + str(dollar_amount) +\
         " and the estimated project length is " + str(project_length) + ". " + due_date + ". "\
        + match + " The purpose of this ticket is to start a preliminary discussion and decide which countries, if any, will move forward with this opportunity.\
        \n\nAs per " + first_name + ": " + opp_desc + "\n\n" + submitted_documents + "\n\n\nI'm adding the following people to the ticket. Everyone, please\
         add others to the ticket as needed or contact me if help is needed doing this.\n" + comment_orig + "\n\n" +\
        opp_link + "\n\nBest,\nNoah"
    
    comment_approvals = "\nHi everyone,\n\nI am opening this approvals ticket for a " + type_var_orig.lower() + " opportunity, " + opp_name + \
        ", that " + countries_orig + " is pursuing with " + donor + ". The project budget is " + str(dollar_amount) +\
         " and the estimated project length is " + str(project_length) + ". " + due_date + ". "\
        + match + "\n\nAs per " + first_name + ": " + opp_desc + "\n\nApprovers,\n\n Kindly let me know your feedback concerning this\
         opportunity" + gng_comm_for_approvals + ". \n\nBest,\nNoah"

    #Takes emails from FH staff and finds their corresponding Helpdesk ID
    for e in emails_list:
        payload_user = {
            "Email": e
        }
        response = requests.get(f"{url}{endpoint_getuser}",auth=(AUTH_USER, AUTH_PASS), params=payload_user)

        try:
            data = response.json()
            user_id_list.append(data['UserID'])
        except JSONDecodeError:
            print("\nEmail: " + e + " is not a valid Helpdesk Email, please adjust the Google Sheet for Staff or the Opportunity.")

    csv_filename = str(ticket_id) + ".csv"
    with open(csv_filename, 'w') as f:
      
        # List of saved subs to be added after approval
        write = csv.writer(f)
        write.writerow(user_id_list)

    #Posts subscribers to the coordination ticket (ticket_id)
    for u in user_id_list:
        payload_sus = {
            "id": ticket_id,
            "userId": int(u)
        }
        if (whisper == "Yes") and (for_testing != "n"):
            response = requests.post(f"{url}{endpoint_postsus}",auth=(AUTH_USER, AUTH_PASS), data=payload_sus)

    payload_comm = {
            "id": ticket_id,
            "body": comment
        }
    response = requests.post(f"{url}{endpoint_comment}",auth=(AUTH_USER, AUTH_PASS), data=payload_comm)
    print(response)

    if whisper != "Yes":
        payload_comm_approvals = {
                "id": approvals_id,
                "body": comment_approvals
            }
        response = requests.post(f"{url}{endpoint_comment}",auth=(AUTH_USER, AUTH_PASS), data=payload_comm_approvals)

        #Posts subscribers to the approvals ticket (ticket_id)
        for user_id in approvals_id_list:
            payload_sus = {
                "id": int(approvals_id),
                "userId": int(user_id)
            }
            if for_testing != "n":
                requests.post(f"{url}{endpoint_postsus}",auth=(AUTH_USER, AUTH_PASS), data=payload_sus)
        
        print(response)

    y += 1


input("\nFinished. Press Enter to exit.")


