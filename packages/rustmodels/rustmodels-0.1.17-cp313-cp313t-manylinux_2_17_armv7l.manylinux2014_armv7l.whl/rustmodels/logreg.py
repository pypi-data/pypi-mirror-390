from . import _rustmodels as rm, model_matrix as mm
from ._rustmodels import LogisticRegressionCore
import polars as pl
import numpy as np
from numpy.typing import NDArray
from pydantic import validate_call, ConfigDict
from typing import cast

########## Wrapper class ##########

class LogisticRegression:
    """
    A class meant to hold the results and metadata of a logistic regression.

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
        load_from_file(filepath: str): A method that will load a LogisticRegression object from a JSON file.
    """

    # TODO: Share functionality with logreg/linreg

    def __init__(self):
        self._model = LogisticRegressionCore()

    ########## Properties ##########

    @property
    def coefficients(self) -> dict[str, float] | None:
        """All levels for categorical variables. Reference level should be the first (index 0)."""
        return self._model.coefficients
    
    @property
    def encoding_data(self) -> rm.Encoder:
        """
        An Encoder object carrying encoding metadata. Used when predicting on other datasets 
        than the one used to fit.
        """
        return self._model.encoding_data

    @property
    def formula(self) -> rm.Formula | None:
        """
        A Formula object containing the formula used in the logistic regression. 
        """
        return self._model.formula
    @formula.setter
    def formula(self, value: rm.Formula)-> None:
        self._model.formula = value

    ########## Public-facing methods ##########

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def fit(self, formula: str, df: pl.DataFrame) -> None:
        """
        Method to fit a logistic regression model.

        Args:
            formula (str): Formula for the regression taking place. This will use the R formula syntax.
            df (pl.DataFrame): A DataFrame containing the data to fit the model. It will be used in 
                conjunction with the formula to create the model matrix. 

        Returns:
            None
        """
        # Parse formula in rust
        parsed_formula = rm._parse_formula(formula) # pyright: ignore[reportPrivateUsage]

        # Model matrix in python
        model_matrix = mm.get_model_matrix(df, parsed_formula)

        # Ensure that y is binary
        _validate_y_for_logistic(model_matrix.y_matrix)
        
        # Matrix math
        model_instance = LogisticRegressionCore()
        model_instance.formula = parsed_formula
        model_instance.fit(
            model_matrix.x_matrix,
            cast(np.ndarray, model_matrix.y_matrix),
            model_matrix.x_col_names,
            model_matrix.encoding_data
        )
        
        self._model = model_instance
        return

    def predict(self, df: pl.DataFrame) -> np.ndarray:
        """
        A method that will use the saved information from an already fit model along
        with new data to output predixtons. 

        Args:
            df (pl.DataFrame): The data which we want to use for predictions.

        Returns:
            np.ndarray: A numpy array of predicted values.

        Raise:
            ValueError: If encoder or formula 
        """
        formula = self._model.formula
        encoder = self._model.encoding_data

        if formula is None or encoder is None:
            raise RuntimeError("Model must be fit before running predictions.")

        model_matrix = mm.get_model_matrix(df, formula, encoder)

        return self._model.predict(
            model_matrix.x_matrix,
            model_matrix.x_col_names
        )

    def save_to_file(self, filepath: str) -> None:
        """
        A method that will save a LogisticRegression object to a JSON file. This file will then
        be available to be loaded and reused.

        Args:
            filepath (str): The filepath for the saved file

        Returns:
            None
        """
        model = self._model
        if model.encoding_data or model.formula is None or model.coefficients is None:
            model.save_to_file(filepath)

    def load_from_file(self, filepath: str) -> None:
        """
        A method that will load a LogisticRegression object from a JSON file.

        Args:
            filepath (str): The filepath for the saved file

        Returns:
            None
        """
        model = self._model
        model.load_from_file(filepath)

########## Functions ##########

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def fit_logistic_regression(formula: str, df: pl.DataFrame) -> LogisticRegression:
    """
    Function that performs a logistic regression fit.

    Args:
        formula (str): Formula for the regression taking place. This will use the R formula syntax.
        df (pl.DataFrame): A DataFrame containing the data to fit the model. It will be used in 
            conjunction with the formula to create the model matrix. 

    Returns:
        LogisticRegression: A 'LogisticRegression' object containing the regression results.
    """
    model_instance = LogisticRegression()
    model_instance.fit(formula, df)
    
    return model_instance

def _validate_y_for_logistic(y_matrix: NDArray[np.float64] | None) -> None:
    """
    Validates that the dependent variable is suitable for logistic regression.

    Raises:
        EncodingError: If y matrix is not 1-dimensional or not binary
    """
    if y_matrix is None:
        raise mm.EncodingError("y matrix must not be empty.")

    if y_matrix.ndim != 1:
        raise mm.EncodingError(f"y data must be a 1D array, but it has {y_matrix.ndim} dimensions.")

    is_binary = np.all((y_matrix == 0.0) | (y_matrix == 1.0))
    if not is_binary:
        raise mm.EncodingError(
            "For logistic regression, the dependent variable must be binary (0s and 1s)."
        )
