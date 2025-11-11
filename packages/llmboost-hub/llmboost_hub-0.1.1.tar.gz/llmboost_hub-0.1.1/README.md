# [LLMBoost Hub (lbh)](https://docs.mangoboost.io/llmboost_hub/)

Manage LLMBoost™ model containers and environments to run, serve, and tune large language models.

---

## Pre-requisites

### Dependencies:
- Python 3.10+
- Docker 27.3.1+
- NVIDIA GPU: [nvidia-docker2](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) or AMD GPU: [ROCm 6.3+](https://rocm.docs.amd.com/en/latest/Installation_Guide/Installation-Guide.html)

### Install LLMBoost Hub:

```bash
pip install llmboost_hub

# Verify installation
lbh --version
```

Note: This document uses `lbh` interchangeably with `llmboost_hub`.

### Login to Hugging Face and Docker:
```bash
huggingface-cli login     # or set HF_TOKEN env var
docker login -u <your_docker_username>
```

---

## Quick start

One-liner to start serving a model (automatically downloads image and model, if needed):
```bash
lbh serve <Repo/Model-Name> # Full model name (including repository or organization name) must match the name from https://huggingface.co
```

For example:
```bash
lbh serve meta-llama/Llama-3.1-8B-Instruct
```

Basic workflow:
```bash
lbh login # authenticate LLMBoost license
lbh search <model> # find supported models, regex-style match
lbh prep <Repo/Model-Name> # download image and model assets
lbh run <Repo/Model-Name> # start container
lbh serve <Repo/Model-Name> # start LLMBoost server inside container
lbh test <Repo/Model-Name> # send test request
lbh stop <Repo/Model-Name> # stop container
```

For more details, see the [Command Reference](#command-reference) section below.

Shell completions:
```bash
eval "$(lbh completions)"                 # current shell
lbh completions [--venv|--profile]        # persist for venv or profile
```

---

## Configuration

*llmboost_hub* uses the following environment variables:

- `LBH_HOME`: base directory for all *llmboost_hub* data. (defaults: (host) `~/.llmboost_hub` <- (container) `/llmboost_hub`)
- `LBH_MODELS`: directory for storing and retrieving model assets. (default: `$LBH_HOME/models`)
- `LBH_WORKSPACE`: mounted user workspace for manually transferring files out of containers. (defaults: (host) `$LBH_HOME/workspace` <- (container) `/user_workspace`)

Notes:
- A configuation file is stored at `$LBH_HOME/config.yaml` with all the above mentioned settings (and other advanced settings). 
  - Precedence order for settings: Environment variables > Configuration file > Defaults
- `LBH_HOME` can only be changed by setting the env var (or in `~/.bashrc`). 
  - WARNING: Changing `LBH_HOME` will cause a new data directory to be used, and all configuration will be reset.
- `HF_TOKEN` is injected automatically when set.

---

## Command Reference

Use `lbh -h` for a summary of all commands, and `lbh [COMMAND] -h` for help with a specific command and all available options.

Use `lbh -v [COMMAND]` for verbose output with any command; shows useful diagnostic info for troubleshooting.

- `lbh login`
  - Reads `$LBH_LICENSE_PATH` or prompts for a token.
  - Validates online and saves the license file.

- `lbh search <model>`
  - Fetches latest models supported by LLMBoost.
  - Filters to available GPU.

- `lbh list [model]`
  - Lists local images joined with lookup.
  - Shows status: 
    - pending: model not prepared; docker image or model assets missing
    - stopped: model prepared but container not running
    - running: container running but idling
    - initializing: container running and starting LLMBoost server
    - serving: LLMBoost server ready to accept requests
    - tuning: autotuner running

- `lbh prep <Repo/Model-Name> [--only-verify] [--fresh]`
  - Pulls the image and downloads HF assets.
  - `--only-verify` checks digests and sizes.
  - `--fresh` removes existing image and re-downloads model assets from Hugging Face.

- `lbh run <Repo/Model-Name> [OPTIONS] -- [DOCKER FLAGS...]`
  - Resolves and starts the container detached.
  - Mounts `$LBH_HOME` and `$LBH_WORKSPACE`. Injects HF_TOKEN.
  - NVIDIA GPUs use `--gpus all`. AMD maps `/dev/dri` and `/dev/kfd`.
  - Useful options: 
    - `--image <image>`: override docker image.
    - `--model_path <model_path>`: override model assets path.
    - `--restart`: restarts container, if already running.
    - Pass extra docker flags after `--`.

- `lbh serve <Repo/Model-Name> [--host 0.0.0.0] [--port 8080] [--detached] [--force]`
  - Starts LLMBoost server inside the container.
  - Waits until ready, unless `--detached`.
  - `--force` skips GPU utilization checks (use if GPU utilization is incorrectly reported by NVidia or AMD GPU drivers).

- `lbh test <Repo/Model-Name> [--query "..."] [-t N] [--host 127.0.0.1] [--port 8080]`
  - Sends a test request to `/v1/chat/completions`.

- `lbh attach <Repo/Model-Name> [-c <container name or ID>]`
  - Opens a shell in the running container.

- `lbh stop <Repo/Model-Name> [-c <container name or ID>]`
  - Stops the container.

- `lbh status [model]`
  - Shows status and model.

- `lbh tune <Repo/Model-Name> [--metrics throughput] [--detached] [--image <image>]`
  - Runs the autotuner. 
  - Store results to `$LBH_HOME/inference.db`, and loads this on next `lbh serve`.

---

## Support

- Docs: https://docs.mangoboost.io/llmboost_hub/
- Website: https://docs.mangoboost.io/llmboost_hub/
- Email: support@mangoboost.io
