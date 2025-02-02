#!/bin/bash

# Define the .profile file location.  The .profile is used here because it is sourced
# for non-interactive shells, which is what the codedeploy agent uses to run things.
PROFILE=$HOME/.profile

# Use ec2metadata from cloud-utils to get the region containing the EC2
REGION=$(ec2metadata --availability-zone | sed 's/.$//')

# This is the list of parameters we want to get and apply to the .profile
PARAMS="ES_HOSTS ES_USER ES_PASSWORD" #ES_INDEX"

# For each param in list, get the value from parameter store and add it to the .profile.  If an export
# already exists update the value, otherwise append the export to the end of the .profile.  Blank spaces
# are removed from final value.
for PARAM in $PARAMS; do
    RAW_VALUE=$(aws ssm get-parameter --name $PARAM --query "Parameter.Value" --output text --region $REGION --with-decryption)
    VALUE=$(echo $RAW_VALUE | tr -d '[:blank:]')
    EXPORT_STATEMENT="export $PARAM=$VALUE"

    if grep -q "^export $PARAM=" $PROFILE; then
        sed -i "s|^export $PARAM=.*|$EXPORT_STATEMENT|" $PROFILE
    else
        echo $EXPORT_STATEMENT >> $PROFILE
    fi
    echo "Feteched and exported $PARAM from parameter store"
done

# Apply changes for the current session
source $PROFILE
