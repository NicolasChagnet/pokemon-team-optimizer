# Pokemon Team Optimizer

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://pokemon-team-optimizer.streamlit.app/)

## Description
This project is about finding optimal Pokemon teams using optimization solvers and a [Pokemon dataset](https://www.kaggle.com/datasets/rounakbanik/pokemon) (with data up to Gen VII) available on Kaggle. To further improve this project, datasets for each "version group" pokedex were created (where version group referers to version bundles such as Red-Blue-Yellow, Gold-Silver-Crystal, Ruby-Sapphire-Emerald, FireRed-LeafGreen, etc...).

**DEMO**: View streamlit app.

The main idea is to express in mathematical terms (see [this notebook](TeamOptimization.ipynb) for an explanation of the method) the following constraints for an optimal team:
1. A team should have 6 Pokemon (flexible).
2. A team should not have more than 1 starter Pokemon (flexible).
3. The base total of the whole team should be maximized.
4. For each type, there should be at least one Pokemon in the team which resists attacks from that type.

That last constraint is the most complicated to implement and required tuning (once again see [the notebook](TeamOptimization.ipynb) for more details). Some of the constraints can be parameterized such as the size of the team, the presence of multiple starters, the inclusion of (pseudo-)legendaries, fossils and finally the explicit inclusion of some Pokemon.

**Other features:**
- Possibility to select/remove (pseudo-)legendaries (ultra beasts are counted as legendaries for this purpose), fossils.
- Possibility of restricting both the *generation* of available Pokemons and the *version group* of the dataset (for example, one can make a team with only gen II Pokemon in GSC, etc...). The default `nat` version corresponds
- Possibility to manually include/exclude specific Pokemon by name (good to complete a partially made team)
- Versions take into account the type matches *at the time*, including the anomalous types in RBY. **NOTE:** in RBY, no Pokemon can resist dragons, however there are no dragon stab moves so they are excluded in the constraint to allow for a solution.

## How to use

You can clone this repository and find the optimized team by using
```console
usage: main.py [-h] [--generation-cap GEN_CAP | -g GENS [GENS ...]] [-v {rby,gsc,rse,frlg,dp,plat,hgss,bw,bw2,xy,oras,sm,usum,swsh,bdsp,sv,nat}]
               [--size-team SIZE_TEAM] [--include-legendaries] [--allow-starters] [-f {all,one,none}] [--include-pseudo-legendaries] [-i IN_TEAM [IN_TEAM ...]]
               [-e OUT_TEAM [OUT_TEAM ...]] [--show-resistances]

Pokemon Team Optimizer

options:
  -h, --help            show this help message and exit
  --generation-cap GEN_CAP
                        Generation cap
  -g GENS [GENS ...], --generations GENS [GENS ...]
                        Pokemon generations to include
  -v {rby,gsc,rse,frlg,dp,plat,hgss,bw,bw2,xy,oras,sm,usum,swsh,bdsp,sv,nat}, --version {rby,gsc,rse,frlg,dp,plat,hgss,bw,bw2,xy,oras,sm,usum,swsh,bdsp,sv,nat}
                        Pokedex version to choose from
  --size-team SIZE_TEAM
                        Size of the team
  --include-legendaries
                        Allow legendaries in the team
  --allow-starters      Allow multiple starters in the team
  -f {all,one,none}, --fossils {all,one,none}
                        Allow one or multiple fossils
  --include-pseudo-legendaries
                        Allow pseudo-legendaries in the team
  -i IN_TEAM [IN_TEAM ...], --include IN_TEAM [IN_TEAM ...]
                        Pokemon to include
  -e OUT_TEAM [OUT_TEAM ...], --exclude OUT_TEAM [OUT_TEAM ...]
                        Pokemon to exclude
  --show-resistances    Show resistance table in the output
```

## Examples

To find an optimal team for Red-Blue-Yellow, you can run
```console
$ python3 main.py -v rby --show-resistances
Success!
The optimal team is composed of
            type1    type2
name                      
arcanine     fire     none
golem        rock   ground
exeggutor   grass  psychic
gyarados    water   flying
lapras      water      ice
snorlax    normal     none

The optimal resistances are:
name              min_val   min_pkmn
against_flying       0.50      golem
against_ice          0.25     lapras
against_electric     0.00      golem
against_normal       0.50      golem
against_fire         0.50   arcanine
against_water        0.50  exeggutor
against_ground       0.00   gyarados
against_poison       0.25      golem
against_fighting     0.50  exeggutor
against_rock         0.50      golem
against_bug          0.50   arcanine
against_ghost        0.00  exeggutor
against_psychic      0.50  exeggutor
against_grass        0.50   arcanine
```
The first part of the output is the optimal team while the second part shows the optimal Pokemon which resists each type. Focusing on the first output, we can see what happens if we allow legendaries up to gen VI
```console
$ python3 main.py -g 6 --include-legendaries
Success!
The optimal team is composed of
           type1   type2
name                    
ho-oh       fire  flying
kyogre     water    none
dialga     steel  dragon
giratina   ghost  dragon
arceus    normal    none
xerneas    fairy    none
```
which is clearly dominated by legendaries. You can also combine version and generation restriction. For example, if you want a pure Gen 2 team in Gold-Silver-Crystal:
```console
Success!
The optimal team is composed of
              type1   type2
name                       
typhlosion     fire    none
crobat       poison  flying
steelix       steel  ground
espeon      psychic    none
kingdra       water  dragon
blissey      normal    none
```

Finally, ff you want to complete your current team, you can also just do
```console
$ python3 main.py -v gsc -i typhlosion xatu
Success!
The optimal team is composed of
              type1   type2
name                       
typhlosion     fire    none
steelix       steel  ground
arcanine       fire    none
xatu        psychic  flying
kingdra       water  dragon
snorlax      normal    none
```

## Future directions

There are a few improvements which will be part of a next release:
- The current data does not reflect the availability of a given Pokemon in a game. A cap at gen II will, for example, allow gen I Pokemon which are not available in gold/silver/crystal. &check;
- Following on the last point, the types of each Pokemon are not constrained to the generation (the fairy type was only introduced in Gen VI yet would be used here for caps below that generation). &check;
- The teams so-created do not optimize for offensive properties. A dataset accounting for a varied moveset could be created in order to maximize the damage and coverage.