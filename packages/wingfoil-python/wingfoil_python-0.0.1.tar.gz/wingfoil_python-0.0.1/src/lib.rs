use pyo3::prelude::*;

/// Simple placeholder function
#[pyfunction]
fn hello() -> &'static str {
    "hello, world"
}

#[pymodule]
fn wingfoil_internal(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(hello, module)?)?;
    Ok(())
}