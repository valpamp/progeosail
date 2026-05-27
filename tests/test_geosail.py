import numpy as np
import pytest

import progeosail


def test_geocyli_matches_huemmrich_aspen_example():
    ccover = np.arange(0.1, 1.1, 0.1)
    rc = np.array([0.0253, 0.4175])
    tc = np.array([0.0360, 0.2313])
    rch = np.array([0.0275, 0.4739])
    rsoil0 = np.array([0.1320, 0.2250])

    expected_rsc = np.array(
        [
            [0.0887, 0.1999],
            [0.0589, 0.1932],
            [0.0396, 0.2006],
            [0.0280, 0.2186],
            [0.0220, 0.2443],
            [0.0198, 0.2750],
            [0.0200, 0.3090],
            [0.0214, 0.3446],
            [0.0233, 0.3809],
            [0.0253, 0.4175],
        ]
    )
    expected_gsfr = np.array(
        [
            [0.3793, 0.2875],
            [0.6132, 0.4355],
            [0.7632, 0.5123],
            [0.8551, 0.5417],
            [0.9074, 0.5393],
            [0.9335, 0.5162],
            [0.9438, 0.4806],
            [0.9457, 0.4382],
            [0.9439, 0.3930],
            [0.9412, 0.3469],
        ]
    )

    actual = np.array(
        [
            progeosail.geocyli(3.5, cover, 42.27, rc, tc, rch, rsoil0)
            for cover in ccover
        ]
    )

    assert np.allclose(actual[:, 0], expected_rsc, atol=5e-4)
    assert np.allclose(actual[:, 1], expected_gsfr, atol=5e-4)


def test_geocone_matches_huemmrich_spruce_example():
    ccover = np.arange(0.1, 1.1, 0.1)
    rc = np.array([0.0466, 0.3286])
    tc = np.array([0.0085, 0.0686])
    rch = np.array([0.0454, 0.3740])
    rsoil0 = np.array([0.0780, 0.3210])

    expected_rsc = np.array(
        [
            [0.0509, 0.2230],
            [0.0334, 0.1623],
            [0.0230, 0.1291],
            [0.0178, 0.1156],
            [0.0159, 0.1153],
            [0.0162, 0.1233],
            [0.0178, 0.1361],
            [0.0199, 0.1512],
            [0.0222, 0.1671],
            [0.0246, 0.1833],
        ]
    )
    expected_gsfr = np.array(
        [
            [0.4018, 0.4307],
            [0.6453, 0.6112],
            [0.7962, 0.7000],
            [0.8842, 0.7347],
            [0.9305, 0.7362],
            [0.9509, 0.7177],
            [0.9566, 0.6882],
            [0.9553, 0.6534],
            [0.9513, 0.6166],
            [0.9468, 0.5794],
        ]
    )

    actual = np.array(
        [
            progeosail.geocone(7.0, cover, 42.27, rc, tc, rch, rsoil0)
            for cover in ccover
        ]
    )

    assert np.allclose(actual[:, 0], expected_rsc, atol=5e-4)
    assert np.allclose(actual[:, 1], expected_gsfr, atol=5e-4)


def test_geocily_alias_matches_geocyli():
    args = (3.5, 0.3, 42.27, 0.0253, 0.0360, 0.0275, 0.1320)

    assert progeosail.geocily(*args) == progeosail.geocyli(*args)


@pytest.mark.parametrize("geo_func", [progeosail.geocone, progeosail.geocyli])
def test_geosail_zero_cover_returns_soil_and_zero_absorption(geo_func):
    rsoil0 = np.array([0.1, 0.2])

    rsc, gsfr = geo_func(
        chw=3.5,
        ccover=0.0,
        tts=42.27,
        rc=np.array([0.3, 0.4]),
        tc=np.array([0.05, 0.1]),
        rch=np.array([0.2, 0.3]),
        rsoil0=rsoil0,
    )

    assert np.allclose(rsc, rsoil0)
    assert np.allclose(gsfr, np.zeros_like(rsoil0))


def test_geocyli_full_cover_returns_crown_reflectance():
    rc = np.array([0.0253, 0.4175])
    tc = np.array([0.0360, 0.2313])
    rch = np.array([0.0275, 0.4739])
    rsoil0 = np.array([0.1320, 0.2250])

    rsc, gsfr = progeosail.geocyli(3.5, 1.0, 42.27, rc, tc, rch, rsoil0)

    assert np.allclose(rsc, rc)
    assert np.all(gsfr >= 0.0)
    assert np.all(gsfr <= 1.0)


def test_geocone_full_cover_includes_shadowed_crown_fraction():
    rc = np.array([0.0466, 0.3286])
    tc = np.array([0.0085, 0.0686])
    rch = np.array([0.0454, 0.3740])
    rsoil0 = np.array([0.0780, 0.3210])

    rsc, gsfr = progeosail.geocone(7.0, 1.0, 42.27, rc, tc, rch, rsoil0)

    assert np.all(rsc <= rc)
    assert np.all(gsfr >= 0.0)
    assert np.all(gsfr <= 1.0)


def test_run_progeosail_rejects_unknown_crown_shape():
    with pytest.raises(ValueError, match="cylinder or cone"):
        progeosail.run_progeosail(
            3.5,
            0.5,
            "sphere",
            1.5,
            40.0,
            8.0,
            0.0,
            0.01,
            0.009,
            3.0,
            -0.35,
            0.01,
            30.0,
            0.0,
            0.0,
            typelidf=1,
            lidfb=-0.15,
            rsoil=1.0,
            psoil=1.0,
        )
