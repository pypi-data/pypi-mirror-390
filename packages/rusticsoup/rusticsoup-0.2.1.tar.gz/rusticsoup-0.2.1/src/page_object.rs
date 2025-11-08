use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyType};
use crate::webpage::WebPage;

/// Field descriptor for PageObject fields
/// Similar to web-poet's field() function
#[pyclass]
#[derive(Clone)]
pub struct Field {
    css: Option<String>,
    xpath: Option<String>,
    attr: Option<String>,
    get_all: bool,
    default: Option<String>,
    required: bool,
}

#[pymethods]
impl Field {
    #[new]
    #[pyo3(signature = (css=None, xpath=None, attr=None, get_all=false, default=None, required=true))]
    pub fn new(
        css: Option<String>,
        xpath: Option<String>,
        attr: Option<String>,
        get_all: bool,
        default: Option<String>,
        required: bool,
    ) -> Self {
        Self {
            css,
            xpath,
            attr,
            get_all,
            default,
            required,
        }
    }

    /// Extract value from WebPage based on field configuration
    pub fn extract(&self, py: Python, page: &WebPage) -> PyResult<PyObject> {
        if let Some(css) = &self.css {
            let spec = self.build_spec(css);
            self.extract_with_spec(py, page, &spec)
        } else if let Some(_xpath) = &self.xpath {
            // XPath support would go here
            Err(PyErr::new::<pyo3::exceptions::PyNotImplementedError, _>(
                "XPath support not yet implemented"
            ))
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Field must have either css or xpath selector"
            ))
        }
    }

    fn __repr__(&self) -> String {
        format!(
            "Field(css={:?}, attr={:?}, get_all={})",
            self.css, self.attr, self.get_all
        )
    }
}

impl Field {

    fn build_spec(&self, selector: &str) -> String {
        let mut spec = selector.to_string();

        if let Some(attr) = &self.attr {
            spec.push('@');
            spec.push_str(attr);
        }

        if self.get_all {
            spec.push_str("@get_all");
        }

        spec
    }

    fn extract_with_spec(&self, py: Python, page: &WebPage, spec: &str) -> PyResult<PyObject> {
        // Parse the spec and extract accordingly
        let parts: Vec<&str> = spec.split('@').collect();

        match parts.len() {
            1 => {
                // Just text
                if self.get_all {
                    page.text_all(py, parts[0])
                } else {
                    Ok(page.text(parts[0])?.into_py(py))
                }
            }
            2 => {
                if parts[1] == "get_all" {
                    page.text_all(py, parts[0])
                } else {
                    // Attribute extraction
                    if self.get_all {
                        page.attr_all(py, parts[0], parts[1])
                    } else {
                        Ok(page.attr(parts[0], parts[1])?.into_py(py))
                    }
                }
            }
            3 => {
                // selector@attr@get_all
                if parts[2] == "get_all" {
                    page.attr_all(py, parts[0], parts[1])
                } else {
                    Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        format!("Invalid field spec: {}", spec)
                    ))
                }
            }
            _ => {
                Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    format!("Invalid field spec: {}", spec)
                ))
            }
        }
    }
}

/// Base class for PageObjects
/// Similar to web-poet's ItemPage
#[pyclass(subclass)]
pub struct PageObject {
    #[pyo3(get)]
    page: Py<WebPage>,
}

#[pymethods]
impl PageObject {
    #[new]
    pub fn new(page: Py<WebPage>) -> Self {
        Self { page }
    }

    /// Extract all fields from the page based on Field descriptors
    #[classmethod]
    pub fn from_page(_cls: &Bound<'_, PyType>, py: Python, page: &WebPage) -> PyResult<PyObject> {
        // This will be called from Python to extract all fields
        // The actual field extraction happens in Python using descriptors
        Ok(page.clone().into_py(py))
    }

    /// Convert PageObject to dict
    pub fn to_dict<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
        let dict = PyDict::new_bound(py);

        // Return the page as a dict representation
        // The actual field extraction will be done in Python
        dict.set_item("_page_url", self.page.bind(py).borrow().url())?;

        Ok(dict)
    }

    fn __repr__(&self) -> String {
        "PageObject()".to_string()
    }
}

/// Processor function decorator
/// Allows defining extraction logic as functions
#[pyclass]
pub struct Processor {
    func: PyObject,
    input_type: Option<String>,
}

#[pymethods]
impl Processor {
    #[new]
    #[pyo3(signature = (func, input_type=None))]
    pub fn new(func: PyObject, input_type: Option<String>) -> Self {
        Self { func, input_type }
    }

    /// Call the processor function
    pub fn __call__(&self, py: Python, page: Py<WebPage>) -> PyResult<PyObject> {
        self.func.call1(py, (page,))
    }

    fn __repr__(&self) -> String {
        format!("Processor(input_type={:?})", self.input_type)
    }
}

/// Helper to create a processor decorator
#[pyfunction]
#[pyo3(signature = (input_type=None))]
pub fn processor(input_type: Option<String>) -> PyResult<ProcessorDecorator> {
    Ok(ProcessorDecorator { input_type })
}

#[pyclass]
pub struct ProcessorDecorator {
    input_type: Option<String>,
}

#[pymethods]
impl ProcessorDecorator {
    fn __call__(&self, _py: Python, func: PyObject) -> PyResult<Processor> {
        Ok(Processor::new(func, self.input_type.clone()))
    }
}

/// Helper function to extract PageObject from WebPage
#[pyfunction]
pub fn extract_page_object<'py>(
    py: Python<'py>,
    page: &WebPage,
    page_object_class: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyDict>> {
    // Get class fields
    let class_dict = page_object_class.getattr("__dict__")?;
    let dict_bound = class_dict.downcast::<PyDict>()?;

    let result = PyDict::new_bound(py);

    // Extract each field
    for (key, value) in dict_bound.iter() {
        if let Ok(key_str) = key.extract::<String>() {
            if !key_str.starts_with('_') {
                // Check if it's a Field descriptor
                if let Ok(field) = value.extract::<Field>() {
                    let extracted_value = field.extract(py, page)?;
                    result.set_item(key_str, extracted_value)?;
                }
            }
        }
    }

    Ok(result)
}
