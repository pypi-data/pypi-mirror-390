"""
Tests for the linear regression model.
"""
import rustmodels

import pytest
import polars as pl
from pydantic import ValidationError

@pytest.mark.parametrize("formula_str, df", [
    (5, pl.DataFrame({"x1": [1, 2], "x2": [3, 4]})),
    ("y ~ x1 + x2", "not_a_dataframe"),
])
def test_linreg_type_errors(
    formula_str,
    df
):
    """
    Test where the linear regression function should raise validation errors.
    """
    with pytest.raises(ValidationError):
        rustmodels.fit_linear_regression(formula_str, df)

@pytest.fixture
def simple_df() -> pl.DataFrame:
    """
    A fixture to create a simple polars DataFrame for testing linear regression.
    """
    return pl.DataFrame({'y': [1, 2, 3], 'x': [1, 2, 2]})

linreg_test_cases = [
    (
        "y ~ x",
        {'intercept': -0.5, 'x': 1.5}
    ),
    (
        "y ~ 0 + x",
        {'x': 11/9}
    )
]

@pytest.mark.parametrize(
    "formula_str, expected_coefficients",
    linreg_test_cases
)
def test_linreg_fit(
    simple_df: pl.DataFrame,
    formula_str: str,
    expected_coefficients: dict[str, float]
):
    """
    Test the fit of the linear regression model.
    """
    results = rustmodels.fit_linear_regression(formula_str, simple_df)

    # Assertions
    assert isinstance(results, rustmodels.LinearRegression)
    assert results.coefficients is not None
    assert results.coefficients.keys() == expected_coefficients.keys()
    for coef_name, expected_value in expected_coefficients.items():
        assert results.coefficients[coef_name] == pytest.approx(expected_value)