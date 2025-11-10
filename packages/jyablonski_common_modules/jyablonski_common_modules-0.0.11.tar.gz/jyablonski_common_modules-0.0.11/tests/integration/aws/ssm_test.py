import boto3
from moto import mock_aws
import pytest

from jyablonski_common_modules.aws import get_ssm_parameter


@mock_aws
def test_get_ssm_parameter_success():
    client = boto3.client("ssm", region_name="us-east-1")
    parameter_name = "jacobs_test_parameter"
    parameter_value = "my super secret value"

    client.put_parameter(
        Name=parameter_name,
        Description="A test parameter",
        Value=parameter_value,
        Type="String",
    )

    parameter = get_ssm_parameter(client=client, parameter_name=parameter_name)

    assert parameter == parameter_value


@mock_aws
def test_get_ssm_parameter_fail():
    client = boto3.client("ssm", region_name="us-east-1")

    parameter_name = "jacobs_test_parameter"
    fake_parameter_name = "this doesn't exist hoe"
    parameter_value = "my super secret value"

    client.put_parameter(
        Name=parameter_name,
        Description="A test parameter",
        Value=parameter_value,
        Type="String",
    )

    with pytest.raises(TypeError):
        parameter = get_ssm_parameter(client=client, parameter_name=fake_parameter_name)
