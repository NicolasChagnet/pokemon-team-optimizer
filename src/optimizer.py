import pulp
import pandas as pd

error_codes = {1: "optimal", 0: "not solved", -1: "unfeasible", -2: "unbounded", -3: "undefined"}


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

    # "No more than one starter" constraint
    prob += pulp.lpSum(x[i] * pkmn["is_starter"] for i, pkmn in pkms.iterrows()) <= 1, "Number starters"
    # "No more than one fossil" constraint
    prob += pulp.lpSum(x[i] * pkmn["is_fossil"] for i, pkmn in pkms.iterrows()) <= 1, "Number fossils"

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
