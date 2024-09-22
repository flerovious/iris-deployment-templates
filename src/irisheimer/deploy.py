import argparse

import pulumi
import pulumi_aws as aws


def deploy_infrastructure(repository_url: str):
    # Define the AMI to use
    ami = aws.ec2.get_ami(
        filters=[{'name': 'name', 'values': ['amzn2-ami-hvm-2.0.*-x86_64-gp2']}],
        owners=["self"],
        most_recent=True
    )

    # Create an IAM Role for EC2 to access required AWS services
    role = aws.iam.Role("ec2InstanceRole",
                        assume_role_policy=aws.iam.get_policy_document(
                            statements=[{
                                "actions": ["sts:AssumeRole"],
                                "effect": "Allow",
                                "principals": [{"type": "Service", "identifiers": ["ec2.amazonaws.com"]}]
                            }]
                        ).json
                        )

    # Create an Instance Profile for the EC2 instance
    instance_profile = aws.iam.InstanceProfile("instanceProfile", role=role.name)

    # Create a VPC
    vpc = aws.ec2.Vpc("my-vpc",
                      cidr_block="10.0.0.0/16",
                      enable_dns_hostnames=True,
                      enable_dns_support=True
                      )

    # Create an Internet Gateway
    internet_gateway = aws.ec2.InternetGateway("my-igw", vpc_id=vpc.id)

    # Create a public subnet
    public_subnet = aws.ec2.Subnet("public-subnet",
                                   vpc_id=vpc.id,
                                   cidr_block="10.0.1.0/24",
                                   map_public_ip_on_launch=True
                                   )

    # Create a route table
    route_table = aws.ec2.RouteTable("my-route-table",
                                     vpc_id=vpc.id,
                                     routes=[{
                                         'cidr_block': '0.0.0.0/0',
                                         'gateway_id': internet_gateway.id
                                     }]
                                     )

    # Associate the route table with the public subnet
    route_table_association = aws.ec2.RouteTableAssociation("route-table-association",
                                                            subnet_id=public_subnet.id,
                                                            route_table_id=route_table.id
                                                            )

    # Create a security group allowing SSH and HTTP access
    security_group = aws.ec2.SecurityGroup("iris-secgrp",
                                           vpc_id=vpc.id,
                                           description="Enable required ports for IRIS",
                                           ingress=[
                                               {'protocol': 'tcp', 'from_port': 80, 'to_port': 80,
                                                'cidr_blocks': ['0.0.0.0/0']},
                                               {'protocol': 'tcp', 'from_port': 22, 'to_port': 22,
                                                'cidr_blocks': ['0.0.0.0/0']},
                                               {'protocol': 'tcp', 'from_port': 1972, 'to_port': 1972,
                                                'cidr_blocks': ['0.0.0.0/0']},
                                               {'protocol': 'tcp', 'from_port': 5000, 'to_port': 5000,
                                                'cidr_blocks': ['0.0.0.0/0']},
                                               {'protocol': 'tcp', 'from_port': 53795, 'to_port': 53795,
                                                'cidr_blocks': ['0.0.0.0/0']},
                                               {'protocol': 'tcp', 'from_port': 53773, 'to_port': 53773,
                                                'cidr_blocks': ['0.0.0.0/0']}
                                           ],
                                           egress=[{'protocol': '-1', 'from_port': 0, 'to_port': 0,
                                                    'cidr_blocks': ['0.0.0.0/0']}]
                                           )

    # Create an EC2 instance
    server = aws.ec2.Instance("web-server",
                              instance_type="t2.micro",
                              vpc_security_group_ids=[security_group.id],
                              ami=ami.id,
                              subnet_id=public_subnet.id,
                              iam_instance_profile=instance_profile.name,
                              user_data=f'''#!/bin/bash
            yum update -y
            yum install -y git docker
            systemctl start docker
            systemctl enable docker
            curl -L "https://github.com/docker/compose/releases/download/v2.2.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            chmod +x /usr/local/bin/docker-compose
            git clone {repository_url} /app
            cd /app
            docker-compose up -d
        ''',
                              tags={
                                  'Name': 'web-server'
                              }
                              )

    pulumi.export("publicIp", server.public_ip)
    pulumi.export("publicDns", server.public_dns)


def main():
    parser = argparse.ArgumentParser(description='Deploy an EC2 instance with Docker Compose')
    parser.add_argument('--repository_url', required=True,
                        help='The Git repository URL containing the Docker Compose file')

    # Parse the arguments
    args = parser.parse_args()

    # Call the function with the repository URL
    deploy_infrastructure(args.repository_url)


if __name__ == "__main__":
    main()

