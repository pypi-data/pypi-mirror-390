import polars as pl
from ._rustmodels import Formula, Encoder, EncodedColumnInfo, EncodingType
import numpy as np
from numpy.typing import NDArray
from typing import Tuple
from dataclasses import dataclass

#################### Classes ####################

@dataclass
class ModelMatrix:
    """
    A class meant to hold the model matrices as well as Encoding metadata

    Attributes:
        x_matrix (numpy.ndarray): A 2D array of floats meant to represent the independent variable
        y_matrix (numpy.ndarray): A 1D array of floats meant to represent the dependent variable
        x_col_names (list[str]): The column names for the x_matrix
        encoding_data (Encoder): A collection of metadata on how the data was encoded
    """
    x_matrix: NDArray[np.float64]
    y_matrix: NDArray[np.float64] | None
    x_col_names: list[str]
    encoding_data: Encoder

#################### Main function ####################

def get_model_matrix(
        data: pl.DataFrame, 
        formula: Formula, 
        encoder: Encoder | None = None,
        for_prediction: bool = False,
        level_encoding_type: EncodingType = EncodingType.Dummy
    ) -> ModelMatrix:
    """
    A function meant to create model matrices from a DataFrame and a formula.

    Cleans the DataFrame and formats the matrices.

    Args:
        data (pl.DataFrame): A DataFrame containing the data to fit the model. It will be used 
            in conjunction with the formula to create the model matrix.
        formula (Formula): A Formula object representing the model formula.
        encoder (Encoder | None): An optional encoder object. If None, the encoder will be fit
            and returned. If not None, the provided encoder will be used and help to verify the
            data. 
        for_prediction (bool): If True, the y column is not necessary
        level_encoding_type (EncodingType): The encoding type to use for categorical variables. It 
            must be Dummy or OneHot.

    Returns:
        ModelMatrix: A ModelMatrix object holding final matrices and encoding info
    """

    ##### Functionality #####
    _ = validate_data_and_formula(data, formula, for_prediction)
    data = select_and_filter(data, formula, for_prediction)
    model_matrices = make_into_matrices(data, formula, encoder, for_prediction, level_encoding_type)
    return model_matrices

#################### Helper functions ####################

def make_into_matrices(
        data: pl.DataFrame, 
        formula: Formula, 
        encoder: Encoder | None,
        for_prediction: bool,
        level_encoding_type: EncodingType = EncodingType.Dummy
    ) -> ModelMatrix:
    """
    A function meant to create model matrices from a cleaned DataFrame and a formula.

    Args:
        data (pl.DataFrame): A DataFrame containing the data to fit the model. It will be used 
            in conjunction with the formula to create the model matrix.
        formula (Formula): A Formula object representing the model formula.
        encoder (Encoder | None): An optional encoder object. If None, the encoder will be fit
            and returned. If not None, the provided encoder will be used and help to verify the
            data.
        for_prediction (bool): If True, the y column is not necessary.
        level_encoding_type (EncodingType): The encoding type to use for categorical variables. It 
            must be Dummy or OneHot.

    Returns:
        ModelMatrix: A ModelMatrix object holding final matrices and encoding info
    """
    if encoder is None:
        encoder = fit_encoder(data, formula, level_encoding_type)
    x_matrix, y_matrix, x_col_names = encode_data(data, formula, encoder, for_prediction)
    model_matrix = ModelMatrix(x_matrix, y_matrix, x_col_names, encoder)

    return model_matrix

def encode_data(
        data: pl.DataFrame, 
        formula: Formula, 
        encoder: Encoder,
        for_prediction: bool
    ) -> Tuple[np.ndarray, np.ndarray | None, list[str]]:
    """
    Turns the data into matrices for X and Y respectively. Used after the data has 
    already been fit for encoding.
    """
    # Y matrix
    y_matrix = None
    if not for_prediction:
        y_col = formula.dependent.name
        dep_encoding = encoder.get_column_mapping(y_col)
        if dep_encoding is None:
            raise EncodingError(f"Dependent variable {y_col} not found in encodings")
        
        encoding_type = dep_encoding.encoding_type
        if encoding_type not in [EncodingType.Bool, EncodingType.Numeric]:
            raise EncodingError(f"Dependent variable {y_col} encoded as {dep_encoding.encoding_type}, not numeric/boolean")
        
        y_matrix = data.select(y_col).to_numpy().squeeze()

    # X Matrix
    x_cols_expressions: list[pl.Expr] = []

    def get_categorical_levels(levels: list[str], encoding_type: EncodingType):
        """ Gets the levels for a categorical encoding type """
        if encoding_type == EncodingType.Dummy:
            return levels[1:]
        elif encoding_type == EncodingType.OneHot:
            return levels
        else:
            raise ValueError(f"Categorical levels shouldn't be found for encoding type '{encoding_type}'")

    for term in formula.independent:
        if term.intercept:
            # Add an expression for a column of 1s for the intercept
            x_cols_expressions.append(pl.lit(1, dtype=pl.Int8).alias("intercept"))
            continue
        elif term.interaction:
            interaction_cols = term.get_columns_from_term()
            if len(interaction_cols) != 2:
                raise NotImplementedError("Only 2-way interactions are currently supported.")

            col1_name, col2_name = interaction_cols[0], interaction_cols[1]
            col1_encoding = encoder.get_column_mapping(col1_name)
            col2_encoding = encoder.get_column_mapping(col2_name)

            if col1_encoding is None or col2_encoding is None:
                raise EncodingError(f"Interaction term {term.name} not found in encodings")

            numeric_encodings = [EncodingType.Numeric, EncodingType.Bool]
            is_col1_numeric = col1_encoding.encoding_type in numeric_encodings
            is_col2_numeric = col2_encoding.encoding_type in numeric_encodings
            is_col1_categorical = col1_encoding.encoding_type in [EncodingType.Dummy, EncodingType.OneHot]
            is_col2_categorical = col2_encoding.encoding_type in [EncodingType.Dummy, EncodingType.OneHot]

            if is_col1_numeric and is_col2_numeric:
                interaction_expr = (
                    pl.col(col1_name).cast(pl.Float64) * pl.col(col2_name).cast(pl.Float64)
                ).alias(f"{col1_name}:{col2_name}")
                x_cols_expressions.append(interaction_expr)
            elif (is_col1_categorical and is_col2_numeric) or (is_col2_categorical and is_col1_numeric):
                if is_col1_categorical:
                    categorical_col_name, numeric_col_name = col1_name, col2_name
                    categorical_encoding_info = col1_encoding
                else:
                    categorical_col_name, numeric_col_name = col2_name, col1_name
                    categorical_encoding_info = col2_encoding

                levels = categorical_encoding_info.levels
                if levels and len(levels) >= 2:
                    numeric_expr = pl.col(numeric_col_name).cast(pl.Float64)
                    levels_to_encode = get_categorical_levels(levels, categorical_encoding_info.encoding_type)
                    for level in levels_to_encode:
                        categorical_expr = pl.when(pl.col(categorical_col_name) == level).then(1).otherwise(0)
                        interaction_expr = (numeric_expr * categorical_expr).alias(
                            f"{categorical_col_name}_{level}:{numeric_col_name}"
                        )
                        x_cols_expressions.append(interaction_expr)
            elif is_col1_categorical and is_col2_categorical:
                levels1 = col1_encoding.levels
                levels2 = col2_encoding.levels

                if levels1 and len(levels1) >= 2 and levels2 and len(levels2) >= 2:
                    levels1_to_encode = get_categorical_levels(levels1, col1_encoding.encoding_type)
                    levels2_to_encode = get_categorical_levels(levels2, col2_encoding.encoding_type)
                    for level1 in levels1_to_encode:
                        for level2 in levels2_to_encode:
                            expr1 = pl.when(pl.col(col1_name) == level1).then(1).otherwise(0)
                            expr2 = pl.when(pl.col(col2_name) == level2).then(1).otherwise(0)
                            interaction_expr = (expr1 * expr2).alias(
                                f"{col1_name}_{level1}:{col2_name}_{level2}"
                            )
                            x_cols_expressions.append(interaction_expr)
            else:
                raise NotImplementedError("This interaction type is not yet implemented.")
        else: # Handle simple (non-interaction, non-intercept) terms
            col_name = term.name
            encoding_info = encoder.get_column_mapping(col_name)

            if encoding_info is None:
                raise EncodingError(f"Independent variable {col_name} not found in encodings")
            
            if encoding_info.encoding_type in [EncodingType.Dummy, EncodingType.OneHot]:
                levels = encoding_info.levels
                if levels is None:
                    raise EncodingError(f"No levels found for {col_name}")

                # Drop the first level as the reference category for dummy encoding
                levels_to_encode = get_categorical_levels(levels, encoding_info.encoding_type)
                for level in levels_to_encode:
                    expr = pl.when(pl.col(col_name) == level).then(1).otherwise(0).alias(f"{col_name}_{level}")
                    x_cols_expressions.append(expr)

            elif encoding_info.encoding_type == EncodingType.Bool:
                x_cols_expressions.append(pl.col(col_name).cast(pl.Int8))

            elif encoding_info.encoding_type == EncodingType.Numeric:
                x_cols_expressions.append(pl.col(col_name))

    if not x_cols_expressions:
        x_matrix = np.empty((data.height, 0))
        x_col_names = []
    else:
        temp_df = data.select(x_cols_expressions)
        x_col_names = temp_df.columns
        x_matrix = temp_df.to_numpy()

    y_return = y_matrix.astype(np.float64) if y_matrix is not None else None
    return x_matrix.astype(np.float64), y_return, x_col_names

def fit_encoder(data: pl.DataFrame, formula: Formula, level_encoding_type: EncodingType) -> Encoder:
    """
    Goes through the data once and finds out how the data will be encoded
    """
    schema = data.schema
    formula_cols = formula.get_column_names()
    encoder = Encoder()

    for col in formula_cols: # Not a try/except block because data has been validated already
        data_type: pl.DataType = schema[col]
        if data_type in [
            # Integer types
            pl.Int8, pl.Int16, pl.Int32, pl.Int64, pl.Int128,
            pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
            # Float types
            pl.Float32, pl.Float64
        ]:
            encoding_info = EncodedColumnInfo(
                None,
                EncodingType.Numeric
            )
        elif data_type == pl.Boolean:
            encoding_info = EncodedColumnInfo(
                None,
                EncodingType.Bool
            )
        elif data_type == pl.Utf8:
            if level_encoding_type not in [EncodingType.Dummy, EncodingType.OneHot]:
                raise ValueError(f"Encoding type {level_encoding_type} not allowed for categorical data.")

            levels = data[col].unique().to_list()
            _ = levels.sort()
            encoding_info = EncodedColumnInfo(
                levels,
                level_encoding_type
            )
        else:
            raise EncodingError(f"Column {col} has unimplemented data type {str(data_type)}")
            
        encoder.add_column_mapping(col, encoding_info)

    return encoder

def get_relevant_cols(formula: Formula, for_prediction: bool) -> list[str]:
    """Helper to get columns needed for fitting or prediction."""
    formula_cols = formula.get_column_names()
    if for_prediction:
        dep_name = formula.dependent.name
        if dep_name in formula_cols:
            formula_cols.remove(dep_name)
    return formula_cols

def select_and_filter(
        data: pl.DataFrame, 
        formula: Formula, 
        for_prediction: bool
    ) -> pl.DataFrame:
    """
    A function to select only the 

    Args:
        data (pl.DataFrame): The DataFrame to be edited
        formula (Formula): A formula object that will be used to select the relevant columns
            and filter them
        for_prediction (bool): If True, the y column is not necessary

    Returns:
        pl.DataFrame: A polars DataFrame with only relevant data included
    """
    # Select relevant cols
    formula_cols = get_relevant_cols(formula, for_prediction)
    relevant_data = data.select(formula_cols)

    # Filter out nulls
    relevant_data = relevant_data.drop_nulls().drop_nans()

    return relevant_data

def validate_data_and_formula(data: pl.DataFrame, formula: Formula, for_prediction: bool):
    """
    A function to validate that:
        1) The data isn't empty
        2) Each necessary column exists

    Args:
        data (pl.DataFrame): The polars DataFrame being validated
        formula (Formula): The formula being validated
        for_prediction (bool): If True, the y column is not necessary

    Returns:
        None

    Raises:
        DataValidationError: If the input DataFrame is empty or if formula columns cannot 
            be found
    """
    # Not empty
    if data.is_empty():
        raise DataValidationError("Empty DataFrame passed: Input must have data")

    # Each column exists
    formula_cols = get_relevant_cols(formula, for_prediction)
    dataframe_cols = data.columns

    for col in formula_cols:
        if col not in dataframe_cols:
            raise DataValidationError(f"Column {col} found in formula but not found in the data")
    
    return

#################### Errors ####################

class DataValidationError(ValueError):
    """
    Error raised when data and formula do not line up
    """
    pass

class EncodingError(ValueError):
    """
    Error raised when the encoding of the data for the Model Matrix goes wrong 
    or has obviously incorrect elements to it.
    """
    pass
