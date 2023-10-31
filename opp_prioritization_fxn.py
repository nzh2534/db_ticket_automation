# Is Food for the Hungry an Incumbent or partnering with an incumbent?
# Yes

# Is this a follow on opportunity?
# Yes

# Does the country office have experience working with the donor?
# Yes

# How long will the project last (in months)
# 36

# What is the opportunity budget?
# 25000000

# Do we have evidence based approaches and models for this opportunity?
# Yes

# Does the opportunity align with country office sector and sub sector priorities?
# Yes

# Will FH be submitting a Concept Note, Full Proposal, EOI, or a Cost Extension? Or is this unknown?
# Full Proposal

# Does the country office have the technical capacity to design and submit this opportunity?
# The GSC is leading technical design and writing

# Incumbent? 
# Follow on?
# Donor experience?
# Multiyear?
# Value?
# Aligns with priorities?
# Evidence based models?
# Light or heavy work?
# GSC or Field leading technical design?
 
# Tier 1 - If (1), (2), (5) $2M+, (4) Multiyear, (7)
 
# Tier 2 - If (1 - No), (6), (7), (5) $2M+, (4) Multiyear
 
# Tier 3 - If (1), (5) Not High, (6), (8) Light
 
# Tier 4 - If (1 - No), (9) GSC and PQT has capacity to submit, (5) >$0.5M

#----------------- Set Priority of Ticket (int 2 = Tier 1; 1 = Tier 2; 0 = Tier 3; -1 = Tier 4) ---------------------

def opp_prioritization_fxn(incumbent,follow_on,donor_exp,length,budget,models,sector,type): #,type,capacity):
    if incumbent == "Yes":
        if budget > 2_000_000 and length > 12 and models == "Yes" and follow_on == "Yes" and donor_exp == "Yes":
            return 2
        elif donor_exp == "Yes" and type in ["Concept Note","Expression of Interest"]:
            return 2
        else:
            return 0
    elif budget > 2_000_000 and length > 12 and models == "Yes" and follow_on == "Yes" and donor_exp == "No":
        return 1
    elif sector == "Yes" and budget >= 2_000_000 and length > 12: #add value proposition
        return 1
    elif donor_exp == "Yes":
        return 0
    else:
        return -1