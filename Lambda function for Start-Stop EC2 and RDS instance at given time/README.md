# Cloudformation-Template
This repo contains the CF templates.



Lambda Function to automatically Start-Stop EC2 and RDS Cloudformation Setup

--->Author: Sumit Tiwari

The purpose of this document is to enable the team to set up Lambda functions which Start-Stop the EC2 and RDS on the Infrastructure as per the working time frame to save the cost using Cloudformation.

Steps 

Step 1: Setup Cloudformation template --->Setting up a Cloudformation template which will create Lambda function, CloudWatch event rule, IAM roles and policies. 

Step 2: Write some Python code --->Python code for creating the function that can start and stop the EC2 and RDS which are having a particular tag. 

Step 3: Infrastructure Setup
AWS Lambda, CW Event, IAM ----->Use AWS Cloudformation to create a IAM role for Lambda, a AWS Lambda function (Start-Stop-EC2-and-RDS) and two AWS CloudWatch Events of start and stop.
S3 bucket ----->This s3 bucket is used to store the CF template in yaml format and the python code in a zip format. 

Step 4: Manual work
1. While creating a stack for cloudformation we have to enter a manual time-frame otherwise the default will be taken (ie Start - 9AM IST and Stop - 9PM IST).
2. Giving tags to the cluster(Amazon Aurora) and instances(EC2 and RDS) so that Lambda function could recognize them. ---Note: In case of Amazon Aurora put tags in the cluster not in the instances.

Cloudformation Template description

Parameter
1. Start
2. Stop


Resources

1. IAM Role
2. Policy
3. Lambda Function
4. Start event with permission
5. Stop event with permission


Python Code

1. EC2 Function
2. RDS Function
3. Amazon Aurora Cluster Function
4. Extra Function with import details
