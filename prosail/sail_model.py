#!/usr/bin/env python
import numpy as np

from prosail import spectral_lib

from .FourSAIL import foursail
from .prospect_d import run_prospect

def geocone(chw, ccover, tts, rc, tc, rch, rsoil0):
    '''
    Huemmrich-style Jasinski function for the ``cone`` shape.
    In the ``cone`` case, the scene reflectance is calculated as the sum of the 
    component reflectances of the illuminated and shadow portions of the 
    background and of the canopy. In the ``cylinder`` case, the contribution of
    the shadowed crown is neglected, because it is assumed to be quantitatively 
    negligible with respect to the other components.

    Parameters
    ----------
    chw : float
        canopy height-to-width ratio. Unitless [.]
    ccover : float
        fraction of canopy cover. Unitless [.]
    tts : float
        sun zenith angle. [deg]
    rc : float
        nadir view reflectance of illuminated crown (outputted by SAIL).
    tc : float
        transmittance through crown (outputted by SAIL).
    rch : float
        hemispheric reflectance of illuminated crown (outputted by SAIL).
    rsoil0 : float
        background reflectance.

    Returns
    -------
    rsc : array of float
        scene reflectances from 400 to 2500 nm.
    gsfr : array of float
        fraction of radiation absorved by canopy from 400 to 2500nm.

    '''
    caspa = np.arctan( ( 1. / (2.*chw) ) )
    # Huemmrich implementation
    if chw > ( 1. / (2.*np.tan( np.radians( tts ) ) ) ):
        # if this condition is satisfied, the arccosine operation is well defined
        beta = np.arccos( np.tan(caspa) / np.tan( np.radians(tts) ) )
    else:
        # we fall back to the no shade value
        beta = 0.
    eta = ( np.tan(beta) - beta ) / np.pi
    fcsh = beta/np.pi
    sfrac = 1.0 - ccover - (1.0 - ccover)**(eta + 1.0)
    ilsoil = 1.0 - ccover - sfrac
    rcsh = tc*rc
    rssh = tc*rsoil0
    # Calculate scene reflectance (rsc) as the sum of the components in the scene
    # (illuminated crown, illuminated background, shadowed background)
    # weighted by their fractions in the scene
    rsc = ccover*(1. - fcsh)*rc + (ccover*fcsh)*rcsh + sfrac*rssh + ilsoil*rsoil0
    # !!! For now we do not implement the fraction of absorbed radiation
    gsfr = 0
    return rsc, gsfr

def geocyli(chw, ccover, tts, rc, tc, rch, rsoil0):
    '''
    Huemmrich-style Jasinski function for the ``cone`` shape.
    In the ``cone`` case, the scene reflectance is calculated as the sum of the 
    component reflectances of the illuminated and shadow portions of the 
    background and of the canopy. In the ``cylinder`` case, the contribution of
    the shadowed crown is neglected, because it is assumed to be quantitatively 
    negligible with respect to the other components.

    Parameters
    ----------
    chw : float
        canopy height-to-width ratio. Unitless [.]
    ccover : float
        fraction of canopy cover. Unitless [.]
    tts : float
        sun zenith angle. [deg]
    rc : float
        nadir view reflectance of illuminated crown (outputted by SAIL).
    tc : float
        transmittance through crown (outputted by SAIL).
    rch : float
        hemispheric reflectance of illuminated crown (outputted by SAIL).
    rsoil0 : float
        background reflectance.

    Returns
    -------
    rsc : array of float
        scene reflectances from 400 to 2500 nm.
    gsfr : array of float
        fraction of radiation absorved by canopy from 400 to 2500nm.

    '''
    # Calculate ETA, the ratio of canopy area to shadow area for an
    # individual crown
    eta = chw*np.tan(np.radians(tts))
    # Using ETA to calculate the fraction of the background that is shadowed (sfrac)
    # and illuminated (ilsoil)
    sfrac = 1.0 - ccover - (1.0 - ccover)**(eta + 1.0)
    ilsoil = 1.0 - ccover - sfrac
    # Reflectance of the shadowed background (rssh)
    rssh = tc*rsoil0
    # Calculate scene reflectance (rsc) as the sum of the components in the scene
    # (illuminated crown, illuminated background, shadowed background)
    # weighted by their fractions in the scene
    rsc = ccover*rc + sfrac*rssh + ilsoil*rsoil0
    # !!! For now we do not implement the fraction of absorbed radiation
    gsfr = 0
    return rsc, gsfr

def run_prosail(n, cab, car,  cbrown, cw, cm, lai, lidfa, hspot,
                tts, tto, psi, ant=0.0, alpha=40., prospect_version="5", 
                typelidf=2, lidfb=0., factor="SDR",
                rsoil0=None, rsoil=None, psoil=None,
                soil_spectrum1=None, soil_spectrum2=None):
    """Run the PROSPECT 5, D or PRO and SAILh radiative transfer models. The 
    soil model is a linear mixture model, where two spectra are combined 
    together as follows:

         rho_soil = rsoil*(psoil*soil_spectrum1+(1-psoil)*soil_spectrum2)
    By default, ``soil_spectrum1`` is a dry soil, and ``soil_spectrum2`` is a
    wet soil, so in that case, ``psoil`` is a surface soil moisture parameter.
    ``rsoil`` is a  soil brightness term. You can provide one or the two
    soil spectra if you want.  The soil spectra must be defined
    between 400 and 2500 nm with 1nm spacing.

    Parameters
    ----------
    n: float
        number of leaf layers. Unitless [-].
    cab: float
        chlorophyll a+b concentration. [g cm^{-2}].
    car: float
        leaf carotenoid concentration. [g cm^{-2}].
    cbrown: float
        brown/senescent pigment concentration. Unitless [-], usually between 0 and 1.
    cw: float
        leaf water content in [g cm^{-2}] or equivalent water thickness in [cm]
    cm: float
        leaf dry matter. [g cm^{-2}].
    lai: float
        leaf area index (LAI). Unitless [-].
    lidfa: float
        a parameter for leaf angle distribution. If typelidf=2, average
        leaf inclination angle.
    tts: float
        Solar zenith angle. [deg]
    tto: float
        Sensor zenith angle. [deg]
    psi: float
        Relative sensor-solar azimuth angle ( saa - vaa ). [deg].
    ant: float
        anthocyanins content. Used in Prospect-D and Prospect-PRO only. [ug cm^{-2}]
    alpha: float
        The alpha angle (in degrees) used in the surface scattering
        calculations. By default it's set to 40 degrees.
    prospect_version: str
        Which PROSPECT version to use. "5", "D" and "PRO" are supported.
    typelidf: int, optional
        The type of leaf angle distribution function to use. By default, it is set
        to 2.
    lidfb: float, optional
        b parameter for leaf angle distribution. If typelidf=2 it is ignored.
    factor: str, optional
        What reflectance factor to return:
        * "SDR": directional reflectance factor (default)
        * "BHR": bi-hemispherical r. f.
        * "DHR": Directional-Hemispherical r. f. (directional illumination)
        * "HDR": Hemispherical-Directional r. f. (directional view)
        * "ALL": All of them
        * "ALLALL": All of the terms calculated by SAIL, including the above
    rsoil0: float, optional
        The soil reflectance spectrum
    rsoil: float, optional
        Soil scalar 1 (brightness)
    psoil: float, optional
        Soil scalar 2 (moisture)
    soil_spectrum1: 2101-element array
        First component of the soil spectrum
    soil_spectrum2: 2101-element array
        Second component of the soil spectrum
    Returns
    --------
    rsfc: array of float
        scene reflectance factor between 400 and 2500 nm.
    gsfr: array of float
        fraction of radiation absorbed by the crown for each wavelenght between
        400 and 2500 nm. In PAR wavelengths this coincides with FAPAR.

    """

    factor = factor.upper()
    if factor not in ["SDR", "BHR", "DHR", "HDR", "ALL", "ALLALL"]:
        raise ValueError(
            "'factor' must be one of SDR, BHR, DHR, HDR, ALL or ALLALL"
        )
    if soil_spectrum1 is not None:
        assert (len(soil_spectrum1) == 2101)
    else:
        soil_spectrum1 = spectral_lib.soil.rsoil1

    if soil_spectrum2 is not None:
        assert (len(soil_spectrum1) == 2101)
    else:
        soil_spectrum2 = spectral_lib.soil.rsoil2

    if rsoil0 is None:
        if (rsoil is None) or (psoil is None):
            raise ValueError(
                "If rsoil0 isn't defined, then rsoil and psoil"
                " must be defined!"
            )
        rsoil0 = rsoil * (
        psoil * soil_spectrum1 + (1. - psoil) * soil_spectrum2)

    wv, refl, trans = run_prospect (n, cab, car,  cbrown, cw, cm, ant=ant, 
                 prospect_version=prospect_version, alpha=alpha)
    
    [tss, too, tsstoo, rdd, tdd, rsd, tsd, rdo, tdo,
         rso, rsos, rsod, rddt, rsdt, rdot, rsodt, rsost, rsot,
         gammasdf, gammasdb, gammaso] = foursail (refl, trans,  
                                                  lidfa, lidfb, typelidf, 
                                                  lai, hspot, 
                                                  tts, tto, psi, rsoil0)

    if factor == "SDR":
        return rsot
    elif factor == "BHR":
        return rddt
    elif factor == "DHR":
        return rsdt
    elif factor == "HDR":
        return rdot
    elif factor == "ALL":
        return [rsot, rddt, rsdt, rdot]
    elif factor == "ALLALL":
        return [tss, too, tsstoo, rdd, tdd, rsd, tsd, rdo, tdo,
         rso, rsos, rsod, rddt, rsdt, rdot, rsodt, rsost, rsot,
         gammasdf, gammasdb, gammaso]

def run_progeosail(chw, ccover, cshp,
                   n, cab, car,  cbrown, cw, cm, lai, lidfa, hspot,
                   tts, tto, psi, ant=0.0, alpha=40., prospect_version="5", 
                   typelidf=2, lidfb=0., factor="SDR",
                   rsoil0=None, rsoil=None, psoil=None,
                   soil_spectrum1=None, soil_spectrum2=None):
    """Run the PROSPECT 5, D or PRO and SAILh radiative transfer models and the 
    selected Jasinski geometric model. The soil model is a linear mixture model, 
    where two spectra are combined together as follows:
    
         rho_soil = rsoil*(psoil*soil_spectrum1+(1-psoil)*soil_spectrum2)
    By default, ``soil_spectrum1`` is a dry soil, and ``soil_spectrum2`` is a
    wet soil, so in that case, ``psoil`` is a surface soil moisture parameter.
    ``rsoil`` is a  soil brightness term. You can provide one or the two
    soil spectra if you want.  The soil spectra must be defined
    between 400 and 2500 nm with 1nm spacing.

    Parameters
    ----------
    chw: float
        height-to-width ratio of the crown. Unitless [-]
    ccover: float
        crown coverage, i.e. ratio of crown surface to soil surface. Unitless [-]
    cshp: str
        shape of the crowns. Currently supports 'cylinder' or 'cone'
    n: float
        number of leaf layers. Unitless [-].
    cab: float
        chlorophyll a+b concentration. [g cm^{-2}].
    car: float
        leaf carotenoid concentration. [g cm^{-2}].
    cbrown: float
        brown/senescent pigment concentration. Unitless [-], usually between 0 and 1.
    cw: float
        leaf water content in [g cm^{-2}] or equivalent water thickness in [cm]
    cm: float
        leaf dry matter. [g cm^{-2}].
    lai: float
        leaf area index (LAI). Unitless [-].
    lidfa: float
        a parameter for leaf angle distribution. If typelidf=2, average
        leaf inclination angle.
    tts: float
        Solar zenith angle. [deg]
    tto: float
        Sensor zenith angle. [deg]
    psi: float
        Relative sensor-solar azimuth angle ( saa - vaa ). [deg].
    ant: float
        anthocyanins content. Used in Prospect-D and Prospect-PRO only. [ug cm^{-2}]
    alpha: float
        The alpha angle (in degrees) used in the surface scattering
        calculations. By default it's set to 40 degrees.
    prospect_version: str
        Which PROSPECT version to use. "5", "D" and "PRO" are supported.
    typelidf: int, optional
        The type of leaf angle distribution function to use. By default, it is set
        to 2.
    lidfb: float, optional
        b parameter for leaf angle distribution. If typelidf=2 it is ignored.
    factor: str, optional
        What reflectance factor to return:
        * "SDR": directional reflectance factor (default)
        * "BHR": bi-hemispherical r. f.
        * "DHR": Directional-Hemispherical r. f. (directional illumination)
        * "HDR": Hemispherical-Directional r. f. (directional view)
        * "ALL": All of them
        * "ALLALL": All of the terms calculated by SAIL, including the above
    rsoil0: float, optional
        The soil reflectance spectrum
    rsoil: float, optional
        Soil scalar 1 (brightness)
    psoil: float, optional
        Soil scalar 2 (moisture)
    soil_spectrum1: 2101-element array
        First component of the soil spectrum
    soil_spectrum2: 2101-element array
        Second component of the soil spectrum
    Returns
    --------
    rsfc: array of float
        scene reflectance factor between 400 and 2500 nm.
    gsfr: array of float
        fraction of radiation absorbed by the crown for each wavelenght between
        400 and 2500 nm. In PAR wavelengths this coincides with FAPAR.

    """

    factor = factor.upper()
    if factor not in ["SDR", "BHR", "DHR", "HDR", "ALL", "ALLALL"]:
        raise ValueError(
            "'factor' must be one of SDR, BHR, DHR, HDR, ALL or ALLALL"
        )
    if soil_spectrum1 is not None:
        assert (len(soil_spectrum1) == 2101)
    else:
        soil_spectrum1 = spectral_lib.soil.rsoil1

    if soil_spectrum2 is not None:
        assert (len(soil_spectrum1) == 2101)
    else:
        soil_spectrum2 = spectral_lib.soil.rsoil2

    if rsoil0 is None:
        if (rsoil is None) or (psoil is None):
            raise ValueError(
                "If rsoil0 isn't defined, then rsoil and psoil"
                " must be defined!"
            )
        rsoil0 = rsoil * (
        psoil * soil_spectrum1 + (1. - psoil) * soil_spectrum2)

    wv, refl, trans = run_prospect (n, cab, car,  cbrown, cw, cm, ant=ant, 
                 prospect_version=prospect_version, alpha=alpha)
    
    [tss, too, tsstoo, rdd, tdd, rsd, tsd, rdo, tdo,
         rso, rsos, rsod, rddt, rsdt, rdot, rsodt, rsost, rsot,
         gammasdf, gammasdb, gammaso] = foursail (refl, trans,  
                                                  lidfa, lidfb, typelidf, 
                                                  lai, hspot, 
                                                  tts, tto, psi, rsoil0)
    if cshp.lower() == 'cone':
        rsc, gsfr = geocone(chw, ccover, tts, rdo, tdo, rdd, rsoil0)
        # rsc, gsfr = geocone(chw, ccover, tts, rso, tdo, rdo, rsoil0)
    elif cshp.lower() == 'cylinder':
        rsc, gsfr = geocyli(chw, ccover, tts, rdo, tdo, rdd, rsoil0)
        # rsc, gsfr = geocyli(chw, ccover, tts, rso, tdo, rdo, rsoil0)
    else:
        raise ValueError('The shape of the crown can be either cylinder or cone!')
    return rsc, gsfr

def run_sail(
    refl,
    trans,
    lai,
    lidfa,
    hspot,
    tts,
    tto,
    psi,
    typelidf=2,
    lidfb=0.0,
    factor="SDR",
    rsoil0=None,
    rsoil=None,
    psoil=None,
    soil_spectrum1=None,
    soil_spectrum2=None,
):
    """Run the SAILh radiative transfer model. The soil model is a linear
    mixture model, where two spectra are combined together as

         rho_soil = rsoil*(psoil*soil_spectrum1+(1-psoil)*soil_spectrum2)

    By default, ``soil_spectrum1`` is a dry soil, and ``soil_spectrum2`` is a
    wet soil, so in that case, ``psoil`` is a surface soil moisture parameter.
    ``rsoil`` is a  soil brightness term. You can provide one or the two
    soil spectra if you want. The soil spectra, and leaf spectra must be defined
    between 400 and 2500 nm with 1nm spacing.

    Parameters
    ----------
    refl: 2101-element array
        Leaf reflectance
    trans: 2101-element array
        leaf transmittance
    lai: float
        leaf area index
    lidfa: float
        a parameter for leaf angle distribution. If ``typliedf``=2, average
        leaf inclination angle.
    hspot: float
        The hotspot parameter
    tts: float
        Solar zenith angle
    tto: float
        Sensor zenith angle
    psi: float
        Relative sensor-solar azimuth angle ( saa - vaa )
    typelidf: int, optional
        The type of leaf angle distribution function to use. By default, is set
        to 2.
    lidfb: float, optional
        b parameter for leaf angle distribution. If ``typelidf``=2, ignored
    factor: str, optional
        What reflectance factor to return:
        * "SDR": directional reflectance factor (default)
        * "BHR": bi-hemispherical r. f.
        * "DHR": Directional-Hemispherical r. f. (directional illumination)
        * "HDR": Hemispherical-Directional r. f. (directional view)
        * "ALL": All of them
        * "ALLALL": All of the terms calculated by SAIL, including the above
    rsoil0: float, optional
        The soil reflectance spectrum
    rsoil: float, optional
        Soil scalar 1 (brightness)
    psoil: float, optional
        Soil scalar 2 (moisture)
    soil_spectrum1: 2101-element array
        First component of the soil spectrum
    soil_spectrum2: 2101-element array
        Second component of the soil spectrum

    Returns
    --------
    Directional surface reflectance between 400 and 2500 nm


    """

    factor = factor.upper()
    if factor not in ["SDR", "BHR", "DHR", "HDR", "ALL", "ALLALL"]:
        raise ValueError(
            "'factor' must be one of SDR, BHR, DHR, HDR, ALL or ALLALL"
        )
    if soil_spectrum1 is not None:
        assert len(soil_spectrum1) == 2101
    else:
        soil_spectrum1 = spectral_lib.soil.rsoil1

    if soil_spectrum2 is not None:
        assert len(soil_spectrum1) == 2101
    else:
        soil_spectrum2 = spectral_lib.soil.rsoil2

    if rsoil0 is None:
        if (rsoil is None) or (psoil is None):
            raise ValueError(
                "If rsoil0 isn't define, then rsoil and psoil"
                " need to be defined!"
            )
        else:
            rsoil0 = rsoil * (
                psoil * soil_spectrum1 + (1.0 - psoil) * soil_spectrum2
            )

    [
        tss,
        too,
        tsstoo,
        rdd,
        tdd,
        rsd,
        tsd,
        rdo,
        tdo,
        rso,
        rsos,
        rsod,
        rddt,
        rsdt,
        rdot,
        rsodt,
        rsost,
        rsot,
        gammasdf,
        gammasdb,
        gammaso,
    ] = foursail(
        refl, trans, lidfa, lidfb, typelidf, lai, hspot, tts, tto, psi, rsoil0
    )

    if factor == "SDR":
        return rsot
    elif factor == "BHR":
        return rddt
    elif factor == "DHR":
        return rsdt
    elif factor == "HDR":
        return rdot
    elif factor == "ALL":
        return [rsot, rddt, rsdt, rdot]
    elif factor == "ALLALL":
        return [
            tss,
            too,
            tsstoo,
            rdd,
            tdd,
            rsd,
            tsd,
            rdo,
            tdo,
            rso,
            rsos,
            rsod,
            rddt,
            rsdt,
            rdot,
            rsodt,
            rsost,
            rsot,
            gammasdf,
            gammasdb,
            gammaso,
        ]


def run_thermal_sail(
    lam,
    tveg,
    tsoil,
    tveg_sunlit,
    tsoil_sunlit,
    t_atm,
    lai,
    lidfa,
    hspot,
    tts,
    tto,
    psi,
    rsoil=None,
    refl=None,
    emv=None,
    ems=None,
    typelidf=2,
    lidfb=0,
):
    c1 = 3.741856e-16
    c2 = 14388.0
    # Calculate the thermal emission from the different
    # components using Planck's Law
    top = (1.0e-6) * c1 * (lam * 1e-6) ** (-5.0)
    Hc = top / (np.exp(c2 / (lam * tveg)) - 1.0)  # Shade leaves
    Hh = top / (np.exp(c2 / (lam * tveg_sunlit)) - 1.0)  # Sunlit leaves
    Hd = top / (np.exp(c2 / (lam * tsoil)) - 1.0)  # shade soil
    Hs = top / (np.exp(c2 / (lam * tsoil_sunlit)) - 1.0)  # Sunlit soil
    Hsky = top / (np.exp(c2 / (lam * t_atm)) - 1.0)  # Sky emission

    # Emissivity calculations
    if refl is not None and emv is None:
        emv = 1.0 - refl  # Assuming absorption is 1

    if rsoil is not None and ems is None:
        ems = 1.0 - rsoil

    if rsoil is None and ems is not None:
        rsoil = 1.0 - ems
    if refl is None and emv is not None:
        refl = 1.0 - emv

    [
        tss,
        too,
        tsstoo,
        rdd,
        tdd,
        rsd,
        tsd,
        rdo,
        tdo,
        rso,
        rsos,
        rsod,
        rddt,
        rsdt,
        rdot,
        rsodt,
        rsost,
        rsot,
        gammasdf,
        gammasdb,
        gammaso,
    ] = foursail(
        refl,
        np.zeros_like(refl),
        lidfa,
        lidfb,
        typelidf,
        lai,
        hspot,
        tts,
        tto,
        psi,
        rsoil,
    )

    gammad = 1.0 - rdd - tdd
    gammao = 1.0 - rdo - tdo - too

    # tso = tss * too + tss * (tdo + rsoil * rdd * too) / (1.0 - rsoil * rdd)
    tso = tsstoo + tss * (tdo + rsoil * rdd * too) / (1.0 - rsoil * rdd)
    ttot = (too + tdo) / (1.0 - rsoil * rdd)
    gammaot = gammao + ttot * rsoil * gammad
    gammasot = gammaso + ttot * rsoil * gammasdf

    aeev = gammaot
    aees = ttot * ems

    Lw = (
        (rdot * Hsky) / np.pi
        + (
            aeev * Hc
            + gammasot * emv * (Hh - Hc)
            + aees * Hd
            + tso * ems * (Hs - Hd)
        )
    ) / np.pi

    dnoem1 = top / (Lw * np.pi)
    Tbright = c2 / (lam * np.log(dnoem1 + 1.0))
    dir_em = 1.0 - rdot
    return Lw, Tbright, dir_em
