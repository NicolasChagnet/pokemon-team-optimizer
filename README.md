# Pokemon Team Optimizer

## Description
This project is about finding optimal Pokemon teams using optimization solvers and a [Pokemon dataset](https://www.kaggle.com/datasets/rounakbanik/pokemon) (with data up to Gen VII) available on Kaggle.

The main idea is to express in mathematical terms (see [this notebook](TeamOptimization.ipynb) for an explanation of the method) the following constraints for an optimal team:
1. A team should have 6 Pokemon (flexible).
2. A team should not have more than 1 starter Pokemon (flexible).
3. The base total of the whole team should be maximized.
4. For each type, there should be at least one Pokemon in the team which resists attacks from that type.

That last constraint is the most complicated to implement and required tuning (once again see [the notebook](TeamOptimization.ipynb) for more details). Some of the constraints can be parameterized such as the size of the team, the presence of multiple starters, the inclusion of (pseudo-)legendaries and finally the explicit inclusion of some Pokemon.

## How to use

You can clone this repository and find the optimized team by using
```bash
python3 main.py [-h] [-g GEN_CAP] [--size-team SIZE_TEAM] [--include-legendaries] [--allow-starters] [--include-pseudo-legendaries] [-i IN_TEAM [IN_TEAM ...]]
```

## Examples

To find an optimal generation 1 team, you can run
```console
$ python3 main.py -g 1
Success!
The optimal team is composed of
               type1     type2
name                          
charizard       fire    flying
poliwrath      water  fighting
magneton    electric     steel
kangaskhan    normal      none
gyarados       water    flying
aerodactyl      rock    flying

The optimal resistances are:
name              min_val    min_pkmn
against_bug          0.25   charizard
against_dark         0.50   poliwrath
against_dragon       0.50    magneton
against_electric     0.50    magneton
against_fairy        0.50   charizard
against_fight        0.50   charizard
against_fire         0.50   charizard
against_flying       0.25    magneton
against_ghost        0.00  kangaskhan
against_grass        0.25   charizard
against_ground       0.00   charizard
against_ice          0.50   poliwrath
against_normal       0.50    magneton
against_poison       0.00    magneton
against_psychic      0.50    magneton
against_rock         0.50   poliwrath
against_steel        0.25    magneton
against_water        0.50   poliwrath
```
The first part of the output is the optimal team while the second part shows the optimal Pokemon which resists each type. Focusing on the first output, we can see what happens if we allow legendaries with no generation restriction
```console
$ python3 main.py --include-legendaries
Success!
The optimal team is composed of
            type1   type2
name                     
mewtwo    psychic    none
kyogre      water    none
groudon    ground    none
rayquaza   dragon  flying
yveltal      dark  flying
solgaleo  psychic   steel
```
which is clearly dominated by legendaries.

If you want to complete your current team, you can also just do
```console
$ python3 main.py -g 2 -i typhlosion xatu
Success!
The optimal team is composed of
              type1   type2
name                       
gyarados      water  flying
aerodactyl     rock  flying
typhlosion     fire    none
xatu        psychic  flying
steelix       steel  ground
houndoom       dark    fire
```

## Future directions

There are a few improvements which will be part of a next release:
- The current data does not reflect the availability of a given Pokemon in a game. A cap at gen II will, for example, allow gen I Pokemon which are not available in gold/silver/crystal.
- Following on the last point, the types of each Pokemon are not constrained to the generation (the fairy type was only introduced in Gen VI yet would be used here for caps below that generation).
- The teams so-created do not optimize for offensive properties. A dataset accounting for a varied moveset could be created in order to maximize the damage and coverage.