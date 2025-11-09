from enum import Enum

########## Formula Utils ##########

class FormulaTerm:
    """
    A class representing a single term in a formula.

    Used in a Formula object. 

    Attributes:
        name (str): The name of the term as it appears in the formula (e.g., "x1", "x2", "x1:x2").
        subtracted (bool): True if the term is being removed from the formula (i.e., "- x2").
        intercept (bool): True if the term is an intercept term (i.e., "1" in the formula).
        interaction (bool): True if this is an interaction term (e.g., "x1:x2").
    """
    @property
    def name(self) -> str:
        """The name of the term as it appears in the formula (e.g., "x1", "x2", "x1:x2")."""
    @property
    def subtracted(self) -> bool:
        """True if the term is being removed from the formula (i.e., "- x2")."""
    @property
    def intercept(self) -> bool: 
        """True if the term is an intercept term (i.e., "1" in the formula)."""
    @property
    def interaction(self) -> bool: 
        """True if this is an interaction term (e.g., "x1:x2")."""
    
    def get_columns_from_term(self) -> list[str]:
        """A method to find all columns used to create this term."""

class Formula:
    """
    An object used to represent a model formula.

    Attributes:
        original (str): The original formula string as provided by the user.
        dependent (FormulaTerm): The dependent variable term.
        independent (List[FormulaTerm]): A list of independent variable terms.
    """
    @property
    def original(self) -> str:
        """The original formula string as provided by the user."""
    @property
    def dependent(self) -> FormulaTerm:
        """The dependent variable term."""
    @property
    def independent(self) -> list[FormulaTerm]:
        """A list of independent variable terms."""

    def get_column_names(self, with_dependent: bool = True) -> list[str]:
        """
        Finds the name of every column in a formula.

        Args:
            with_dependent (bool): A boolean that if true indicates we would like for 
                the dependent variable column name to be added in to the returned list.
        """

def _parse_formula(formula: str) -> Formula:
    """
    An internal function to take in a user-defined string and return a Formula object.

    Args:
        formula (str): A string representing the formula, using R-style syntax (e.g., "y ~ x1 + x2 - x3").

    Returns:
        Formula: A Formula object representing the parsed formula.
    """

def _is_numeric(s: str) -> bool: ...

########## Model Matrix Utils ##########

class EncodingType(Enum):
    """
    An enum representing the type of encoding used for variables.

    Attributes:
        Dummy: Dummy encoding
        OneHot: One-hot encoding
        Bool: Direct cast for boolean variables
        Numeric: Variables that don't need transformation at all
    """
    Dummy: ...
    OneHot: ...
    Bool: ...
    Numeric: ...

    @property
    def name(self) -> str:
        """The name of the enum variant."""

class EncodedColumnInfo:
    """
    A class representing information about how a column is encoded.

    Attributes:
        levels (List[str] | None): All levels for categorical variables. Reference level should be the first (index 0).
        encoding_type (EncodingType): The type of encoding used for the variable.
    """
    def __init__(self, levels: list[str] | None, encoding_type: EncodingType) -> None: ...

    @property
    def levels(self) -> list[str] | None:
        """All levels for categorical variables. Reference level should be the first (index 0)."""
    @property
    def encoding_type(self) -> EncodingType:
        """The type of encoding used for the variable."""

class Encoder:
    """
    A class to handle encoding of variables in a model matrix.

    Attributes:
        column_mappings (Dict[str, EncodedColumnInfo]): A mapping of column name to info on the encoding.
    """
    def __init__(self) -> None: ...    

    @property
    def column_mappings(self) -> dict[str, EncodedColumnInfo]:
        """A mapping of column name to info on the encoding."""
    
    @column_mappings.setter
    def column_mappings(self, value: dict[str, EncodedColumnInfo]) -> None: ...

    def add_column_mapping(self, col_name: str, col_info: EncodedColumnInfo) -> None:
        """
        Adds a single column and its encoding info to the mapping.
        """

    def get_column_mapping(self, col_name: str) -> EncodedColumnInfo | None:
        """
        Gets the encoding info for a single column.

        Args:
            col_name (String): The name of the column to retrieve.

        Returns:
            EncodedColumnInfo | None: The encoding information for the column,
                or None if the column is not found in the mapping.
        """

########## LinReg ##########

import numpy as np

class LinearRegressionCore:
    """
    A rust-built class meant to hold the results and metadata of a linear regression. This
    class is the internal representation of a linear regression model, and does the 
    behind-the-scenes work for the user-facing LinearRegression class.

    Attributes:
        coefficients (dict[str, float]): A dictionary of coefficient names and values.
        encoding_data (Encoder): Encoding metadata. Used when predicting on other datasets 
            than the one used to fit. 
        formula (Formula): A Formula object containing the formula used to fit the linear 
            regression.

    Methods:
        fit(design_matrix: ModelMatrix): Fits the regression model.
        predict(data: polars.DataFrame): Uses the model to make predictions on a new DataFrame.
        save_to_file(filepath: str): Saves the model to a given filepath.
        load_from_file(filepath: str): A method that will load a LinearRegressionCore object from 
            a JSON file.
    """

    def __init__(self):
        pass

    ########## Attributes ##########

    @property
    def coefficients(self) -> dict[str, float] | None:
        """All levels for categorical variables. Reference level should be the first (index 0)."""

    @property
    def encoding_data(self) -> Encoder:
        """
        An Encoder object carrying encoding metadata. Used when predicting on other datasets 
        than the one used to fit.
        """

    @property
    def formula(self) -> Formula | None:
        """
        A Formula object containing the formula used in the linear regression. 
        """
    @formula.setter
    def formula(self, value: Formula)-> None: ...

    ########## Public Methods ##########

    def fit(
            self, 
            x_matrix: np.ndarray, 
            y_matrix: np.ndarray,
            x_col_names: list[str], 
            encoder: Encoder
        ) -> None:
        """
        A method to fit a linear regression using the contents of a ModelMatrix object. Internally 
        saves results and metadata. 
        """

    def predict(self, x_matrix: np.ndarray, x_col_names: list[str]):
        """
        A method that takes a polars DataFrame and uses it to generate predictions for each 
        row in that DataFrame. The DataFrame must hold data that can be run through this model.
        """

    def save_to_file(self, filepath: str) -> None:
        """
        A method that will save a LinearRegressionCore object to a JSON file. This file will then
        be available to be loaded and reused.

        Args:
            filepath: The filepath for the saved file

        Returns:
            None
        """

    def load_from_file(self, filepath: str) -> None:
        """
        A method that will load a LinearRegressionCore object from a JSON file.

        Args:
            filepath: The filepath for the saved file

        Returns:
            None
        """

########## LogReg ##########

class LogisticRegressionCore:
    """
    A rust-built class meant to hold the results and metadata of a logistic regression. This
    class is the internal representation of a logistic regression model, and does the 
    behind-the-scenes work for the user-facing LogisticRegression class.

    Attributes:
        coefficients (dict[str, float]): A dictionary of coefficient names and values.
        encoding_data (Encoder): Encoding metadata. Used when predicting on other datasets 
            than the one used to fit. 
        formula (Formula): A Formula object containing the formula used to fit the logistic 
            regression.

    Methods:
        fit(design_matrix: ModelMatrix): Fits the regression model.
        predict(data: polars.DataFrame): Uses the model to make predictions on a new DataFrame.
        save_to_file(filepath: str): Saves the model to a given filepath.
        load_from_file(filepath: str): A method that will load a LogisticRegressionCore object from 
            a JSON file.
    """

    def __init__(self):
        pass

    ########## Attributes ##########

    @property
    def coefficients(self) -> dict[str, float] | None:
        """All levels for categorical variables. Reference level should be the first (index 0)."""

    @property
    def encoding_data(self) -> Encoder:
        """
        An Encoder object carrying encoding metadata. Used when predicting on other datasets 
        than the one used to fit.
        """

    @property
    def formula(self) -> Formula | None:
        """
        A Formula object containing the formula used in the logistic regression. 
        """
    @formula.setter
    def formula(self, value: Formula)-> None: ...

    ########## Public Methods ##########

    def fit(
            self, 
            x_matrix: np.ndarray, 
            y_matrix: np.ndarray,
            x_col_names: list[str], 
            encoder: Encoder,
            max_iterations: int = 25,
            convergence_delta: float = 1e-8
        ) -> None:
        """
        A method to fit a logistic regression using the contents of a ModelMatrix object. Internally 
        saves results and metadata. 
        """

    def predict(self, x_matrix: np.ndarray, x_col_names: list[str]):
        """
        A method that takes a polars DataFrame and uses it to generate predictions for each 
        row in that DataFrame. The DataFrame must hold data that can be run through this model.
        """

    def save_to_file(self, filepath: str) -> None:
        """
        A method that will save a LogisticRegressionCore object to a JSON file. This file will then
        be available to be loaded and reused.

        Args:
            filepath (str): The filepath for the saved file

        Returns:
            None
        """

    def load_from_file(self, filepath: str) -> None:
        """
        A method that will load a LogisticRegressionCore object from a JSON file.

        Args:
            filepath (str): The filepath for the saved file

        Returns:
            None
        """

########## LogReg ##########

class PenaltySpecification:
    """
    A class meant to hold information about the way a specified variable is penalized in the regression. 

    Initialization:
        variable_name (str): The name of the variable to be penalized. This is meant to match the 
            name of the column in the model matrix that is to be penalized. If the variable is 
            categorical, use this + the categorical_level param to find the relevant variable. For
            interaction terms, use the syntax 'variable1_level:variable2_level' (with levels potentially
            not necessary).
        categorical_level (str | None): The optional level of the categorical variable that 
            we want to penalize.
        lambda_param (float): The lambda parameter for penalization.
        target (float): The number to penalize towards (defaults to 0).
    """

    def __init__(self, variable_name: str, categorical_level: str | None, lambda_param: float, target: float = 0):
        pass

class PenalizedLogisticRegressionCore:
    """
    A rust-built class meant to hold the results and metadata of a penalized logistic regression. This
    class is the internal representation of a penalized logistic regression model, and does the 
    behind-the-scenes work for the user-facing PenalizedLogisticRegression class.

    Attributes:
        coefficients (dict[str, float]): A dictionary of coefficient names and values.
        encoding_data (Encoder): Encoding metadata. Used when predicting on other datasets 
            than the one used to fit. 
        formula (Formula): A Formula object containing the formula used to fit the penalized logistic 
            regression.

    Methods:
        fit(design_matrix: ModelMatrix): Fits the regression model.
        predict(data: polars.DataFrame): Uses the model to make predictions on a new DataFrame.
        save_to_file(filepath: str): Saves the model to a given filepath.
        load_from_file(filepath: str): A method that will load a PenalizedLogisticRegressionCore object from 
            a JSON file.
    """

    def __init__(self):
        pass

    ########## Attributes ##########

    @property
    def coefficients(self) -> dict[str, float] | None:
        """All levels for categorical variables. Reference level should be the first (index 0)."""

    @property
    def encoding_data(self) -> Encoder:
        """
        An Encoder object carrying encoding metadata. Used when predicting on other datasets 
        than the one used to fit.
        """

    @property
    def formula(self) -> Formula | None:
        """
        A Formula object containing the formula used in the penalized logistic regression. 
        """
    @formula.setter
    def formula(self, value: Formula)-> None: ...

    ########## Public Methods ##########

    def fit(
            self, 
            x_matrix: np.ndarray, 
            y_matrix: np.ndarray,
            x_col_names: list[str], 
            encoder: Encoder,
            penalty_specs: list[PenaltySpecification] | None = None,
            max_iterations: int = 25,
            convergence_delta: float = 1e-8
        ) -> None:
        """
        A method to fit a penalized logistic regression using the contents of a ModelMatrix object. Internally 
        saves results and metadata. 
        """

    def predict(self, x_matrix: np.ndarray, x_col_names: list[str]):
        """
        A method that takes a polars DataFrame and uses it to generate predictions for each 
        row in that DataFrame. The DataFrame must hold data that can be run through this model.
        """

    def save_to_file(self, filepath: str) -> None:
        """
        A method that will save a PenalizedLogisticRegressionCore object to a JSON file. This file will then
        be available to be loaded and reused.

        Args:
            filepath (str): The filepath for the saved file

        Returns:
            None
        """

    def load_from_file(self, filepath: str) -> None:
        """
        A method that will load a PenalizedLogisticRegressionCore object from a JSON file.

        Args:
            filepath (str): The filepath for the saved file

        Returns:
            None
        """
