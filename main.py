import pandas as pd
import pulp
import argparse
from src.optimizer import optimize_team_weakness_improved
from src import config

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


def main(
    gen_cap=None,
    size_team=6,
    include_legendaries=False,
    include_pseudolegendaries=False,
    fossils="none",
    allow_multiple_starters=False,
    in_team=[],
):
    # Load the dataset
    pkms = pd.read_csv(config.path_latest_file)

    # Limit the Pokemons to the generation cap
    if gen_cap is not None:
        pkms = pkms.loc[pkms["generation"] <= gen_cap]

    # Boolean variable to distinguish latest stage starters
    if allow_multiple_starters:
        pkms["is_starter"] = 0

    match fossils:
        case "all":
            pkms["is_fossil"] = 0
        case "none":
            pkms = pkms.loc[pkms["is_fossil"] == 0]

    # Remove legendaries
    if not include_legendaries:
        pkms = pkms.loc[pkms["is_legendary"] == 0]

    # Remove pseudo-legendaries
    if not include_pseudolegendaries:
        pkms = pkms.loc[pkms["is_pseudo_legendary"] == 0]
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
    "-f",
    "--fossils",
    help="Allow one or multiple fossils",
    type=str,
    choices=["all", "one", "none"],
    dest="fossils",
    default="none",
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
        gen_cap=args.gen_cap,
        size_team=args.size_team,
        include_legendaries=args.include_legendaries,
        include_pseudolegendaries=args.include_pseudo_legendaries,
        allow_multiple_starters=args.allow_multiple_starters,
        fossils=args.fossils,
        in_team=args.in_team,
    )
