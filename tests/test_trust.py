from atlas_runtime import trust
import tempfile

def test_trust_update():
    with tempfile.TemporaryDirectory() as tmp:
        tp = trust.TrustProfiles(data_dir=tmp)
        prof = tp.update("atlas-dev", 0.9)
        assert prof["trustScore"] > 0.8
