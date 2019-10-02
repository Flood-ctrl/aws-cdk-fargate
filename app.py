#!/usr/bin/env python3

from aws_cdk import core

from hello.hello_stack import FargateApp


app = core.App()
FargateApp(app, "fargate-cdk-app-1", env={'region': 'us-east-2'})
FargateApp(app, "hello-cdk-2", env={'region': 'us-west-2'})

app.synth()