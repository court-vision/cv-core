"""
The crypto layer alone. The credential-service tests (dual-read, backfill,
plaintext fallback) stay in the consuming repos — they import models this
package deliberately does not have.
"""

import pytest
from cryptography.fernet import Fernet

from cv_core import crypto
from cv_core.crypto import CredentialDecryptionError


@pytest.fixture
def keys(monkeypatch):
    """Install a two-version keyring and clear the lru cache around each test."""
    k1, k2 = Fernet.generate_key().decode(), Fernet.generate_key().decode()
    monkeypatch.setenv("CREDENTIAL_KEYS", f"1:{k1},2:{k2}")
    crypto.reset_cache()
    yield (k1, k2)
    crypto.reset_cache()


@pytest.mark.unit
class TestDisabled:
    def test_unset_means_disabled_not_broken(self, monkeypatch):
        monkeypatch.delenv("CREDENTIAL_KEYS", raising=False)
        crypto.reset_cache()
        assert crypto.is_enabled() is False
        assert crypto.current_version() is None
        crypto.reset_cache()


@pytest.mark.unit
class TestRoundtrip:
    def test_encrypts_with_the_newest_version(self, keys):
        ciphertext, version = crypto.encrypt('{"espn_s2": "secret"}')
        assert version == 2
        assert "secret" not in ciphertext

    def test_decrypt_roundtrips(self, keys):
        ciphertext, version = crypto.encrypt("token-material")
        assert crypto.decrypt(ciphertext, version) == "token-material"

    def test_old_versions_still_decrypt_after_rotation(self, keys, monkeypatch):
        ciphertext, version = crypto.encrypt("pre-rotation")
        assert version == 2
        k3 = Fernet.generate_key().decode()
        monkeypatch.setenv(
            "CREDENTIAL_KEYS",
            f"1:{keys[0]},2:{keys[1]},3:{k3}",
        )
        crypto.reset_cache()
        assert crypto.current_version() == 3
        # Rows written under version 2 must stay readable until re-encrypted.
        assert crypto.decrypt(ciphertext, 2) == "pre-rotation"


@pytest.mark.unit
class TestFailuresAreLoud:
    """A dropped or wrong key must raise, never return an empty credential."""

    def test_missing_version_raises(self, keys):
        ciphertext, _ = crypto.encrypt("x")
        with pytest.raises(CredentialDecryptionError):
            crypto.decrypt(ciphertext, 9)

    def test_wrong_key_for_version_raises(self, keys, monkeypatch):
        ciphertext, version = crypto.encrypt("x")
        rogue = Fernet.generate_key().decode()
        monkeypatch.setenv("CREDENTIAL_KEYS", f"1:{keys[0]},2:{rogue}")
        crypto.reset_cache()
        with pytest.raises(CredentialDecryptionError):
            crypto.decrypt(ciphertext, version)
