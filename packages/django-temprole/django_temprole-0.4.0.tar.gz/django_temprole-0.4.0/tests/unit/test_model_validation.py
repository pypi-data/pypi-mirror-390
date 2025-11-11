from contextlib import nullcontext as does_not_raise

import pytest
from django.core.exceptions import ValidationError
from freezegun import freeze_time
from test_utils.date_utils import _dtt
from test_utils.factories import TemporaryRoleFactory


@freeze_time("2022-01-14")
@pytest.mark.parametrize(
    "start, end, expectation",
    [
        pytest.param(
            None,
            None,
            pytest.raises(ValidationError, match='You need at least one of either Start or End date'),
            id='missing-dates',
        ),
        pytest.param(
            _dtt('2012-01-19 17:21:00 ITA'),
            _dtt('2012-01-19 16:21:00 ENG'),
            pytest.raises(ValidationError, match='Start date must be before end date'),
            id='end-before-start',
        ),
        pytest.param(
            _dtt('2012-01-19 17:21:00 ITA'), _dtt('2012-01-19 16:21:01 ENG'), does_not_raise(), id='just-1-second'
        ),
        pytest.param(_dtt('2012-01-19 17:21:00 ITA'), _dtt('2012-01-19 17:22:00 ITA'), does_not_raise(), id='ok'),
    ],
)
def test_temp_role_dates(start, end, expectation, db):
    with expectation:
        TemporaryRoleFactory(start_datetime=start, end_datetime=end)
        assert True
