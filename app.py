#!/usr/bin/env python3

from aws_cdk import core

from fargate.fargate_stack import FargateApp


app = core.App()
FargateApp(app, "fargate-cdk-app-1", env={'region': 'us-east-2'})

app.synth()