use pyo3::{prelude::*};
use std::{collections::HashMap};
use numpy::{IntoPyArray, PyArray1, PyReadonlyArray1, PyReadonlyArray2};
use ndarray::{ArrayView1, ArrayView2, Array1, Array2};
use ndarray_linalg::{error::LinalgError, Inverse};
use serde::{Serialize, Deserialize};

use crate::models::utils::{formula_utils::Formula, model_matrix_utils::Encoder};
use crate::models::base::{BaseModel, Model};

// ---------- Penalized Logreg main class ----------

/// The main penalized logistic regression class. Holds data and performs operations
#[pyclass]
#[derive(Serialize, Deserialize)]
pub struct PenalizedLogisticRegressionCore {
    #[serde(flatten)]
    pub base: BaseModel,
    pub penalties: Option<HashMap<String, PenaltySpecification>>
}

impl Model for PenalizedLogisticRegressionCore {
    fn base(&self) -> &BaseModel {
        &self.base
    }
}

#[pymethods]
impl PenalizedLogisticRegressionCore {

    // ---------- Init ----------

    #[new]
    pub fn new() -> Self {
        Self {
            base: BaseModel::new("PenalizedLogisticRegression".to_string()),
            penalties: None
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

    #[pyo3(signature = (x_matrix, y_matrix, x_col_names, encoder, penalties = None, max_iterations = 25, convergence_delta = 1e-8))]
    pub fn fit(
        &mut self, 
        x_matrix: PyReadonlyArray2<f64>, 
        y_matrix: PyReadonlyArray1<f64>,
        x_col_names: Vec<String>, 
        encoder: &Encoder,
        penalties: Option<Vec<PenaltySpecification>>,
        max_iterations: i128,
        convergence_delta: f64
    ) -> Result<(), PenalizedLogisticRegressionError> {        
        // Using IWLS as described here: https://retostauffer.github.io/Rfoehnix/articles/logisticregression.html
        // Ridge regression described here: https://www.youtube.com/watch?v=mpuKSovz9xM&t=103s
            // Go to like 12:00 to see how the ridge penalty works with matrices 
            // He explains that lambda times identity matrix where each column in the I corresponds to 
                // an x var is the added penalty.
        // Ridge logistic with Newton-Raphson here: https://www.r-bloggers.com/2018/06/classification-from-scratch-penalized-ridge-logistic-4-8/
            // Old algo: beta_new = beta_old - fancy_inverted * fancy_different = beta_old - (xt_w_x_inv) * 
            //                    = xt_w_x_inv * xt_w_z
            // So: Add ridge panelty in before inverting xt_w_x_inv but after this step: xt_w.dot(&x_array_view)
            // Penalty in the article is 2 * lambda * identity

        self.map_penalties_to_cols(&penalties, &x_col_names)?;

        let x_array_view: ArrayView2<f64> = x_matrix.as_array();
        let y_array_view: ArrayView1<f64> = y_matrix.as_array();

        // Initialize
        let n_observations: usize = y_array_view.len();
        let n_features: usize = x_array_view.ncols();

        let mut pred_probs: Array1<f64> = Array1::from_elem(n_observations, 0.5);
        let mut beta_old: Array1<f64> = Array1::from_elem(n_features, 0.0);
        let mut i: i128 = 1;
            // All predicted probabilities start at .5
            // p(1 - p) = .5 * .5 = .25
            // Weights are stored as 1d array because they are in fact a 2d array with
            // only diagonals != 0. Storing all of that is wasteful.
        let mut weights: Array1<f64> = Array1::from_elem(n_observations, 0.25);
        let mut log_likelihood_old: f64 = f64::INFINITY;
        let mut delta: f64 = f64::INFINITY;

        let penalty_matrix: Array2<f64> = self.get_penalty_matrix(&x_col_names);
        let lambdas: Array1<f64> = self.get_lambdas_vector(&x_col_names);
        let target_vector: Array1<f64> = self.get_targets_vector(&x_col_names);

        // Do IWLS algo
        while i <= max_iterations && delta > convergence_delta {

            // Calculate new coefficients

            let x_t: ArrayView2<f64> = x_array_view.t();
                // The division by &weights corresponds to the multiplication by W^(-1). Since W is 
                // a diagonal matrix represented by the weights array, multiplying by its inverse is 
                // the same as an element-wise division by the weights themselves.
                // Shape of z is (num_observations, 1)
            let z: Array1<f64> = x_array_view.dot(&beta_old) + (&y_array_view - &pred_probs) / &weights;

            let xt_w: Array2<f64> = &x_t * &weights;
            let xt_w_x_inv: Array2<f64> = (xt_w.dot(&x_array_view) + &penalty_matrix).inv()?;
            let xt_w_z: Array1<f64> = xt_w.dot(&z);
            let xt_w_z_penalty: Array1<f64> = xt_w_z + penalty_matrix.dot(&target_vector);
            let beta_new: Array1<f64> = xt_w_x_inv.dot(&xt_w_z_penalty);

            // Calculate log-likelihood

            pred_probs = x_array_view.dot(&beta_new)
                .mapv(|eta| 1.0 / (1.0 + (-eta).exp()));

            let unpenalized_log_likelihood_sum: f64 = ndarray::Zip::from(&y_array_view)
                .and(&pred_probs)
                .map_collect(|&y, &p| {
                    const EPSILON: f64 = 1e-9;
                    let p_clipped: f64 = p.max(EPSILON).min(1.0 - EPSILON);
                    y * p_clipped.ln() + (1.0 - y) * (1.0 - p_clipped).ln()
                })
                .sum();

            let penalty_term: f64 = ndarray::Zip::from(&lambdas)
                .and(&beta_new)
                .and(&target_vector)
                .map_collect(|&lambda, &beta, &target| {
                    lambda * (beta - target).powi(2)
                })
                .sum();

            let log_likelihood_new: f64 = unpenalized_log_likelihood_sum - penalty_term;
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
            return Err(PenalizedLogisticRegressionError::ConvergenceFail)
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

impl PenalizedLogisticRegressionCore { // Non-python methods
    fn map_penalties_to_cols(
        &mut self,
        py_penalties: &Option<Vec<PenaltySpecification>>,
        x_col_names: &Vec<String>
    ) -> Result<(), PenalizedLogisticRegressionError> {
        let mut mapped_penalties: HashMap<String, PenaltySpecification> = HashMap::new();

        if let Some(penalty_specs) = py_penalties {
            for col_name in x_col_names.iter() {
                let mut applicable_specs: Vec<&PenaltySpecification> = Vec::new();
                for spec in penalty_specs {
                    if let Some(level) = &spec.categorical_level {
                        if col_name == &format!("{}_{}", spec.variable_name, level) {
                            applicable_specs.push(spec);
                        }
                    } else {
                        if col_name == &spec.variable_name {
                            applicable_specs.push(spec);
                        }
                    }
                }

                if applicable_specs.is_empty() {
                    continue;
                }

                let specs_with_level: Vec<&&PenaltySpecification> = applicable_specs.iter()
                    .filter(|spec| spec.categorical_level.is_some())
                    .collect();

                let best_spec: &PenaltySpecification;

                if specs_with_level.len() == 1 {
                    best_spec = specs_with_level[0];
                } else if specs_with_level.len() > 1 {
                    return Err(PenalizedLogisticRegressionError::MultiplePenalties(col_name.clone()));
                } else { // No specs with categorical_level
                    let specs_without_level: Vec<&&PenaltySpecification> = applicable_specs.iter()
                        .filter(|spec| spec.categorical_level.is_none())
                        .collect();
                    
                    if specs_without_level.len() == 1 {
                        best_spec = specs_without_level[0];
                    } else if specs_without_level.len() > 1 {
                        return Err(PenalizedLogisticRegressionError::MultiplePenalties(col_name.clone()));
                    } else {
                        // This case should ideally not be reached if applicable_specs is not empty
                        // and all specs have been filtered. Let's throwx an error if we reach here.
                        return Err(PenalizedLogisticRegressionError::MultiplePenalties(format!("Internal error: No best spec found for {}", col_name)));
                    }
                }
                
                mapped_penalties.insert(col_name.clone(), best_spec.clone());
            }
        }

        self.penalties = Some(mapped_penalties);
        Ok(())
    }

    fn get_lambdas_vector(&self, x_col_names: &Vec<String>) -> Array1<f64> {
        let n_features = x_col_names.len();
        let mut lambdas = Array1::zeros(n_features);
        if let Some(penalty_map) = &self.penalties {
            for (i, col_name) in x_col_names.iter().enumerate() {
                if let Some(spec) = penalty_map.get(col_name) {
                    lambdas[i] = spec.lambda_param;
                }
            }
        }
        lambdas
    }

    fn get_targets_vector(&self, x_col_names: &Vec<String>) -> Array1<f64> {
        let n_features = x_col_names.len();
        let mut targets = Array1::zeros(n_features);
        if let Some(penalty_map) = &self.penalties {
            for (i, col_name) in x_col_names.iter().enumerate() {
                if let Some(spec) = penalty_map.get(col_name) {
                    targets[i] = spec.target;
                }
            }
        }
        targets
    }

    fn get_penalty_matrix(&self, x_col_names: &Vec<String>) -> Array2<f64> {
        let lambdas = self.get_lambdas_vector(x_col_names);
        return 2.0 * Array2::from_diag(&lambdas)
    }
}

// ---------- Penalties ----------

#[pyclass]
#[derive(Serialize, Deserialize, Clone)]
pub struct PenaltySpecification {
    pub variable_name: String,
    pub categorical_level: Option<String>,
    pub lambda_param: f64,
    pub target: f64
}

#[pymethods]
impl PenaltySpecification {

    // ---------- Init ----------

    #[new]
    #[pyo3(signature = (variable_name, categorical_level, lambda_param, target = 0.0))]
    pub fn new(variable_name: String, categorical_level: Option<String>, lambda_param: f64, target: f64) -> PyResult<Self> {
        if lambda_param < 0.0 {
            return Err(PenalizedLogisticRegressionError::InvalidLambda.into());
        }
        
        Ok(Self {
            variable_name: variable_name,
            categorical_level: categorical_level,
            lambda_param: lambda_param, 
            target: target
        })
    }
}

// ---------- Error ----------

use pyo3::exceptions::PyValueError;

/// Error type for formula parsing issues.
#[derive(Debug, Clone)]
pub enum PenalizedLogisticRegressionError {
    InversionImpossible,
    ConvergenceFail,
    MultiplePenalties(String),
    InvalidLambda
}

impl std::fmt::Display for PenalizedLogisticRegressionError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            PenalizedLogisticRegressionError::InversionImpossible => write!(f, "Matrix inversion failed. The matrix may be singular."),
            PenalizedLogisticRegressionError::ConvergenceFail => write!(f, "Algorithm failed to converge"),
            PenalizedLogisticRegressionError::MultiplePenalties(var) => write!(f, "Multiple penalties specified for variable: {}", var),
            PenalizedLogisticRegressionError::InvalidLambda => write!(f, "Lambda parameter must be greater than or equal to 0."),
        }
    }
}

impl std::convert::From<PenalizedLogisticRegressionError> for PyErr {
    fn from(err: PenalizedLogisticRegressionError) -> PyErr {
        // All errors map best to ValueError in python
        PyValueError::new_err(err.to_string())
    }
}

impl std::error::Error for PenalizedLogisticRegressionError {}

impl From<LinalgError> for PenalizedLogisticRegressionError {
    fn from(_: LinalgError) -> Self {
        PenalizedLogisticRegressionError::InversionImpossible
    }
}
