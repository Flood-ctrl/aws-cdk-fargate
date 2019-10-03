from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_logs as logs,
    aws_elasticloadbalancingv2 as elbv2,
)

http_port = 80
task_def_cpu = "256"
task_def_memory_mb = "512"

class FargateApp(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(
            self, "MyVpc",
            max_azs=2
        )

        cluster = ecs.Cluster(
            self, "EC2Cluster",
            vpc=vpc
        )

        security_group = ec2.SecurityGroup(
            self, "SecurityGroup",
            vpc=vpc,
            allow_all_outbound=True,
        )

        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.all_tcp(),
            description="Allow all traffic"
        )

        app_target_group = elbv2.ApplicationTargetGroup(
            self, "AppTargetGroup",
            port=http_port,
            vpc=vpc,
            target_type=elbv2.TargetType.IP,
        )

        elastic_loadbalancer = elbv2.ApplicationLoadBalancer(
            self, "ALB",
            vpc=vpc,
            internet_facing=True,
            security_group=security_group,
        )

        app_listener = elbv2.ApplicationListener(
            self, "AppListener",
            load_balancer=elastic_loadbalancer,
            port=http_port,
            default_target_groups=[app_target_group],
        )

        task_definition = ecs.TaskDefinition(
            self, "TaskDefenition",
            compatibility=ecs.Compatibility.FARGATE,
            cpu=task_def_cpu,
            memory_mib=task_def_memory_mb,
        )

        container_defenition = ecs.ContainerDefinition(
            self, "ContainerDefenition",
            image=ecs.ContainerImage.from_registry("vulnerables/web-dvwa"),
            task_definition=task_definition,
            logging=ecs.AwsLogDriver(
                stream_prefix="DemoContainerLogs",
                log_retention=logs.RetentionDays.ONE_DAY,
            ),
        )

        container_defenition.add_port_mappings(
            ecs.PortMapping(
                container_port=http_port,
            )
        )

        fargate_service = ecs.FargateService(
            self, "FargateService",
            task_definition=task_definition,
            cluster=cluster,
            security_group=security_group,
        )

        fargate_service.attach_to_application_target_group(
            target_group=app_target_group,
        )

        core.CfnOutput(
        self, "LoadBalancerDNS",
        value=elastic_loadbalancer.load_balancer_dns_name
        )
