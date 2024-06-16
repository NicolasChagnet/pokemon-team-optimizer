import pandas as pd
import pulp
import argparse

list_starters_final_stage = [
    "venusaur",
    "charizard",
    "blastoise",
    "typhlosion",
    "meganium",
    "feraligatr",
    "swampert",
    "blaziken",
    "sceptile",
    "torterra",
    "infernape",
    "empoleon",
    "serperior",
    "emboar",
    "samurott",
    "chesnaught",
    "delphox",
    "greninja",
    "decidueye",
    "incineroar",
    "primarina",
    "rillaboom",
    "cinderace",
    "inteleon",
    "meowscarada",
    "skeledirge",
    "quaquaval",
]

list_pseudo_legendaries = [
    "dragonite",
    "tyranitar",
    "salamence",
    "metagross",
    "garchomp",
    "hydreigon",
    "goodra",
    "kommo-o",
    "dragapult",
    "hisuian Goodra",
    "baxcalibur",
]

type_columns = [
    "against_bug",
    "against_dark",
    "against_dragon",
    "against_electric",
    "against_fairy",
    "against_fight",
    "against_fire",
    "against_flying",
    "against_ghost",
    "against_grass",
    "against_ground",
    "against_ice",
    "against_normal",
    "against_poison",
    "against_psychic",
    "against_rock",
    "against_steel",
    "against_water",
]

error_codes = {1: "optimal", 0: "not solved", -1: "unfeasible", -2: "unbounded", -3: "undefined"}


def present_solution_weaknesses(team, types):
    """Given a subset of Pokemon, highlights which Pokemon is resistant for each type.

    Args:
        team (pandas.DataFrame): DataFrame with the Pokemon team.
        types (list(str)): List of type columns to consider.

    Returns:
        pandas.DataFrame: DataFrame indexed by type and with columns the team Pokemons
        as well as the minimal damage value and the Pokemon for which it happens.
    """
    team_by_name = team.set_index("name")
    team_by_types = team_by_name[types].transpose()
    team_by_types["min_val"] = team_by_types.min(axis=1)
    team_by_types["min_pkmn"] = team_by_types.idxmin(axis=1)
    team_by_types["type1"] = team_by_name.loc[team_by_types["min_pkmn"].values, "type1"].values
    team_by_types["type2"] = team_by_name.loc[team_by_types["min_pkmn"].values, "type2"].values
    return team_by_types


def optimize_team_weakness_improved(pkms, types, size_team=6, in_team=[]):
    """Solves the optimization problem associated with an optimal Pokemon team

    Args:
        pkms (pandas.DataFrame): Dataset containing the Pokemon information.
        types (list(str)): List of type columns.
        size_team (int, optional): Size of the team to find. Defaults to 6.
        in_team (list, optional): List of indexes Pokemon to manually include in the team. Defaults to [].

    Returns:
        pandas.DataFrame: Subset of the dataset corresponding to the team.
    """
    prob = pulp.LpProblem("Pokemon_Team_Optimization", pulp.LpMaximize)

    # Define the boolean variables
    x = pulp.LpVariable.dicts("x", range(len(pkms)), cat="Binary")
    y = pulp.LpVariable.dicts("y", (range(len(types)), range(len(pkms))), cat="Binary")
    z = pulp.LpVariable.dicts("z", (range(len(types)), range(len(pkms))), cat="Binary")

    # Define the base total sum
    prob += pulp.lpSum(pkmn["base_total"] * x[i] for i, pkmn in pkms.iterrows()), "Maximal base total"

    # Define the size constraint
    prob += pulp.lpSum(x[i] for i in range(len(pkms))) == size_team, "Team Size"

    # "No more than one start" constraint
    prob += pulp.lpSum(x[i] * pkmn["starter"] for i, pkmn in pkms.iterrows()) <= 1, "Number starter"

    # If some Pokemons must be in the team
    # Add a constraint to make sure they are included
    for idx in in_team:
        prob += x[idx] == 1

    # Define the weakness sum bound for each type
    # Based on https://stackoverflow.com/questions/51939363/pulp-milp-constraint-at-least-one-variable-must-be-below-0
    m = 100
    for a, type_col in enumerate(types):
        prob += pulp.lpSum(z[a][i] for i in range(len(pkms))) >= 1  # Overall constraint for each type
        for i, pkmn in pkms.iterrows():
            prob += z[a][i] <= x[i], f"Contraint z 1 for {a},{i}"
            prob += z[a][i] <= y[a][i], f"Contraint z 2 for {a},{i}"
            prob += z[a][i] >= x[i] + y[a][i] - 1, f"Contraint z 3 for {a},{i}"
            prob += x[i] * pkmn[type_col] <= 0.5 + m * (1 - y[a][i]), f"Weakness {type_col} for pokemon {i}"

    # Solve the problem
    out_code = prob.solve(pulp.apis.PULP_CBC_CMD(msg=False))

    if out_code == 1:
        print("Success!")
        idxs_sol = [i for i in range(len(pkms)) if pulp.value(x[i]) == 1]
        pkms_selected = pkms.loc[idxs_sol]
        return pkms_selected
    else:
        print(f"Error: {error_codes[out_code]}.")
        return None


def main(
    gen_cap=None,
    size_team=6,
    include_legendaries=False,
    include_pseudolegendaries=False,
    allow_multiple_starters=False,
    in_team=[],
):
    # Load the dataset
    pkms = pd.read_csv("pokemon.csv")
    # Drop the Pokemons above the Generation cap and columns we will not use
    pkms = pkms.drop(
        [
            "abilities",
            "attack",
            "base_egg_steps",
            "base_happiness",
            "capture_rate",
            "classfication",
            "defense",
            "experience_growth",
            "height_m",
            "hp",
            "japanese_name",
            "percentage_male",
            "sp_attack",
            "sp_defense",
            "speed",
            "weight_kg",
        ],
        axis=1,
    )
    pkms["name"] = pkms["name"].str.lower()
    # Boolean variable to distinguish latest stage starters
    pkms["starter"] = 0
    if not allow_multiple_starters:
        pkms["starter"] = pkms["name"].isin(list_starters_final_stage).astype(int)
    # Limit the Pokemons to the generation cap
    if gen_cap is not None:
        pkms = pkms.loc[pkms["generation"] <= gen_cap]

    # Remove legendaries
    if not include_legendaries:
        pkms = pkms.loc[pkms["is_legendary"] == 0]

    # Remove pseudo-legendaries
    if not include_pseudolegendaries:
        pkms = pkms.loc[-pkms["name"].isin(list_pseudo_legendaries)]
    pkms = pkms.reset_index(drop=True)
    # Look for manual Pokemon to include in the team

    in_team_idx = []
    if len(in_team) > size_team:
        raise ValueError("Too many Pokemon to manually include")
    if len(in_team) > 0:
        for pkmn_name in in_team:
            idx = pkms.loc[pkms["name"] == pkmn_name].index
            if idx.empty:
                raise ValueError("Pokemon {pkmn_name} not included in the dataset!")
            in_team_idx += [idx[0]]
    # Call optimizer
    team = optimize_team_weakness_improved(pkms, type_columns, size_team=size_team, in_team=in_team_idx)
    if team is not None:
        print("The optimal team is composed of")
        print(f"{team[['name', 'type1', 'type2']].set_index('name').fillna('none')}")
        print("\nThe optimal resistances are:")
        print(present_solution_weaknesses(team, type_columns)[["min_val", "min_pkmn"]])


parser = argparse.ArgumentParser(description="Pokemon Team Optimizer.")
parser.add_argument("-g", "--generation-cap", help="Generation cap", type=int, default=None, dest="gen_cap")
parser.add_argument("--size-team", help="Size of the team", type=int, default=6, dest="size_team")
parser.add_argument(
    "--include-legendaries", help="Allow legendaries in the team", action="store_true", dest="include_legendaries"
)
parser.add_argument(
    "--allow-starters", help="Allow multiple starters in the team", action="store_true", dest="allow_multiple_starters"
)
parser.add_argument(
    "--include-pseudo-legendaries",
    help="Allow pseudo-legendaries in the team",
    action="store_true",
    dest="include_pseudo_legendaries",
)
parser.add_argument("-i", "--include", nargs="+", help="Pokemon to include", default=[], dest="in_team")

if __name__ == "__main__":
    args = parser.parse_args()
    main(
        args.gen_cap,
        args.size_team,
        args.include_legendaries,
        args.include_pseudo_legendaries,
        args.allow_multiple_starters,
        in_team=args.in_team,
    )
