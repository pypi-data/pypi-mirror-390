# Basil Core
BASIL (Bayesian Analytic Sampling and Integrating Library) Core utilities;

Core utilities: A bunch of c functions that are faster than numpy matrix operations (and more conservative of your computer's RAM).

I am using this primarily in gravitational-wave population synthesis, for postprocessing with different binary evolution simulations.

User guide and jupyter notebooks incoming TBD.

## stats

`basil_core.stats.distance`
Right now, this includes a Bhattacharyya distance, Helinski distance, and relative entropy calculation
The relative entropy calculation has the advantage that it can accept pre-computed log values for P and Q.

## Astro

`basil_core.astro.coordinates` includes many coordinate transforms useful for GW astronomy, including chieff/chiminus transformations and tidal deformability parameters.

`basil_core.astro.orbit` includes many useful napkin calculations for GW astronomy, such as a timescale for a GW merger as a function of radius.
Many of these were adapted from [hush](https://github.com/katiebreivik/hush)

## Installation:

```
python3 -m pip install basil-core
```

## Contributing

We are open to pull requests.

If you would like to make a contribution, please explain what changs your are making and why.

## License
[MIT](https://choosealicense.come/licenses/mit)
