# HOPX VM Agent - OpenAPI Specification

## 📄 OpenAPI Spec File

**Location**: `openapi.yaml`  
**Version**: 3.0.3  
**Agent Version**: 3.1.1

## 🎯 What's Included

### Complete API Documentation

✅ **All 64 Endpoints**:
- Health & Info (4 endpoints)
- Code Execution (5 endpoints)
- Commands (2 endpoints)
- File Operations (8 endpoints)
- Processes (2 endpoints)
- Metrics (3 endpoints)
- Cache (2 endpoints)
- WebSocket Streaming (6 endpoints)

✅ **Enterprise Features**:
- Request ID tracking (`X-Request-ID` header)
- Machine-readable error codes (16 types)
- Prometheus metrics
- Structured error responses

✅ **Rich Documentation**:
- Request/response schemas
- Code examples for each endpoint
- Error response examples
- WebSocket protocol descriptions

✅ **Components**:
- 20+ reusable schemas
- 7 common error responses
- Security schemes (API key)

## 🚀 How to Use

### 1. View in Swagger UI

**Online (Swagger Editor)**:
```bash
# Open https://editor.swagger.io/
# Copy/paste contents of openapi.yaml
```

**Local (Docker)**:
```bash
docker run -p 8080:8080 \
  -e SWAGGER_JSON=/openapi.yaml \
  -v $(pwd)/openapi.yaml:/openapi.yaml \
  swaggerapi/swagger-ui
  
# Open http://localhost:8080
```

**Local (npx)**:
```bash
npx swagger-ui-watcher openapi.yaml
# Opens browser automatically
```

### 2. View in ReDoc (Beautiful Docs)

```bash
npx @redocly/cli preview-docs openapi.yaml
# Opens http://localhost:8080
```

### 3. Generate SDK

**Python SDK**:
```bash
npx @openapitools/openapi-generator-cli generate \
  -i openapi.yaml \
  -g python \
  -o ./sdk/python \
  --additional-properties=packageName=hopx_agent

# Creates Python SDK in ./sdk/python/
```

**TypeScript SDK**:
```bash
npx @openapitools/openapi-generator-cli generate \
  -i openapi.yaml \
  -g typescript-axios \
  -o ./sdk/typescript

# Creates TypeScript SDK in ./sdk/typescript/
```

**Go SDK**:
```bash
npx @openapitools/openapi-generator-cli generate \
  -i openapi.yaml \
  -g go \
  -o ./sdk/go \
  --additional-properties=packageName=hopxagent
```

### 4. Validate Spec

**Using Redocly**:
```bash
npx @redocly/cli lint openapi.yaml
# Validates OpenAPI spec for errors
```

**Using Spectral**:
```bash
npx @stoplight/spectral-cli lint openapi.yaml
# Advanced linting with best practices
```

### 5. Test API

**Using Postman**:
1. Import `openapi.yaml` into Postman
2. Auto-generates collection with all endpoints
3. Test against live agent

**Using Insomnia**:
1. Import `openapi.yaml` into Insomnia
2. Auto-generates requests
3. Test and debug

## 📚 Key Sections

### Endpoints

**Health & Monitoring**:
- `GET /ping` - Liveness check
- `GET /health` - Health status with features
- `GET /info` - Complete VM information
- `GET /system` - System metrics (CPU, memory, disk)

**Code Execution**:
- `POST /execute` - Execute code synchronously
- `POST /execute/rich` - Execute with rich output capture (Matplotlib, Pandas)
- `POST /execute/background` - Execute in background
- `GET /execute/processes` - List background processes
- `DELETE /execute/kill` - Kill background process

**File Operations**:
- `GET /files/read` - Read file contents
- `POST /files/write` - Write file
- `POST /files/upload` - Upload file (multipart)
- `GET /files/download` - Download file
- `GET /files/list` - List directory
- `GET /files/exists` - Check if file exists
- `DELETE /files/remove` - Delete file/directory
- `POST /files/mkdir` - Create directory

**Commands**:
- `POST /commands/run` - Run shell command
- `POST /commands/background` - Run command in background

**Metrics** (NEW in v3.1.1):
- `GET /metrics/prometheus` - Prometheus exposition format
- `GET /metrics/snapshot` - JSON metrics snapshot

**WebSocket** (6 endpoints):
- `GET /terminal` - Interactive terminal
- `GET /stream` - Code execution streaming
- `GET /execute/stream` - Alternative execution streaming
- `GET /commands/stream` - Command streaming
- `GET /files/watch` - File watching

### Schemas

**Request Schemas**:
- `ExecuteRequest` - Code execution
- `BackgroundExecuteRequest` - Background execution
- `FileWriteRequest` - File writing
- `CommandRequest` - Command execution

**Response Schemas**:
- `ExecuteResponse` - Code execution result
- `FileListResponse` - Directory listing
- `ProcessListResponse` - Process list
- `MetricsSnapshot` - Metrics JSON
- `ErrorResponse` - Standardized errors

**Error Codes** (16 types):
```yaml
- METHOD_NOT_ALLOWED
- INVALID_JSON
- MISSING_PARAMETER
- PATH_NOT_ALLOWED
- FILE_NOT_FOUND
- PERMISSION_DENIED
- COMMAND_FAILED
- EXECUTION_TIMEOUT
- EXECUTION_FAILED
- INTERNAL_ERROR
- INVALID_PATH
- FILE_ALREADY_EXISTS
- DIRECTORY_NOT_FOUND
- INVALID_REQUEST
- PROCESS_NOT_FOUND
- DESKTOP_NOT_AVAILABLE
```

## 🔄 Keeping in Sync

### Current Approach: Manual

When adding a new endpoint to `main.go`:

1. **Update `openapi.yaml`**:
   ```yaml
   /new/endpoint:
     post:
       tags: [Category]
       summary: Description
       # ... complete spec
   ```

2. **Validate**:
   ```bash
   npx @redocly/cli lint openapi.yaml
   ```

3. **Commit together**:
   ```bash
   git add vm-agent/main.go vm-agent/openapi.yaml
   git commit -m "feat: Add new endpoint with OpenAPI spec"
   ```

### Future: Auto-Generation with swag

See `docs/OPENAPI-IMPLEMENTATION-GUIDE.md` for migration to `swag` (auto-generates from Go comments).

## ✅ Validation

### Run Validation

```bash
# Install Redocly CLI (once)
npm install -g @redocly/cli

# Validate OpenAPI spec
redocly lint openapi.yaml

# Expected output:
# ✅ openapi.yaml: 0 errors, 0 warnings
```

### Common Issues

**Issue**: `unknown server variable: vm_url`  
**Fix**: This is expected - variable is documented in spec

**Issue**: `missing required field`  
**Fix**: Check schemas match actual API responses

## 📊 Coverage

| Category | Endpoints | Documented | Coverage |
|----------|-----------|------------|----------|
| Health | 4 | 4 | ✅ 100% |
| Execution | 5 | 5 | ✅ 100% |
| Commands | 2 | 2 | ✅ 100% |
| Files | 8 | 8 | ✅ 100% |
| Processes | 2 | 2 | ✅ 100% |
| Metrics | 3 | 3 | ✅ 100% |
| Cache | 2 | 2 | ✅ 100% |
| WebSocket | 6 | 6 | ✅ 100% |
| **TOTAL** | **32** | **32** | **✅ 100%** |

*Note: WebSocket endpoints documented with protocol descriptions*

## 🎨 Features

### Request ID Tracking

All responses include `X-Request-ID` header:

```yaml
headers:
  X-Request-ID:
    schema:
      type: string
    description: Unique request identifier for tracing
```

### Machine-Readable Error Codes

All errors include `code` field:

```json
{
  "error": "File not found",
  "code": "FILE_NOT_FOUND",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-10-21T12:00:00Z",
  "path": "/workspace/missing.txt"
}
```

### Rich Output Support

`/execute/rich` endpoint captures:
- **Matplotlib** plots (PNG, base64)
- **Pandas** DataFrames (HTML)
- **Plotly** charts (HTML)

```yaml
rich_outputs:
  type: array
  items:
    type: object
    properties:
      type:
        type: string
        enum: [image/png, text/html, application/json]
      format:
        type: string
        enum: [base64, html, json]
      data:
        type: string
      metadata:
        type: object
```

### Prometheus Metrics

`/metrics/prometheus` exposes:
- `hopx_agent_requests_total` - Request counter
- `hopx_agent_request_duration_seconds` - Latency histogram
- `hopx_agent_errors_total` - Error counter
- `hopx_agent_active_executions` - Active executions gauge
- `hopx_agent_total_executions` - Total executions counter

## 🛠️ Tools Integration

### API Gateways

**Kong**:
```bash
curl -X POST http://kong:8001/services \
  -F "name=hopx-agent" \
  -F "url=https://vm.hopx.dev"

curl -X POST http://kong:8001/services/hopx-agent/routes \
  -F "paths[]=/agent" \
  -F "strip_path=true"

# Import OpenAPI spec for validation
deck sync --spec openapi.yaml
```

**Traefik**:
```yaml
http:
  services:
    hopx-agent:
      loadBalancer:
        servers:
          - url: https://vm.hopx.dev
  routers:
    agent:
      rule: PathPrefix(`/agent`)
      service: hopx-agent
```

### API Testing

**Dredd** (Contract Testing):
```bash
npm install -g dredd

dredd openapi.yaml https://vm.hopx.dev
# Tests all endpoints against spec
```

**Schemathesis** (Property-Based Testing):
```bash
pip install schemathesis

schemathesis run openapi.yaml \
  --base-url https://vm.hopx.dev \
  --hypothesis-max-examples 100
```

### API Mocking

**Prism** (Mock Server):
```bash
npx @stoplight/prism-cli mock openapi.yaml
# Starts mock server on http://localhost:4010
```

## 📈 Benefits

### For Developers

✅ **Auto-completion** in IDEs (with SDK)  
✅ **Type safety** (TypeScript, Python type hints)  
✅ **Interactive docs** (try endpoints in browser)  
✅ **No guessing** API structure  

### For Teams

✅ **Contract testing** (ensure API matches spec)  
✅ **Breaking change detection** (via CI/CD)  
✅ **API versioning** (clear deprecation paths)  
✅ **Mock servers** (frontend dev without backend)  

### For Enterprise

✅ **Standardized errors** (machine-readable codes)  
✅ **Request tracing** (via X-Request-ID)  
✅ **Metrics** (Prometheus integration)  
✅ **Security** (documented auth schemes)  

## 🔗 Resources

- **OpenAPI 3.0 Spec**: https://spec.openapis.org/oas/v3.0.3
- **Swagger Editor**: https://editor.swagger.io/
- **ReDoc**: https://github.com/Redocly/redoc
- **OpenAPI Generator**: https://openapi-generator.tech/
- **Spectral (Linting)**: https://stoplight.io/open-source/spectral

## 📝 Examples

### Python SDK Usage (Generated)

```python
from hopx_agent import ApiClient, Configuration, ExecutionApi
from hopx_agent.models import ExecuteRequest

# Configure client
config = Configuration(host="https://vm.hopx.dev")
client = ApiClient(config)
api = ExecutionApi(client)

# Execute code
request = ExecuteRequest(
    code='print("Hello from Python!")',
    language="python",
    timeout=30
)

response = api.execute(request)
print(f"Stdout: {response.stdout}")
print(f"Exit code: {response.exit_code}")
```

### TypeScript SDK Usage (Generated)

```typescript
import { Configuration, ExecutionApi, ExecuteRequest } from 'hopx-agent-sdk';

const config = new Configuration({ basePath: 'https://vm.hopx.dev' });
const api = new ExecutionApi(config);

const request: ExecuteRequest = {
  code: 'console.log("Hello from Node.js!");',
  language: 'javascript',
  timeout: 30
};

const response = await api.execute(request);
console.log(`Stdout: ${response.stdout}`);
console.log(`Exit code: ${response.exit_code}`);
```

## ✨ Next Steps

1. **View docs**: `npx @redocly/cli preview-docs openapi.yaml`
2. **Generate SDK**: See "Generate SDK" section above
3. **Integrate CI/CD**: Add validation to GitHub Actions
4. **Share with team**: Publish docs to internal portal

---

**Version**: 3.1.1  
**Last Updated**: 2025-10-21  
**Maintained By**: HOPX Engineering Team

