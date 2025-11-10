from rustmodels import _rustmodels as rm
import pytest
from typing import Optional

@pytest.mark.parametrize("formula_str, expected_result_str, expected_error, error_message_pattern", [
    ('y~x1+x2', "y ~ 1 + x1 + x2", None, None),
    ('y~0 + x1+x2', "y ~ x1 + x2", None, None),
    ('y~-x2 + x1+x2', "y ~ 1 + x1", None, None),
    ('y~x1*x2', "y ~ 1 + x1 + x2 + x1:x2", None, None),
    ('y~x1:x2 + 0', "y ~ x1:x2", None, None),
    ('y~x1 + x2 + 5', "y ~ 1 + x1 + x2", None, None),
    ('y~0 + x1 + x1 + x1 + x3', "y ~ x1 + x3", None, None),
    ('y ~ -x1 + x2 + 5', "y ~ 1 + x2", None, None),
    ('y ~ x1 - 1', "y ~ x1", None, None),
    ('y ~ -1 + x1 + 1', "y ~ x1", None, None),
    
    # Error cases
    ('', None, ValueError, r"Formula cannot be empty"),
    ('y x1 + x2', None, ValueError, r"Formula must contain '~' to separate dependent and independent variables"),
    ('y ~~~~', None, ValueError, r"Formula cannot contain multiple '~' characters"),
    (' ~ x1 + x2', None, ValueError, r"Dependent variable cannot be empty"),
    ('y ~ ', None, ValueError, r"Independent variables cannot be empty"),
    ('y ~ x1*x2*x3', None, ValueError, r"Invalid term found in formula:")
])
def test_parse_formula(
    formula_str: str, 
    expected_result_str: Optional[str],
    expected_error: Optional[type[Exception]],
    error_message_pattern: Optional[str]
):
    if expected_error and error_message_pattern:
        with pytest.raises(expected_error, match=error_message_pattern):
            rm._parse_formula(formula_str) # pyright: ignore [reportPrivateUsage]
        return

    parsed_formula = rm._parse_formula(formula_str) # pyright: ignore [reportPrivateUsage]
    assert str(parsed_formula) == expected_result_str


