# Communication tests
This directory contains a tool for testing SiLA 2 communication.

## How to test your implementation
### Client
For testing your client implementation

- Create a SiLA Client application which connects to a SiLA Server and preforms [these requests](client-instructions.md).
- Start the test server (see below)
- Execute your client application
- Shutdown stop the test server

The test server tests if all expected requests were made.

### Server
For testing your server implementation

- Create a SiLA Server application which implements these features:
  - [SiLAService](https://gitlab.com/SiLA2/sila_base/-/blob/master/feature_definitions/org/silastandard/core/SiLAService-v1_0.sila.xml)
  - [AnyTypeTest](https://gitlab.com/SiLA2/sila_base/-/blob/master/feature_definitions/org/silastandard/test/AnyTypeTest-v1_0.sila.xml)
  - [AuthenticationService](https://gitlab.com/SiLA2/sila_base/-/blob/master/feature_definitions/org/silastandard/core/AuthenticationService-v1_0.sila.xml)
  - [AuthenticationTest](https://gitlab.com/SiLA2/sila_base/-/blob/master/feature_definitions/org/silastandard/test/AuthenticationTest-v1_0.sila.xml)
  - [AuthorizationService](https://gitlab.com/SiLA2/sila_base/-/blob/master/feature_definitions/org/silastandard/core/AuthorizationService-v1_0.sila.xml)
  - [BasicDataTypesTest](https://gitlab.com/SiLA2/sila_base/-/blob/master/feature_definitions/org/silastandard/test/BasicDataTypesTest-v1_0.sila.xml)
  - [BinaryTransferTest](https://gitlab.com/SiLA2/sila_base/-/blob/master/feature_definitions/org/silastandard/test/BinaryTransferTest-v1_0.sila.xml)
  - [ErrorHandlingTest](https://gitlab.com/SiLA2/sila_base/-/blob/master/feature_definitions/org/silastandard/test/ErrorHandlingTest-v1_0.sila.xml)
  - [ListDataTypeTest](https://gitlab.com/SiLA2/sila_base/-/blob/master/feature_definitions/org/silastandard/test/ListDataTypeTest-v1_0.sila.xml)
  - [MetadataConsumerTest](https://gitlab.com/SiLA2/sila_base/-/blob/master/feature_definitions/org/silastandard/test/MetadataConsumerTest-v1_0.sila.xml)
  - [MetadataProviderTest](https://gitlab.com/SiLA2/sila_base/-/blob/master/feature_definitions/org/silastandard/test/MetadataProviderTest-v1_0.sila.xml)
  - [MultiClientTest](https://gitlab.com/SiLA2/sila_base/-/blob/master/feature_definitions/org/silastandard/test/MultiClientTest-v1_0.sila.xml)
  - [ObservableCommandTest](https://gitlab.com/SiLA2/sila_base/-/blob/master/feature_definitions/org/silastandard/test/ObservableCommandTest-v1_0.sila.xml)
  - [ObservablePropertyTest](https://gitlab.com/SiLA2/sila_base/-/blob/master/feature_definitions/org/silastandard/test/ObservablePropertyTest-v1_0.sila.xml)
  - [StructureDataTypeTest](https://gitlab.com/SiLA2/sila_base/-/blob/master/feature_definitions/org/silastandard/test/StructureDataTypeTest-v1_0.sila.xml)
  - [UnobservableCommandTest](https://gitlab.com/SiLA2/sila_base/-/blob/master/feature_definitions/org/silastandard/test/UnobservableCommandTest-v1_0.sila.xml)
  - [UnobservablePropertyTest](https://gitlab.com/SiLA2/sila_base/-/blob/master/feature_definitions/org/silastandard/test/UnobservablePropertyTest-v1_0.sila.xml)
- Start your server application
- Run the test client application (see below)

The test client performs gRPC requests and tests if your server sent the expected responses.

## Usage
### Installation
Run the following commands to download and install the tool (requires Python >= 3.9):
```shell
pip install sila2-interop-communication-tester
```

### Run the test client
1. Start your server
2. Run `python -m sila2_interop_communication_tester.test_client [options]`
    - This program sends requests to your server and checks if the responses were correct
    - Afterwards, it prints a report and optionally exports it in a standardized format
    - Options:
      - `--server-address`: The address of your server (default: `127.0.0.1:50052`)
      - `--roots-cert-file FILE`: The PEM-encoded roots certificate file required to connect to your server (default: no encryption)
      - `--report-file FILE`, `--testsuite-name NAME`: If set, a JUnit-like XML report file with the provided test suite name will be generated
      - `--html-file FILE`: If set, a HTML report will be generated
      - `--timeout NUM`: Set the per-test timeout (default: 30 seconds)
      - `--debug`: Increase the logging granularity
      - `test1 test2 test3 ...`: If set, only the specified tests or test sets will be executed. Examples:
        - Test directory: `test_error_handling`
        - Test file: `test_error_handling/test_observable_commands.py` (file)
        - Test: `test_error_handling/test_observable_commands.py::test_raise_defined_execution_error_observably_info_rejects_invalid_uuids`
3. (Stop your server)

### Run the test server
1. Run `python -m sila2_interop_communication_tester.test_server [options]`
   - This will host a SiLA Server which expects a defined set of requests from your client
   - The list of expected requests can be found [here](client-instructions.md)
   - Options:
     - `--server-address`: The address for hosting the server (default: `127.0.0.1:50052`)
     - `--cert-file FILE`, `--key-file FILE`: The PEM-encoded certificate and private key to be used by the server (default: no encryption)
     - `--report-file FILE`, `--testsuite-name NAME`: If set, a JUnit-like XML report file with the provided test suite name will be generated
     - `--html-file FILE`: If set, a HTML report will be generated
     - `test1 test2 test3 ...`: If set, only the specified tests or test sets will be executed. Examples:
       - Test file: `test_binary_transfer.py`
       - Test: `test_binary_transfer.py::test_small_binary_property_is_read`
2. Run your client
3. Interrupt the test server (Ctrl+C, `SIGINT`)
   - The program will shut down the SiLA Server and evaluate the requests it received
   - Afterwards, it prints a report and optionally exports it in a standardized format

## Development
### Setup
- Install Python >= 3.9
- Open a terminal, navigate to this directory (containing `pyproject.toml`)
- Run `pip install -e .[dev]` for an editable installation with all development dependencies

### Add/update feature code
- Run `python add-features.py FDL-FILES`, it will convert .sila.xml files to .proto and .py files and store them in the appropriate directories

### Extend the test client
- The tests are implemented in [test_client/test_/](sila2_interop_communication_tester/test_client)
- Test directories, files and functions have to have the prefix `test_`
- When adding a new feature, copy and adapt a `conftest.py` file from one of the existing test directories
  - It provides the stub code for the feature as a [pytest fixture](https://docs.pytest.org/en/6.2.x/fixture.html)
- Take a look at the existing features to get an impression on how to implement your own tests

### Extend the test server
- The SiLA Server is implemented in [test_server/server_implementation](sila2_interop_communication_tester/test_server/server_implementation)
- Tests are implemented in [test_server/tests](sila2_interop_communication_tester/test_server/tests)
- Test files and functions have to have the prefix `test_`
- If a test method is declared with the parameter `server_calls`, this parameter will contain a collection of all calls that the server received while it was running
  - Detail: That collection is injected via the [pytest fixtures](https://docs.pytest.org/en/6.2.x/fixture.html) mechanism
- That `server_calls` object is structured like this:
  - `server_calls[call_endpoint]` returns a list of all calls received for that endpoint, e.g. `"SiLAService.Get_ServerName"`
  - each entry in that list is a `ServerCall` object
  - `ServerCall` objects have multiple fields:
    - `timestamp`: a `datetime` object reporting the time when the call was received
    - `end_timestamp`: a `datetime` object reporting the time just before returning the response/error
    - `duration`: a `timedelta`, different between `timestamp` and `end_timestamp`
    - `request`: the received request message
    - `metadata`: a dictionary containing all received SiLA Client Metadata messages
      - use the message type as key: `metadata[MetadataProviderTest_pb2.Metadata_StringMetadata]`
    - `result`: either the response message or a `GrpcStatus` object
      - `GrpcStatus` objects have two fields: the `code` (`grpc.StatusCode`) and `details` (the details string)
    - `successful`: `True` if the call ended with a response message, `False` if it ended with an error

## Integration in Linux-based CI pipelines
**Install Python**
In Debian-based Docker images, Python and Pip can be installed with `apt install -y python3-pip python3-is-python`.
Alpine images are not recommended, since some dependencies might be incompatible with musl libc.

**Install tool**
Run the following commands to download and install the tool:
```shell
pip install sila2-interop-communication-tester
```

**Run tool**
Executing server and client processes in parallel works as follows:
```shell
# start server process, redirect all output to a file `server.log`, detach the process, store its process ID in `server_pid`
start-server > server.log 2>&1 & server_pid=$!
# wait for server startup (adjust time as suitable)
sleep 10
# run client
run-client
# terminate server process (`-INT` is Ctrl+C, `-TERM` is default behavior)
kill -INT $server_pid
```

## How to find what caused a reported issue
- The test server logs all gRPC interactions
  - Be careful with the timing: The log messages are generated after an RPC finished. This can lead to ordering issues. The message itself contains the start and end timestamp for the RPC.
- Both test programs print the following:
  - progress, e.g. `test_XYZ ..FF.` (`.` is a successful test, `F` a failure)
  - detailed failure reports in plain text (not very well structured if you are not familiar with the testing and Python gRPC framework)
  - list of all test results, e.g. `PASSED test_XYZ` or `FAILED test_ABC`, including the final error message (sometimes useful, usually not detailed enough)
  - summary: `X failed, Y passed in Zs`
- The HTML report (`--html-file FILE`) is probably the best resource for finding the problem causing a test failure
  - it provides the same output as the printed error details, but in a more consumable way
