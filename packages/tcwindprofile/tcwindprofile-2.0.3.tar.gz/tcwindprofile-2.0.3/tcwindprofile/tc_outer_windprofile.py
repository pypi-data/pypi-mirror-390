# tcwindprofile/tc_outer_windprofile.py

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%% Wind profile from R0mean --> R34kt
#%% Exact solution to model of non-convecting wind profile (Emanuel 2004; Chavas et al. 2015 JAS)
#%% Notes:
#%% - It is a single integration inwards from R0. *Cannot* integrate out
#%%   from R34kt, it may blow up (math is weird)
#%% - Could do a simpler approximate profile instead, but this solution is
#%%   just as fast doing some sort of curve fit, so might as well use exact

import numpy as np

def E04_outerwind_r0input_nondim_MM0(r0, fcor, Cd, w_cool, Nr):
    """
    Exact Emanuel 2004 inner integration from R0→R34kt
    Returns:
      rrfracr0 : nondimensional radius array (r/r0)
      MMfracM0 : nondimensional angular momentum (M/M0)
    """
    fcor = abs(fcor)
    M0 = 0.5 * fcor * r0**2
    dr = 0.001 if (200e3 < r0 < 2500e3) else 0.0001
    Nr = min(Nr, int(1/dr))
    rrfracr0 = np.arange(1 - (Nr-1)*dr, 1+dr, dr)
    MM = np.full(rrfracr0.shape, np.nan)
    MM[-1] = 1
    rtemp, Mtemp = rrfracr0[-2], MM[-1]
    MM[-2] = Mtemp

    # loop inward
    for i in range(Nr-2):
        gam = Cd * fcor * r0 / w_cool
        dM = gam * ((Mtemp - rtemp**2)**2) / (1 - rtemp**2)
        Mtemp -= dM * dr
        rtemp -= dr
        MM[-3-i] = Mtemp

    return rrfracr0, MM


def outer_windprofile(r0_m, fcor, Cd, w_cool, V34kt_ms):
    """
    Wrapper that:
      1) calls E04_outerwind_r0input_nondim_MM0 to get rrfracr0, MM
      2) builds a physical wind profile vv_E04approx(r)
      3) zooms to r < 1.2 R0 and interpolates vv(r)
      4) profile set to NaN inside of radius of input wind speed (e.g. V34kt_ms))
    Returns:
      rr_m : radii [m]
      vv_outer_ms : wind speeds [m/s]
    """
    # 1) exact integration
    Nr=100000
    rrfracr0_E04, MMfracM0_E04 = E04_outerwind_r0input_nondim_MM0(r0_m, fcor, Cd, w_cool, Nr)
    M0_E04approx = 0.5 * fcor * r0_m**2
    rr_E04approx = rrfracr0_E04 * r0_m
    vv_E04approx = (M0_E04approx / r0_m) * ((MMfracM0_E04 / rrfracr0_E04) - rrfracr0_E04)
    vv_E04approx[vv_E04approx > 2 * V34kt_ms] = np.nan
    
    # Zoom into relevant radii
    r0_plot = 1.2 * r0_m
    dr = 100     #[m]; radial increment
    rr_m = np.arange(0, r0_plot + dr, dr)  # [m]
    # Interpolate approx-E04 solution to original radius vector
    vv_outer_ms = np.interp(rr_m, rr_E04approx, vv_E04approx)

    # # 2) build velocity
    # M0 = 0.5 * fcor * r0_m**2
    # rr_E04 = rrfracr0 * r0_m
    # vv = (M0 / r0_m) * ((MMfracM0 / rrfracr0) - rrfracr0)
    # vv[vv > 2 * V34kt_ms] = np.nan

    # # 3) zoom & interpolate
    # r0_plot = 1.2 * r0_m
    # rr_m= rr_full_m[rr_full_m < r0_plot]
    # vv_interp_ms = np.interp(rr_m, rr_E04, vv)
    return rr_m, vv_outer_ms
