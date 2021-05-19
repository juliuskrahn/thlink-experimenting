The thlink backend embraces a microservice architecture and is built on AWS.

## Structure and Deployment with the AWS CDK (python)
- Each microservice defines its CDK stack in '{name}/app/stack.py' (the working directory during deployment is '/backend')
- 'app.py' contains the CDK app and imports and initializes each microservice stack
- All requirements for the deployment process are listed in 'app_requirements.txt' (requirements listed in '{name}/requirements.txt' are microservice internal)
