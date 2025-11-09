# tcwindprofile/plot_windprofile.py

import matplotlib.pyplot as plt

def plot_wind_and_pressure(
    # wind profile inputs
    rr_wind_km, vv_ms,
    Rmax_km, Vmaxmean_ms,
    R34kt_km, V34kt_ms,
    R0_km, lat_deg,
    # pressure profile inputs
    rr_pres_km, PP_mb,
    Renv_km, Penv_mb, Pmin_mb,
    save_path: str = "tc_wind_pressure_profiles"
):
    """
    Plot wind profile (top) and pressure profile (bottom) in one figure.

    Parameters
    ----------
    rr_wind_km : array_like
        Radii for wind [km]
    vv_ms : array_like
        Wind speeds [m/s]
    Rmax_km, Vmaxmean_ms : float
        Radius and value of maximum wind
    R34kt_km, V34kt_ms : float
        Radius and value of 34 kt mean wind
    R0_km : float
        Outer radius where wind drops to zero
    lat_deg : float
        Latitude (for annotation only)

    rr_pres_km : array_like
        Radii for pressure [km]
    PP_mb : array_like
        Pressure profile [mb]
    Renv_km, Penv_mb : float
        Environmental radius & pressure
    Pmin_mb : float
        Minimum central pressure

    save_path : str, optional
        If given, figure will be saved to `<save_path>.jpg`.
    
    Returns
    -------
    fig, (ax1, ax2)
        The Figure and Axes objects.
    """

    # Figure size: 15 cm wide, 30 cm tall
    # fig, (ax1, ax2) = plt.subplots(
    #     2, 1,
    #     figsize=(15/2.54, 30/2.54),
    #     sharex=False
    # )
    fig, (ax1, ax2) = plt.subplots(
        2, 1,
        figsize=(15/2.54, 22.5/2.54),
        sharex=False,
        gridspec_kw={'height_ratios': [2, 1]}
    )

    # ── Top: Wind profile ───────────────────────────────────────────────
    ax1.plot(rr_wind_km, vv_ms, color='m', linewidth=3, zorder=1)
    ax1.plot(Rmax_km, Vmaxmean_ms, 'k.', markersize=20, zorder=5)
    ax1.plot(R34kt_km, V34kt_ms, 'k.', markersize=20, zorder=5)
    ax1.plot(R0_km, 0, 'm*', markersize=20, zorder=5)
    ax1.plot([R0_km, R0_km], [0, 1000], 'k--', linewidth=1)
    ax1.set_xlim(0, 1.1 * R0_km)
    ax1.set_ylim(0, 1.1 * Vmaxmean_ms)
    ax1.set_xlabel('radius [km]')
    ax1.set_ylabel('azimuthal wind speed [m/s]')
    ax1.set_title('Wind profile', fontsize=12)

    ann1 = (
        f"Inputs:\n"
        f"Vmax_mean = {Vmaxmean_ms:.1f} m/s\n"
        f"R34kt_mean = {R34kt_km:.1f} km\n"
        f"lat = {lat_deg:.1f}°N\n\n"
        f"Output:\n"
        f"Rmax = {Rmax_km:.1f} km\n"
        f"R0 = {R0_km:.1f} km"
    )
    ax1.text(
        0.95, 0.95, ann1,
        transform=ax1.transAxes,
        ha='right', va='top',
        fontsize=10,
        bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
    )

    # ── Bottom: Pressure profile ────────────────────────────────────────
    ax2.plot(rr_pres_km, PP_mb, color='m', linewidth=3, zorder=1)
    ax2.plot(0, Pmin_mb, 'k.', markersize=15, zorder=5)
    ax2.plot([Renv_km, Renv_km], [0, 10000], 'k--', linewidth=1)
    ax2.plot(Renv_km, Penv_mb, 'k.', markersize=15, zorder=5)
    ax2.set_xlim(0, 1.1 * Renv_km)
    ax2.set_ylim(0.98 * Pmin_mb, 1020)
    ax2.set_xlabel('radius [km]')
    ax2.set_ylabel('sea-level pressure [mb]')
    ax2.set_title('Pressure profile', fontsize=12)

    ann2 = (
        f"Inputs:\n"
        f"Penv = {Penv_mb:.1f} mb\n"
        f"Output:\n"
        f"Pmin = {Pmin_mb:.1f} mb\n"
    )
    ax2.text(
        0.2, 0.4, ann2,
        transform=ax2.transAxes,
        ha='left', va='top',
        fontsize=10,
        bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
    )

    plt.tight_layout()
    if save_path:
        fig.savefig(f"{save_path}.jpg", dpi=300)
    plt.show()

    return fig, (ax1, ax2)
