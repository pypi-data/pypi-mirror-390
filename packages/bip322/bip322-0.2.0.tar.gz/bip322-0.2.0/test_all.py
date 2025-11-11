import pytest
import bip322

# Known-good sample
ADDRESS_OK = "bc1p6rfm6ncxysjtlkmxt64v2v7zwkn50k4r5d87njv399m88d3n9s6qr82egk"
MESSAGE_OK = (
    "I certify that the blockchain address "
    "bc1p6rfm6ncxysjtlkmxt64v2v7zwkn50k4r5d87njv399m88d3n9s6qr82egk "
    "belongs to did:pkh:bip122:000000000019d6689c085ae165831e93:"
    "bc1p6rfm6ncxysjtlkmxt64v2v7zwkn50k4r5d87njv399m88d3n9s6qr82egk "
    "on Tue, 04 Nov 2025 09:47:29 GMT"
)
SIG_OK = (
    "AUG3Km/EO+ukRNIzGP7YzAS2RfzrIfK7eIEfVrxi/ddEhOGsPiB3jpirvL4bmd/"
    "T0/LTz5cavqu89BaJhP1YTBAzAQ=="
)

ADDRESS_BAD = "invalid_address"
# Tampered signature (first char A→B; still valid base64 but should fail verification)
SIG_BAD = (
    "BUG3Km/EO+ukRNIzGP7YzAS2RfzrIfK7eIEfVrxi/ddEhOGsPiB3jpirvL4bmd/"
    "T0/LTz5cavqu89BaJhP1YTBAzAQ=="
)

# Tampered message (another address → should fail)
MESSAGE_BAD = (
    "I certify that the blockchain address "
    "bc1pn0r0kt6smktxnntdfqj8grczwzv9r5vfqg29seay05xzdmpl7x9q4cdyv3 "
    "belongs to did:pkh:bip122:000000000019d6689c085ae165831e93:"
    "bc1pn0r0kt6smktxnntdfqj8grczwzv9r5vfqg29seay05xzdmpl7x9q4cdyv3 "
    "on Tue, 04 Nov 2025 09:47:29 GMT"
)

@pytest.mark.parametrize(
    "address,message,signature,expected_validation_success",
    [
        pytest.param(ADDRESS_OK, MESSAGE_OK, SIG_OK, True, id="valid"),
        pytest.param(ADDRESS_BAD, MESSAGE_OK, SIG_OK, False, id="invalid address"),
        pytest.param(ADDRESS_OK, MESSAGE_OK, SIG_BAD, False, id="invalid signature"),
        pytest.param(ADDRESS_OK, MESSAGE_BAD, SIG_OK, False, id="invalid message"),
    ],
)
def test_all(address: str, message: str, signature: str, expected_validation_success: bool) -> None:
    if expected_validation_success:
        assert bip322.verify_simple_encoded(address, message, signature) is None
    else:
        with pytest.raises(bip322.VerificationError):
            bip322.verify_simple_encoded(address, message, signature)


def test_kwargs_ok():
    import bip322
    assert bip322.verify_simple_encoded(
        address=ADDRESS_OK,
        message=MESSAGE_OK,
        base64_signature=SIG_OK,
    ) is None
