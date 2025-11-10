from . import _rustmodels as rm, model_matrix as mm
from ._rustmodels import LinearRegressionCore
import polars as pl
from pydantic import validate_call, ConfigDict
import numpy as np
from typing import cast

########## Wrapper class ##########

class LinearRegression:
    """
    A class meant to hold the results and metadata of a linear regression.

    Attributes:
        coefficients (dict[str, float]): A dictionary of coefficient names and values.
        encoding_data (Encoder): Encoding metadata. Used when predicting on other datasets 
            than the one used to fit. 
        formula (Formula): A Formula object containing the formula used to fit the 
            regression.

    Methods:
        fit(design_matrix: ModelMatrix): Fits the regression model.
        predict(data: polars.DataFrame): Uses the model to make predictions on a new DataFrame.
        save_to_file(filepath: str): Saves the model to a given filepath.
        load_from_file(filepath: str): A method that will load a LinearRegression object from a JSON file.
    """

    def __init__(self):
        self._model = LinearRegressionCore()

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
        A Formula object containing the formula used in the linear regression. 
        """
        return self._model.formula
    @formula.setter
    def formula(self, value: rm.Formula)-> None:
        self._model.formula = value

    ########## Public-facing methods ##########

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def fit(self, formula: str, df: pl.DataFrame) -> None:
        """
        Method to fit a linear regression model.

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
        
        # Matrix math
        model_instance = LinearRegressionCore()
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
        A method that will save a LinearRegressionCore object to a JSON file. This file will then
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
        A method that will load a LinearRegression object from a JSON file.

        Args:
            filepath (str): The filepath for the saved file

        Returns:
            None
        """
        model = self._model
        model.load_from_file(filepath)

########## Functions ##########

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def fit_linear_regression(formula: str, df: pl.DataFrame) -> LinearRegression:
    """
    Function that performs a linear regression fit.

    Args:
        formula (str): Formula for the regression taking place. This will use the R formula syntax.
        df (pl.DataFrame): A DataFrame containing the data to fit the model. It will be used in 
            conjunction with the formula to create the model matrix. 

    Returns:
        LinearRegression: A 'LinearRegression' object containing the regression results.
    """
    model_instance = LinearRegression()
    model_instance.fit(formula, df)
    
    return model_instance