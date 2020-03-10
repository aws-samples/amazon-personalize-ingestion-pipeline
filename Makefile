# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

S3_BUCKET ?= retail-solution-ingest-bucket
REGION ?= eu-west-1

all: build

build:
	aws cloudformation package \
		--template-file stack.template \
		--s3-bucket $(S3_BUCKET) \
		--output-template-file packaged-template.yaml
	aws cloudformation deploy \
		--template-file packaged-template.yaml \
		--s3-bucket $(S3_BUCKET) \
		--stack-name personalize-retail-ingest-solution \
		--capabilities CAPABILITY_IAM \
		--region $(REGION) \
		--parameter-overrides $$(cat parameters.cfg)

describe:
	@echo "--API URL--"
	@aws cloudformation describe-stacks --stack-name personalize-retail-ingest-solution \
		--query 'Stacks[0].Outputs[?OutputKey==`ApiURL`].OutputValue' \
		--output text \
		--region $(REGION)
	@echo "--Interaction Stream Name--"
	@aws cloudformation describe-stacks --stack-name personalize-retail-ingest-solution \
		--query 'Stacks[0].Outputs[?OutputKey==`CustomerInteractionStreamName`].OutputValue' \
		--output text \
		--region $(REGION)
	@echo "--Raw Data Bucket--"
	@aws cloudformation describe-stacks --stack-name personalize-retail-ingest-solution \
		--query 'Stacks[0].Outputs[?OutputKey==`RawDataBucket`].OutputValue' \
		--output text \
		--region $(REGION)
clean:
	aws cloudformation delete-stack \
		--stack-name personalize-retail-ingest-solution \
		--region $(REGION)