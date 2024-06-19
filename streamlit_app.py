import streamlit as st
import main
from src import config
import pandas as pd

data_all = pd.read_csv(config.get_file_loc("nat"))
all_pkmn_names = data_all["name"]

# Streamlit UI
st.title("Pokemon Team Optimizer")

st.sidebar.header("Input Parameters")
legendaries = st.sidebar.toggle("Include legendaries")
plegendaries = st.sidebar.toggle("Include pseudo-legendaries")
starters = st.sidebar.toggle("Allow more than one starter?")
fossils = st.sidebar.selectbox("Include fossils?", ("all", "one", "none"), index=2)
version = st.sidebar.selectbox(
    "Version restriction",
    config.list_games.keys(),
    index=len(config.list_games.keys()) - 1,
    format_func=lambda x: config.list_games_names[x],
)
size_team = st.sidebar.number_input("Size of the team: ", min_value=1, max_value=len(all_pkmn_names), value=6)
gens = st.sidebar.multiselect("What generations should be included (empty means all)?", range(1, config.NGENS + 1))
in_team = st.sidebar.multiselect("Pokemons to include:", all_pkmn_names)
out_team = st.sidebar.multiselect("Pokemons to exclude:", all_pkmn_names)


if st.button("Solve"):
    team, resistances = main.team_optimizer(
        gen_cap=None,
        gens=gens,
        version=version,
        size_team=size_team,
        fossils=fossils,
        include_legendaries=legendaries,
        include_pseudolegendaries=plegendaries,
        allow_multiple_starters=starters,
        in_team=in_team,
        out_team=out_team,
    )
    team = team.rename(columns={"name": "Pokemon", "type1": "Type 1", "type2": "Type 2"})
    resistances = resistances.rename(
        index={0: "Type"}, columns={"min_val": "Minimal factor", "min_pkmn": "Optimal defender"}
    )
    st.subheader("Result")
    if team is None:
        st.write("Status: Error!")
    else:
        st.write("Status: Success!")
        st.data_editor(
            team[["img", "Pokemon", "Type 1", "Type 2"]],
            column_config={"img": st.column_config.ImageColumn("Sprite", help="Pokemon sprite")},
            hide_index=True,
            width=500,
            disabled=True,
        )
        st.write(
            resistances[["Minimal factor", "Optimal defender"]].transpose(),
            width=500,
        )

    # st.subheader("Variable Values")
    # for var, value in result["Variables"].items():
    #     st.write(f"{var}: {value}")
