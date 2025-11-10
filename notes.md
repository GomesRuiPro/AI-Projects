Versions: https://pytorch.org/get-started/locally/ 
- PACKAGES

(venv) rgomes@BBD-MWS-11801:~/ubisoft_repos/innovation/FeedbackerAi$ grep -f requirements.txt <(pip list)
Package                                  Version
---------------------------------------- ------------------
annotated-types                          0.7.0
anyio                                    4.10.0
async-timeout                            4.0.3
attrs                                    25.3.0
av                                       15.1.0
backoff                                  2.2.1
bcrypt                                   4.3.0
build                                    1.3.0
cachetools                               5.5.2
certifi                                  2025.8.3
charset-normalizer                       3.4.3
chromadb                                 1.1.0
click                                    8.3.0
coloredlogs                              15.0.1
contourpy                                1.3.2
cycler                                   0.12.1
distro                                   1.9.0
durationpy                               0.10
exceptiongroup                           1.3.0
ffmpeg-python                            0.2.0
filelock                                 3.19.1
flatbuffers                              25.2.10
fonttools                                4.60.0
fsspec                                   2025.9.0
future                                   1.0.0
fvcore                                   0.1.5.post20221221
google-api-core                          2.25.1
google-api-python-client                 2.182.0
google-auth                              2.40.3
google-auth-httplib2                     0.2.0
googleapis-common-protos                 1.70.0
greenlet                                 3.2.4
grpcio                                   1.75.0
h11                                      0.16.0
hf-xet                                   1.1.10
httpcore                                 1.0.9
httplib2                                 0.31.0
httptools                                0.6.4
httpx                                    0.28.1
huggingface-hub                          0.35.0
humanfriendly                            10.0
idna                                     3.10
importlib_metadata                       8.7.0
importlib_resources                      6.5.2
iopath                                   0.1.10
isodate                                  0.7.2
Jinja2                                   3.1.6
json-spec                                0.12.0
jsoncomment                              0.4.2
jsonpatch                                1.33
jsonpointer                              3.0.0
jsonschema                               4.25.1
jsonschema-specifications                2025.9.1
kiwisolver                               1.4.9
kubernetes                               33.1.0
langchain                                0.3.27
langchain-chroma                         0.2.6
langchain-core                           0.3.76
langchain-ollama                         0.3.8
langchain-text-splitters                 0.3.11
langsmith                                0.4.29
Mako                                     1.3.10
markdown-it-py                           4.0.0
MarkupSafe                               3.0.2
matplotlib                               3.10.6
mdurl                                    0.1.2
mmh3                                     5.2.0
mpmath                                   1.3.0
networkx                                 3.4.2
numpy                                    2.2.6
nvidia-cublas-cu12                       12.9.1.4
nvidia-cuda-cupti-cu12                   12.9.79
nvidia-cuda-nvrtc-cu12                   12.9.86
nvidia-cuda-runtime-cu12                 12.9.79
nvidia-cudnn-cu12                        9.10.2.21
nvidia-cufft-cu12                        11.4.1.4
nvidia-cufile-cu12                       1.14.1.1
nvidia-curand-cu12                       10.3.10.19
nvidia-cusolver-cu12                     11.7.5.82
nvidia-cusparse-cu12                     12.5.10.65
nvidia-cusparselt-cu12                   0.7.1
nvidia-nccl-cu12                         2.27.3
nvidia-nvjitlink-cu12                    12.9.86
nvidia-nvtx-cu12                         12.9.79
oauthlib                                 3.3.1
ollama                                   0.5.4
onnxruntime                              1.22.1
opencv-python                            4.12.0.88
opencv-python-headless                   4.12.0.88
opentelemetry-api                        1.37.0
opentelemetry-exporter-otlp-proto-common 1.37.0
opentelemetry-exporter-otlp-proto-grpc   1.37.0
opentelemetry-proto                      1.37.0
opentelemetry-sdk                        1.37.0
opentelemetry-semantic-conventions       0.58b0
orjson                                   3.11.3
overrides                                7.7.0
packaging                                25.0
pandas                                   2.3.2
parameterized                            0.9.0
pillow                                   11.3.0
pip                                      25.2
platformdirs                             4.4.0
polars                                   1.33.1
portalocker                              3.2.0
posthog                                  5.4.0
proto-plus                               1.26.1
protobuf                                 6.32.1
psutil                                   7.1.0
pyasn1                                   0.6.1
pyasn1_modules                           0.4.2
pybase64                                 1.4.2
pycuda                                   2025.1.2
pydantic                                 2.11.9
pydantic_core                            2.33.2
Pygments                                 2.19.2
pyparsing                                3.2.5
PyPika                                   0.48.9
pyproject_hooks                          1.2.0
python-dateutil                          2.9.0.post0
python-dotenv                            1.1.1
pytools                                  2025.2.4
pytorchvideo                             0.1.5
pytz                                     2025.2
PyYAML                                   6.0.2
referencing                              0.36.2
regex                                    2025.9.18
requests                                 2.32.5
requests-oauthlib                        2.0.0
requests-toolbelt                        1.0.0
rich                                     14.1.0
rpds-py                                  0.27.1
rsa                                      4.9.1
safetensors                              0.6.2
scipy                                    1.15.3
setuptools                               59.6.0
shellingham                              1.5.4
siphash24                                1.8
six                                      1.17.0
sniffio                                  1.3.1
SQLAlchemy                               2.0.43
sympy                                    1.14.0
tabulate                                 0.9.0
tenacity                                 9.1.2
termcolor                                3.1.0
tokenizers                               0.22.1
tomli                                    2.2.1
torch                                    2.8.0+cu129
torchaudio                               2.8.0+cu129
torchvision                              0.23.0+cu129
tqdm                                     4.67.1
transformers                             4.56.2
triton                                   3.4.0
typer                                    0.19.1
typing_extensions                        4.15.0
typing-inspection                        0.4.1
tzdata                                   2025.2
ultralytics                              8.3.202
ultralytics-thop                         2.0.17
uritemplate                              4.2.0
urllib3                                  2.5.0
uvicorn                                  0.36.0
uvloop                                   0.21.0
watchfiles                               1.1.0
websocket-client                         1.8.0
websockets                               15.0.1
yacs                                     0.1.8
youtube-search-python                    1.6.6
yt-dlp                                   2025.9.5
zipp                                     3.23.0
zstandard                                0.25.0

- WSL:
C:\Users\rgomes>wsl -l -v
  NAME      STATE           VERSION
* Ubuntu    Running         2

- WSL UBUNTU:

(venv) rgomes@BBD-MWS-11801:~/ubisoft_repos/innovation/FeedbackerAi$ lsb_release -a
No LSB modules are available.
Distributor ID: Ubuntu
Description:    Ubuntu 22.04.3 LTS
Release:        22.04
Codename:       jammy

- PYTHON:
 rgomes@BBD-MWS-11801:~/ubisoft_repos/innovation/FeedbackerAi$ python
Python 3.10.12 (main, Aug 15 2025, 14:32:43) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.


- CUDA driver
(venv) rgomes@BBD-MWS-11801:~/ubisoft_repos/innovation/FeedbackerAi$ nvcc --version
nvcc: NVIDIA (R) Cuda compiler driver
Copyright (c) 2005-2025 NVIDIA Corporation
Built on Tue_May_27_02:21:03_PDT_2025
Cuda compilation tools, release 12.9, V12.9.86
Build cuda_12.9.r12.9/compiler.36037853_0

- CUDA version:

(venv) rgomes@BBD-MWS-11801:~/ubisoft_repos$ nvidia-smi
Mon Sep 22 13:40:51 2025       
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 580.76.04              Driver Version: 580.97         CUDA Version: 13.0     |
+-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce RTX 3080 ...    On  |   00000000:01:00.0 Off |                  N/A |
| N/A   52C    P8             13W /  122W |       0MiB /  16384MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+



Feature implemented:
- set a number of different models for object detection, environment and movement. DONE
- get genre will be stubbed for now - DONE
- install the model coming from hugging face or - DOEN
- check and filter by confidence - DONE
- Show image with squares for object detection - DONE
- Caching - DONE
- Web scrapping - DONE
- Sources linked with LLM - DONE
- restructure model class with fallback (factory, iterator and strategy DPs) - DONE
- Figure out how to move from a composite object > dict  and send the values to the web scrapper tool (issue in Utilities) DONE
- fix issue where openai is reading Xth frame at a time. it should read all frames but then preselected by the model after DONE
- Connect non local LLM get Trends with VLM: get from source > extract keywords and format answer > convert answer to features  DONE


TODO features:
- ask VLM to look for these features > show results

- REFACTORING:
  - fix userinput problem when it should depend on input and the output expected , especially when working with reviews
  - make each operation flexible: you should be able to use userinput
  - make each method in each agent to NOT work with objects but string or so. Easier to implement stubs
  - clean player and sources entities factories to avoid using is_enabled flag (shouldnt we just remove it?)
  - make sources and player to have an execute() method instead of get_reviews and get_...
  - implement intersect and concatenate methods from agent
  - clean imports into a single file..

Next features:

- improve performance: Example Workflow:
Extract comments/reviews.
Run keyword extraction/NLP analysis.
Generate a list of trending keywords/phrases. (most common keywrods mentioend)
Visualize trends over time (charts, heatmaps).
Summarize insights based on context and frequency.

- create individual models based on age group, region, gender (model execution process is the same, but data is different so finetuning would be different) - audience segmentation
- 
- set the models locally
- finetune models to gaming context
- create pipelines / chain of responsability pattern to run those model in certain order
- create a new model to replace the LLM to a SocialMedia API > sentiment-analysis > summarization > theme/keyword extraction process for accurate results (this represents one model. we would need a model for each type of source where the API is different)
- getGenre needs to be improved by detecting also subgenres
- Try to make this bot script to run as a subprocess in the backgroud.
- When looking to finetune, try to automatically detect when a game is booting and record that session for a couple of minutes. Put it in a specific folder so that we can later manually decide how to label it
- run bot in background
- do video capture automatically once a game starts

LIMITATIONS:

1) Models are not gaming focused or to the Ubisoft context. Results might be innacurate

ERRORS:

