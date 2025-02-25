#----------------- Set Priority of Ticket (int 2 = Tier 1; 1 = Tier 2; 0 = Tier 3; -1 = Tier 4) ---------------------

def opp_prioritization_fxn(incumbent,follow_on,donor_exp,length,budget,models,sector,type):
    """
    Determines the priority of an opportunity based on various criteria.

    Criteria:
    - Incumbent?
    - Follow on?
    - Donor experience?
    - Multiyear?
    - Value?
    - Aligns with priorities?
    - Evidence based models?
    - Light or heavy work?
    - GSC or Field leading technical design?

    Tiers:
    - Tier 1: If (1), (2), (5) $2M+, (4) Multiyear, (7)
    - Tier 2: If (1 - No), (6), (7), (5) $2M+, (4) Multiyear
    - Tier 3: If (1), (5) Not High, (6), (8) Light
    - Tier 4: If (1 - No), (9) GSC and PQT has capacity to submit, (5) >$0.5M

    Parameters:
    incumbent (str): Indicates if the opportunity is incumbent.
    follow_on (str): Indicates if the opportunity is a follow-on.
    donor_exp (str): Indicates if there is donor experience.
    length (int): Length of the project in months.
    budget (int): Budget of the project.
    models (str): Indicates if evidence-based models are used.
    sector (str): Indicates if the opportunity aligns with sector priorities.
    type (str): Type of the opportunity (e.g., Concept Note, Expression of Interest).

    Returns:
    int: Priority of the opportunity (2 = Tier 1, 1 = Tier 2, 0 = Tier 3, -1 = Tier 4).
    """
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