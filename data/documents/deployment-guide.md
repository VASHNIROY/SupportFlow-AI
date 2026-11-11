# Application Deployment Guide

## Deployment requirements

Before deploying an application, the developer must:

- Ensure all automated tests pass
- Obtain code review approval
- Confirm that the build pipeline is successful
- Verify that required environment variables are configured

## Production deployment

Production deployments must be performed through the approved CI/CD pipeline.

Direct manual changes to production servers are not allowed.

## Rollback

If a deployment causes an incident, the team should roll back to the last known stable version and notify the incident commander.