# Simple Pulumi Deployment Instructions

This README provides quick instructions for deploying and updating your FastAPI application using Pulumi and pnpm.

## Prerequisites

- [pnpm](https://pnpm.io/installation) installed
- [Pulumi CLI](https://www.pulumi.com/docs/get-started/install/) installed
- AWS credentials configured

## Deployment Steps

1. **Install dependencies**

   Run the following command to install the required dependencies:

   ```bash
   pnpm install
   ```

2. **Deploy the stack**

   To deploy your application, run:

   ```bash
   pulumi up
   ```

   Review the proposed changes and confirm by typing `yes` when prompted.

3. **Access your application**

   After deployment, Pulumi will output the public IP or DNS of your EC2 instance. You can access your application via **HTTP** using this address.

## Updating the Application

To update your application:

1. Make your desired changes to the code or configuration.

2. Destroy the existing resources:

   ```bash
   pulumi destroy
   ```

   Confirm the destruction when prompted.

3. Redeploy the updated stack:

   ```bash
   pulumi up
   ```

   Review and confirm the changes.

## Note

- This deployment uses HTTP. For production environments, consider setting up HTTPS for secure communication.
- Remember to destroy your resources when they're no longer needed to avoid unnecessary charges.
