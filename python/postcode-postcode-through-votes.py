 #!/usr/bin/python
# -*- coding: utf8 -*-
import pickle
import pandas as pd
import math

dane = pd.read_csv("../data/processed/votes_with_city_wojewodztwo.csv", sep=';', encoding = "utf8")


wroclaw_votes = dane[(dane['Miasto']==u'Wrocław') & ((dane['Prog_1'] > 0)|(dane['Prog_2'] > 0)|(dane['Prog_3'] > 0))]
wroclaw_records = wroclaw_votes.to_records()

# matrix: (vote1.id, vote2.id, projects(vote1) interstesction projects(vote2)
#  
votes_to_votes_through_projects = {v[1] : {} for v in wroclaw_records}

project_votes = {}
for vote in wroclaw_records:
    for i in [-3,-4,-5]:
        p = vote[i]
        if p not in project_votes:
            project_votes[p] = []
        project_votes[p].append(vote[1])
del project_votes[0]


# vote id -> postcode
votes_to_codes = { vote[1] : vote[-7].replace('-','') for vote in wroclaw_records }

# (post_code1, post_code2, list of votes that ) 
codes_from_votes = { vote[-7].replace('-','') : {} for vote in wroclaw_records }

# (post_code1, post_code2, list of votes that ) 
codes_from_projects = { vote[-7].replace('-','') : {} for vote in wroclaw_records }

all_votes = len(wroclaw_records)


print("Counting votes".format(thresh))

i = 0

step = int(math.ceil(0.1*all_votes))
thresh = step

for vote in wroclaw_records:
    code = vote[-7].replace('-','')
    # projects that vote voted for
    p_v = [vote[i] for i in [-3,-4,-5] if vote[i] > 0]
    
    # for each project
    for p in p_v:
        # get all votes that voted on the project
        for vid in project_votes[p]:
            # get post code of each vote 
            cooccured_code = votes_to_codes[vid]

            # this post code project wise co-occurs with the original votes postcode
            if cooccured_code not in codes_from_votes[code]:
                codes_from_votes[code][cooccured_code] = []

            if cooccured_code not in codes_from_projects[code]:
                codes_from_projects[code][cooccured_code] = []
            
            # count the votes? that make two postcodes co-occur
            codes_from_votes[code][cooccured_code].append(vid)
            codes_from_projects[code][cooccured_code].append(p)

    if i > thresh:
        print("{} percent done".format(thresh))
        thresh+=step

    i+=1

codes_weighted_by_vote_count = { vote[-7].replace('-','') : {} for vote in wroclaw_records }
codes_weighted_by_project_count = { vote[-7].replace('-','') : {} for vote in wroclaw_records }

print("Counting unique votes".format(thresh))

for k1 in codes_from_votes.keys():
    for k2 in codes_from_votes[k1].keys():
        codes_from_votes[k1][k2] = list(set(codes_from_votes[k1][k2]))
        codes_weighted_by_vote_count[k1][k2] = len(codes_from_votes[k1][k2]) 


for k1 in codes_from_projects.keys():
    for k2 in codes_from_projects[k1].keys():
        codes_from_projects[k1][k2] = list(set(codes_from_projects[k1][k2]))
        codes_weighted_by_project_count[k1][k2] = len(codes_from_projects[k1][k2])


print("Saving votes".format(thresh))

with open("./postcodes-coocuring-by-votes.pkl","w") as fp:
    pickle.dump(codes_from_votes, fp)

with open("./postcodes-coocuring-by-project.pkl","w") as fp:
    pickle.dump(codes_from_projects, fp)

print("Saving weights".format(thresh))

weights = {
    'codes_weighted_by_vote_count' : codes_weighted_by_vote_count,
    'codes_weighted_by_project_count' : codes_weighted_by_project_count,

}
with open("./postcodes-coocuring-weights.pkl","w") as fp:
    pickle.dump(weights, fp)
