from aws_cdk_constructs.ecs.fargate_validator import FargateValidator
import pytest


@pytest.mark.parametrize(
    'cpu, mem',
    [
        (256, 512),
        (256, 1024),
        (256, 2048),
        (512, 1024),
        (512, 2048),
        (512, 3072),
        (512, 4096),
    ],
)
def test_fargate_valid_types(cpu, mem):
    try:
        FargateValidator(cpu=cpu, mem=mem)
    except ValueError:
        assert False


@pytest.mark.parametrize('cpu, mem', [(256, 4096), (512, 512)])
def test_fargate_raises_exception(cpu, mem):
    with pytest.raises(ValueError):
        FargateValidator(cpu=cpu, mem=mem)
