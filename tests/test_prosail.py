import numpy as np
import os
import progeosail
from pytest import fixture


@fixture
def datadir(request):
    filename = request.module.__file__
    test_dir = os.path.dirname(filename)
    data_dir = os.path.join(test_dir, "data")

    def getter(filename):
        return os.path.join(data_dir, filename)

    return getter


def test_rsot_prosail5(datadir):
    fname = datadir("REFL_CAN.txt")
    w, resv, rdot, rsot, rddt, rsdt = np.loadtxt(fname, unpack=True)
    rr = progeosail.run_prosail(
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
        10.0,
        0.0,
        typelidf=1,
        lidfb=-0.15,
        rsoil=1.0,
        psoil=1.0,
        factor="SDR",
    )
    assert np.allclose(rsot, rr, atol=0.01)


def test_rdot_prosail5(datadir):
    fname = datadir("REFL_CAN.txt")
    w, resv, rdot, rsot, rddt, rsdt = np.loadtxt(fname, unpack=True)
    rr = progeosail.run_prosail(
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
        10.0,
        0.0,
        typelidf=1,
        lidfb=-0.15,
        rsoil=1.0,
        psoil=1.0,
        factor="HDR",
    )
    assert np.allclose(rdot, rr, atol=0.01)


def test_rddt_prosail5(datadir):
    fname = datadir("REFL_CAN.txt")
    w, resv, rdot, rsot, rddt, rsdt = np.loadtxt(fname, unpack=True)
    rr = progeosail.run_prosail(
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
        10.0,
        0.0,
        typelidf=1,
        lidfb=-0.15,
        rsoil=1.0,
        psoil=1.0,
        factor="BHR",
    )
    assert np.allclose(rddt, rr, atol=0.01)


def test_rsdt_prosail5(datadir):
    fname = datadir("REFL_CAN.txt")
    w, resv, rdot, rsot, rddt, rsdt = np.loadtxt(fname, unpack=True)
    rr = progeosail.run_prosail(
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
        10.0,
        0.0,
        typelidf=1,
        lidfb=-0.15,
        rsoil=1.0,
        psoil=1.0,
        factor="DHR",
    )
    assert np.allclose(rsdt, rr, atol=0.01)
