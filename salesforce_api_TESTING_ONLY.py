# %%
import requests
import json

# %%
f = open('sf_creds.json')
creds = json.load(f)

# %%
url = "https://test.salesforce.com/services/oauth2/token"
response = requests.post(f"{url}", data=creds)

# %%
access_token = response.json().get("access_token")
instance_url = response.json().get("instance_url")

# %%
endpoint_award = "/services/data/v31.0/sobjects/Future_Gift__c"

### "Name": STR/80
### "Short_Name__c": STR/255
### "Status__c": STR LIST
### "Amount__c": INT
### "Primary_Sector__c": STR LIST
# "Account__c": ACC ID,
### "RecordTypeId": "0128W000001HrRaQAK"

### Status_Date__c: DATE --> "2021-06-02"
### Geographic_Location__c: STR LIST --> "a2SOu0000000dkXMAQ"
### Secondary_Sector__c: STR LIST --> "Food Security;Nutrition"
### Funding_Office__c: STR LIST --> "JIFH"
### Funding_Type__c: STR LIST --> "USG"
### Project_Files_Documentation__c: STR/255
### Response_Category__c: STR LIST --> "Development Response"
### Grant_Hierarchy_Type__c: STR LIST --> "Prime"
### Award_Type__c: STR LIST --> "Grant"
### Description__c: STR/32768
### Opportunity_Source__c: STR LIST --> "Country Office"
### Estimated_Project_Start_Date__c: DATE --> "2021-06-02"
### Resilience_Themes__c: STR LIST --> "Yes"
### Duration_in_Months__c: INT --> 12
### Likelihood__c: STR LIST --> "Tier 2 - 70-90%"
### Concept_Note__c: STR LIST --> "No"
### Full_Proposal__c: STR LIST --> "Yes"
### Cost Extension: STR LIST --> "No"
### Cost_Share_Required__c: STR LIST --> "Yes"
### Coordination_Ticket__c: URL/255 --> "https://helpdesk.fh.org/helpdesk/Ticket/56934916"
### Approval_Ticket__c: URL/255 --> "https://helpdesk.fh.org/helpdesk/Ticket/56934917"
### Due_Date__c: Date --> "2021-06-02"
### ------ Submission_Didn_t_Submit_Date__c: Date --> "2021-06-02"
### Budget_Ceiling__c: INT --> 98765

payload_award = json.dumps({
    "Name": "Test Award",
    "Short_Name__c": "Test Award",
    "Status__c": "Prospect",
    "Amount__c": 9876,
    "Primary_Sector__c": "Health",
    "Account__c": "001Ou000004X2dSIAS",
    "RecordTypeId": "0128W000001HrRaQAK",
    "Status_Date__c": "2021-06-02",
    "Geographic_Location__c": "a2SOu0000000dkXMAQ",
    "Secondary_Sector__c": "Food Security;Livelihoods",
    "Funding_Office__c": "JIFH",
    "Funding_Type__c": "USG",
    "Project_Files_Documentation__c": "www.google.com",
    "Response_Category__c": "Development Response",
    "Grant_Hierarchy_Type__c": "Prime",
    "Award_Type__c": "Grant",
    "Description__c": "Test Description",
    "Opportunity_Source__c": "Country Office",
    "Estimated_Project_Start_Date__c": "2021-06-02",
    "Resilience_Themes__c": "Yes",
    "Duration_in_Months__c": 12,
    "Likelihood__c": "Tier 2 - 70-90%",
    "Concept_Note__c": "No",
    "Full_Proposal__c": "Yes",
    "Cost_Extension__c": "No",
    "Cost_Share_Required__c": "Yes",
    "Coordination_Ticket__c": "https://helpdesk.fh.org/helpdesk/Ticket/56934916",
    "Approval_Ticket__c": "https://helpdesk.fh.org/helpdesk/Ticket/56934917",
    "Due_Date__c": "2021-06-02",
    "Submission_Didn_t_Submit_Date__c": "2021-06-02",
    "Budget_Ceiling__c": 98765
})
d = open('sf_creds.json')
data = json.load(d)
data_sf = json.dumps(data)
response = requests.post(f"{instance_url}{endpoint_award}",headers={'Content-type':'application/json', "Authorization":"Bearer " + access_token}, data=payload_award)

# %%
sf_url = instance_url + "/lightning/r/Future_Gift__c/" + response.json()['id'] + "/view"

# %%
sf_url