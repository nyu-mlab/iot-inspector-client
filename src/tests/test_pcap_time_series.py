import pandas as pd
import numpy as np
from iot_inspector.analysis.pcap_time_series import bin_traffic


def test_single_packet_upload():
    df = pd.DataFrame({
        "rel_time": [0.02],
        "upload_bytes": [1000],
        "download_bytes": [0]
    })

    bins, up, down = bin_traffic(df, bin_size=0.05)

    assert np.sum(up) == 1000
    assert np.sum(down) == 0


def test_single_packet_download():
    df = pd.DataFrame({
        "rel_time": [0.03],
        "upload_bytes": [0],
        "download_bytes": [500]
    })

    bins, up, down = bin_traffic(df, bin_size=0.05)

    assert np.sum(up) == 0
    assert np.sum(down) == 500


def test_multiple_packets_same_bin():
    df = pd.DataFrame({
        "rel_time": [0.01, 0.02],
        "upload_bytes": [100, 200],
        "download_bytes": [0, 0]
    })

    bins, up, down = bin_traffic(df, bin_size=0.05)

    assert np.sum(up) == 300
    assert np.sum(down) == 0


def test_packets_in_different_bins():
    df = pd.DataFrame({
        "rel_time": [0.01, 0.06],
        "upload_bytes": [100, 200],
        "download_bytes": [0, 0]
    })

    bins, up, down = bin
