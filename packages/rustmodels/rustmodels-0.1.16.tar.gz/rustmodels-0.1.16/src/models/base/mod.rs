use pyo3::{prelude::*};
use serde::{Serialize, Deserialize};
use serde::de::DeserializeOwned;
use std::collections::HashMap;

use crate::models::utils::{formula_utils::Formula, model_matrix_utils::Encoder};

// ---------- Base Model data type ----------

#[derive(Serialize, Deserialize, Clone, Default)]
pub struct BaseModel {
    pub coefficients: Option<HashMap<String, f64>>,
    pub encoding_data: Encoder,
    pub formula: Option<Formula>,
    pub model_type: String
}

impl BaseModel {
    pub fn new(model_type: String) -> Self {
        Self {
            model_type,
            ..Self::default()
        }
    }
}

// ---------- Base Model trait ----------

/// A single trait that shares functionalioty and demands some standards of 
/// all model types.
pub trait Model: Serialize + DeserializeOwned {

    // ---------- Specifically for the trait ----------

    /// Exists so that the `save_to_file_rust` method works in this trait.
    fn base(&self) -> &BaseModel;

    // ---------- Same across the board ----------

    // --- Save & load ---

    /// A rust implementation for all models. Will save the data if the model 
    /// has already been fit. 
    fn save_to_file_rust(&self, filepath: String) -> PyResult<()> {
        // Make sure the model is fitted before saving.
        if self.base().coefficients.is_none() {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Model has not been fitted yet. Cannot save an empty model."
            ));
        }

        // Create an instance of our serializable "view" of the model.
        let json_string = serde_json::to_string_pretty(self)
            .map_err(|e| {
                pyo3::exceptions::PyIOError::new_err(format!("Failed to serialize model: {}", e))
            })?;

        // Write the string to a file
        std::fs::write(&filepath, json_string).map_err(|e| {
            pyo3::exceptions::PyIOError::new_err(format!("Failed to write to file '{}': {}", filepath, e))
        })?;

        Ok(())
    }

    /// Loads a model from a json file.
    fn load_from_file_rust(&mut self, filepath: String) -> PyResult<()> {
        // Read the file into a string
        let json_string = std::fs::read_to_string(&filepath).map_err(|e| {
            pyo3::exceptions::PyIOError::new_err(format!("Failed to read file '{}': {}", filepath, e))
        })?;

        // Deserialize the string directly - becomes a model now
        let loaded_model: Self = serde_json::from_str(&json_string).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("Failed to deserialize model from JSON: {}", e))
        })?;

        // If loaded model type doesn't match the struct type, throw an error
        if self.base().model_type != loaded_model.base().model_type {
            return Err(pyo3::exceptions::PyValueError::new_err(format!(
                "Model type mismatch: Cannot load a '{}' model into a '{}' object.",
                loaded_model.base().model_type,
                self.base().model_type
            )));
        }

        *self = loaded_model;

        Ok(())
    }
}

