import * as aws from "@pulumi/aws";
import * as awsx from "@pulumi/awsx";
import * as pulumi from "@pulumi/pulumi";

// Create an ECR repository
const repo = new awsx.ecr.Repository("my-repo");

// Build and push the Docker image to ECR
const image = new awsx.ecr.Image("my-app-image", {
  repositoryUrl: repo.url,
  context: "./",
  platform: "linux/amd64", // Build the image for the Linux x86-64 platform
});

// Get the latest Amazon Linux 2 AMI
const ami = aws.ec2.getAmi({
  filters: [
    { name: "name", values: ["amzn2-ami-hvm-2.0.*-x86_64-gp2"] },
  ],
  owners: ["amazon"],
  mostRecent: true,
});

// Create an IAM Role for EC2 to access ECR
const role = new aws.iam.Role("ec2InstanceRole", {
  assumeRolePolicy: aws.iam.assumeRolePolicyForPrincipal({ Service: "ec2.amazonaws.com" }),
});

// Attach the AmazonEC2ContainerRegistryReadOnly policy to the role
const rolePolicyAttachment = new aws.iam.RolePolicyAttachment("ec2ECRPolicy", {
  role: role,
  policyArn: "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
});

// Create an Instance Profile for the EC2 instance
const instanceProfile = new aws.iam.InstanceProfile("instanceProfile", {
  role: role,
});

// Create a VPC
const vpc = new aws.ec2.Vpc("my-vpc", {
  cidrBlock: "10.0.0.0/16",
  enableDnsHostnames: true,
  enableDnsSupport: true,
});

// Create an Internet Gateway
const internetGateway = new aws.ec2.InternetGateway("my-igw", {
  vpcId: vpc.id,
});

// Create a public subnet
const publicSubnet = new aws.ec2.Subnet("public-subnet", {
  vpcId: vpc.id,
  cidrBlock: "10.0.1.0/24",
  mapPublicIpOnLaunch: true,
});

// Create a route table
const routeTable = new aws.ec2.RouteTable("my-route-table", {
  vpcId: vpc.id,
  routes: [
    {
      cidrBlock: "0.0.0.0/0",
      gatewayId: internetGateway.id,
    },
  ],
});

// Associate the route table with the public subnet
const routeTableAssociation = new aws.ec2.RouteTableAssociation("route-table-association", {
  subnetId: publicSubnet.id,
  routeTableId: routeTable.id,
});

// Create a security group
const securityGroup = new aws.ec2.SecurityGroup("web-secgrp", {
  description: "Enable HTTP access",
  vpcId: vpc.id,
  ingress: [
    { protocol: "tcp", fromPort: 80, toPort: 80, cidrBlocks: ["0.0.0.0/0"] },
    { protocol: "tcp", fromPort: 22, toPort: 22, cidrBlocks: ["0.0.0.0/0"] },
  ],
  egress: [
    { protocol: "-1", fromPort: 0, toPort: 0, cidrBlocks: ["0.0.0.0/0"] },
  ],
});

// Create an EC2 instance that runs the Docker container on free tier x84-64 platform
const server = new aws.ec2.Instance("web-server", {
  instanceType: "t2.micro",
  vpcSecurityGroupIds: [securityGroup.id],
  ami: ami.then(ami => ami.id),
  subnetId: publicSubnet.id,
  iamInstanceProfile: instanceProfile.id,
  userData: pulumi.interpolate`#!/bin/bash
    yum update -y
    yum install -y docker
    systemctl start docker
    systemctl enable docker
    $(aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${repo.url})
    docker run -d --restart unless-stopped -p 80:8000 ${image.imageUri}
  `,
  tags: {
    Name: "web-server",
  },
});

// Export the public IP and public DNS name of the EC2 instance
export const publicIp = server.publicIp;
export const publicDns = server.publicDns;

// Export the ECR repository URL and the Docker image URI
export const repositoryUrl = repo.url;
export const imageUri = image.imageUri;
