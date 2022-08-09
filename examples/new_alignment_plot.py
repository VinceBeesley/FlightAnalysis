import streamlit as st




col0, col1, col2 = st.columns([1,3,1])

i = col0.selectbox("man", [i for i in range(17)])

col2.write(f"{p23_def[i].info.name}: {score}")
col2.write({k: v for k, v in dgs.items() if sum(v) > 0})

plot = col0.selectbox("chart", ["flown","intended", "corrected"])

match plot:
    case "flown":
        col1.plotly_chart(plotsec(p23[i].get_data(aligned), height=800, nmodels=5))
    case "intended":
        col1.plotly_chart(plotsec(p23[i].get_data(intended_template), height=800, nmodels=5))
    case "corrected":
        col1.plotly_chart(plotsec(p23[i].get_data(corrected_template), height=800, nmodels=5))
