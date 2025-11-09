use pyo3::{prelude::*};
use std::collections::HashMap;
use serde::{Serialize, Deserialize};

// ---------- Main Util for going from formula -> model matrix ----------
// Will take a formula struct and dictionaries from a polars df and create a model
// matrix. This returned value will be used to run models. 



// ---------- Helper functions ----------


// ---------- Structs & enums ----------

// Make the ModelMatrix class. Fields: var_names, data

// #[pyclass]
// pub struct ModelMatrix {
//     x_matrix: ,
//     y_matrix: ,
//     encoding_data: Encoder
// }


/// A struct that holds data on hhow columns are encoded during the modeling process.
/// 
/// Attributes:
/// - `column_mappings`: A mapping of column name to info on the encoding
#[derive(Clone, Serialize, Deserialize, Default)]
#[pyclass]
pub struct Encoder {
    pub column_mappings: HashMap<String, EncodedColumnInfo>
}

#[pymethods]
impl Encoder {
    #[new]
    pub fn new() -> Self {
        Self {
            column_mappings: HashMap::new(),
        }
    }

    #[getter]
    fn get_column_mappings(&self) -> HashMap<String, EncodedColumnInfo> {
        self.column_mappings.clone()
    }

    #[setter]
    fn set_column_mappings(&mut self, mappings: HashMap<String, EncodedColumnInfo>) {
        self.column_mappings = mappings;
    }

    /// Adds a single column and its encoding info to the mapping.
    ///
    /// Args:
    /// - `col_name` (String): The name of the column to add.
    /// - `col_info` (EncodedColumnInfo): The encoding information for that column.
    fn add_column_mapping(&mut self, col_name: String, col_info: EncodedColumnInfo) {
        self.column_mappings.insert(col_name, col_info);
    }

    /// Gets the encoding info for a single column.
    ///
    /// Args:
    /// - `col_name` (String): The name of the column to retrieve.
    ///
    /// Returns:
    /// - EncodedColumnInfo | None: The encoding information for the column,
    ///         or None if the column is not found in the mapping.
    fn get_column_mapping(&self, col_name: String) -> Option<EncodedColumnInfo> {
        self.column_mappings.get(&col_name).cloned()
    }
}

/// Holds information about how a column is encoded.
/// 
/// Fields:
/// - levels: The (optional) vector holding all encoded levels. 
/// - encoding_type: The type of encoding used.
/// 
/// Methods:
#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct EncodedColumnInfo {
    levels: Option<Vec<String>>,   // All levels for categorical variables. Reference level should be the first(index 0)
    encoding_type: EncodingType
}

#[pymethods]
impl EncodedColumnInfo {
    #[new]
    fn new(levels: Option<Vec<String>>, encoding_type: EncodingType) -> Self {
        Self {
            levels,
            encoding_type,
        }
    }

    #[getter]
    fn levels(&self) -> Option<Vec<String>> {
        self.levels.clone()
    }

    #[getter]
    fn encoding_type(&self) -> EncodingType {
        self.encoding_type.clone()
    }
}

/// Enum to represent the type of encoding used for variables.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[pyclass(eq)]
pub enum EncodingType {
    Dummy,    // Dummy encoding
    OneHot,   // One-hot encoding
    Bool,     // Direct cast for boolean variables
    Numeric   // Variables that don't need transformation at all
}

#[pymethods]
impl EncodingType {
    #[getter]
    fn name(&self) -> &str {
        match self {
            EncodingType::Dummy => "Dummy",
            EncodingType::OneHot => "OneHot",
            EncodingType::Bool => "Bool",
            EncodingType::Numeric => "Numeric",
        }
    }
}

// ---------- Errors ----------

use pyo3::exceptions::{PyTypeError, PyValueError};

/// Error type for matrix creation issues.
#[derive(Debug, Clone)]
pub enum ModelMatrixError {
    InvalidData(String),
    MissingColumn(String),
    InvalidType(String),
    InvalidTerm(String)
}


impl std::fmt::Display for ModelMatrixError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            ModelMatrixError::InvalidData(msg) => write!(f, "Invalid data: {}", msg),
            ModelMatrixError::MissingColumn(column) => write!(f, "{} not found in data", column),
            ModelMatrixError::InvalidType(column) => write!(f, "{} has an invalid type", column),
            ModelMatrixError::InvalidTerm(column) => write!(f, "{} should not be included in the model matrix", column)
        }
    }
}

impl std::convert::From<ModelMatrixError> for PyErr {
    fn from(err: ModelMatrixError) -> PyErr {
        match err {
            ModelMatrixError::InvalidData(msg) => PyValueError::new_err(msg),
            ModelMatrixError::MissingColumn(column) => PyValueError::new_err(column),
            ModelMatrixError::InvalidType(column) => PyTypeError::new_err(column),
            ModelMatrixError::InvalidTerm(column) => PyValueError::new_err(column)
        }
    }
}

impl std::error::Error for ModelMatrixError {}

