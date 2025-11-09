# tcwindprofile

# A fast, robust, physics-based model for the complete radial profile of tropical cyclone wind and pressure
#### Author: Dan Chavas (2025)

A package that creates fast, robust, physics-based radial profiles of the tropical cyclone rotating wind and pressure from inputs Vmax, R34kt, and latitude. Based on the latest observationally-validated science on the structure of the wind field and pressure.

Cite this package: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15442673.svg)](https://doi.org/10.5281/zenodo.15442673) . Also a paper is in prep with co-authors Dandan Tao and Robert Nystrom

Objective: To provide a faster and easier-to-use approximation to the physics-based wind model [code](https://doi.org/10.4231/CZ4P-D448) of Chavas+ (2015 JAS). That model is state-of-the-art, but slow. We want something faster/simpler that also better fits observations while staying true to the physics.


# Model motivation:
The Chavas+ (2015) model has been extensively validated for real-world TCs, in terms of both physics and hazards/impacts:

Physics:
1. Reproduces characteristic TC wind structure from the entire QuikSCAT and HWIND databases ([Chavas+ 2015 JAS](https://doi.org/10.1175/JAS-D-15-0014.1))
2. Reproduces characteristic modes of TC wind field variability due to variations in intensity and outer size from the Extended Best Track database ([Chavas and Lin 2016 JAS](https://doi.org/10.1175/JAS-D-15-0185.1)).
3. Successfully predicts that wind field structure does not change significantly in a warmer world as seen in both climate-scale and storm-scale models ([Schenkel+ 2023](https://doi.org/10.1175/JCLI-D-22-0066.1))

Hazards/impacts:
4. When used as forcing for a surge model, it reproduces the historical record of U.S. peak storm surge remarkably well ([Gori+ 2023 JGR-A](https://doi.org/10.1029/2022JD037312)). It performs better than prevailing empirical wind field model [Wang+ 2022 JGR-A](https://doi.org/10.1029/2021JD036359)).
5. When used as forcing for a physics-based rainfall model, it reproduces the climatology of U.S. tropical cyclone inland rainfall remarkably well -- and dramatically better than existing empirical wind field models ([Xi+ 2020 J. Hydromet.](https://doi.org/10.1175/JHM-D-20-0035.1)).
6. When used to model all hazards (wind, coastal surge, inland flooding), predicts the county-level distribution of economic damage quite well ([Gori+ 2025 ERL, accepted](https://www.researchgate.net/publication/391588102_Sensitivity_of_tropical_cyclone_risk_across_the_US_to_changes_in_storm_climatology_and_socioeconomic_growth)).


# Model components
Full modeling pipeline:
1. Estimate Rmax from R34kt: ref [Chavas and Knaff 2022 WAF](https://doi.org/10.1175/WAF-D-21-0103.1) "A Simple Model for Predicting the Tropical Cyclone Radius of Maximum Wind from Outer Size"
2. Estimate R0 from R34kt: analytic approximate solution, from model of ref [Emanuel 2004](https://doi.org/10.1017/CBO9780511735035.010) ("Tropical cyclone energetics and structure") / [Chavas+ 2015 JAS](https://doi.org/10.1175/JAS-D-15-0014.1) "A model for the complete radial structure of the tropical cyclone wind field. Part I: Comparison with observed structure" / [Chavas and Lin 2016 JAS](https://doi.org/10.1175/JAS-D-15-0185.1) "Part II: Wind field variability" 
3. Generate outer wind profile R34kt to R0: same refs as previous
4. Generate inner wind profile inside R34kt: mod rankine, ref [Fig 8 of Klotzbach et al. 2022 JGR-A](https://doi.org/10.1029/2022JD037030) ("Characterizing continental US hurricane risk: Which intensity metric is best?")
5. Generate complete wind profile: merge inner and outer
6. Estimate Pmin: ref [Chavas Knaff Klotzbach 2025 WAF](https://doi.org/10.1175/WAF-D-24-0031.1) ("A simple model for predicting tropical cyclone minimum central pressure from intensity and size")
7. Generate pressure profile that matches Pmin: same ref as previous

Currently, this code uses a quadratic profile inside the eye (r$<$Rmax), a modified‐Rankine vortex between Rmax and R34kt (inner model), and the E04 model beyond R34kt. It is very similar to the full physics-based wind profile model of Chavas et al. (2015) ([code here](http://doi.org/10.4231/CZ4P-D448)), but is simpler and much faster, and also includes a more reasonable eye model.

The model starts from the radius of 34kt, which is the most robust measure of size we have: it has long been routinely-estimated operationally; it is at a low enough wind speed to be accurately estimated by satellites over the ocean (higher confidence in data); and it is less noisy because it is typically outside the convective inner-core of the storm. The model then encodes the latest science to estimate 1) Rmax from R34kt (+ Vmax, latitude), 2) the radius of vanishing wind R0 from R34kt (+ latitude, an environmental constant), and 3) the minimum pressure Pmin from Vmax, R34kt, latitude, translation speed, and environmental pressure. Hence, it is very firmly grounded in the known physics of the tropical cyclone wind field while also matching the input data. It is also guaranteed to be very well‐behaved for basically any input parameter combination.
