#!/bin/bash -xe

yum update -y aws-cfn-bootstrap

#
# ~~~~~~~~~~ Get environment info. 
# Variables will be available within the custom user-data.sh
#
AZ_IN_USE=$(curl http://169.254.169.254/latest/meta-data/placement/availability-zone/)

#
# ~~~~~~~~~~ Export environment variables. 
# Variables will be available within the custom user-data.sh
#
MY_VARS_FILE=/root/MY_VARS_FILE
touch $MY_VARS_FILE
echo "export ApplicationName=_ApplicationName_" >> $MY_VARS_FILE
echo "export Environment=_Environment_" >> $MY_VARS_FILE
echo "export S3CodeBucket=_S3CodeBucket_" >> $MY_VARS_FILE
echo "export S3AssetsBucket=_S3AssetsBucket_" >> $MY_VARS_FILE
echo "export S3ConfigurationsBucket=_S3Bucket_" >> $MY_VARS_FILE
echo "export S3ConfigurationsRootFolder=_S3Bucket_/_ApplicationName_/_Environment_" >> $MY_VARS_FILE
echo "export IsAppPublic=_IsAppPublic_" >> $MY_VARS_FILE
echo "export AZInUse=_AzInUse_" >> $MY_VARS_FILE
echo "export DataVolumeId=_DataVolumeId_" >> $MY_VARS_FILE
echo "export SMTPServer=_SMTPServer_" >> $MY_VARS_FILE
echo "export SMTPPort=_SMTPPort_" >> $MY_VARS_FILE
echo "export EFS=_EFS_" >> $MY_VARS_FILE
echo "export AWS_REGION=eu-west-1" >> $MY_VARS_FILE
echo "export EC2_TRAFFIC_PORT=_EC2_TRAFFIC_PORT_" >> $MY_VARS_FILE
#ADDITIONAL_VARIABLES_HERE
source $MY_VARS_FILE

#
# ~~~~~~~~~~ Download and execute custom user-data script
#
cd /root
aws s3 cp s3://_S3Bucket_/_ApplicationName_/_Environment_/_UserDataS3Key_ user-data.sh
chmod +x user-data.sh
./user-data.sh

# To force user data to fail is external user-data fails
if [ $? -ne 0 ]
then 
exit 1
fi

# ~~~~~~~~~~ Do not remove, this is to force manual ASG rolling update
Toggle=_ToggleToTriggerRollingUpdate_

#
# ~~~~~~~~~~ Finally send cft-signal (Dynamically replace ASG logical id)
#
# NB: This is programmatically added in the Construct