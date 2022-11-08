# PROGEOSAIL Python Bindings WORK IN PROGRESS

#### Valerio Pampanoni ``valerio.pampanoni@pm.me``

## Description

This is a fork of the [jgomezdans/prosail](https://github.com/jgomezdans/prosail) Python bindings to the PROSPECT and SAIL leaf and canopy reflectance models. In addition to the features provided by the original code, I have ported over functions of [Huemmrich's GeoSail model](https://www.sciencedirect.com/science/article/pii/S003442570000184X), which exploits [Jasinski's geometric model](https://ieeexplore.ieee.org/abstract/document/46705/) to represent discontinuous vegetation canopies. At the moment, the `geocone` and `geocily` functions are available to model cone-shaped and square cylinder-shaped trees respectively, but feel free to open a PR and implement more shapes.

The bindings implement the following models:

* **PROSPECT**: versions 5 and D. Flexibility to add/modify leaf absorption profiles.
* **SAIL**: FourSAIL version. The thermal extension of the model is also implemented, although this hasn't been widely tested.
* **GEO**: GEO part of Huemmrich's GeoSail code.
* Simple Lambertian soil reflectance model

Furthermore, I have completely re-written the parameter intervals, which were completely wrong in the original README, and link to my PhD thesis for a detailed explanation of the meaning of each variable. At the end of the README you can also find a small bibliography regarding the radiative transfer models, and another section about their usage for live fuel moisture content estimation.

## Using the bindings

Once you import the bindings into the namespace with

    import prosail
    
you can then run SAIL (using prescribed leaf reflectance and transmittance spectra, as well as canopy structure/soil parameters), PROSPECT and both (e.g. use PROSPECT to provide the spectral leaf optical properties).

### `run_sail`

To run SAIL with two element arrays of leaf reflectance and transmittance sampled at 1nm between 400 and 2500 nm `rho` and `tau`, using a black soil (e.g. zero reflectance), you can just do 

    rho_canopy = prosail.run_sail(rho, tau, lai, lidfa, hspot, sza, vza, raa, rsoil0=np.zeros(2101))

Here, `lai` is the LAI, `lidfa` is the mean leaf angle in degrees, `hspot` is the hotspot parameter, `sza`, `vza` and `raa` are the solar zenith, sensor zenith and relative azimuth angles, and `rsoil0` is set to an array of 0s to define the soil reflectance.

You have quite a few other options:

* You can use a different way of specifying the leaf angle distribution (by default we use a Campbell distribution with one single parameter, but you might want to use the Verhoef distribution). The Verhoef distribution is selected by adding the extra keyword `typelidf=1` and the two parameters are given by `lidfa` and the additional optional parameter `lidfb`.
* You can use the internal soil spectrum model. This model is basically `rho_soil = rsoil*(psoil*soil_spectrum1+(1-psoil)*soil_spectrum2)`. The first spectrum is a dry soil, the second one a wet one. You can also set the spectra using the `soil_spectrum1` and `soil_spectrum2` keywords.
* By default, we return the surface directional reflectance, but you can choose other reflectance factors (e.g. BHR, DHR, HDR).

### `run_prospect`

To calculate leaf reflectance and transmittance using the PROSPECT model, you can use the `run_prospect` function. You can select either the PROSPECT-5 or PROSPECT-D versions (by default, version 'D' is used). A call to this would look like:
   
    lam, rho, tau = prosail.run_prospect(n, cab, car, cbrown, cw, cm, ant=8.0)
    
Where the parameters are all scalars, and have their usual PROSPECT meanings (see table below). `ant` stands for anthocyannins, which isn't present in PROSPECT-5.

To do the same for PROSPECT-5...

    lam, rho, tau = prosail.run_prospect(n, cab, car, cbrown, cw, cm, prospect_version='5')
    
### `run_prosail`

The marriage of heaven and hell, PROSPECT being fed into SAIL in one go! Same options as the two other functions put together:

    rho_canopy = prosail.run_prosail(n, cab, car, cbrown, cw, cm, lai, lidfa, hspot, tts, tto, psi, \
                        ant=0.0, alpha=40.0, prospect_version='5', typelidf=2, lidfb=0.0, \
                        factor='SDR', rsoil0=None, rsoil=None, psoil=None, \
                        soil_spectrum1=None, soil_spectrum2=None)

### `run_progeosail`


The marriage of heaven and hell, PROSPECT being fed into SAIL in one go! Same options as the two other functions put together:



    rho_canopy = prosail.run_prosail(n, cab, car, cbrown, cw, cm, lai, lidfa, hspot, tts, tto, psi, \

                        ant=0.0, alpha=40.0, prospect_version='5', typelidf=2, lidfb=0.0, \

                        factor='SDR', rsoil0=None, rsoil=None, psoil=None, \

                        soil_spectrum1=None, soil_spectrum2=None)

## The parameters

The parameters used by the models, their units and realistic minimum and maximum values sourced in the literature can be found in the following table:

| Parameter   | Description of parameter        | Units        |Typical min | Typical max |
|-------------|---------------------------------|--------------|------------|-------------|
|   N         | Leaf structure parameter        | N/A          | 1.0        | 3.0         |
|  cab        | Chlorophyll a+b concentration   | ug/cm2       | 0          | 100         |
|  caw        | Equivalent water thickiness     | cm           | 0.0001     | 0.0360      |
|  car        | Carotenoid concentration        | ug/cm2       | 0          | 10          |
|  cbrown     | Brown pigment                   | NA           | 0          | 1           |
|  cm         | Dry matter content              | g/cm2        | 0.0017     | 0.096       |
|  lai        | Leaf Area Index                 | N/A          | 0          | 7           |
|  lidfa      | Leaf angle distribution         | N/A          | -          | -           |
|  lidfb      | Leaf angle distribution         | N/A          | -          | -           |
|  psoil      | Dry/Wet soil factor             | N/A          | 0          | 1           |
|  rsoil      | Soil brightness factor          | N/A          | 0          | 1           |
|  hspot      | Hotspot parameter               | N/A          | 0.01       | 0.40        |
|  tts        | Solar zenith angle              | deg          | 0          | 90          |
|  tto        | Observer zenith angle           | deg          | 0          | 90          |
|  phi        | Relative azimuth angle          | deg          | 0          | 360         |
| typelidf    | Leaf angle distribution type    | Integer      | -          | -           |

The values are mostly sourced from Quan et al (2021), but you can find similar values in Prikaziuk et al (2019).
### Specifying the leaf angle distribution

The parameter ``typelidf`` regulates the leaf angle distribution family being used. The following options are understood:

* ``typelidf = 1``: use the two parameter LAD parameterisation, where ``a`` and ``b`` control the average leaf slope and the distribution bimodality, respectively. Typical distributions
are given by the following parameter  choices:

| LIDF type    | ``LIDFa`` |  ``LIDFb``       |
|--------------|-----------|------------------|
| Planophile   |    1      |  0               |
|   Erectophile|    -1     |   0              |
|   Plagiophile|     0     |  -1              |
|  Extremophile|    0      |  1               |
|   Spherical  |    -0.35  |  -0.15           |
|   Uniform    |     0     |   0              |

* ``typelidf = 2`` Ellipsoidal distribution, where ``LIDFa`` parameter stands for mean leaf angle (0 degrees is planophile, 90 degrees is erectophile). ``LIDFb`` parameter is ignored.
   
### The soil model

The soil model is a fairly simple linear mixture model, where two spectra are mixed and then a brightness term added:

    rho_soil = rsoil*(psoil*soil_spectrum1+(1-psoil)*soil_spectrum2)


The idea is that one of the spectra is a dry soil and the other a wet soil, so soil moisture is then contorlled by ``psoil``. ``rsoil`` is just a brightness scaling term.

### Bibliography of the Radiative Transfer Models

### Bibliography of Live Fuel Moisture Content Estimation using the RTMs
