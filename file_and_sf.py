import json
import requests
import numpy as np

import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

RECORD_ID = os.environ.get("RECORD_ID")
TOKEN_URL = os.environ.get("TOKEN_URL")
ENDPOINT_AWARD = os.environ.get("ENDPOINT_AWARD")
ENDPOINT_ACCOUNT = os.environ.get("ENDPOINT_ACCOUNT")
ENDPOINT_AREA = os.environ.get("ENDPOINT_AREA")

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

def file_and_update(username,password,grant,source,country,status,date,donor,budget,desc,funding_type,funding_office,submission_type,ticket_id,app_id,resilience_check,due_date,match,submitted_var,months,ceiling,start_date,role,opp_type,primary_sect,donor_abbr,opp_abbr,likelihood,award_type,sect_list):
  f = open('sf_creds.json')
  creds = json.load(f)
  response = requests.post(f"{TOKEN_URL}", data=creds)
  access_token = response.json().get("access_token")
  instance_url = response.json().get("instance_url")

  def lookup(field, endpoint, url_break):
    response = requests.get(f"{instance_url}{endpoint}",headers={'Content-type':'application/json', "Authorization":"Bearer " + access_token})
    account_dict = {}
    for i in response.json()['records']:
        account_dict[i['Name'].lower()] = i['attributes']['url']

    account_check = True
    while account_check:
        if field.lower() in account_dict.keys():
            account_check = False
        else:
            print(f"Not an {url_break} {field}")
            field = input(f"Input a new {url_break}: ")

    return account_dict[field.lower()].split(url_break + "/")[1]
  
  country_lookup = lookup(country, ENDPOINT_AREA, "Area__c")
  account_lookup = lookup(donor, ENDPOINT_ACCOUNT, "Account")
      
       
  base_obj = {"RecordTypeId": RECORD_ID}
  base_obj['Geographic_Location__c'] = country_lookup
  base_obj['Account__c'] = account_lookup

  base_obj["Name"] = grant
  base_obj["Short_Name__c"] = grant
  base_obj["Opportunity_Source__c"] = source
  base_obj['Status_Date__c'] = date
  base_obj['Amount__c'] = budget
  base_obj['Description__c'] = desc
  base_obj['Funding_Type__c'] = funding_type
  base_obj['Funding_Office__c'] = funding_office
  base_obj['Coordination_Ticket__c'] = "https://helpdesk.fh.org/helpdesk/Ticket/" + str(ticket_id)
  base_obj['Approval_Ticket__c'] = "https://helpdesk.fh.org/helpdesk/Ticket/" + str(app_id)
  base_obj['Resilience_Themes__c'] = resilience_check
  base_obj['Due_Date__c'] = due_date
  base_obj['Duration_in_Months__c'] = months
  base_obj['Budget_Ceiling__c'] = ceiling
  base_obj['Estimated_Project_Start_Date__c'] = start_date
  base_obj['Grant_Hierarchy_Type__c'] = role
  base_obj['Primary_Sector__c'] = "".join(primary_sect)
  base_obj['Award_Type__c'] = award_type
  base_obj['Secondary_Sector__c'] = ";".join(sect_list)

  if status == "Development":
    base_obj['Status__c'] = "Proposal Development"
  elif status == "In Consideration":
    base_obj['Status__c'] = "Prospect"
  elif status == "Submitted":
    base_obj['Status__c'] = "Under Donor Review"

  if submission_type == "Concept Note":
    base_obj["Concept_Note__c"] = "Yes"
    base_obj["Full_Proposal__c"] = "No"
    base_obj['Cost_Extension__c'] = "No"
  elif submission_type == "Full Proposal":
    base_obj["Concept_Note__c"] = "No"
    base_obj["Full_Proposal__c"] = "Yes"
    base_obj['Cost_Extension__c'] = "No"
  elif submission_type == "Cost Extension":
    base_obj["Concept_Note__c"] = "No"
    base_obj["Full_Proposal__c"] = "No"
    base_obj['Cost_Extension__c'] = "Yes"

  if match == "Match is required.":
    base_obj['Cost_Share_Required__c'] = "Yes"
  elif match == "Match is not required.":
    base_obj['Cost_Share_Required__c'] = "No"

  if submitted_var == "Yes":
    base_obj['Submission_Didn_t_Submit_Date__c'] = due_date

  if opp_type == 'Development':
    base_obj['Response_Category__c'] = "Development Response"
  elif opp_type == 'Relief':
    base_obj['Response_Category__c'] = "Emergency Response"

  if likelihood == 2:
    base_obj['Likelihood__c'] = "Tier 1 - >90%"
  elif likelihood == 1:
    base_obj['Likelihood__c'] = "Tier 2 - 70-90%"
  else:
    base_obj['Likelihood__c'] = "Tier 3 - <70%"

  payload_award = json.dumps(base_obj, cls=NpEncoder)
  with open("output.json", "w") as outfile:
    outfile.write(payload_award)
  response = requests.post(f"{instance_url}{ENDPOINT_AWARD}",headers={'Content-type':'application/json', "Authorization":"Bearer " + access_token}, data=payload_award)
  print(response.json())
  sf_url = instance_url + "/lightning/r/Future_Gift__c/" + response.json()['id'] + "/view"

  return ["Salesforce: " + sf_url,"<br>\n\nGoogle Drive Folder: ##"]
