# Inventory Management Object Detection

## Install and run

To run the services use docker-compose:

```bash
$ docker-compose up --build -d
```

### Modules

We make use of [multi-stage docker builds](https://docs.docker.com/develop/develop-images/multistage-build/) so we can have into the same Dockerfile environments for testing and also for deploying our service.

### Setup Model

Once you have your final model, copy your .pt weights file inside model/models/ folder. Make sure to edit the model/settingspy accordingly.