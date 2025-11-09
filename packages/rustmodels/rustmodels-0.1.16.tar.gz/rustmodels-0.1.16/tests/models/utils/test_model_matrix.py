
import pytest
from rustmodels import _rustmodels as rm, model_matrix as mm
import polars as pl
import numpy as np

@pytest.fixture
def df() -> pl.DataFrame:
    """
    A fixture to create a polars DataFrame for testing.
    """
    return pl.DataFrame({
        'y': [1, 2, 3, 4, 5, 3, 6, 8, 7, 10],
        'x_int': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        'x_bool': [True, False, True, False, True, False, True, False, True, False],
        'x_str': ['ab', 'cd', 'de', None, 'ab', 'ab', 'cd', 'de', 'ab', None]
    })

model_matrix_test_cases = [
    # Standard case
    (
        'y ~ x_int + x_bool',
        np.array([
            [1, 2, 1], [1, 3, 0], [1, 4, 1], [1, 5, 0], [1, 6, 1],
            [1, 7, 0], [1, 8, 1], [1, 9, 0], [1, 10, 1], [1, 11, 0]
        ]),
        np.array([1, 2, 3, 4, 5, 3, 6, 8, 7, 10]),
        ['intercept', 'x_int', 'x_bool'],
        {'y': rm.EncodingType.Numeric, 'x_int': rm.EncodingType.Numeric, 'x_bool': rm.EncodingType.Bool}
    ),

    # Case with no intercept
    (
        'y ~ 0 + x_int + x_bool',
        np.array([
            [2, 1], [3, 0], [4, 1], [5, 0], [6, 1],
            [7, 0], [8, 1], [9, 0], [10, 1], [11, 0]
        ]),
        np.array([1, 2, 3, 4, 5, 3, 6, 8, 7, 10]),
        ['x_int', 'x_bool'],
        {'y': rm.EncodingType.Numeric, 'x_int': rm.EncodingType.Numeric, 'x_bool': rm.EncodingType.Bool}
    ),

    # Case with str & None
    (
        'y ~ 0 + x_str',
        np.array([
            [0, 0], [1, 0], [0, 1], [0, 0],
            [0, 0], [1, 0], [0, 1], [0, 0]
        ]),
        np.array([1, 2, 3, 5, 3, 6, 8, 7]),
        ['x_str_cd', 'x_str_de'],
        {'y': rm.EncodingType.Numeric, 'x_str': rm.EncodingType.Dummy}
    ),

    # Case with str-bool interactions
    (
        'y ~ x_str:x_bool',
        np.array([
            [1, 0, 0], [1, 0, 0], [1, 0, 1], [1, 0, 0],
            [1, 0, 0], [1, 1, 0], [1, 0, 0], [1, 0, 0]
        ]),
        np.array([1, 2, 3, 5, 3, 6, 8, 7]),
        ['intercept', 'x_str_cd:x_bool', 'x_str_de:x_bool'],
        {'y': rm.EncodingType.Numeric, 'x_str': rm.EncodingType.Dummy, 'x_bool': rm.EncodingType.Bool}
    ),
]

@pytest.mark.parametrize(
    "formula_str, expected_x, expected_y, expected_x_cols, expected_encodings",
    model_matrix_test_cases
)
def test_model_matrix(
    df: pl.DataFrame,
    formula_str: str,
    expected_x: np.ndarray,
    expected_y: np.ndarray,
    expected_x_cols: list[str],
    expected_encodings: dict[str, rm.EncodingType]
):
    """
    Test for creating a model matrix.
    """
    parsed_formula = rm._parse_formula(formula_str)
    model_matrix = mm.get_model_matrix(df, parsed_formula)

    # Assertions for y_matrix
    np.testing.assert_array_equal(model_matrix.y_matrix, expected_y)

    # Assertions for x_matrix
    assert model_matrix.x_col_names == expected_x_cols
    np.testing.assert_array_equal(model_matrix.x_matrix, expected_x)

    # Assertions for encoding_data
    encoder = model_matrix.encoding_data
    assert isinstance(encoder, rm.Encoder)
    
    for col_name, expected_encoding_type in expected_encodings.items():
        encoding_info = encoder.get_column_mapping(col_name)
        assert encoding_info is not None
        assert encoding_info.encoding_type == expected_encoding_type
        if expected_encoding_type != rm.EncodingType.Dummy:
            assert encoding_info.levels is None
