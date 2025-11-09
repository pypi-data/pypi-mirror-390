# tcwindprofile/tc_outer_radius_estimate.py

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%% Very good estimate of outer edge of storm, R0mean (where v=0)
#%% Analytic approximation of R0mean, from physical model of non-convecting wind profile (Emanuel 2004; Chavas et al. 2015 JAS)

#%% Citation forthcoming...

import numpy as np

def estimate_outer_radius(R34ktmean_m, V34kt_ms, fcor,
                          Cd: float = 1.5e-3,
                          w_cool: float = 2/1000,
                          beta: float = 1.35) -> float:
    """
    Analytically approximate the storm outer radius R0 (where v→0)
    using the Emanuel 2004 / Chavas et al. 2015 non‑convecting wind model.
    
    Parameters
    ----------
    R34ktmean_m : float
      Mean radius of 34 kt wind (m)
    V34kt : float
      34 kt wind speed (m/s)
    fcor : float
      Coriolis parameter (s⁻¹)
    Cd : float, optional
      Drag coefficient (default 1.5e-3)
    w_cool : float, optional
      radiative cooling-induced subsidence rate (m/s) (default 2 / 1000)
    beta : float, optional
      Model parameter (default 1.35)
    
    Returns
    -------
    R0_dMdrcnstmod : float
      Estimated outer radius (m)
    """
    chi = 2 * Cd / w_cool
    Mfit = R34ktmean_m * V34kt_ms + 0.5 * fcor * R34ktmean_m**2

    c1 = 0.5 * fcor
    c2 = 0.5 * beta * fcor * R34ktmean_m
    c3 = -Mfit
    c4 = -R34ktmean_m * Mfit - chi * (beta * R34ktmean_m * V34kt_ms)**2
    coeffs = [c1, c2, c3, c4]

    roots = np.roots(coeffs).real
    candidates = roots[roots > 0]
    if candidates.size == 0:
        raise ValueError("No positive root found for outer radius")
    return candidates[0]
