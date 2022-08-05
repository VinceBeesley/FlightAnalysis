import streamlit as st
st.set_page_config(layout="wide")

from flightplotting import plotsec
from geometry import Transformation, Euler, P0
from pytest import fixture

from flightanalysis.schedule.definition import *
from flightanalysis.schedule.elements import *
from flightanalysis.criteria.comparison import *
from flightanalysis.criteria.local import *

col0, col1, col2 = st.columns([1,3,1])

md = ManDef.basic_f3a("vline")

md.add_loop(np.pi/2)
md.add_roll_combo(
    md.mps.add(ManParm(
        "roll1",
        Combination([
            [np.pi/2, np.pi/2],
            [-np.pi/2, -np.pi/2]
        ]), 0
    ))
)
md.add_loop(np.pi/2)
md.add_roll_combo(
    md.mps.add(ManParm(
        "roll2",
        Combination([
            [np.pi],
            [-np.pi]
        ]), 0
    )),
    l=100
)
md.add_loop(-np.pi/2)
md.add_roll_combo(
    md.mps.add(ManParm(
        "roll3",
        Combination([
            [np.pi/2, np.pi/2],
            [-np.pi/2, -np.pi/2]
        ]), 0
    ))
)
md.add_loop(-np.pi/2)
man = md.create()


for el in man.elements:
    if el.__class__ is Loop:
        el.radius = col0.slider(f"{el.uid} radius", 5.0, 100.0, el.radius)
    if el.__class__ is Line:
        if el.roll == 0:
            el.length = col0.slider(f"{el.uid} length", 5.0, 300.0, el.length)
        else:
            el.length = el.speed * abs(el.roll) / col0.slider(f"{el.uid} roll rate", np.pi/4, 3*np.pi, el.rate)
            el.roll = 2*np.pi * col0.slider(f"{el.uid}_roll", -2.0, 2.0, el.roll / (2 * np.pi) )



template = man.create_template(Transformation(P0(), Euler(np.pi, 0, 0)))

for roll in [md.mps.roll1, md.mps.roll2, md.mps.roll3]:       
    col0.write(f"{roll.name} Option {roll.criteria.check_option(roll.collect(man.elements))} was flown")

col1.plotly_chart(plotsec(template, nmodels=10, height=800))


downgrades = md.mps.collect(man)

score = 10 - sum([sum(dgs) for dgs in downgrades.values()])
    
col2.write(f"Inter Element Score = {score}")

col2.write("Inter Element Downgrades")
col2.json(md.mps.collect(man))