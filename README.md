# hai-proxy

Docker image with a Flask web app to provide a crude REST API for [HAI Omni library](https://github.com/ylukin/hai-omni-communication-library). This Docker image currently only exposes the light and zone units. There is no authentication in this API, therefore this should be considered as experimental code at this time.\

For a reference client implementation, see the following [plugins](https://github.com/ylukin/hass/tree/master/custom_components/hai) for [Home Assistant](https://www.home-assistant.io).  

## Quick Start

Follow these instructions to build your image from scratch:

* Compile the [HAI Omni library](https://github.com/ylukin/hai-omni-communication-library) and copy the **hai** binary and hai.conf file to your project working directory
* Build the Docker image:

```bash
docker build -t hai-proxy .
```

* Create a **config** folder and copy your hai.conf to it
* Run the container (see included docker-compose.yml example):

```bash
docker-compose up -d
```
