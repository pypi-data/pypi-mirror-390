openapi: 3.0.3
info:
  title: HOPX VM Agent API
  version: 3.1.1
  description: |
    Complete REST API for the HOPX VM Agent - code execution, file operations, 
    terminal access, process management, and system metrics.
    
    **Features:**
    - Code execution (Python, JavaScript, Go, Bash)
    - Rich output capture (Matplotlib, Pandas, Plotly)
    - File system operations
    - WebSocket streaming
    - Background process management
    - System metrics & observability
    - IPython kernel integration
    
    **Enterprise Features:**
    - Request ID tracking (X-Request-ID header)
    - Machine-readable error codes
    - Prometheus metrics
    - Structured logging
    
  contact:
    name: HOPX Support
    url: https://hopx.dev
    email: support@hopx.dev
  license:
    name: Proprietary
    url: https://hopx.dev/license

servers:
  - url: https://{vm_url}
    description: HOPX VM Agent (running inside VM)
    variables:
      vm_url:
        default: localhost:7777
        description: VM-specific URL (e.g., 7777-vmid.region.vms.hopx.dev)

tags:
  - name: Health
    description: Health checks and system info
  - name: Execution
    description: Code execution (sync, async, streaming)
  - name: Files
    description: File system operations
  - name: Commands
    description: Shell command execution
  - name: Processes
    description: Background process management
  - name: Terminal
    description: WebSocket terminal access
  - name: Streaming
    description: WebSocket streaming for code execution
  - name: IPython
    description: IPython kernel integration
  - name: Metrics
    description: Observability and metrics
  - name: Cache
    description: Execution cache management
  - name: Desktop
    description: Desktop/VNC features (if available)

security:
  - ApiKeyAuth: []

paths:
  # ============================================================================
  # HEALTH & INFO
  # ============================================================================
  
  /ping:
    get:
      tags: [Health]
      summary: Ping endpoint
      description: Simple liveness check
      responses:
        '200':
          description: Agent is alive
          content:
            text/plain:
              schema:
                type: string
                example: pong
  
  /health:
    get:
      tags: [Health]
      summary: Health check
      description: Detailed health status with features and uptime
      responses:
        '200':
          description: Health status
          headers:
            X-Request-ID:
              schema:
                type: string
              description: Unique request identifier
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HealthResponse'
  
  /info:
    get:
      tags: [Health]
      summary: VM information
      description: Complete VM agent information including version, features, and endpoints
      responses:
        '200':
          description: VM info
          headers:
            X-Request-ID:
              schema:
                type: string
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/InfoResponse'
  
  /system:
    get:
      tags: [Health]
      summary: System metrics
      description: CPU, memory, disk usage
      responses:
        '200':
          description: System metrics
          headers:
            X-Request-ID:
              schema:
                type: string
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SystemMetrics'

  # ============================================================================
  # CODE EXECUTION
  # ============================================================================
  
  /execute:
    post:
      tags: [Execution]
      summary: Execute code (synchronous)
      description: |
        Execute code synchronously and wait for completion.
        
        **Supported languages:** python, python3, node, nodejs, javascript, js, bash, sh, shell, go
        
        **Timeout:** Default 30s, max 300s
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ExecuteRequest'
            examples:
              python:
                summary: Python execution
                value:
                  code: |
                    print("Hello from Python!")
                    result = 2 + 2
                    print(f"Result: {result}")
                  language: python
                  timeout: 30
              javascript:
                summary: JavaScript execution
                value:
                  code: |
                    console.log("Hello from Node.js!");
                    const result = 2 + 2;
                    console.log(`Result: ${result}`);
                  language: javascript
                  timeout: 30
      responses:
        '200':
          description: Execution completed
          headers:
            X-Request-ID:
              schema:
                type: string
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ExecuteResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '408':
          $ref: '#/components/responses/Timeout'
        '500':
          $ref: '#/components/responses/InternalError'
  
  /execute/rich:
    post:
      tags: [Execution]
      summary: Execute code with rich output capture
      description: |
        Execute code and automatically capture rich outputs like:
        - Matplotlib plots (PNG)
        - Pandas DataFrames (HTML)
        - Plotly charts (HTML)
        
        **Requirements:** matplotlib, pandas, plotly must be installed
        
        **300ms delay** after execution to ensure files are written to disk
      requestBody:
        required: true
        content:
          application/json:
            schema:
              allOf:
                - $ref: '#/components/schemas/ExecuteRequest'
                - type: object
                  properties:
                    capture_rich:
                      type: boolean
                      default: true
                      description: Enable rich output capture
                    working_dir:
                      type: string
                      default: /tmp
                      description: Working directory for execution
            examples:
              matplotlib:
                summary: Matplotlib plot
                value:
                  code: |
                    import matplotlib
                    matplotlib.use('Agg')
                    import matplotlib.pyplot as plt
                    
                    plt.figure(figsize=(8, 6))
                    plt.plot([1, 2, 3, 4], [1, 4, 9, 16])
                    plt.title('Square Numbers')
                    plt.savefig('/tmp/plot.png')
                    print("Plot saved!")
                  language: python
                  timeout: 30
                  working_dir: /tmp
      responses:
        '200':
          description: Execution with rich outputs
          headers:
            X-Request-ID:
              schema:
                type: string
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/ExecuteResponse'
                  - type: object
                    properties:
                      rich_outputs:
                        type: array
                        items:
                          $ref: '#/components/schemas/RichOutput'
        '400':
          $ref: '#/components/responses/BadRequest'
  
  /execute/background:
    post:
      tags: [Execution]
      summary: Execute code in background
      description: |
        Start code execution in background and return immediately.
        
        Use `/execute/processes` to check status and `/execute/kill` to terminate.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/BackgroundExecuteRequest'
      responses:
        '200':
          description: Background execution started
          headers:
            X-Request-ID:
              schema:
                type: string
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BackgroundExecuteResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
  
  /execute/processes:
    get:
      tags: [Execution, Processes]
      summary: List background processes
      description: List all background execution processes with status
      responses:
        '200':
          description: List of processes
          headers:
            X-Request-ID:
              schema:
                type: string
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ProcessListResponse'
  
  /execute/kill:
    delete:
      tags: [Execution, Processes]
      summary: Kill background process
      description: Terminate a running background process
      parameters:
        - name: process_id
          in: query
          required: true
          schema:
            type: string
          description: Process ID to kill
      responses:
        '200':
          description: Process killed
          headers:
            X-Request-ID:
              schema:
                type: string
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: Process killed successfully
                  process_id:
                    type: string
        '400':
          $ref: '#/components/responses/BadRequest'
        '404':
          $ref: '#/components/responses/ProcessNotFound'
  
  /execute/ipython:
    post:
      tags: [Execution, IPython]
      summary: Execute code in IPython kernel
      description: Execute code using IPython kernel with richer output support
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ExecuteRequest'
      responses:
        '200':
          description: IPython execution result
          headers:
            X-Request-ID:
              schema:
                type: string
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ExecuteResponse'
        '400':
          $ref: '#/components/responses/BadRequest'

  # ============================================================================
  # COMMANDS
  # ============================================================================
  
  /commands/run:
    post:
      tags: [Commands]
      summary: Run shell command
      description: |
        Execute a shell command and wait for completion.
        
        **Note:** Command runs in `/bin/sh -c` by default.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [command]
              properties:
                command:
                  type: string
                  description: Shell command to execute
                  example: "echo 'Hello World'"
                timeout:
                  type: integer
                  default: 30
                  description: Timeout in seconds
                working_dir:
                  type: string
                  default: /workspace
                  description: Working directory
            examples:
              simple:
                summary: Simple command
                value:
                  command: "ls -la /workspace"
                  timeout: 10
              pipeline:
                summary: Pipeline command
                value:
                  command: "cat /etc/os-release | grep PRETTY_NAME"
                  timeout: 5
      responses:
        '200':
          description: Command executed
          headers:
            X-Request-ID:
              schema:
                type: string
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CommandResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '408':
          $ref: '#/components/responses/Timeout'
  
  /commands/background:
    post:
      tags: [Commands]
      summary: Run command in background
      description: Start a shell command in background
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [command]
              properties:
                command:
                  type: string
                timeout:
                  type: integer
                  default: 300
                name:
                  type: string
                  description: Optional process name
      responses:
        '200':
          description: Command started
          headers:
            X-Request-ID:
              schema:
                type: string
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BackgroundExecuteResponse'

  # ============================================================================
  # FILE OPERATIONS
  # ============================================================================
  
  /files/read:
    get:
      tags: [Files]
      summary: Read file contents
      description: |
        Read file contents as text.
        
        **Security:** Only allowed paths can be read (e.g., /workspace, /tmp)
      parameters:
        - name: path
          in: query
          required: true
          schema:
            type: string
          description: File path to read
          example: /workspace/script.py
      responses:
        '200':
          description: File contents
          headers:
            X-Request-ID:
              schema:
                type: string
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FileContentResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '403':
          $ref: '#/components/responses/PathNotAllowed'
        '404':
          $ref: '#/components/responses/FileNotFound'
  
  /files/write:
    post:
      tags: [Files]
      summary: Write file
      description: |
        Write content to a file (creates or overwrites).
        
        **Security:** Only allowed paths can be written
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/FileWriteRequest'
            examples:
              python_script:
                summary: Python script
                value:
                  path: /workspace/hello.py
                  content: |
                    print("Hello, World!")
                    print("This is a test script")
      responses:
        '200':
          description: File written
          headers:
            X-Request-ID:
              schema:
                type: string
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FileResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '403':
          $ref: '#/components/responses/PathNotAllowed'
  
  /files/upload:
    post:
      tags: [Files]
      summary: Upload file (multipart)
      description: |
        Upload a file using multipart/form-data.
        
        **Form fields:**
        - `file`: File to upload
        - `path`: Destination path (optional, defaults to /workspace/{filename})
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                file:
                  type: string
                  format: binary
                  description: File to upload
                path:
                  type: string
                  description: Destination path (optional)
      responses:
        '200':
          description: File uploaded
          headers:
            X-Request-ID:
              schema:
                type: string
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FileResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '403':
          $ref: '#/components/responses/PathNotAllowed'
  
  /files/download:
    get:
      tags: [Files]
      summary: Download file
      description: Download file as binary stream
      parameters:
        - name: path
          in: query
          required: true
          schema:
            type: string
          description: File path to download
      responses:
        '200':
          description: File contents
          headers:
            X-Request-ID:
              schema:
                type: string
            Content-Disposition:
              schema:
                type: string
              description: attachment; filename="..."
          content:
            application/octet-stream:
              schema:
                type: string
                format: binary
        '403':
          $ref: '#/components/responses/PathNotAllowed'
        '404':
          $ref: '#/components/responses/FileNotFound'
  
  /files/list:
    get:
      tags: [Files]
      summary: List directory contents
      description: List files and directories in a path
      parameters:
        - name: path
          in: query
          required: true
          schema:
            type: string
          description: Directory path
          example: /workspace
      responses:
        '200':
          description: Directory listing
          headers:
            X-Request-ID:
              schema:
                type: string
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FileListResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '403':
          $ref: '#/components/responses/PathNotAllowed'
        '404':
          $ref: '#/components/responses/DirectoryNotFound'
  
  /files/exists:
    get:
      tags: [Files]
      summary: Check if file exists
      description: Check if a file or directory exists
      parameters:
        - name: path
          in: query
          required: true
          schema:
            type: string
          description: Path to check
      responses:
        '200':
          description: Existence check result
          headers:
            X-Request-ID:
              schema:
                type: string
          content:
            application/json:
              schema:
                type: object
                properties:
                  exists:
                    type: boolean
                  path:
                    type: string
        '403':
          $ref: '#/components/responses/PathNotAllowed'
  
  /files/remove:
    delete:
      tags: [Files]
      summary: Delete file or directory
      description: Remove a file or directory (recursive for directories)
      parameters:
        - name: path
          in: query
          required: true
          schema:
            type: string
          description: Path to delete
      responses:
        '200':
          description: File deleted
          headers:
            X-Request-ID:
              schema:
                type: string
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FileResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '403':
          $ref: '#/components/responses/PathNotAllowed'
        '404':
          $ref: '#/components/responses/FileNotFound'
  
  /files/mkdir:
    post:
      tags: [Files]
      summary: Create directory
      description: Create a directory (creates parent directories if needed)
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [path]
              properties:
                path:
                  type: string
                  description: Directory path to create
                  example: /workspace/myproject/src
      responses:
        '200':
          description: Directory created
          headers:
            X-Request-ID:
              schema:
                type: string
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FileResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '403':
          $ref: '#/components/responses/PathNotAllowed'

  # ============================================================================
  # PROCESSES
  # ============================================================================
  
  /processes:
    get:
      tags: [Processes]
      summary: List system processes
      description: List running system processes (via ps)
      responses:
        '200':
          description: Process list
          headers:
            X-Request-ID:
              schema:
                type: string
          content:
            application/json:
              schema:
                type: object
                properties:
                  processes:
                    type: array
                    items:
                      type: object
                      properties:
                        pid:
                          type: integer
                        command:
                          type: string
                        user:
                          type: string

  # ============================================================================
  # METRICS & OBSERVABILITY
  # ============================================================================
  
  /metrics:
    get:
      tags: [Metrics]
      summary: Agent metrics (legacy)
      description: Basic agent metrics (deprecated, use /metrics/snapshot)
      responses:
        '200':
          description: Metrics
          headers:
            X-Request-ID:
              schema:
                type: string
          content:
            application/json:
              schema:
                type: object
  
  /metrics/prometheus:
    get:
      tags: [Metrics]
      summary: Prometheus metrics
      description: |
        Metrics in Prometheus exposition format.
        
        **Metrics:**
        - `hopx_agent_requests_total` - Total requests by endpoint/method/status
        - `hopx_agent_request_duration_seconds` - Request latency histogram
        - `hopx_agent_errors_total` - Total errors by endpoint/method/code
        - `hopx_agent_active_executions` - Active code executions (gauge)
        - `hopx_agent_total_executions` - Total code executions (counter)
      responses:
        '200':
          description: Prometheus metrics
          content:
            text/plain:
              schema:
                type: string
              example: |
                # HELP hopx_agent_requests_total Total number of requests
                # TYPE hopx_agent_requests_total counter
                hopx_agent_requests_total{endpoint="/execute",method="POST",status="200"} 42
                
                # HELP hopx_agent_active_executions Current number of active code executions
                # TYPE hopx_agent_active_executions gauge
                hopx_agent_active_executions 2
  
  /metrics/snapshot:
    get:
      tags: [Metrics]
      summary: Metrics snapshot (JSON)
      description: |
        JSON snapshot of key agent metrics.
        
        **Includes:**
        - Uptime
        - Total requests
        - Total errors
        - Active executions
        - Total executions
      responses:
        '200':
          description: Metrics snapshot
          headers:
            X-Request-ID:
              schema:
                type: string
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MetricsSnapshot'

  # ============================================================================
  # CACHE
  # ============================================================================
  
  /cache/stats:
    get:
      tags: [Cache]
      summary: Cache statistics
      description: Get execution cache statistics
      responses:
        '200':
          description: Cache stats
          headers:
            X-Request-ID:
              schema:
                type: string
          content:
            application/json:
              schema:
                type: object
                properties:
                  total_cached:
                    type: integer
                  hit_rate:
                    type: number
  
  /cache/clear:
    post:
      tags: [Cache]
      summary: Clear cache
      description: Clear execution cache
      responses:
        '200':
          description: Cache cleared
          headers:
            X-Request-ID:
              schema:
                type: string
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string

  # ============================================================================
  # WEBSOCKET ENDPOINTS
  # ============================================================================
  
  /terminal:
    get:
      tags: [Terminal]
      summary: WebSocket terminal
      description: |
        WebSocket endpoint for interactive terminal access.
        
        **Protocol:**
        - Client → Server: Terminal input (text)
        - Server → Client: Terminal output (text)
        
        **Connection:** Upgrade to WebSocket
      responses:
        '101':
          description: Switching Protocols (WebSocket)
        '400':
          $ref: '#/components/responses/BadRequest'
  
  /stream:
    get:
      tags: [Streaming]
      summary: WebSocket code streaming
      description: |
        WebSocket endpoint for streaming code execution.
        
        **Protocol:**
        - Client → Server: `{"code": "...", "language": "python"}`
        - Server → Client: Stream messages (stdout, stderr, result, error, complete)
      responses:
        '101':
          description: Switching Protocols (WebSocket)
  
  /stream/ipython:
    get:
      tags: [Streaming, IPython]
      summary: WebSocket IPython streaming
      description: WebSocket endpoint for IPython kernel streaming
      responses:
        '101':
          description: Switching Protocols (WebSocket)
  
  /execute/stream:
    get:
      tags: [Streaming]
      summary: WebSocket execution stream
      description: Alternative WebSocket endpoint for code execution streaming
      responses:
        '101':
          description: Switching Protocols (WebSocket)
  
  /commands/stream:
    get:
      tags: [Streaming]
      summary: WebSocket command streaming
      description: WebSocket endpoint for streaming command execution
      responses:
        '101':
          description: Switching Protocols (WebSocket)
  
  /files/watch:
    get:
      tags: [Streaming, Files]
      summary: WebSocket file watcher
      description: WebSocket endpoint for watching file changes
      responses:
        '101':
          description: Switching Protocols (WebSocket)

# ==============================================================================
# COMPONENTS
# ==============================================================================

components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Secret
      description: Optional API secret for authentication
  
  schemas:
    # -------------------------------------------------------------------------
    # HEALTH & INFO
    # -------------------------------------------------------------------------
    
    HealthResponse:
      type: object
      properties:
        status:
          type: string
          example: healthy
        agent:
          type: string
          example: hopx-vm-agent-desktop
        version:
          type: string
          example: 3.1.1
        uptime:
          type: string
          example: 2h34m12s
        go_version:
          type: string
          example: go1.22.2
        vm_id:
          type: string
          example: 1760954509layu9lw0
        features:
          type: object
          properties:
            code_execution:
              type: boolean
            file_operations:
              type: boolean
            terminal_access:
              type: boolean
            websocket_streaming:
              type: boolean
            rich_output:
              type: boolean
            background_jobs:
              type: boolean
            ipython_kernel:
              type: boolean
            system_metrics:
              type: boolean
            languages:
              type: array
              items:
                type: string
              example: [python, javascript, bash, go]
        active_streams:
          type: integer
          example: 0
    
    InfoResponse:
      type: object
      properties:
        vm_id:
          type: string
        agent:
          type: string
        agent_version:
          type: string
        os:
          type: string
        arch:
          type: string
        go_version:
          type: string
        vm_ip:
          type: string
        vm_port:
          type: string
        start_time:
          type: string
          format: date-time
        uptime:
          type: number
          description: Uptime in seconds
        endpoints:
          type: object
          additionalProperties:
            type: string
          description: Map of endpoint names to HTTP methods + paths
        features:
          type: object
          description: Available features
    
    SystemMetrics:
      type: object
      properties:
        cpu:
          type: object
          properties:
            usage_percent:
              type: number
            cores:
              type: integer
        memory:
          type: object
          properties:
            total:
              type: integer
            used:
              type: integer
            free:
              type: integer
            usage_percent:
              type: number
        disk:
          type: object
          properties:
            total:
              type: integer
            used:
              type: integer
            free:
              type: integer
            usage_percent:
              type: number
        uptime:
          type: number
          description: System uptime in seconds
    
    # -------------------------------------------------------------------------
    # EXECUTION
    # -------------------------------------------------------------------------
    
    ExecuteRequest:
      type: object
      required: [code, language]
      properties:
        code:
          type: string
          description: Code to execute
          example: print("Hello, World!")
        language:
          type: string
          description: Programming language
          enum: [python, python3, node, nodejs, javascript, js, bash, sh, shell, go]
          example: python
        timeout:
          type: integer
          description: Timeout in seconds
          default: 30
          minimum: 1
          maximum: 300
    
    ExecuteResponse:
      type: object
      properties:
        stdout:
          type: string
          description: Standard output
        stderr:
          type: string
          description: Standard error
        exit_code:
          type: integer
          description: Exit code (0 = success)
        execution_time:
          type: number
          description: Execution time in seconds
          format: float
        timestamp:
          type: string
          format: date-time
        language:
          type: string
        success:
          type: boolean
          description: Whether execution succeeded (exit_code == 0)
    
    BackgroundExecuteRequest:
      allOf:
        - $ref: '#/components/schemas/ExecuteRequest'
        - type: object
          properties:
            name:
              type: string
              description: Optional process name for identification
    
    BackgroundExecuteResponse:
      type: object
      properties:
        process_id:
          type: string
          description: Unique process identifier
        execution_id:
          type: string
          description: Execution identifier
        status:
          type: string
          enum: [running, completed, failed, killed]
        start_time:
          type: string
          format: date-time
        message:
          type: string
        name:
          type: string
          description: Process name (if provided)
    
    ProcessInfo:
      type: object
      properties:
        process_id:
          type: string
        execution_id:
          type: string
        name:
          type: string
        status:
          type: string
          enum: [running, completed, failed, killed]
        language:
          type: string
        start_time:
          type: string
          format: date-time
        end_time:
          type: string
          format: date-time
        exit_code:
          type: integer
          nullable: true
        duration:
          type: number
          description: Duration in seconds
        pid:
          type: integer
          description: System process ID
    
    ProcessListResponse:
      type: object
      properties:
        processes:
          type: array
          items:
            $ref: '#/components/schemas/ProcessInfo'
        count:
          type: integer
        timestamp:
          type: string
          format: date-time
    
    RichOutput:
      type: object
      properties:
        type:
          type: string
          enum: [image/png, text/html, application/json]
          description: MIME type
        format:
          type: string
          enum: [base64, html, json]
        data:
          type: string
          description: Output data (base64 for images, HTML for tables, etc.)
        metadata:
          type: object
          properties:
            source:
              type: string
              enum: [matplotlib, pandas, plotly, other]
            filename:
              type: string
            size:
              type: integer
    
    # -------------------------------------------------------------------------
    # COMMANDS
    # -------------------------------------------------------------------------
    
    CommandResponse:
      type: object
      properties:
        stdout:
          type: string
        stderr:
          type: string
        exit_code:
          type: integer
        execution_time:
          type: number
        command:
          type: string
        timestamp:
          type: string
          format: date-time
    
    # -------------------------------------------------------------------------
    # FILES
    # -------------------------------------------------------------------------
    
    FileInfo:
      type: object
      properties:
        name:
          type: string
          description: File or directory name
        path:
          type: string
          description: Full path
        size:
          type: integer
          description: Size in bytes
        is_directory:
          type: boolean
        modified_time:
          type: string
          format: date-time
        permissions:
          type: string
          description: Unix permissions (e.g., drwxr-xr-x)
    
    FileListResponse:
      type: object
      properties:
        files:
          type: array
          items:
            $ref: '#/components/schemas/FileInfo'
        path:
          type: string
          description: Directory path
        count:
          type: integer
          description: Number of files
    
    FileContentResponse:
      type: object
      properties:
        content:
          type: string
          description: File contents
        path:
          type: string
        size:
          type: integer
          description: Size in bytes
    
    FileWriteRequest:
      type: object
      required: [path, content]
      properties:
        path:
          type: string
          description: File path to write
          example: /workspace/script.py
        content:
          type: string
          description: File contents
    
    FileResponse:
      type: object
      properties:
        message:
          type: string
        path:
          type: string
        success:
          type: boolean
        size:
          type: integer
          description: File size (for write operations)
        timestamp:
          type: string
          format: date-time
    
    # -------------------------------------------------------------------------
    # METRICS
    # -------------------------------------------------------------------------
    
    MetricsSnapshot:
      type: object
      properties:
        uptime_seconds:
          type: number
          description: Agent uptime in seconds
        total_requests:
          type: integer
          description: Total HTTP requests handled
        total_errors:
          type: integer
          description: Total errors encountered
        active_executions:
          type: integer
          description: Current active code executions
        total_executions:
          type: integer
          description: Total code executions completed
    
    # -------------------------------------------------------------------------
    # ERRORS
    # -------------------------------------------------------------------------
    
    ErrorResponse:
      type: object
      required: [error, timestamp]
      properties:
        error:
          type: string
          description: Human-readable error message
          example: File not found
        code:
          type: string
          description: Machine-readable error code
          enum:
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
          example: FILE_NOT_FOUND
        request_id:
          type: string
          description: Request ID for tracing (from X-Request-ID header)
          example: 550e8400-e29b-41d4-a716-446655440000
        timestamp:
          type: string
          format: date-time
        path:
          type: string
          description: Related file path (for file operation errors)
        details:
          type: object
          additionalProperties: true
          description: Additional error context
  
  # ---------------------------------------------------------------------------
  # REUSABLE RESPONSES
  # ---------------------------------------------------------------------------
  
  responses:
    BadRequest:
      description: Bad Request
      headers:
        X-Request-ID:
          schema:
            type: string
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
          examples:
            invalid_json:
              value:
                error: Invalid JSON in request body
                code: INVALID_JSON
                request_id: 550e8400-e29b-41d4-a716-446655440000
                timestamp: "2025-10-21T12:00:00Z"
            missing_parameter:
              value:
                error: Missing required parameter
                code: MISSING_PARAMETER
                request_id: 550e8400-e29b-41d4-a716-446655440001
                timestamp: "2025-10-21T12:00:00Z"
                details:
                  missing_field: code
    
    PathNotAllowed:
      description: Forbidden - Path not allowed
      headers:
        X-Request-ID:
          schema:
            type: string
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
          example:
            error: Access denied - path not allowed
            code: PATH_NOT_ALLOWED
            path: /etc/passwd
            request_id: 550e8400-e29b-41d4-a716-446655440002
            timestamp: "2025-10-21T12:00:00Z"
    
    FileNotFound:
      description: File not found
      headers:
        X-Request-ID:
          schema:
            type: string
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
          example:
            error: File not found
            code: FILE_NOT_FOUND
            path: /workspace/nonexistent.txt
            request_id: 550e8400-e29b-41d4-a716-446655440003
            timestamp: "2025-10-21T12:00:00Z"
    
    DirectoryNotFound:
      description: Directory not found
      headers:
        X-Request-ID:
          schema:
            type: string
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
          example:
            error: Directory not found
            code: DIRECTORY_NOT_FOUND
            path: /workspace/nonexistent
            request_id: 550e8400-e29b-41d4-a716-446655440004
            timestamp: "2025-10-21T12:00:00Z"
    
    ProcessNotFound:
      description: Process not found
      headers:
        X-Request-ID:
          schema:
            type: string
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
          example:
            error: Process not found
            code: PROCESS_NOT_FOUND
            request_id: 550e8400-e29b-41d4-a716-446655440005
            timestamp: "2025-10-21T12:00:00Z"
            details:
              process_id: abc123
    
    Timeout:
      description: Request timeout
      headers:
        X-Request-ID:
          schema:
            type: string
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
          example:
            error: Execution timeout
            code: EXECUTION_TIMEOUT
            request_id: 550e8400-e29b-41d4-a716-446655440006
            timestamp: "2025-10-21T12:00:00Z"
            details:
              timeout_seconds: 30
    
    InternalError:
      description: Internal server error
      headers:
        X-Request-ID:
          schema:
            type: string
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
          example:
            error: Internal server error
            code: INTERNAL_ERROR
            request_id: 550e8400-e29b-41d4-a716-446655440007
            timestamp: "2025-10-21T12:00:00Z"

