from atlas_runtime import anomaly

def test_repeater():
    ad = anomaly.AnomalyDetector()
    for i in range(3):
        ad.add_entry({"outcome": "failure", "role": "atlas-dev", "error": "test"})
    res = ad.detect()
    assert any(a["type"] == "repeater" for a in res)
