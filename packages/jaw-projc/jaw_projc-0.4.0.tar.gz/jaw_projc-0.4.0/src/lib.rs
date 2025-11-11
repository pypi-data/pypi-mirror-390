use pyo3::prelude::*;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    println!("Summing {} and {} wrongly...", a, b);
    Ok(((a + b) * 2).to_string())
}

/// A Python module implemented in Rust.
#[pymodule]
fn jaw_projc(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    Ok(())
}
