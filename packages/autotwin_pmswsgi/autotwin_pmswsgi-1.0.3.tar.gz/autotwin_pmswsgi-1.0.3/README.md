[![PyPI - License](https://img.shields.io/pypi/l/autotwin_pmswsgi)](https://github.com/AutotwinEU/proc-mining-serv/blob/main/LICENSE)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/autotwin_pmswsgi)](https://www.python.org/downloads/)
[![PyPI - Version](https://img.shields.io/pypi/v/autotwin_pmswsgi)](https://pypi.org/project/autotwin_pmswsgi/)

# Processing Mining Service (PMS) WSGI for Auto-Twin

The processing mining service (PMS) WSGI implements a RESTful API that invokes
different system discovery modules to automatically create, update and delete
graph models, Petri nets and automata in a system knowledge graph (SKG).
Besides, the RESTful API enables the execution of a battery model for estimating
the state of charge (SoC) across a time period.

## Installation
To facilitate installation, the PMS WSGI is released as a Python module,
`autotwin_pmswsgi`, in the PyPI repository. `autotwin_pmswsgi` implicitly
depends on `pygraphviz`. This dependency however cannot be resolved
automatically by `pip`. As a preparation, you need to install `pygraphviz`
manually, following instructions provided
[here](https://pygraphviz.github.io/documentation/stable/install.html).
Whenever `pygraphviz` is available, the latest version of `autotwin_pmswsgi`
can be easily installed with `pip`.

    pip install autotwin_pmswsgi

## Deployment
The PMS WSGI is almost ready to be deployed for production use once
`autotwin_pmswsgi` is installed successfully. Four environment variables are
additionally required to specify the [Neo4j](https://github.com/neo4j/neo4j)
instance that holds the SKG of the system under consideration.

| Name             | Description                                              |
|------------------|----------------------------------------------------------|
| `NEO4J_URI`      | URI of the Neo4j instance, e.g. `neo4j://localhost:7687` |
| `NEO4J_USERNAME` | Username for the Neo4j instance, e.g. `neo4j`            |
| `NEO4J_PASSWORD` | Password for the Neo4j instance, e.g. `12345678`         |
| `NEO4J_DATABASE` | Database where the SKG is stored, e.g. `neo4j`           |

After setting the above environment variables, you can start up the PMS WSGI on
a [Waitress](https://github.com/Pylons/waitress) server by executing

    waitress-serve autotwin_pmswsgi:wsgi

## Containerization
To enable containerization, the PMS WSGI is also released as a Docker image,
`ghcr.io/autotwineu/proc-mining-serv`, in the GHCR registry. Suppose that a
Docker engine is running on your machine. Deploying the PMS WSGI on a Docker
container named `proc-mining-serv` can be done via a single command.

Windows:

    docker run --detach ^
    --env NEO4J_URI=<NEO4J_URI> ^
    --env NEO4J_USERNAME=<NEO4J_USERNAME> ^
    --env NEO4J_PASSWORD=<NEO4J_PASSWORD> ^
    --env NEO4J_DATABASE=<NEO4J_DATABASE> ^
    --volume <CLUSTERING_DIRECTORY>:/proc-mining-serv/clusterings ^
    --volume <BATTERY_MODEL_DIRECTORY>:/proc-mining-serv/battery-models ^
    --name proc-mining-serv ^
    --pull always ghcr.io/autotwineu/proc-mining-serv

Linux:

    docker run --detach \
    --env NEO4J_URI=<NEO4J_URI> \
    --env NEO4J_USERNAME=<NEO4J_USERNAME> \
    --env NEO4J_PASSWORD=<NEO4J_PASSWORD> \
    --env NEO4J_DATABASE=<NEO4J_DATABASE> \
    --volume <CLUSTERING_DIRECTORY>:/proc-mining-serv/clusterings \
    --volume <BATTERY_MODEL_DIRECTORY>:/proc-mining-serv/battery-models \
    --name proc-mining-serv \
    --pull always ghcr.io/autotwineu/proc-mining-serv

`<NEO4J_URI>`, `<NEO4J_USERNAME>`, `<NEO4J_PASSWORD>` and `<NEO4J_DATABASE>`
correspond to the values of the four environment variables required by the PMS
WSGI (see [Deployment](#deployment)). `<CLUSTERING_DIRECTORY>` and
`<BATTERY_MODEL_DIRECTORY>` are host directories where clustering and battery
model files are located.

## RESTful API
The PMS WSGI listens HTTP requests on port `8080` and is accessible through a
RESTful API that exposes the following endpoints for different types of models.
The content types of the request and response for each API endpoint are either
`application/json` or `application/octet-stream`.

--------------------------------------------------------------------------------

### API Endpoints for Graph Models

<details>
    <summary>
        <code>POST</code>
        <code><b>/graph-model</b></code>
        <code>(create a graph model in the SKG)</code>
    </summary>
    <br/>

**Parameters**
> None

**Body**
> Content: `application/json`
>
> | Key                        | Type                    | Default                                   | Description                                                       |
> |----------------------------|-------------------------|-------------------------------------------|-------------------------------------------------------------------|
> | `name`                     | `string`                | `"System"`                                | Name of the system to be discovered                               |
> | `version`                  | `string`                | `""`                                      | Version of the system to be discovered                            |
> | `data:clustering:path`     | `string`                | `""`<sup id="gm-mk-1">[*](#gm-fn-1)</sup> | Name of the clustering file to be used                            |
> | `data:clustering:default`  | `string`                | `""`<sup id="gm-mk-2">[†](#gm-fn-2)</sup> | Cluster of parts absent from the clustering file                  |
> | `data:filters:interval`    | `array[number\|string]` | `[0.0, 0.0]`                              | Interval during which events are selected                         |
> | `data:filters:station`     | `array[string]`         | `[]`<sup id="gm-mk-3">[‡](#gm-fn-3)</sup> | Set of stations at which events are selected                      |
> | `data:filters:family`      | `array[string]`         | `[]`<sup>[‡](#gm-fn-3)</sup>              | Set of families for which events are selected                     |
> | `data:filters:type`        | `array[string]`         | `[]`<sup>[‡](#gm-fn-3)</sup>              | Set of types for which events are selected                        |
> | `data:usage`               | `number`                | `0.5`                                     | Minimum data usage to be ensured                                  |
> | `model:time_unit`          | `string`                | `"s"`                                     | Unified time unit of algorithm and model parameters               |
> | `model:operation:io_ratio` | `number`                | `1.5`                                     | Minimum ratio of input to output for an ATTACH/COMPOSE operation  |
> | `model:operation:co_ratio` | `number`                | `0.5`                                     | Minimum ratio of cross to output for an ATTACH/ORDINARY operation |
> | `model:operation:oi_ratio` | `number`                | `1.5`                                     | Minimum ratio of output to input for a DETACH/DECOMPOSE operation |
> | `model:operation:ci_ratio` | `number`                | `0.5`                                     | Minimum ratio of cross to input for a DETACH/ORDINARY operation   |
> | `model:formula:ratio`      | `number`                | `0.0`                                     | Minimum ratio of a formula to the primary one                     |
> | `model:delays:seize`       | `number`                | `0.0`                                     | Maximum delay in seizing a queued part                            |
> | `model:delays:release`     | `number`                | `0.0`                                     | Maximum delay in releasing a blocked part                         |
> | `model:cdf:replace_pts`    | `boolean`               | `false`                                   | Replace or drop invalid samples in a processing time CDF          |
> | `model:cdf:replace_tts`    | `boolean`               | `false`                                   | Replace or drop invalid samples in a transfer time CDF            |
> | `model:cdf:points`         | `number`                | `100`                                     | Maximum number of points in a CDF                                 |
>
> <sup id="gm-fn-1">* An empty string disables the import of clustering information. [↩](#gm-mk-1)</sup><br><sup id="gm-fn-2">† An empty string ignores parts not belonging to any clusters. [↩](#gm-mk-2)</sup><br><sup id="gm-fn-3">‡ An empty array refers to the universe of stations/families/types. [↩](#gm-mk-3)</sup>

> Example:
> ```json
> {
>     "name": "Pizza Line",
>     "version": "V4",
>     "data": {
>         "filters": {
>             "interval": [
>                 0,
>                 500000000
>             ],
>             "station": [],
>             "family": [],
>             "type": []
>         },
>         "usage": 0.5
>     },
>     "model": {
>         "time_unit": "ms",
>         "operation": {
>             "io_ratio": 1.5,
>             "co_ratio": 0.5,
>             "oi_ratio": 1.5,
>             "ci_ratio": 0.5
>         },
>         "formula": {
>             "ratio": 0.06
>         },
>         "delays": {
>             "seize": 30000,
>             "release": 0
>         },
>         "cdf": {
>             "replace_pts": false,
>             "replace_tts": false,
>             "points": 100
>         }
>     }
> }
> ```

**Response**
> Code: `201`

> Content: `application/json`
>
> | Key        | Type     | Description                     |
> |------------|----------|---------------------------------|
> | `model_id` | `string` | ID of the generated graph model |

> Example:
> ```json
> {
>     "model_id": "4:31f61bae-dad6-4cda-bb63-d4700847dea5:620887"
> }
> ```

</details>

--------------------------------------------------------------------------------

### API Endpoints for Petri Nets

<details>
    <summary>
        <code>POST</code>
        <code><b>/petri-net</b></code>
        <code>(create a Petri net in the SKG)</code>
    </summary>
    <br/>

**Parameters**
> None

**Body**
> Content: `application/json`
>
> | Key                        | Type                    | Default                                   | Description                                                       |
> |----------------------------|-------------------------|-------------------------------------------|-------------------------------------------------------------------|
> | `name`                     | `string`                | `"System"`                                | Name of the system to be discovered                               |
> | `version`                  | `string`                | `""`                                      | Version of the system to be discovered                            |
> | `data:filters:interval`    | `array[number\|string]` | `[0.0, 0.0]`                              | Interval during which events are selected                         |
> | `data:filters:station`     | `array[string]`         | `[]`<sup id="pn-mk-1">[*](#pn-fn-1)</sup> | Set of stations at which events are selected                      |
> | `data:filters:family`      | `array[string]`         | `[]`<sup>[*](#pn-fn-1)</sup>              | Set of families for which events are selected                     |
> | `data:filters:type`        | `array[string]`         | `[]`<sup>[*](#pn-fn-1)</sup>              | Set of types for which events are selected                        |
> | `data:usage`               | `number`                | `0.5`                                     | Minimum data usage to be ensured                                  |
> | `model:operation:io_ratio` | `number`                | `1.5`                                     | Minimum ratio of input to output for an ATTACH/COMPOSE operation  |
> | `model:operation:co_ratio` | `number`                | `0.5`                                     | Minimum ratio of cross to output for an ATTACH/ORDINARY operation |
> | `model:operation:oi_ratio` | `number`                | `1.5`                                     | Minimum ratio of output to input for a DETACH/DECOMPOSE operation |
> | `model:operation:ci_ratio` | `number`                | `0.5`                                     | Minimum ratio of cross to input for a DETACH/ORDINARY operation   |
> | `model:formula:ratio`      | `number`                | `0.0`                                     | Minimum ratio of a formula to the primary one                     |
>
> <sup id="pn-fn-1">* An empty array refers to the universe of stations/families/types. [↩](#pn-mk-1)</sup>

> Example:
> ```json
> {
>     "name": "Pizza Line",
>     "version": "V4",
>     "data": {
>         "filters": {
>             "interval": [
>                 0,
>                 500000000
>             ],
>             "station": [],
>             "family": [],
>             "type": []
>         },
>         "usage": 0.5
>     },
>     "model": {
>         "operation": {
>             "io_ratio": 1.5,
>             "co_ratio": 0.5,
>             "oi_ratio": 1.5,
>             "ci_ratio": 0.5
>         },
>         "formula": {
>             "ratio": 0.06
>         }
>     }
> }
> ```

**Response**
> Code: `201`

> Content: `application/json`
>
> | Key        | Type     | Description                   |
> |------------|----------|-------------------------------|
> | `model_id` | `string` | ID of the generated Petri net |

> Example:
> ```json
> {
>     "model_id": "4:31f61bae-dad6-4cda-bb63-d4700847dea5:620887"
> }
> ```

</details>

--------------------------------------------------------------------------------

### API Endpoints for Automata

<details>
    <summary>
        <code>POST</code>
        <code><b>/automaton</b></code>
        <code>(create an automaton in the SKG)</code>
    </summary>
    <br/>

**Parameters**
> None

**Body**
> Content: `application/json`
>
> | Key                     | Type                    | Default      | Description                               |
> |-------------------------|-------------------------|--------------|-------------------------------------------|
> | `name`                  | `string`                | `"System"`   | Name of the system to be discovered       |
> | `version`               | `string`                | `""`         | Version of the system to be discovered    |
> | `data:filters:interval` | `array[number\|string]` | `[0.0, 0.0]` | Interval during which events are selected |
> | `model:pov`             | `string`                | `"item"`     | Point of view to be focused on            |

> Example:
> ```json
> {
>     "name": "Pizza Line",
>     "version": "V4",
>     "data": {
>         "filters": {
>             "interval": [
>                 0,
>                 500000000
>             ]
>         }
>     },
>     "model": {
>         "pov": "item"
>     }
> }
> ```

**Response**
> Code: `201`

> Content: `application/json`
>
> | Key        | Type     | Description                   |
> |------------|----------|-------------------------------|
> | `model_id` | `string` | ID of the generated automaton |

> Example:
> ```json
> {
>     "model_id": "4:31f61bae-dad6-4cda-bb63-d4700847dea5:620887"
> }
> ```

</details>

--------------------------------------------------------------------------------

### API Endpoints for Battery Models

<details>
    <summary>
        <code>GET</code>
        <code><b>/api/v1/projects/ids</b></code>
        <code>(get the project IDs of battery models)</code>
    </summary>
    <br/>

**Parameters**
> None

**Body**
> None

**Response**
> Code: `200`

> Content: `application/json`
>
> | Key              | Type     | Description                             |
> |------------------|----------|-----------------------------------------|
> | `i:projectUUID`  | `string` | Project ID of the `i`-th battery model  |
> | `i:scenarioUUID` | `string` | Scenario ID of the `i`-th battery model |

> Example:
> ```json
> [
>     {
>         "projectUUID": "31f61bae-dad6-4cda-bb63-d4700847dea5",
>         "scenarioUUID": "31f61bae-dad6-4cda-bb63-d4700847dea5"
>     }
> ]
> ```

</details>

<details>
    <summary>
        <code>GET</code>
        <code><b>/api/v1/scenario-executions/ids</b></code>
        <code>(get the execution IDs of battery models)</code>
    </summary>
    <br/>

**Parameters**
> None

**Body**
> None

**Response**
> Code: `200`

> Content: `application/json`
>
> | Key      | Type     | Description                              |
> |----------|----------|------------------------------------------|
> | `i:uuid` | `string` | Execution ID of the `i`-th battery model |

> Example:
> ```json
> [
>     {
>         "uuid": "31f61bae-dad6-4cda-bb63-d4700847dea5"
>     }
> ]
> ```

</details>

<details>
    <summary>
        <code>GET</code>
        <code><b>/api/v1/scenario-executions/{execution_id}/parameters</b></code>
        <code>(get the parameters of a battery model)</code>
    </summary>
    <br/>

**Parameters**
> | Name           | Type     | Description                       |
> |----------------|----------|-----------------------------------|
> | `execution_id` | `string` | Execution ID of the battery model |

**Body**
> None

**Response**
> Code: `200`

> Content: `application/json`
>
> | Key | Type     | Description                           |
> |-----|----------|---------------------------------------|
> | `i` | `object` | `i`-th parameter of the battery model |

> Example:
> ```json
> []
> ```

</details>

<details>
    <summary>
        <code>GET</code>
        <code><b>/api/v1/scenario-executions/{execution_id}/json</b></code>
        <code>(get estimations by a battery model)</code>
    </summary>
    <br/>

**Parameters**
> | Name           | Type     | Description                       |
> |----------------|----------|-----------------------------------|
> | `execution_id` | `string` | Execution ID of the battery model |

**Body**
> Content: `application/json`
>
> | Key                     | Type                    | Default      | Description                            |
> |-------------------------|-------------------------|--------------|----------------------------------------|
> | `interval`              | `array[number]`         | `[0, 0]`     | Interval during which SoC is estimated |

> Example:
> ```json
> {
>     "interval": [
>         1730419200000,
>         1732924800000
>     ]
> }
> ```

**Response**
> Code: `200`

> Content: `application/json`
>
> | Key                  | Type     | Description                          |
> |----------------------|----------|--------------------------------------|
> | `component`          | `string` | ID of the current component          |
> | `data:i:name`        | `string` | Name of the `i`-th data entry        |
> | `data:i:description` | `string` | Description of the `i`-th data entry |
> | `data:i:type`        | `string` | Type of the `i`-th data entry        |
> | `data:i:payload`     | `string` | Payload of the `i`-th data entry     |

> Example:
> ```json
> {
>     "component": "C12",
>     "data": [
>         {
>             "name": "Battery DT SoC",
>             "description": "Battery DT SoC results",
>             "type": "chart",
>             "payload": "[{\"time\": 1730419200000, \"value\": 50.0}]"
>         },
>         {
>             "name": "Battery DT Voltage",
>             "description": "Battery DT Voltage results",
>             "type": "chart",
>             "payload": "[{\"time\": 1730419200000, \"value\": 800.0}]"
>         }
>     ]
> }
> ```

</details>

<details>
    <summary>
        <code>GET</code>
        <code><b>/api/v1/scenario-executions/{execution_id}/out</b></code>
        <code>(get estimations by a battery model)</code>
    </summary>
    <br/>

**Parameters**
> | Name           | Type     | Description                       |
> |----------------|----------|-----------------------------------|
> | `execution_id` | `string` | Execution ID of the battery model |

**Body**
> Content: `application/json`
>
> | Key                     | Type                    | Default      | Description                            |
> |-------------------------|-------------------------|--------------|----------------------------------------|
> | `interval`              | `array[number]`         | `[0, 0]`     | Interval during which SoC is estimated |

> Example:
> ```json
> {
>     "interval": [
>         1730419200000,
>         1732924800000
>     ]
> }
> ```

**Response**
> Code: `200`

> Content: `application/octet-stream`, `attachment; filename=out.zip`

</details>

--------------------------------------------------------------------------------
