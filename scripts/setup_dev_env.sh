source /home/bernard/projects/cdk_prevent_cfn_output/scripts/dev_env_vars.sh
cd /home/bernard/projects/cdk_prevent_cfn_output
source .venv/bin/activate
unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
unset AWS_SESSION_TOKEN
unset AWS_WEB_IDENTITY_TOKEN_FILE
aws sso login --profile dev
export CDK_DEFAULT_ACCOUNT=139497713478
export CDK_DEFAULT_REGION=eu-central-1
export AWS_PROFILE=dev
export AWS_REGION=eu-central-1