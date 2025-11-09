use pyo3::{prelude::*};
use std::{collections::HashMap};
use numpy::{IntoPyArray, PyArray1, PyReadonlyArray1, PyReadonlyArray2};
use ndarray::{ArrayView1, ArrayView2, Array1, Array2};
use ndarray_linalg::{error::LinalgError, Inverse};
use serde::{Serialize, Deserialize};

use crate::models::utils::{formula_utils::Formula, model_matrix_utils::Encoder};
use crate::models::base::{BaseModel, Model};

// ---------- Logreg main class ----------

/// The main logistic regression class. Holds data and performs operations
#[pyclass]
#[derive(Serialize, Deserialize)]
pub struct LogisticRegressionCore {
    #[serde(flatten)]
    pub base: BaseModel
}

impl Model for LogisticRegressionCore {
    fn base(&self) -> &BaseModel {
        &self.base
    }
}

#[pymethods]
impl LogisticRegressionCore {

    // ---------- Init ----------

    #[new]
    pub fn new() -> Self {
        Self {
            base: BaseModel::new("LogisticRegression".to_string())
        }
    }

    // ---------- Properties ----------

    #[getter]
    pub fn get_coefficients(&self) -> Option<HashMap<String, f64>> {
        self.base.coefficients.clone()
    }

    #[setter]
    pub fn set_coefficients(&mut self, new_coefficients: HashMap<String, f64>) {
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

    #[pyo3(signature = (x_matrix, y_matrix, x_col_names, encoder, max_iterations = 25, convergence_delta = 1e-8))]
    pub fn fit(
        &mut self, 
        x_matrix: PyReadonlyArray2<f64>, 
        y_matrix: PyReadonlyArray1<f64>,
        x_col_names: Vec<String>, 
        encoder: &Encoder,
        max_iterations: i128,
        convergence_delta: f64
    ) -> Result<(), LogisticRegressionError> {
        // Using IWLS as described here: https://retostauffer.github.io/Rfoehnix/articles/logisticregression.html

        let x_array_view: ArrayView2<f64> = x_matrix.as_array();
        let y_array_view: ArrayView1<f64> = y_matrix.as_array();

        // Initialize
        let n_observations: usize = y_array_view.len();
        let n_features: usize = x_array_view.ncols();

        let mut pred_probs: Array1<f64> = Array1::from_elem(n_observations, 0.5);
        let mut beta_old: Array1<f64> = Array1::from_elem(n_features, 0.0);
        let mut i: i128 = 1;
            // p(1 - p) = .5 * .5 = .25
            // Weights are stored as 1d array because they are in fact a 2d array with
            // only diagonals != 0. Storing all of that is wasteful.
        let mut weights: Array1<f64> = Array1::from_elem(n_observations, 0.25);
        let mut log_likelihood_old: f64 = f64::INFINITY;
        let mut delta: f64 = f64::INFINITY;

        // Do IWLS algo
        while i <= max_iterations && delta > convergence_delta {

            // Calculate new coefficients

            let x_t: ArrayView2<f64> = x_array_view.t();
                // The division by &weights corresponds to the multiplication by W^(-1). Since W is 
                // a diagonal matrix represented by the weights array, multiplying by its inverse is 
                // the same as an element-wise division by the weights themselves.
                // Shape is (num_observations, 1)
            let z: Array1<f64> = x_array_view.dot(&beta_old) + (&y_array_view - &pred_probs) / &weights;

            let xt_w: Array2<f64> = &x_t * &weights;
            let xt_w_x_inv: Array2<f64> = xt_w.dot(&x_array_view).inv()?;
            let xt_w_z: Array1<f64> = xt_w.dot(&z);
            let beta_new: Array1<f64> = xt_w_x_inv.dot(&xt_w_z);

            // Calculate log-likelihood

            pred_probs = x_array_view.dot(&beta_new)
                .mapv(|eta| 1.0 / (1.0 + (-eta).exp()));
            let log_likelihood_new: f64 = ndarray::Zip::from(&y_array_view)
                .and(&pred_probs)
                .map_collect(|&y, &p| {
                    const EPSILON: f64 = 1e-9;
                    let p_clipped = p.max(EPSILON).min(1.0 - EPSILON);
                    y * p_clipped.ln() + (1.0 - y) * (1.0 - p_clipped).ln()
                })
                .sum();
            delta = (log_likelihood_new - log_likelihood_old).abs();

            // Reassign for next iteration
            log_likelihood_old = log_likelihood_new;
            beta_old = beta_new;
            weights = pred_probs.map(
                |p: &f64| p * (1.0 - p)
            );

            i += 1
        }

        if delta > convergence_delta {
            return Err(LogisticRegressionError::ConvergenceFail)
        }

        // Save results

        let coefficients: HashMap<String, f64> = x_col_names
            .into_iter()
            .zip(beta_old.into_iter())
            .collect();

        self.base.coefficients = Some(coefficients);
        self.base.encoding_data = encoder.clone();

        return Ok(());
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

        // Multiply and convert to probabilities
        let logits: Array1<f64> = x_array.dot(&beta);
        let probs: Array1<f64> = logits.mapv(|logit: f64| 1.0 / (1.0 + (-logit).exp()));

        probs.into_pyarray(py).into()
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
pub enum LogisticRegressionError {
    InversionImpossible,
    ConvergenceFail
}

impl std::fmt::Display for LogisticRegressionError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            LogisticRegressionError::InversionImpossible => write!(f, "Formula cannot be empty"),
            LogisticRegressionError::ConvergenceFail => write!(f, "Algorithm failed to converge")
        }
    }
}

impl std::convert::From<LogisticRegressionError> for PyErr {
    fn from(err: LogisticRegressionError) -> PyErr {
        // All errors map best to ValueError in python
        PyValueError::new_err(err.to_string())
    }
}

impl std::error::Error for LogisticRegressionError {}

impl From<LinalgError> for LogisticRegressionError {
    fn from(_: LinalgError) -> Self {
        LogisticRegressionError::InversionImpossible
    }
}
