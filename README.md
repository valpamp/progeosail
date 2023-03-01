# PROGEOSAIL Python Bindings WORK IN PROGRESS

#### Valerio Pampanoni, mailto: ``valerio.pampanoni@uniroma1.it`` (Institutional), ``valerio.pampanoni@pm.me`` (Personal)

## Repo Description

This is a fork of the [jgomezdans/prosail](https://github.com/jgomezdans/prosail) Python bindings to the PROSPECT [1] and SAIL [2] leaf and canopy reflectance models. In addition to the features provided by the original code, I have ported over functions of Huemmrich's GeoSail model [3, 4], which exploits Jasinski's geometric model [5] to represent discontinuous vegetation canopies. At the moment, the `geocone` and `geocily` functions are available to model cone-shaped and square cylinder-shaped trees respectively, but feel free to open a PR and implement more shapes.

The default spectrum supported by this module falls between 400 and 2500 nm, with a spacing of 1 nm.

The bindings implement the following models:

* **PROSPECT**: versions 5 [6] and D [7]. Flexibility to add/modify leaf absorption profiles.
* **SAIL**: FourSAIL [8] version. The thermal extension of the model is also implemented, although this hasn't been widely tested.
* **GEO**: GEO part of Huemmrich's GeoSail code.
* Simple Lambertian soil reflectance model

Furthermore, I have completely re-written the parameter intervals, which were wrong in the original README, and refer you to paragraphs 3.1.1, 3.1.2 and 3.1.3 of [my PhD thesis](https://iris.uniroma1.it/handle/11573/1666953) for a detailed explanation of the meaning of each PROSPECT-D, 4SAIL and GEO variable respectively. The values are mostly sourced from [12], but you can find similar values in [13]. At the end of the README you can also find a small bibliography regarding the radiative transfer models, and another section about their usage for Live Fuel Moisture Content estimation.

## Using the bindings

Import the bindings into the namespace with

    import progeosail
    
If the import was successful, you may choose to run PROSPECT and SAIL individually or to run their coupled version in one go. Keep in mind that should you choose to run SAIL individually, you will have to provide your own leaf reflectance and transmittance spectra arrays, while using PROSPECT will allow you to generate them by setting the model parameters appropriately.

The progeosail module contains the following functions:

* `run_prospect`
* `run_sail`
* `run_prosail`
* `run_progeosail`

We will now go through each function individually.

### The PROSPECT Model and the `run_prospect` Function

PROSPECT returns leaf reflectance and transmittance based on the biochemical characteristics of the leaf. Many different PROSPECT versions have surfaced since the publication of the original model in 1990, often introducing new parameters in the form of pigments. This implies that different model versions may require different parameters in order to run, and this module allows to choose between PROSPECT-5 and PROSPECT-D, which is used by default. The "D" in PROSPECT-D stands for "Dynamic", which refers to its capability to reproduce leaf phenology thanks to the addition of the anthocyanin pigment among the model variables. The complete list of PROSPECT-D model variables is summarized in the following table:

| Parameter   | Description of parameter        | Units        |Typical min | Typical max |
|-------------|---------------------------------|--------------|------------|-------------|
|   N         | Leaf structure parameter        | -            | 1.0        | 3.0         |
|  cab        | Chlorophyll a+b concentration   | ug/cm2       | 0          | 100         |
|  caw        | Equivalent water thickness      | cm           | 0.0001     | 0.0360      |
|  car        | Carotenoid concentration        | ug/cm2       | 0          | 10          |
|  ant        | Anthocyanin concentration       | ug/cm2       | 0          | 40          |
|  cbrown     | Brown pigment                   | -            | 0          | 1           |
|  cm         | Dry matter content              | g/cm2        | 0.0017     | 0.0960      |

In order to run PROSPECT-D we will have to call the `run_prospect` function and supply the anthocyanin pigment concentration (ant) as a keyword argument in addition to the leaf structure parameter (n), chlorophyll a and b concentration (cab), carotenoid pigment concentration (car), brown pigment (cbrown), water thickness (cw) and dry matter content (cm) as positional arguments:

    wv, rho, tau = prosail.run_prospect(n, cab, car, cbrown, cw, cm, ant=8.0)

Where `rho` and `tau` represent the , leaf reflectance and transmittance spectra respectively, and `wv` the wavelengths at which they were calculated.

In order to run PROSPECT-5, the `prospect_version` keyword argument must be supplied and must be set to `'5'`, while there is no need to supply the anthocyanin content, since it is not included in the model:

    lam, rho, tau = prosail.run_prospect(n, cab, car, cbrown, cw, cm, prospect_version='5')

### The SAIL Model and the `run_sail` Function

The Scattering by Arbitrarily Inclined Leaves (SAIL) model is one of the most widely used canopy reflectance models, and it was developed as an extension to Suits' 1972 one-dimensional, non-lambertian directional reflectance model [9]. In 1984, Verhoef proposed a novel solution of Suits' equations, introducing the Leaf Inclination Distribution Function (`LIDF`) in order to improve the model performance against changing illumination and viewing angles.

<img src="https://user-images.githubusercontent.com/50947671/222136080-f5f092a3-16e4-4dd3-9347-2d7b58342640.png" width="50%" height="50%">

**Figure 1: Suits' canopy model**

An example of Suits' model is shown in the previous figure: each canopy layer (e.g. grain, stalk, leaves) is modeled as a horizontal, infinitely extended layer, and in turn each layer is composed of randomly distributed and homogeneously mixed components. The parameters of the SAIL model are summarized in the following table:

| Parameter   | Description of parameter        | Units        |Typical min | Typical max |
|-------------|---------------------------------|--------------|------------|-------------|
|  lai        | Leaf Area Index                 | -            | 0          | 7           |
|  lidfa      | Average Leaf Slope (Angle)      | - (deg)      | -          | -           |
|  lidfb      | Distribution bi-modality        | -            | -          | -           |
|  psoil      | Dry/Wet soil factor             | -            | 0          | 1           |
|  rsoil      | Soil brightness factor          | -            | 0          | 1           |
|  hspot      | Hotspot parameter               | -            | 0.01       | 0.40        |
|  tts        | Solar zenith angle              | deg          | 0          | 90          |
|  tto        | Observer zenith angle           | deg          | 0          | 90          |
|  phi        | Relative azimuth angle          | deg          | 0          | 360         |
| typelidf    | Leaf angle distribution type    | Integer      | -          | -           |

In addition to the Leaf Area Index (LAI) and the hotspot factor (hspot), SAIL requires the user to define a number of parameters related to the inclination of the leaves that compose the canopy, the soil reflectance spectrum, and the solar and viewing illumination angles. In order to avoid confusion and to explain the ways these parameters can be supplied using this module, it is worth dedicating a small paragraph to each of them.

##### The Soil Spectra

As anticipated, SAIL requires the user to supply a soil reflectance spectrum in order to run. This module offers two pre-loaded soil spectra, `rsoil1` which represents a dry soil, and `rsoil2` which represents a wet soil. The numpy arrays containing the reflectance spectra can be accessed through the spectral_lib module as follows:

    soil_spectrum1 = spectral_lib.soil.rsoil1
    soil_spectrum2 = spectral_lib.soil.rsoil2

<img src="https://user-images.githubusercontent.com/50947671/222151586-109cd31d-1cdd-4667-88fd-831bdc1a4dd8.png" width="50%" height="50%">

**Figure 2: Default pyprosail soil spectra**

Through the `psoil` and `rsoil` parameters allow the user to mix these two spectra in controlled proportions, using the following linear mixture model, where two spectra are mixed and then a brightness term added:

    rho_soil = rsoil*(psoil*soil_spectrum1 + (1-psoil)*soil_spectrum2)

`psoil` can be considered a "soil dryness parameter", as values close to zero will return a soil reflectance spectrum dominated by the wet soil, while values close to one will return a soil reflectance spectrum dominated by the dry soil. `rsoil` acts as a generic soil brightness parameter, which we may use to scale the soil reflectance values.

The user may therefore use the two parameters `psoil` and `rsoil` to mix the default spectra as shown earlier. In addition, the user may supply an entirely new soil spectrum using the `rsoil0` positional argument. Needless to say, if `rsoil0` is supplied, the `run_sail` function will ignore `psoil` and `rsoil` if they were supplied. If no `rsoil0` was supplied and only one of the `psoil` and `rsoil` parameters was supplied, the the `run_sail` function will throw an error.

###### The Leaf Inclination Distribution Function

The Leaf Inclination Distribution Function (`LIDF`) is used to represent in a simple way a number of different leaf orientations. Verhoef [10] described a method
to define a number of different LIDFs using two parameters: average leaf slope `LIDFa`, and distribution bi-modality `LIDFb`. In addition to this method of LIDF representation, this library allows to use a simple ellipsoidal function characterized by a singular parameter representing the average leaf inclination angle.
The parameter ``typelidf`` allows to switch between one method and the other:

* ``typelidf = 1``: use the Verhoef two-parameter method, where ``LIDFa`` and ``LIDFb`` control the average leaf slope and the distribution bimodality, respectively. Popular distributions are given by the following parameter combinations:

| LIDF type    | ``LIDFa`` |  ``LIDFb``       |
|--------------|-----------|------------------|
| Planophile   |    1      |  0               |
|   Erectophile|    -1     |   0              |
|   Plagiophile|     0     |  -1              |
|  Extremophile|    0      |  1               |
|   Spherical  |    -0.35  |  -0.15           |
|   Uniform    |     0     |   0              |

* ``typelidf = 2`` Campbell distribution, where ``LIDFa`` parameter represents the average leaf angle (0 degrees is planophile, 90 degrees is erectophile). In this case, the ``LIDFb`` parameter is ignored.

By default, the `run_sail` function expects `typelidf = 2`, and therefore only the `LIDFa` value is required to run it. If the user wants to use the Verhoef parametrization, `typelidf` should be set to `1`, and both `LIDFa` and `LIDFb` should be supplied.

#### Solar and Viewing Angles

A graphical representation of the Sun-Sensor geometry is shown in the following figure:

<img src="https://user-images.githubusercontent.com/50947671/222156657-e98d726a-94c5-4d97-9f0f-0f06ad928d43.png" width="50%" height="50%">

**Figure 3: Sun-Sensor geometry scheme**

SAIL expects the user to set the following three angular parameters:

* The Solar Zenith Angle (SZA) `tts`
* The Viewer Zenith Angle (VZA) `tt0`
* The Relative Azimuth Angle (RAA) `phi`, defined as the difference between the Solar Azimuth Angle (SAA) and the Viewer Azimuth Angle (VAA)

##### Running SAIL

To run SAIL with two one-dimensional arrays of leaf reflectance and transmittance sampled with a 1 nm spacing between 400 and 2500 nm `rho` and `tau`, using an ideal black soil (e.g. zero reflectance), we can use the following command:

    rho_canopy = prosail.run_sail(rho, tau, lai, lidfa, hspot, sza, vza, raa, rsoil0=np.zeros(2101))

As explained in the previous sections, the user may:

* use a Verhoef-style two-parameter LIDF:

        rho_canopy = prosail.run_sail(rho, tau, lai, lidfa, hspot, sza, vza, raa, lidftype=1, lidfb=lidfb, rsoil0=np.zeros(2101))

* use `psoil` and `rsoil` to mix the default spectra:

        rho_canopy = prosail.run_sail(rho, tau, lai, lidfa, hspot, sza, vza, raa, lidftype=1, lidfb=lidfb, rsoil=rsoil, psoil=psoil)

* re-assign the `soil_spectrum1` and `soil_spectrum2` keywords to supply custom soil spectra and mix them using the `psoil` and `rsoil` keywords:

        rho_canopy = prosail.run_sail(rho, tau, lai, lidfa, hspot, sza, vza, raa, lidftype=1, lidfb=lidfb, rsoil, psoil, soil_spectrum1=custom_soil1, soil_spectrum2=custom_soil2)

By default, `run_sail` returns the surface directional reflectance (SDR), but you can choose other reflectance factors by setting using the `factor` keyword argument to the appropriate value:

| `factor`     | Description                                               |
|--------------|-----------------------------------------------------------|
| SDR          | Surface Directional Reflectance factor                    |
| BHR          | Bi-Hemispherical Reflectance factor                       |
| DHR          | Directional-Hemispherical Reflectance factor              |
| HDR          | Hemispherical-Directional Reflectance factor              |
| ALL          | All of the above                                          |
| ALLALL       | All of the terms calculated by SAIL, including the above  |

### PROSPECT + SAIL and the `run_prosail` Function

As anticipated, PROSPECT's output in terms of leaf reflectance and transmittance spectra can be directly fed into SAIL as an input. The inversion of PROSPECT is relatively easy, but from a remote sensing point of view, inverting the reflectance spectra of a singular leaf has limited applicability. On the other hand, SAIL provides a description of a leaf canopy, but its inversion from satellite or airborne data can be feasible only when several measurements from different viewing angles are available, which is almost never the case. To solve this issue, the two models were coupled into PROSAIL [73] since the early nineties. A graphical representation of the coupling scheme is shown in Figure 4.

<img src="https://user-images.githubusercontent.com/50947671/222176447-62afb55d-f953-4a60-b5f5-308b90925c9a.png" width="50%" height="50%">

**Figure 4: PROSPECT + SAIL Coupling Scheme**

The `run_prosail` function can be used to run the combination of PROSPECT-5 or PROSPECT-D and SAIL in one step:

    rho_canopy = prosail.run_prosail(n, cab, car, cbrown, cw, cm, lai, lidfa, hspot, tts, tto, psi)

### ProGeoSail and the `run_progeosail` Function

In 2001 [3], the SAIL model was coupled with the Jasinski Geometric model (GEO) with the objective to allow the description of radiation reflected by and transmitted through discontinuous vegetation. In order to port this functionality to `pyprosail`, we rewrote the Fortran subroutines `GEOCONE` and `GEOCILY` to Python, and interfaced them with the existing PROSAIL functions. At the moment, only nadir view is supported, and for this reason only the Sun Zenith Angle is included in the input variables, while the Viewing Zenith Angle is assumed to be zero.

| Parameter   | Description                                    | Units |
|-------------|------------------------------------------------|-------|
| `tts`       | Sun Zenith Angle                               | deg   |
| `rc`        | Nadir-view reflectance of illuminated canopy   | -     |
| `tc`        | Transmittance through canopy                   | -     |
| `rch`       | Hemispheric reflectance through canopy         | -     |
| `chw`       | Canopy height-to-width ratio                   |  m/m  |
| `ccover`    | Fraction of Canopy Cover                       | m^2/m^2 |
|  `cshp`     | Crown Shape                                    | -       |  

The reflectance and transmittance spectra are all supplied by SAIL. If the Observer Zenith Angle `tto` is set to zero (nadir view), the hemispherical-directional reflectance and transmittance through the canopy will correspond to `rc` and `tc` respectively, while the bi-hemispherical reflectance factor will correspond to `rch`. The `cshp` parameter allows to set the tree shape among the two currently supported, which are `'cylinder'` and '`cone`'. More can be implemented following the methodology described in [5].

A minimal `run_progeosail` run would look like this:

    rho_canopy = prosail.run_progeosail(chw, ccover, cshp, 
                                        n, cab, car, cbrown, cw, cm, \
                                        lai, lidfa, hspot, tts, tto, psi)

### Bibliography
[1] [S. Jacquemoud and F. Baret, PROSPECT: A model of leaf optical properties spectra, Remote sensing of environment, 34 (1990), pp. 75–91](https://www.sciencedirect.com/science/article/abs/pii/003442579090100Z)

[2] [W. Verhoef, Light scattering by leaf layers with application to canopy reflectance modeling: The SAIL model, Remote sensing of environment, 16
(1984), pp. 125–141](https://www.sciencedirect.com/science/article/abs/pii/0034425784900579)

[3] [K. Huemmrich, The GeoSail model: a simple addition to the SAIL model to describe discontinuous canopy reflectance, Remote Sensing of Environment, 75 (2001), pp. 423–431](https://www.sciencedirect.com/science/article/pii/S003442570000184X)

[4] [K. Huemmrich, PBOREAS TE-18 Geosail Canopy Reflectance Model, 2000, Online Resource (Last Accessed on 2023/03/01)](https://daac.ornl.gov/cgi-bin/dsviewer.pl?ds_id=532)

[5] [M. F. Jasinski and P. S. Eagleson, The structure of red-infrared scattergrams of semivegetated landscapes, IEEE Transactions on geoscience and remote sensing, 27 (1989), pp. 441–451.](https://ieeexplore.ieee.org/abstract/document/46705/)

[6] [J.-B. Feret, C. François, G. P. Asner, A. A. Gitelson, R. E. Martin, L. P. Bidel, S. L. Ustin, G. Le Maire, and S. Jacquemoud, PROSPECT-4 and 5: Advances in the leaf optical properties model separating photosynthetic pigments, Remote sensing of environment, 112 (2008), pp. 3030–3043](https://www.sciencedirect.com/science/article/pii/S0034425708000813)

[7] [J.-B. Féret, A. Gitelson, S. Noble, and S. Jacquemoud, PROSPECT-D: towards modeling leaf optical properties through a complete lifecycle, Remote
Sensing of Environment, 193 (2017), pp. 204–215.](https://www.sciencedirect.com/science/article/pii/S0034425717300962)

[8] [W. Verhoef, L. Jia, and Z. Su., Optical-thermal canopy radiance directionality modelling by unified 4SAIL model. (2007).
Optical-thermal canopy radiance directionality modelling by unified 4SAIL model](https://reports.nlr.nl/server/api/core/bitstreams/ecd3960d-4c3c-4a76-9bd6-186044eb0862/content)

[9] [G. Suits, G. Safir, and A. Ellingbroe, Prediction of directional reflectance of a corn field under stress, Nasa. Manned Spacecraft Center 4th Ann. Earth Resources Program Rev., Vol. 2, (1972).](https://ntrs.nasa.gov/api/citations/19720021681/downloads/19720021681.pdf)

[10] [W. Verhoef, Theory of radiative transfer models applied in optical remote sensing of vegetation canopies, Wageningen University and Research, (1998).](https://library.wur.nl/WebQuery/wurpubs/fulltext/210943)

[11] [S. Jacquemoud, F. Baret, and J. Hanocq, Modeling spectral and bidirectional soil reflectance, Remote sensing of Environment, 41 (1992), pp. 123–132.](https://www.academia.edu/download/36304247/jacquemoud1992a.pdf)

[12] [X. Quan, M. Yebra, D. Riaño, B. He, G. Lai, and X. Liu, Global fuel moisture content mapping from MODIS, International Journal of Applied Earth Observation and Geoinformation, 101 (2021), p. 102354.](https://www.sciencedirect.com/science/article/pii/S0303243421000611)

[13] [E. Prikaziuk and C. van der Tol, Global sensitivity analysis of the SCOPE model in Sentinel-3 Bands: thermal domain focus, Remote sensing, 11 (2019),
p. 2424.](https://www.mdpi.com/2072-4292/11/20/2424/pdf)

###

### Figure References

Figure 1: [9]

Figure 3: [X. Ma, A. Huete, N. N. Tran, J. Bi, S. Gao, and Y. Zeng, Sun Angle Effects on Remote-Sensing Phenology Observed and Modelled Using Himawari-8, Remote Sensing, 12 (2020)](https://www.mdpi.com/698742)

Figure 4: [T. Kattenborn, Linking Canopy Reflectance and Plant Functioning through
Radiative Transfer Models, PhD thesis, KIT-Bibliothek, 2019.](https://www.researchgate.net/profile/Teja-Kattenborn/publication/333193182_Linking_Canopy_Reflectance_and_Plant_Functioning_through_Radiative_Transfer_Models/links/5ce0329a458515712eb4ac70/Linking-Canopy-Reflectance-and-Plant-Functioning-through-Radiative-Transfer-Models.pdf)
