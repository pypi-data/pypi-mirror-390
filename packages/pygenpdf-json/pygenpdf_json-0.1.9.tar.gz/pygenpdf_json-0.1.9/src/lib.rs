use pyo3::prelude::*;
use genpdf_json;

/// A Python module implemented in Rust.
#[pymodule]
fn pygenpdf_json(m: &Bound<'_, PyModule>) -> PyResult<()> {    
    m.add_function(wrap_pyfunction!(render_json_base64, m)?)?;
    m.add_function(wrap_pyfunction!(render_json_file, m)?)?;
    m.add_function(wrap_pyfunction!(render_base64_from_sqlite, m)?)?;
    m.add_function(wrap_pyfunction!(render_file_from_sqlite, m)?)?;
    Ok(())
}

#[pyfunction]
fn render_json_base64(json_string: String) -> PyResult<String>{
    let file_pdf_base64 = genpdf_json::render_json_base64(&json_string);
    return Ok(file_pdf_base64.unwrap());    
}

#[pyfunction]
fn render_base64_from_sqlite(db_path: String) -> PyResult<String>{
    let file_pdf_base64 = genpdf_json::render_base64_from_sqlite(&db_path);
    return Ok(file_pdf_base64.unwrap());    
}

#[pyfunction]
fn render_json_file(json_path: String, output_path: String) -> PyResult<()>{
    let _ = genpdf_json::render_json_file(json_path, output_path).unwrap();
    Ok(())       
}

#[pyfunction]
fn render_file_from_sqlite(db_path: String, output_path: String) -> PyResult<()>{
    let _ = genpdf_json::render_file_from_sqlite(db_path, output_path).unwrap();
    Ok(())       
}
