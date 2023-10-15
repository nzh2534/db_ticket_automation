import json
import requests
import numpy as np

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)
    
sf_area = {
        'Bangladesh':'a2S8W000003n5VbUAI',
        'Bolivia':'a2S8W000003n5VMUAY',
        'Burundi':'a2S8W000003n5VSUAY',
        'Cambodia':'a2S8W000003n5VYUAY',
        'Democratic Republic of the Congo':'a2S8W000003n5VTUAY',
        'Dominican Republic':'a2S8W000003n5VKUAY',
        'Ethiopia':'a2S8W000003n5VQUAY',
        'Guatemala':'a2S8W000003n5VNUAY',
        'Haiti':'a2S8W000003n5VJUAY',
        'Indonesia':'a2S8W000003n5VaUAI',
        'Kenya':'a2S8W000003n5VUUAY',
        'Mozambique':'a2S8W000003n5VVUAY',
        'Nicaragua':'a2S8W000003n5VOUAY',
        'Peru':'a2S8W000003n5VLUAY',
        'Philippines':'a2S8W000003n5VZUAY',
        'Rwanda':'a2S8W000003n5VWUAY',
        'South Sudan':'a2S8W000003n5VPUAY',
        'Uganda':'a2S8W000003n5VRUAY',
        'United States': 'a2S8W000003n5VeUAI'
        }

def sf_award(username,password,grant,source,country,status,date,donor,
                    budget,desc,funding_type,funding_office,submission_type,ticket_id,
                    app_id,resilience_check,due_date,match,submitted_var,months,ceiling,
                    start_date,role,opp_type,primary_sect,donor_abbr,opp_abbr,likelihood,award_type,sect_list):
  
  base_obj = {"RecordTypeId": "0128W000001HrRaQAK"}

  base_obj['Geographic_Location__c'] = sf_area[country]
  base_obj['Account__c'] = "001Ou000004X2dSIAS" #Need to update in prod

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


  f = open('sf_creds.json')
  creds = json.load(f)  
  url = "https://test.salesforce.com/services/oauth2/token"
  response = requests.post(f"{url}", data=creds)
  access_token = response.json().get("access_token")
  instance_url = response.json().get("instance_url")
  endpoint_award = "/services/data/v31.0/sobjects/Future_Gift__c"
  payload_award = json.dumps(base_obj, cls=NpEncoder)
  with open("output.json", "w") as outfile:
    outfile.write(payload_award)
  response = requests.post(f"{instance_url}{endpoint_award}",headers={'Content-type':'application/json', "Authorization":"Bearer " + access_token}, data=payload_award)
  print(response.json())
  sf_url = instance_url + "/lightning/r/Future_Gift__c/" + response.json()['id'] + "/view"

  return sf_url