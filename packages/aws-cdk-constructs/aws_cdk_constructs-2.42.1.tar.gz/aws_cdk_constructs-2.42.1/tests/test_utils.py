import pytest

from aws_cdk_constructs.utils import *


@pytest.mark.parametrize(
    'raw, normalized',
    [
        ('qa', 'QA'),
        ('Qa', 'QA'),
        ('production', 'Production'),
        ('PrOducTion', 'Production'),
        ('sharedservices', 'SharedServices'),
        ('ShARedServices', 'SharedServices'),
        ('anyother', 'Development'),
    ],
)
def test_normalize_environment_parameter(raw, normalized):
    assert normalize_environment_parameter(raw) == normalized
