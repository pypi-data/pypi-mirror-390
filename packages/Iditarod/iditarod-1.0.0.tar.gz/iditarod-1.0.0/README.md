Iditarod
========

Iditarod is visualizer for [Shavitt graphs](https://doi.org/10.1002/jcc.26080), which are a representation of the complete configuration state function (CSF) expansion space within a molecular electronic structure calculation.

Graph settings
--------------

The light grid can be toggled with the "Grid" checkbox. It represents all possible CSFs with a given number of orbitals. The maximum number of orbitals supported is 35, beyond that the number of CSFs can exceed the limits of 64-bit integers.

![grid graph](images/grid.png)

The colored balls and cylinders can be toggled with the "Wfn" (wave function) checkbox. They represent all possible CSFs compatible with the specified number electrons (and orbitals) and multiplicity, and with any RAS or GAS restrictions. The cylinders are colored by step vector type: red: "0", yellow: "u", purple: "d", blue: "2". 

![wave function graph](images/wfn.png)

RAS restrictions can be specified by setting the number of orbitals and maximum number of holes in RAS1, and the number of orbitals and maximum number of electrons in RAS3. GAS restrictions can be specified with any number of "*n* *m* *l*" triplets, separated by semicolons, where "*n*" is the number of orbitals in the GAS subspace, and "*m*" and "*l*" are the minimum and maximum allowed *cumulative* number of electrons in all subspaces up to that point.

The total number of CSFs (not counting different spin projection values), vertices and edges in the selected wave function graph is displayed.

Representations
---------------

Several representations are available:

* "Projected" is close to the most common representation in the literature. The vertical axis corresponds to the number of orbitals. The horizontal axis is a combination of the number of electrons and intermediate spin.

  ![projected representation](images/projected.png)

* "Canonical" is a straightforward representation of the (*a*,*b*,*c*) Paldus values as the three orthogonal axes. Note that step vectors of type "d" (down) are unit cube diagonals.

  ![canonical representation](images/canonical.png)

* "Symmetric": the vertical axis is the number of orbitals, the horizontal axis is the number of "excess" electrons (positive: more electrons than orbitals, negative: more orbitals than electrons), the depth axis is twice the intermediate spin (the *b* value). The grid is a face-centered cubic lattice, all step vectors are of the same length and join nearest neighbors, only the "side" diagonals are missing. **This is the default**.

  ![symmetric representation](images/symmetric.png)

* "Natural": the vertical axis is the number of orbitals, the horizontal axis is the number of electrons, the depth axis is the intermediate spin.

  ![natural representation](images/natural.png)

The sliders below the selectors for electrons, orbitals and multiplicity show the planes where these are constant.

![constant electrons plane](images/electrons.webp)
![constant orbitals plane](images/orbitals.webp)
![constant multiplicity plane](images/multiplicity.webp)

CSF highlight and coupling
--------------------------

Any single CSF can be highlighted in white by writing its string in the box. Alternatively, the slider and selector can be used to select a CSF by its index (in lexicographic order: "2" < "u" < "d" < "0").

![highlighted CSF](images/csf.png)

If an operator is specified, by setting its multiplicity, and indices for creation and annihilation orbitals (space-separated), all possible CSFs coupling to the selected one can be highlighted in red by toggling the "Coupling" checkbox. If the "Allow different spin" checkbox is checked, also CSFs of different spin (and/or number of electrons) will be considered. Note that this does not take into account the order of creation/annihilation operators or their specific spin coupling, the coupling CSFs are an "upper bound" to the possible ones.

![highlighted coupling](images/coupling.png)
