from rustmodels import LogisticRegression, fit_logistic_regression
from rustmodels.model_matrix import EncodingError

import pytest
import polars as pl
from pydantic import ValidationError

@pytest.mark.parametrize("formula_str, df, expected_error", [
    (5, pl.DataFrame({"x1": [1, 2], "x2": [3, 4]}), ValidationError),
    ("y ~ x1 + x2", "not_a_dataframe", ValidationError),
    ("y ~ x1", pl.DataFrame({"y": [5, 2], "x1": [1, 2]}), EncodingError)
])
def test_linreg_errors(
    formula_str,
    df,
    expected_error
):
    """
    Test where the fitting of a logistic regression should raise errors.
    """
    with pytest.raises(expected_error):
        model = LogisticRegression()
        model.fit(formula_str, df)

@pytest.fixture
def simple_df() -> pl.DataFrame:
    """
    A fixture to create a simple polars DataFrame for testing linear regression.
    """
    return pl.DataFrame({'y': [0, 0, 0, 0, 0, 1, 1, 1, 1, 1], 
                         'x': [1, 2, 1.3, 1, 0, 10, 11, 12, 9, 10]}, 
                         strict=False)

logreg_test_cases = [
    (
        "y ~ 0 + x",
        {'x': .2641182220995727}
    )
]

@pytest.mark.parametrize(
    "formula_str, expected_coefficients",
    logreg_test_cases
)
def test_linreg_fit(
    simple_df: pl.DataFrame,
    formula_str: str,
    expected_coefficients: dict[str, float]
):
    """
    Test the fit of the logistic regression model.
    """
    model = fit_logistic_regression(formula_str, simple_df)

    # Assertions
    assert isinstance(model, LogisticRegression)
    assert model.coefficients is not None
    assert model.coefficients.keys() == expected_coefficients.keys()
    for coef_name, expected_value in expected_coefficients.items():
        assert model.coefficients[coef_name] == pytest.approx(expected_value)

@pytest.mark.parametrize(
    "formula_str, expected_preds",
    [('y ~ x', [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0])]
)
def test_logreg_preds(
    simple_df: pl.DataFrame,
    formula_str: str,
    expected_preds: list[float]
):
    """
    Test the predictions of the logistic regression model.
    """
    model = fit_logistic_regression(formula_str, simple_df)
    preds = model.predict(simple_df)
    assert preds == pytest.approx(expected_preds, abs=1e-2)
