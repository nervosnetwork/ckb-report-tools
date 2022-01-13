#!/usr/bin/env bash

# ENVIRONMENT VARIABLES:
# 
#   * AWS_ACCESS_KEY, required, the AWS access key
#   * AWS_SECRET_KEY, required, the AWS secret key
#   * GITHUB_TOKEN, required, GitHub API authentication token
set -euo pipefail
AWS_ACCESS_KEY=${AWS_ACCESS_KEY_ID}
AWS_SECRET_KEY=${AWS_SECRET_ACCESS_KEY}
GITHUB_TOKEN=${GITHUB_TOKEN}
SCRIPT_PATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
function markdown_report() {
    case "$OSTYPE" in
        darwin*)
            if ! type gsed &> /dev/null || ! type ggrep &> /dev/null; then
                echo "GNU sed and grep not found! You can install via Homebrew" >&2
                echo >&2
                echo "    brew install grep gnu-sed" >&2
                exit 1
            fi

            SED=gsed
            GREP=ggrep
            ;;
        *)
            SED=sed
            GREP=grep
            ;;
    esac
    echo "**Daily VM check List**:"
    echo "| Instance_Tag | Instance_Id | State | Region | Launch_Time | Instance_Link |"
    echo "| :--- | :--- | :--- | :--- | :--- | :--- |"
    cat ${GITHUB_WORKSPACE}/instances.txt
    echo -e "\n**Daily VPC check List**:"
    echo "| VPC_Tag | VPC_Id | State | Region | VPC_Link |"
    echo "| :--- | :--- | :--- | :--- | :--- |"
    cat ${GITHUB_WORKSPACE}/vpc.txt
    echo -e "\n**Daily Key Pairs check List**:"
    echo "| Key_Nmae | Key_Id | Key_Type | Region |"
    echo "| :--- | :--- | :--- | :--- |"
    cat ${GITHUB_WORKSPACE}/keypairs.txt
    echo -e "\n**Daily Security Groups check List**:"
    echo "| Group_Name | Group_Id | Vpc_Id | Region | SG_Link"
    echo "| :--- | :--- | :--- | :--- | :--- |"
    cat ${GITHUB_WORKSPACE}/sg.txt
}

# Upload report through GitHub issue comment
function github_add_comment() {
    report="$1"
    export GITHUB_TOKEN=${GITHUB_TOKEN}
    $SCRIPT_PATH/ok.sh add_comment nervosnetwork/ckb-internal 1665 "$report"
}
function main() {
  aws configure set aws_access_key_id ${AWS_ACCESS_KEY}
  aws configure set aws_secret_access_key ${AWS_SECRET_KEY}
  aws configure set region us-west-2
  #region, created-time, resource link
  aws ec2 describe-regions --output text --query Regions[*].[RegionName] >>regions.txt
  while read -r region;
  do
    region=$(echo "$region" | tr -d '[:space:]')
    aws ec2 describe-instances --region $region --filters "Name=instance-state-code,Values=16" |jq '.Reservations[].Instances[] | "| \(.Tags[].Value) | \(.InstanceId) | \(.State.Name) | '$region' | \(.LaunchTime) | https://us-east-2.console.aws.amazon.com/ec2/v2/home?region='$region'#InstanceDetails:instanceId=\(.InstanceId) |"'| sed 's/\"//g' >>${GITHUB_WORKSPACE}/instances.txt
    aws ec2 describe-vpcs --region $region --filters "Name=is-default,Values=false" |jq '.Vpcs[] | "| \(.Tags[].Value) | \(.VpcId) | \(.State) | '$region' | https://'$region'.console.aws.amazon.com/vpc/home?region='$region'#VpcDetails:VpcId=\(.VpcId) |"'| sed 's/\"//g' >>${GITHUB_WORKSPACE}/vpc.txt
    aws ec2 describe-key-pairs  --region $region |jq '.KeyPairs[] | "| \(.KeyName) | \(.KeyPairId) | \(.KeyType) | '$region' |"'| sed 's/\"//g' >>${GITHUB_WORKSPACE}/keypairs.txt
    aws ec2 describe-security-groups --region $region |jq '.SecurityGroups[] | "| \(.GroupName) | \(.GroupId) | \(.VpcId) | '$region' | https://'$region'.console.aws.amazon.com/ec2/v2/home?region='$region'#SecurityGroup:groupId=\(.GroupId) "' | sed 's/\"//g' >>${GITHUB_WORKSPACE}/sg.txt
  done < "regions.txt"
  github_add_comment "$(markdown_report)"
}

main $*
