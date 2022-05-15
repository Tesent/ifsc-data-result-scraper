import random
from time import sleep

import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import json
import csv

url = 'https://components.ifsc-climbing.org/results/'

filename = "results.csv"

#try:
#    print("Loaded file : " + filename)
#    csv = open(filename, "r")
#    last_line = csv.readlines()[-1]
#    print("Last line " + last_line)
#    last_line_id = last_line[0:5]
#    last_line_id = [int(i) for i in last_line_id.split() if i.isdigit()]
#    print("Last line id : " + str(last_line_id[0]))
#
#    csv.close()
#except:
#    print("Could not open the file")

class Result:
    def __init__(self, id: int, event_name: str, date: str, category: str):
        self.id = id
        self.event_name = event_name
        self.date = date
        self.category = category

#Ask others if qulification, semi-final and final are needed/wanted to have with athlete.
class Athlete:
    def __init__(self, id: int, rank: int, first: str, last: str, country: str, qualification: str, semi_final: str , final :str
                 ):
        self.id = id
        self.rank = rank
        self.first = first
        self.last = last
        self.country = country
        self.qualification = qualification
        self.semi_final = semi_final
        self.final = final
#Starting ID in the webiste the first recorded event has id of 65
id = 823
timeout_ms = 1500
#Events that has no competitions
errors = 0
#Fields for the .csv file
fields = ["ID" ,"Competition Title", "Competition Date","Athlete ID" ,"First", "Last", "Nation", "Category", "Rank", "Qualification", "Semifinal", "Final"]

#url for the event
url_event_year_place = lambda id: f'https://components.ifsc-climbing.org/results-api.php?api=event_results&event_id={id}'
#Url for the full list of competitors
url_event_athlete_list = lambda api: f'https://components.ifsc-climbing.org/results-api.php?api=event_full_results&result_url={api}'

while True:
    event = requests.get(url_event_year_place(id))
    event_soup = bs(event.text, 'html.parser')
    json_event_soup = json.loads(event_soup.prettify())
    print(json_event_soup)
    #Check that event exists
    if not 'error' in json_event_soup:
        for d_cats in json_event_soup["d_cats"]:
            #Collect event id, league name, year, and category from d_cats
            csv_year = Result(json_event_soup["id"], json_event_soup["name"], json_event_soup["local_start_date"], d_cats["dcat_name"])
            full_results_url = d_cats["full_results_url"]

            #Collect list of all the athletes that were in the event
            event_athlete_request = requests.get(url_event_athlete_list(full_results_url))
            event_athlete_request_soup = bs(event_athlete_request.text, "html.parser")
            json_athlete_soup = json.loads(event_athlete_request_soup.prettify())
            print(str(csv_year.id) + " " + csv_year.event_name + " " + csv_year.date + " " + csv_year.category)
            athletes = []
            #Check that json_athelet_soup does not have 'error'
            #Some events have a competion but does not have any rankings
            if not 'error' in json_athlete_soup:
                if json_athlete_soup["ranking"]:
                    for rank in json_athlete_soup["ranking"]:
                        #All athletes have qualifications but may not have semi_final or final
                        try:
                            qualification = rank["rounds"][0]["score"]
                        except:
                            qualification = ""
                        try:
                            semi_final = rank["rounds"][1]["score"]
                        except:
                            semi_final = ""
                        try:
                            final = rank["rounds"][2]["score"]
                        except:
                            final = ""
                        athlete = Athlete(rank["athlete_id"], rank["rank"], rank["firstname"] ,rank["lastname"],
                              rank["country"], qualification, semi_final, final)

                        #Some athletes have incosistent data which is why we have try: except:
                        try:
                            print(str(athlete.id) + " " + str(athlete.rank) + " " + athlete.first + " " + athlete.last + " " + athlete.country + " " + athlete.qualification + " " + athlete.semi_final + " " + athlete.final)
                        except:
                            print("Error in printing")
                        #Collect athlete and event information to a dict
                        athlete_dict = {
                            "ID" : csv_year.id,
                            "Competition Title" : csv_year.event_name,
                            "Competition Date": csv_year.date,
                            "Athlete ID": athlete.id,
                            "First": athlete.first,
                            "Last": athlete.last,
                            "Nation": athlete.country,
                            "Category": csv_year.category,
                            "Rank": athlete.rank,
                            "Qualification" : athlete.qualification,
                            "Semifinal" : athlete.semi_final,
                            "Final" : athlete.final
                        }
                        #Append collected info to athletes array
                        athletes.append(athlete_dict)
                    print("Writing to file")
                    #Sleep between writing in order to not cause too much stress to the server
                    divider = random.randint(500, 1000)
                    sleep(timeout_ms / divider)
                    with open(filename, 'a', encoding="utf-8") as file:
                        writer = csv.DictWriter(file, fieldnames=fields)
                        writer.writeheader()
                        writer.writerows(athletes)
        id += 1
        errors = 0
    else:
        print("No event at " + str(id) + " skipping event")
        id += 1
        errors += 1
    #if continues errors exceeds more than 100, break from while loop
    if errors > 100:
        break;
print("Result scrapper finished")