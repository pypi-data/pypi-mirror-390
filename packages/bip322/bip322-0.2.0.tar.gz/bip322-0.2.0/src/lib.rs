use pyo3::prelude::*;
use pyo3::exceptions::PyException;
use ::bip322 as bip322_rs;

pyo3::create_exception!(bip322, VerificationError, PyException);

#[pyfunction(
    text_signature = "(address, message, base64_signature)",
    signature = (address, message, base64_signature)
)]
#[pyo3(name = "verify_simple_encoded")]
#[doc = "Verify a base64-encoded BIP-322 signature.\n\n\
           Args:\n  address (str): Bitcoin address\n  \
                 message (str): message text\n  \
                 base64_signature (str): base64 signature\n\n\
           Returns:\n  None if valid, else raises VerificationError"]
fn verify_simple_encoded(address: &str, message: &str, base64_signature: &str) -> PyResult<()> {
    bip322_rs::verify_simple_encoded(address, message, base64_signature)
        .map_err(|err| VerificationError::new_err(err.to_string()))
}

#[pymodule]
#[pyo3(name = "bip322")]  // Python import name: `import bip322`
fn bip322_py(_py: Python, m: &Bound<PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(verify_simple_encoded, m)?)?;
    m.add("VerificationError", m.py().get_type_bound::<VerificationError>())?;
    Ok(())
}
