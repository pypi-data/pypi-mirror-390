import aws_cdk as cdk
import pytest
from aws_cdk.assertions import Template

from aws_cdk_constructs.efs.volume import EFSVolume


@pytest.fixture
def app():
    return cdk.App()


@pytest.fixture
def stack(app):
    return cdk.Stack(app, 'test-stack')


@pytest.fixture
def vpc(stack):
    return cdk.aws_ec2.Vpc(stack, 'test-vpc')


def test_created_volume(stack, vpc, environment_parameters):
    volume = EFSVolume(
        scope=stack,
        id='volume-id',
        environment='development',
        environments_parameters=environment_parameters,
        vpc=vpc,
        volume_mount_path='/opt/mount',
        app_name='test-app',
    )

    assert isinstance(volume._efs_security_group, cdk.aws_ec2.SecurityGroup)
    assert isinstance(volume.efs, cdk.aws_efs.FileSystem)
    assert isinstance(
        volume.efs_volume_configuration, cdk.aws_ecs.EfsVolumeConfiguration
    )


def test_created_volume_template(stack, vpc, environment_parameters):
    EFSVolume(
        scope=stack,
        id='volume-id',
        environment='development',
        environments_parameters=environment_parameters,
        vpc=vpc,
        volume_mount_path='/opt/mount',
        app_name='test-app',
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::EFS::FileSystem',
        {
            'FileSystemTags': [
                {'Key': 'HasBackup', 'Value': 'false'},
                {'Key': 'Name', 'Value': 'test-stack/volume-id-efs'},
            ]
        },
    )
    template.resource_count_is('AWS::EFS::MountTarget', 2)


def test_grant_access_to_volume(stack, vpc, environment_parameters):
    volume = EFSVolume(
        scope=stack,
        id='volume-id',
        environment='development',
        environments_parameters=environment_parameters,
        vpc=vpc,
        volume_mount_path='/opt/mount',
        app_name='test-app',
    )
    sg = cdk.aws_ec2.SecurityGroup(
        stack,
        'SecurityGroup',
        vpc=vpc,
        description='Allow ssh access to ec2 instances',
        allow_all_outbound=False,
    )
    volume.grant_access(peer=sg)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::EC2::SecurityGroupIngress', {'IpProtocol': 'tcp', 'ToPort': 2049}
    )


def test_get_mount_point(stack, vpc, environment_parameters):
    volume = EFSVolume(
        scope=stack,
        id='volume-id',
        environment='development',
        environments_parameters=environment_parameters,
        vpc=vpc,
        volume_mount_path='/opt/mount',
        app_name='test-app',
    )
    mount_point = volume.get_mount_point()
    isinstance(mount_point, cdk.aws_ecs.MountPoint)


def test_development_policy_and_backup(stack, vpc, environment_parameters):
    EFSVolume(
        scope=stack,
        id='volume-id',
        environment='development',
        environments_parameters=environment_parameters,
        vpc=vpc,
        volume_mount_path='/opt/mount',
        to_be_backed_up=True,
        app_name='test-app',
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::EFS::FileSystem',
        {
            'FileSystemTags': [
                {'Key': 'HasBackup', 'Value': 'false'},
                {'Key': 'Name', 'Value': 'test-stack/volume-id-efs'},
            ]
        },
    )
    template.has_resource('AWS::EFS::FileSystem', {'DeletionPolicy': 'Delete'})
    template.has_resource(
        'AWS::EFS::FileSystem', {'UpdateReplacePolicy': 'Delete'}
    )


def test_production_policy(stack, vpc, environment_parameters):
    EFSVolume(
        scope=stack,
        id='volume-id',
        environment='production',
        environments_parameters=environment_parameters,
        vpc=vpc,
        volume_mount_path='/opt/mount',
        app_name='test-app',
    )

    template = Template.from_stack(stack)
    template.has_resource('AWS::EFS::FileSystem', {'DeletionPolicy': 'Retain'})
    template.has_resource(
        'AWS::EFS::FileSystem', {'UpdateReplacePolicy': 'Retain'}
    )


def test_production_default_enabled_backup(stack, vpc, environment_parameters):
    EFSVolume(
        scope=stack,
        id='volume-id',
        environment='production',
        environments_parameters=environment_parameters,
        vpc=vpc,
        volume_mount_path='/opt/mount',
        app_name='test-app',
    )
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::EFS::FileSystem',
        {
            'FileSystemTags': [
                {'Key': 'HasBackup', 'Value': 'true'},
                {'Key': 'Name', 'Value': 'test-stack/volume-id-efs'},
            ]
        },
    )


def test_production_disabled_backup(stack, vpc, environment_parameters):
    EFSVolume(
        scope=stack,
        id='volume-id',
        environment='production',
        environments_parameters=environment_parameters,
        vpc=vpc,
        volume_mount_path='/opt/mount',
        to_be_backed_up=False,
        app_name='test-app',
    )
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::EFS::FileSystem',
        {
            'FileSystemTags': [
                {'Key': 'HasBackup', 'Value': 'false'},
                {'Key': 'Name', 'Value': 'test-stack/volume-id-efs'},
            ]
        },
    )
