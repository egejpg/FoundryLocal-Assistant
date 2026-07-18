# FastAPI Knowledge Base

## What is FastAPI?
FastAPI is a modern Python web framework for building APIs, built on top of Starlette for the web parts and Pydantic for data validation. It is designed around standard Python type hints, which it uses to validate request data, serialize responses, and generate interactive documentation automatically. It targets both high performance and a fast, low-friction developer experience.

## Installing FastAPI
FastAPI can be installed with pip using `pip install fastapi`. To actually run an application you also need an ASGI server such as Uvicorn, installed separately or via the `fastapi[standard]` extra, which bundles Uvicorn and a few other commonly used tools.

## Creating Your First FastAPI Application
A minimal FastAPI app starts by creating an instance of the `FastAPI` class, then attaching route functions to it with decorators. For example, importing `FastAPI`, creating `app = FastAPI()`, and defining a function decorated with `@app.get("/")` that returns a dictionary is enough to have a working API with a single endpoint.

## Running a FastAPI Server with Uvicorn
Uvicorn is the ASGI server that actually runs a FastAPI application and handles incoming HTTP connections. A typical command is `uvicorn main:app --reload`, where `main` is the Python file name and `app` is the FastAPI instance inside it; `--reload` restarts the server automatically when code changes during development.

## The Purpose of Uvicorn
FastAPI itself only defines how requests should be handled; it does not listen on a network socket or manage connections. Uvicorn is the piece that actually accepts TCP connections, parses HTTP, and passes requests into the ASGI application (FastAPI) according to the ASGI specification, then sends the response back to the client.

## Creating a GET Endpoint
A GET endpoint is created by decorating a function with `@app.get("/path")`. The function's return value, usually a dictionary or a Pydantic model, is automatically converted into a JSON response. Path and query parameters can be added directly as function arguments with type hints.

## Creating a POST Endpoint
A POST endpoint uses `@app.post("/path")` instead of `@app.get`. The request body is typically declared as a parameter typed with a Pydantic model; FastAPI parses the incoming JSON body, validates it against that model, and passes it into the function as a regular Python object.

## Path Parameters
Path parameters are parts of the URL itself, such as the `item_id` in `/items/{item_id}`. They are declared by including `{name}` in the route string and adding a matching function parameter with a type hint, such as `item_id: int`; FastAPI validates and converts the value automatically.

## Query Parameters
Query parameters are extra values passed after a `?` in the URL, like `/items?skip=0&limit=10`. Any function parameter that is not part of the path and is not a request body is treated as a query parameter by default, and can be given a default value to make it optional.

## Validating Request Data with Pydantic Models
Pydantic models are Python classes that inherit from `BaseModel` and declare fields with type hints. When a Pydantic model is used as a request body type, FastAPI automatically validates incoming JSON against the model's field types and constraints, returning a clear validation error if the data does not match.

## Returning JSON Responses
By default, FastAPI converts whatever a route function returns (dictionaries, lists, or Pydantic models) into a JSON response using its own JSON-compatible encoder. For more control over headers, status codes, or media type, a route can instead return a `JSONResponse` object explicitly.

## Handling HTTP Exceptions
FastAPI provides an `HTTPException` class that can be raised inside a route function to return a specific HTTP status code along with an error message, for example `raise HTTPException(status_code=404, detail="Item not found")`. FastAPI catches this exception and turns it into a proper JSON error response.

## Dependency Injection
FastAPI has a built-in dependency injection system based on the `Depends` function. A dependency is typically a function whose return value is computed once per request and then passed into route functions that declare it as a parameter, which is useful for things like shared database connections, authentication checks, or common query parameters.

## Organizing Routes with APIRouter
`APIRouter` lets routes be defined in separate modules instead of all in one file. Each router collects its own set of path operations, and is later included into the main `FastAPI` app with `app.include_router(router)`, optionally with a shared prefix or tags for documentation grouping.

## Uploading Files
File uploads are handled using the `UploadFile` type from FastAPI, combined with `File(...)` as the parameter default. `UploadFile` gives access to the file's content as a stream along with metadata like filename and content type, and is more memory-efficient than reading the whole file into memory at once.

## Connecting FastAPI to a SQLite Database
A common pattern is to use Python's built-in `sqlite3` module or an ORM such as SQLAlchemy to open a connection to a `.db` file. The connection setup is usually wrapped as a dependency so that each request gets its own connection or session, which is then closed automatically after the request completes.

## Implementing Middleware
Middleware in FastAPI is added with the `@app.middleware("http")` decorator or by using `app.add_middleware(...)`. A middleware function receives the request, can inspect or modify it, calls the next handler in the chain, and can also modify the response before it is returned to the client.

## Enabling CORS
Cross-Origin Resource Sharing is enabled by adding `CORSMiddleware` from `fastapi.middleware.cors`, registered on the app with `app.add_middleware(CORSMiddleware, allow_origins=[...], allow_methods=[...], ...)`. This tells browsers which external origins are allowed to call the API from client-side JavaScript.

## Asynchronous Endpoints with async and await
Route functions can be declared with `async def` instead of a plain `def`, allowing them to use `await` for asynchronous operations like non-blocking database or network calls. FastAPI supports both synchronous and asynchronous route functions side by side in the same application.

## Accessing the Automatic Swagger Documentation
FastAPI automatically generates interactive API documentation based on the routes and Pydantic models in the app. The Swagger UI version is available at the `/docs` path by default, and an alternative ReDoc-based view is available at `/redoc`, both without any extra configuration.

## Creating Custom Response Models
The `response_model` parameter on a route decorator lets you declare a separate Pydantic model describing the shape of the response, independent of the model used for input. This is useful for hiding internal fields, such as a password hash, that should never be sent back to the client.

## Using Background Tasks
FastAPI's `BackgroundTasks` lets a route function schedule work, such as sending an email or writing a log, to run after the response has already been sent to the client. A route adds a function to run via `background_tasks.add_task(...)`, which keeps the request itself fast.

## Securing Endpoints with Authentication
FastAPI provides security utilities under `fastapi.security`, such as `OAuth2PasswordBearer` and `HTTPBasic`, that can be used as dependencies on protected routes. A route declares a security dependency, and FastAPI automatically handles extracting credentials and documenting the security scheme in the docs.

## Implementing JWT Authentication
JWT authentication in FastAPI is typically built by combining `OAuth2PasswordBearer` for extracting the token from requests with a library like `python-jose` or `pyjwt` for encoding and decoding the token itself. A dependency function verifies the token's signature and expiration, then returns the associated user for use inside protected routes.

## Adding Request and Response Validation
Beyond basic Pydantic types, validation can be tightened with field constraints, such as minimum and maximum length, numeric ranges, or regular expressions, declared directly on model fields. FastAPI checks these constraints automatically and returns a structured 422 error listing exactly which fields failed and why.

## Handling Form Data
Form data, as opposed to JSON, is read using the `Form` parameter default from FastAPI, similar to how request bodies use Pydantic models. This is commonly used for traditional HTML form submissions or for login endpoints that expect `application/x-www-form-urlencoded` data.

## Using WebSockets
FastAPI supports WebSocket connections through the `@app.websocket("/path")` decorator, which gives the handler a `WebSocket` object for sending and receiving messages over a persistent connection. This is useful for real-time features like chat or live notifications, as opposed to the request/response cycle used by regular HTTP endpoints.

## Testing FastAPI Endpoints
FastAPI applications are commonly tested with `TestClient` from `fastapi.testclient`, which wraps the app and lets tests call routes directly without running a real server. Combined with a testing framework like `pytest`, this allows sending requests and asserting on status codes and JSON response bodies.

## Deploying a FastAPI Application
Deployment usually involves running the app behind a production ASGI server such as Uvicorn or Gunicorn with Uvicorn workers, often placed behind a reverse proxy like Nginx. Containerizing the app with Docker is a common approach, since it packages the app, its dependencies, and the server configuration together for consistent deployment.

## FastAPI versus Flask
Flask is a WSGI-based framework that is simple and flexible but does not include built-in data validation or automatic documentation, usually relying on extensions for those features. FastAPI is ASGI-based, supports asynchronous code natively, and includes automatic validation, serialization, and interactive documentation out of the box, which generally makes it faster to build and safer for API-focused projects.