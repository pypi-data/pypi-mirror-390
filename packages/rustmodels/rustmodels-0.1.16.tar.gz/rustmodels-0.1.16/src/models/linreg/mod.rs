use pyo3::{prelude::*};
use std::collections::HashMap;
use numpy::{IntoPyArray, PyArray1, PyReadonlyArray1, PyReadonlyArray2};
use ndarray::{ArrayView1, ArrayView2, Array1, Array2};
use ndarray_linalg::{error::LinalgError, Inverse};
use serde::{Serialize, Deserialize};

use crate::models::utils::{formula_utils::Formula, model_matrix_utils::Encoder};
use crate::models::base::{BaseModel, Model};

// ---------- Linreg main class ----------

// REMEMBER: If possible, use GPU for speed

/// A class meant to hold the results and metadata of a linear regression.
/// 
/// Attributes:
/// - coefficients (dict[str, float]): A dictionary of coefficient names and values.
/// - _encoding_data (Encoder): Encoding metadata. Used when predicting on other datasets 
///         than the one used to fit. 
/// 
/// Methods:
/// - save_to_file(filepath: str): Saves the model to a given filepath.
/// - load_from_file(filepath: str): A method that will load a LinearRegression object from a JSON file.
/// - predict(data: polars.DataFrame): Uses the model to make predictions on a new DataFrame
/// - fit(design_matrix: ModelMatrix): Fits the regression model.
#[pyclass]
#[derive(Serialize, Deserialize)]
pub struct LinearRegressionCore {
    #[serde(flatten)]
    pub base: BaseModel
}

impl Model for LinearRegressionCore {
    fn base(&self) -> &BaseModel {
        &self.base
    }
}

#[pymethods]
impl LinearRegressionCore {
    #[new]
    fn new() -> Self {
        Self {
            base: BaseModel::new("LinearRegression".to_string())
        }
    }

    // ---------- Properties ----------

    #[getter]
    fn get_coefficients(&self) -> Option<HashMap<String, f64>> {
        self.base.coefficients.clone()
    }

    #[setter]
    fn set_coefficients(&mut self, new_coefficients: HashMap<String, f64>) {
        self.base.coefficients = Some(new_coefficients);
    }

    #[getter]
    pub fn get_encoding_data(&self) -> Encoder {
        self.base.encoding_data.clone()
    }

    #[getter]
    pub fn get_formula(&self) -> Option<Formula> {
        self.base.formula.clone()
    }

    #[setter]
    pub fn set_formula(&mut self, new_formula: Formula) {
        self.base.formula = Some(new_formula);
    }

    // ---------- Methods ----------

    /// A method to fit a linear regression using a ModelMatrix object. Internally saves 
    /// results and metadata. 
    fn fit(
        &mut self, 
        x_matrix: PyReadonlyArray2<f64>, 
        y_matrix: PyReadonlyArray1<f64>,
        x_col_names: Vec<String>, 
        encoder: &Encoder
    ) -> Result<(), LinearRegressionError> {
        let x_array_view: ArrayView2<f64> = x_matrix.as_array();
        let y_array_view: ArrayView1<f64> = y_matrix.as_array();

        let xtx: Array2<f64> = x_array_view.t().dot(&x_array_view);
        let xty: Array1<f64> = x_array_view.t().dot(&y_array_view);

        let xtxi: Result<Array2<f64>, LinalgError> = xtx.inv();
        let xtxi = match xtxi {
            Ok(inv) => inv,
            Err(_) => {
                return Err(LinearRegressionError::InversionImpossible)
            }
        };

        let results_matrix: Array1<f64> = xtxi.dot(&xty);
        let coefficients: HashMap<String, f64> = x_col_names
            .into_iter()
            .zip(results_matrix.into_iter())
            .collect();

        self.base.coefficients = Some(coefficients);
        self.base.encoding_data = encoder.clone();

        return Ok(())
    }

    fn predict(
        &self, 
        py: Python,
        x_matrix: PyReadonlyArray2<f64>, 
        x_col_names: Vec<String>
    ) -> Py<PyArray1<f64>> {

        // Get coefficients ready
        let beta: Array1<f64> = if let Some(coefficients) = &self.base.coefficients {
            x_col_names
                .iter()
                .map(|name| *coefficients.get(name).unwrap_or(&0.0))
                .collect()
        } else {
            Array1::zeros(x_col_names.len())
        };

        // Get x ready
        let x_array: ArrayView2<f64> = x_matrix.as_array();

        // Multiply
        let preds: Array1<f64> = x_array.dot(&beta);

        preds.into_pyarray(py).into()
    }

    fn save_to_file(&self, filepath: String) -> PyResult<()> {
        self.save_to_file_rust(filepath)
    }

    fn load_from_file(&mut self, filepath: String) -> PyResult<()> {
        self.load_from_file_rust(filepath)
    }
}

// ---------- Error ----------

use pyo3::exceptions::PyValueError;

/// Error type for formula parsing issues.
#[derive(Debug, Clone)]
pub enum LinearRegressionError {
    InversionImpossible
}

impl std::fmt::Display for LinearRegressionError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            LinearRegressionError::InversionImpossible => write!(f, "Formula cannot be empty")
        }
    }
}

impl std::convert::From<LinearRegressionError> for PyErr {
    fn from(err: LinearRegressionError) -> PyErr {
        // All errors map best to ValueError in python
        PyValueError::new_err(err.to_string())
    }
}

impl std::error::Error for LinearRegressionError {}

// ---------- Module ----------

// /// Internal function to create the linreg submodule. Should be run in src/lib.rs.
// pub fn create_linreg_module(py: Python<'_>) -> PyResult<Bound<'_, PyModule>> {
//     let m = PyModule::new(py, "linreg_internal")?;
//     m.add_class::<LinearRegression>()?;
//     Ok(m)
// }


