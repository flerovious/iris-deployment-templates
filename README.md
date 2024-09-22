# 🪻 Irisheimer

Irisheimer is a specialized CLI tool designed to streamline the deployment of InterSystems IRIS applications using Flask WSGI servers on AWS infrastructure. This project aims to provide a simple, one-command solution that sets up your application to be deployment-ready from the start.

## Purpose

The primary goal of Irisheimer is to eliminate the complex, time-consuming setup process typically associated with deploying InterSystems IRIS applications on AWS. By automating the generation of Pulumi configurations, Irisheimer allows developers to focus on their application logic rather than infrastructure setup.

## Features

- Generates a `main.py` file with Pulumi AWS configuration tailored for InterSystems IRIS and Flask
- Customizes the configuration with your provided Git repository URL
- Sets up EC2 instance, VPC, security groups, and other necessary AWS resources
- Configures the EC2 instance to run a Flask WSGI server optimized for InterSystems IRIS
- Ensures all necessary ports for IRIS are opened in the security group

## Prerequisites

- Python 3.7+
- pip
- [Poetry](https://python-poetry.org/docs/#installation) (for development)
- Basic familiarity with InterSystems IRIS and Flask

## Installation

Install Irisheimer directly from PyPI:

```bash
pip install irisheimer
```

For development:

```bash
git clone https://github.com/your-username/irisheimer.git
cd irisheimer
poetry install
```

## Usage

To set up your InterSystems IRIS Flask application for AWS deployment:

```bash
irisheimer <repository-url>
```

Replace `<repository-url>` with the URL of your Git repository containing the IRIS Flask application.

Example:

```bash
irisheimer https://github.com/your-username/your-iris-flask-app.git
```

This command generates a `main.py` file in your current working directory, containing the Pulumi configuration for deploying your IRIS Flask application on AWS.

## Generated Configuration

The `main.py` file includes Pulumi code to create AWS resources optimized for InterSystems IRIS:

- EC2 instance (sized appropriately for IRIS)
- VPC
- Internet Gateway
- Public Subnet
- Route Table
- Security Group (with IRIS-specific ports opened)

The EC2 instance's user data script:

1. Updates the system
2. Installs necessary dependencies (Git, Docker, Docker Compose)
3. Clones your specified repository
4. Sets up and starts your IRIS Flask application using Docker Compose

## Next Steps

After generating `main.py`:

1. Review and adjust the configuration if needed.
2. Ensure [Pulumi](https://www.pulumi.com/docs/get-started/install/) is installed and configured.
3. Run `pulumi up` in the directory containing `main.py` to deploy your infrastructure.
4. Once deployed, your IRIS Flask application will be running on AWS and accessible via the EC2 instance's public IP or DNS.

## Contributing

Contributions to improve Irisheimer are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)

## Support

If you encounter any issues or have questions about deploying InterSystems IRIS applications with Irisheimer, please open an issue on the GitHub repository.
