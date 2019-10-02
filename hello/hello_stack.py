from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elbv2,
)


class MyStack(core.Stack):

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

        # security_group.add_ingress_rule(
        #     ec2.Peer.any_ipv4(), 
        #     ec2.Port.all_tcp(),
        # )

        app_target_group = elbv2.ApplicationTargetGroup(
            self, "AppTargetGroup",
            port=80,
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
            port=80,
            default_target_groups=[app_target_group],
        )

        #elastic_loadbalancer.add_listener(app_listener)

        task_definition = ecs.TaskDefinition(
            self, "TaskDefenition",
            compatibility=ecs.Compatibility.FARGATE,
            cpu="256",
            memory_mib="512",
        )

        container_defenition = ecs.ContainerDefinition(
            self, "ContainerDefenition",
            image=ecs.ContainerImage.from_registry("vulnerables/web-dvwa"),
            task_definition=task_definition,
        )
        
        container_defenition.add_port_mappings(
            ecs.PortMapping(
                container_port=80,
            )
        )

        #container_defenition.container_port(80)

        # task_definition.add_container(
        #     "DemoContainer",
        #     image=ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample"),
        # )

        fargate_service = ecs.FargateService(
            self, "FargateService",
            task_definition=task_definition,
            cluster=cluster,
            security_group=security_group,
        )
        
        fargate_service.attach_to_application_target_group(
            target_group=app_target_group,
        )