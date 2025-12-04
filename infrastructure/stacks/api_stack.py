from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    CfnOutput,
    BundlingOptions,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_iam as iam,
)
from constructs import Construct
import os


class ApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # DynamoDB Table for Events
        events_table = dynamodb.Table(
            self, "EventsTable",
            table_name="Events",
            partition_key=dynamodb.Attribute(
                name="eventId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,  # For dev/test only
        )
        
        # Lambda function for FastAPI with bundled dependencies
        api_lambda = lambda_.Function(
            self, "EventsApiLambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="main.handler",
            code=lambda_.Code.from_asset(
                "../backend",
                bundling=BundlingOptions(
                    image=lambda_.Runtime.PYTHON_3_11.bundling_image,
                    command=[
                        "bash", "-c",
                        "pip install -r requirements.txt -t /asset-output --platform manylinux2014_x86_64 --only-binary=:all: --upgrade || "
                        "pip install -r requirements.txt -t /asset-output && "
                        "cp -au . /asset-output"
                    ],
                )
            ),
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={
                "EVENTS_TABLE_NAME": events_table.table_name,
            }
        )
        
        # Grant Lambda permissions to access DynamoDB
        events_table.grant_read_write_data(api_lambda)
        
        # API Gateway REST API
        api = apigateway.LambdaRestApi(
            self, "EventsApi",
            handler=api_lambda,
            proxy=True,
            rest_api_name="Events API",
            description="FastAPI Events CRUD API",
            deploy_options=apigateway.StageOptions(
                stage_name="prod",
                throttling_rate_limit=100,
                throttling_burst_limit=200,
            ),
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["*"],
                allow_credentials=True,
            )
        )
        
        # Outputs
        CfnOutput(
            self, "ApiUrl",
            value=api.url,
            description="API Gateway endpoint URL",
            export_name="EventsApiUrl"
        )
        
        CfnOutput(
            self, "TableName",
            value=events_table.table_name,
            description="DynamoDB table name",
            export_name="EventsTableName"
        )
