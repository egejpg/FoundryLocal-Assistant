# Foundry Local Knowledge Base

## What is Foundry Local?
Foundry Local is a runtime and SDK from Microsoft that lets applications run large language models directly on a user's device, without needing a cloud account or constant internet connection. It manages downloading, caching, and running models locally, choosing the best available hardware acceleration automatically.

## Installing the Foundry Local SDK
The Python SDK is installed with pip, for example `pip install foundry-local-sdk` on macOS or Linux, or `pip install foundry-local-sdk-winml` on Windows for better hardware acceleration support. No separate server or account setup is required before installing.

## Initializing the SDK
A Foundry Local application starts by creating a `Configuration` object, usually with an `app_name`, and passing it to `FoundryLocalManager.initialize(config)`. After initialization, `FoundryLocalManager.instance` gives access to the shared manager object used for the rest of the session.

## The Model Catalog
The manager exposes a `catalog` object that lists all models available for local use. A specific model is retrieved with `catalog.get_model("model-alias")`, where the alias is a short name like `phi-3.5-mini` or `qwen3-embedding-0.6b`; if the alias does not exist, `get_model` returns `None`.

## Downloading Models
A model object has a `download()` method that fetches its files from the catalog to local disk. The `is_cached` attribute can be checked first to avoid re-downloading a model that has already been pulled in a previous run; `download()` also accepts an optional progress callback function to report percentage completion.

## Loading and Unloading Models
Once a model has been downloaded, `load()` brings it into memory so it can process requests, and `unload()` releases that memory when it is no longer needed. Loading typically happens once per process run, even if the model was already downloaded in a previous session.

## Execution Providers
Execution providers, or EPs, are the underlying hardware acceleration backends, such as CUDA, DirectML, or OpenVINO, that Foundry Local uses to run models efficiently on a given machine. Calling `manager.download_and_register_eps()` ensures the right EP packages are downloaded and registered before any model is loaded.

## Hardware Acceleration
Foundry Local automatically detects the capabilities of the current machine, including GPU, NPU, and CPU, and selects an appropriate execution provider without requiring manual configuration. This means the same application code can run efficiently across different laptops with different hardware.

## The Chat Client and complete_chat
After a chat model is loaded, `model.get_chat_client()` returns a client object used to send conversations to the model. Calling `client.complete_chat(messages)`, where `messages` is a list of role/content dictionaries such as `system` and `user`, returns a response object whose text can be read from `response.choices[0].message.content`.

## Generating Embeddings
Once an embedding model is loaded, `model.get_embedding_client()` returns a client with two useful methods: `generate_embedding(text)` for a single string, and `generate_embeddings(list_of_texts)` for a batch. Both return numeric vectors representing the semantic meaning of the input text, which can then be compared using similarity measures like cosine similarity.

## Model Caching Behavior
Downloaded models are stored in a local cache folder so that subsequent runs of the same application do not need to download them again. Only loading into memory happens on every run; the network is only used again if a model is missing from the cache or a newer version is explicitly requested.

## Streaming Chat Responses
In addition to `complete_chat`, which returns a full response at once, some chat clients support a streaming method that yields partial chunks of text as they are generated. This is useful for showing responses to a user incrementally instead of waiting for the entire answer to finish.

## Supported Platforms
Foundry Local supports Windows, macOS, and Linux, with platform-specific packages available for better hardware integration, such as the WinML-based package on Windows. The same Python API surface works across these platforms once the correct package variant is installed.

## Privacy and Offline Benefits
Because inference happens entirely on the local device, no request or response data needs to leave the machine, which is valuable for privacy-sensitive or regulated use cases. Applications also continue to work without an internet connection once the required models have been downloaded once.

## Choosing a Model Alias
Model aliases in the catalog represent specific pre-optimized models, and different aliases trade off between speed and answer quality; smaller aliases like a "mini" model load and respond faster but may produce less detailed answers than larger ones. If an alias is misspelled or unavailable, `catalog.list_models()` can be used to inspect all valid aliases and their names.