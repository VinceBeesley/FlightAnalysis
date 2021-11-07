from flightanalysis.fc_json import FCJson
from flightanalysis import Section, get_schedule
import numpy as np
import pandas as pd
from pathlib import Path
import json
from flightplotting.plots import plotdtw, plotsec, grid3dplot

def np_encoder(object):
    if isinstance(object, np.generic):
        return object.item()



def create_alignment_assesment(fcj_path: str, results_path: str, show_plots: bool = False):
    print("reading fcj ")
    with open(fcj_path) as f:
        fcj = FCJson.parse_fc_json(f)

    #get the scored part of the flight
    fcj_aligned = fcj.schedule.get_subset(fcj.sec, 0, 17)

    #create a section that has not been labelled
    sec = fcj_aligned.remove_labels()

    #get the schedule, with the connecting lines between manoeuvres linked to the following manoeuvre
    sched = get_schedule(fcj.schedule.category, fcj.schedule.name)

    print("creating template")
    #take some measurements and create a new template based on those
    distance = sec.y.mean()
    speed = sec.bvx.mean()
    print("distance = {}, speed = {}".format(distance, speed))
    template = sched.scale_distance(distance).create_raw_template(sec[0].direction, speed, distance)

    print("performing full alignment")
    #perform the alignment of the entire sequence.
    dist, aligned = Section.align(sec, template, 5)

    print("reading results")
    results = []
    for man in sched.manoeuvres[:-1]:

        #the first element is the line before the manoeuvre. in the fcj section that line is shared
        #with the last element of the previous manoeuvre. The start of the first element will therefore
        #always be later in the fcj section than in the fully split section.
        #The last point of all but the last element should coincide very closely. 

        for elm in man.elements:
            try:

                fcjsec = elm.get_data(fcj_aligned)
                fullsec = elm.get_data(aligned)

                results.append([man.name, elm.uid, fcjsec[-1].flight_time, fullsec[-1].flight_time])
                #print("{}, element {}, fcjduration={}, fullduration={}".format(*results[-1]))
            except Exception as ex:
                print(str(ex))

        fig=grid3dplot([[
            plotdtw(man.get_data(fcj_aligned), man.elements),
            plotdtw(man.get_data(aligned), man.elements)
        ]])
        fig.write_html(results_path.replace(".csv", "_{}.html".format(man.name)))

        
    df = pd.DataFrame(results, columns=['manoeuvre', 'element', 'fcj_duration', 'full_duration'])

    df["difference"] = abs(df.fcj_duration - df.full_duration)

    df.to_csv(results_path, index=False)

    worst_elm = df.loc[df.difference == df.difference.max()].iloc[0]

    fig=grid3dplot([[
            plotdtw(fcj_aligned, fcj.schedule.manoeuvres),
            plotdtw(aligned, sched.manoeuvres)
        ]])
    fig.write_html(results_path.replace(".csv", "_dtw.html"))
    if show_plots:
        fig.show()

    return dict(
        schedule = fcj.schedule.name,
        fcj = Path(fcj_path).name,
        csv = Path(results_path).name,
        total_difference = df.difference.sum(),
        worst_manoeuvre = worst_elm.manoeuvre,
        worst_elm = worst_elm.element,
        worst_elm_difference = worst_elm.difference,
        **fcj.sec.get_wind()
    )



def assess_folder(input_folder, output_folder, show_plots: bool=False):
    results = []
    for path in Path(input_folder).glob("*.json"):
        res = create_alignment_assesment(
            str(path), 
            str(Path(output_folder) / "{}.csv".format(path.stem)),
            show_plots
        )
        results.append(res)
        
        print(json.dumps(res, indent=4, default=np_encoder))
        break
    return pd.DataFrame(results)

if __name__ == "__main__":
    results = assess_folder(
        "/home/tom/Documents/AutoJudge/fc_jsons",
        "/home/tom/Documents/AutoJudge/fc_json_assessments",
        False
        )

    results.to_csv("dtw_assessment_summary.csv")
    pass