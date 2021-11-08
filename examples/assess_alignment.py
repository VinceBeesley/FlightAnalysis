from flightanalysis.fc_json import FCJson
from flightanalysis import Section, get_schedule, Schedule
from flightanalysis.schedule.elements import get_rates, El
import numpy as np
import pandas as pd
from pathlib import Path
import json
from flightplotting.plots import plotdtw, plotsec, grid3dplot
from tqdm import tqdm


def np_encoder(object):
    if isinstance(object, np.generic):
        return object.item()

def create_template(sec: Section, sched: Schedule, scaling: str):
    #take some measurements and create a new template based on those
    _rates = get_rates(sec)
    rates = {}
    for key, value in _rates.items():
        if isinstance(key, type):
            rates[key.__name__] = value
        else:
            rates[key]=value

    if scaling =="global":
        template = sched.scale_distance(_rates["distance"]).create_raw_template(sec[0].direction, _rates["speed"], _rates["distance"])
    elif scaling == "measure":
        template = sched.match_rates(_rates).create_raw_template(sec[0].direction, _rates["speed"], _rates["distance"])
    
    return template



def create_alignment_assesment(results_path: str, sched: Schedule, aligned: Section, fcj_aligned: Section):
    results = []
    for man in sched.manoeuvres[:-1]:
        for elm in man.elements:
            try:
                fcjsec = elm.get_data(fcj_aligned)
                fullsec = elm.get_data(aligned)
                results.append([man.name, elm.uid, fcjsec[-1].flight_time, fullsec[-1].flight_time])
            except Exception as ex:
                pass
                #print(str(ex))

        try:
            grid3dplot([[
                plotdtw(man.get_data(fcj_aligned), man.elements),
                plotdtw(man.get_data(aligned), man.elements)
            ]]).write_html(results_path.replace(".csv", "_{}.html".format(man.name)))
        
        except Exception as ex:
            pass
            #print(str(ex))
        
    df = pd.DataFrame(results, columns=['manoeuvre', 'element', 'fcj_duration', 'full_duration'])
    df.insert(len(df.columns),"difference", abs(df.fcj_duration - df.full_duration))

    return df




def parse_fc_json(path):
    with open(path) as f:
        fcj = FCJson.parse_fc_json(f)

        #get the scored part of the flight
        fcj_aligned = fcj.schedule.get_subset(fcj.sec, 0, 17)

        #create a section that has not been labelled
        sec = fcj_aligned.remove_labels()

        #get the schedule, with the connecting lines between manoeuvres linked to the following manoeuvre
        sched = get_schedule(fcj.schedule.category, fcj.schedule.name)

    return fcj, fcj_aligned, sec, sched


def assess_folder(input_folder, output_folder):
    results = []
    
    for path in tqdm(list(Path(input_folder).glob("*.json"))):

        fcj, fcj_aligned, sec, sched = parse_fc_json(path)
     
        for scaling in tqdm(["measure", "global"]):

            template = create_template(sec, sched, scaling)

            for whiten in tqdm([True, False]):

                dist, aligned = Section.align(sec, template, 5, whiten)

                results_path = str(Path(output_folder) / "{}_{}_{}.csv".format(path.stem, "whi" if whiten else "raw", scaling))
                
                df = create_alignment_assesment(results_path, sched, aligned, fcj_aligned)
                df.to_csv(results_path, index=False)

                worst_elm = df.loc[df.difference == df.difference.max()].iloc[0]

                grid3dplot([[
                    plotdtw(fcj_aligned, sched.manoeuvres),
                    plotdtw(aligned, sched.manoeuvres)
                ]]).write_html(results_path.replace(".csv", "_dtw.html"))
                
                results.append(dict(
                    schedule = fcj.schedule.name,
                    fcj = path.name,
                    csv = Path(results_path).name,
                    total_difference = df.difference.sum(),
                    worst_manoeuvre = worst_elm.manoeuvre,
                    worst_elm = worst_elm.element,
                    worst_elm_difference = worst_elm.difference,
                    whiten=whiten, 
                    scaling=scaling,
                    dtw_dist = dist,
                    **fcj.sec.get_wind()
                ))
                
                #print(json.dumps(results[-1], indent=4, default=np_encoder))
    return pd.DataFrame(results)

if __name__ == "__main__":
    results = assess_folder(
        "/home/tom/Documents/AutoJudge/fc_jsons",
        "/home/tom/Documents/AutoJudge/fc_json_assessments"
        )

    results.to_csv("dtw_assessment_summary.csv")
    pass