# Model Benchmarking

This is a preliminary benchmark of some local models.
The [test suites](tests) try to highlight the usage and features of llme.
The ranking should not be considered fair or rigorous, since many uncontrolled variables (still) impact it.

Moreover, the experiments are done with more or less recent versions of llme, the test suites, the models, or the server.
This explains possible discrepancies with the numbers.

The benchmark is also used to check the API compatibility with local LLM servers.

Most models come from the [huggingface](https://huggingface.co/).
GUFF models are served by [llama.cpp](https://github.com/ggml-org/llama.cpp) (and [llama-swap](https://github.com/mostlygeek/llama-swap)).
MLX models are served by [nexa](https://github.com/NexaAI/nexa-sdk).
The others models come from the [ollama](https://ollama.com/) repository and are served by the ollama server.

These preliminary results show that there is a lot of variation in the performance of the models, and that if the model size or the temperature does something, but it's not clear what...
The larger is not always the better.

## Legend

* PASS: the task was successfully completed.
* ALMOST: some tasks have a fallback validation.
* FAIL: the task was successfully completed.
* ERROR: there was an error during the task.
  Most are server errors: images unsupported by the model, or context too large.
* TIMEOUT: the task was not completed before 3 minutes.
  Usually it means the model went into repeating itself and running the same commands again and again without progress or giving the hand to the user.
  Note that we do not check if the task was successful or not.

## Basic stats

<!-- the contents bellow this line are generated -->

* 82 models
* 151 model configurations
* 7 task suites
* 53 tasks
* 7943 task executions
* 21,452 messages
* 5,453,984 predicted tokens

## Results by models

| Model                                                                                | PASS     | ALMOST   | FAIL     | ERROR    | TIMEOUT   |   Total |
|:-------------------------------------------------------------------------------------|:---------|:---------|:---------|:---------|:----------|--------:|
| 🟡 [unsloth/gpt-oss-20b-GGUF]:F16 mode=native                                        | 38 (72%) | 1 (2%)   | 10 (19%) | 3 (6%)   | 1 (2%)    |      53 |
| 🟡 [unsloth/gpt-oss-120b-GGUF]:F16 mode=native                                       | 38 (72%) | 1 (2%)   | 9 (17%)  | 3 (6%)   | 2 (4%)    |      53 |
| 🟡 [unsloth/Qwen3-VL-235B-A22B-Instruct-GGUF]:Q4_K_M mode=markdown                   | 36 (68%) | 3 (6%)   | 13 (25%) | 0        | 1 (2%)    |      53 |
| 🟡 [unsloth/Qwen3-VL-235B-A22B-Instruct-GGUF]:Q4_K_M mode=native                     | 35 (66%) | 3 (6%)   | 12 (23%) | 0        | 3 (6%)    |      53 |
| 🟡 [unsloth/gpt-oss-20b-GGUF]:Q4_K_M t=1.0 mode=native                               | 35 (66%) | 1 (2%)   | 12 (23%) | 4 (8%)   | 1 (2%)    |      53 |
| 🟡 [unsloth/gpt-oss-20b-GGUF]:Q4_K_M t=0.5 mode=native                               | 35 (66%) | 0        | 10 (19%) | 5 (9%)   | 3 (6%)    |      53 |
| 🟠 [unsloth/gpt-oss-20b-GGUF]:Q4_K_M mode=native                                     | 34 (64%) | 2 (4%)   | 11 (21%) | 4 (8%)   | 2 (4%)    |      53 |
| 🟠 [unsloth/gpt-oss-120b-GGUF]:Q4_K_M mode=native                                    | 34 (64%) | 0        | 12 (23%) | 4 (8%)   | 3 (6%)    |      53 |
| 🟠 [unsloth/gpt-oss-20b-GGUF]:Q4_K_M t=0.0 mode=native                               | 34 (64%) | 0        | 11 (21%) | 4 (8%)   | 4 (8%)    |      53 |
| 🟠 [unsloth/Qwen3-235B-A22B-Instruct-2507-GGUF]:Q4_K_M mode=native                   | 33 (62%) | 2 (4%)   | 13 (25%) | 3 (6%)   | 2 (4%)    |      53 |
| 🟠 [unsloth/Qwen3-235B-A22B-Instruct-2507-GGUF]:Q4_K_M mode=markdown                 | 32 (60%) | 3 (6%)   | 12 (23%) | 3 (6%)   | 3 (6%)    |      53 |
| 🟠 [unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF]:BF16 mode=native                      | 32 (60%) | 2 (4%)   | 15 (28%) | 3 (6%)   | 1 (2%)    |      53 |
| 🟠 [unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF]:Q4_K_M mode=markdown                  | 31 (58%) | 2 (4%)   | 16 (30%) | 3 (6%)   | 1 (2%)    |      53 |
| 🟠 [unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF]:BF16 mode=markdown                    | 31 (58%) | 1 (2%)   | 15 (28%) | 3 (6%)   | 3 (6%)    |      53 |
| 🟠 [qwen3-coder]:30b t=0.0 mode=native                                               | 29 (55%) | 2 (4%)   | 20 (38%) | 0        | 2 (4%)    |      53 |
| 🟠 [qwen3-coder]:30b t=0.5 mode=native                                               | 29 (55%) | 1 (2%)   | 21 (40%) | 0        | 2 (4%)    |      53 |
| 🟠 [qwen3-coder]:30b mode=native                                                     | 29 (55%) | 1 (2%)   | 23 (43%) | 0        | 0         |      53 |
| 🟠 [unsloth/GLM-4.5-Air-GGUF]:Q4_K_M mode=markdown                                   | 29 (55%) | 1 (2%)   | 8 (15%)  | 11 (21%) | 4 (8%)    |      53 |
| 🟠 [unsloth/MiniMax-M2-GGUF]:Q4_K_M mode=markdown                                    | 29 (55%) | 0        | 20 (38%) | 3 (6%)   | 1 (2%)    |      53 |
| 🟠 [qwen3-coder]:30b t=1.5 mode=native                                               | 28 (53%) | 2 (4%)   | 22 (42%) | 0        | 1 (2%)    |      53 |
| 🟠 [gpt-oss]:latest mode=native                                                      | 28 (53%) | 1 (2%)   | 20 (38%) | 0        | 4 (8%)    |      53 |
| 🟠 [unsloth/Qwen3-4B-Thinking-2507-GGUF]:F16 mode=native                             | 28 (53%) | 0        | 20 (38%) | 3 (6%)   | 2 (4%)    |      53 |
| 🟠 [unsloth/Qwen3-235B-A22B-GGUF]:Q4_K_M mode=native                                 | 28 (53%) | 0        | 17 (32%) | 4 (8%)   | 4 (8%)    |      53 |
| 🟠 [unsloth/cogito-v2-preview-llama-70B-GGUF]:Q4_K_M mode=markdown                   | 27 (51%) | 3 (6%)   | 15 (28%) | 3 (6%)   | 5 (9%)    |      53 |
| 🟠 [unsloth/Qwen3-4B-Thinking-2507-GGUF]:F16 mode=markdown                           | 27 (51%) | 0        | 15 (28%) | 3 (6%)   | 8 (15%)   |      53 |
| 🟠 [unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF]:Q4_K_M mode=native                    | 26 (49%) | 3 (6%)   | 20 (38%) | 3 (6%)   | 1 (2%)    |      53 |
| 🟠 [unsloth/Qwen3-30B-A3B-GGUF]:BF16 mode=native                                     | 26 (49%) | 2 (4%)   | 19 (36%) | 4 (8%)   | 2 (4%)    |      53 |
| 🟠 [unsloth/Qwen3-235B-A22B-GGUF]:Q4_K_M mode=markdown                               | 26 (49%) | 1 (2%)   | 13 (25%) | 4 (8%)   | 9 (17%)   |      53 |
| 🟠 [unsloth/Qwen3-4B-Thinking-2507-GGUF]:Q4_K_M mode=native                          | 26 (49%) | 0        | 18 (34%) | 4 (8%)   | 5 (9%)    |      53 |
| 🟠 [unsloth/cogito-v2-preview-llama-405B-GGUF]:Q4_K_M mode=markdown                  | 25 (47%) | 2 (4%)   | 5 (9%)   | 3 (6%)   | 18 (34%)  |      53 |
| 🟠 [unsloth/Qwen3-30B-A3B-GGUF]:Q4_K_M mode=native                                   | 25 (47%) | 2 (4%)   | 18 (34%) | 6 (11%)  | 2 (4%)    |      53 |
| 🟠 [qwen3-coder]:30b t=1.0 mode=native                                               | 25 (47%) | 0        | 28 (53%) | 0        | 0         |      53 |
| 🟠 [unsloth/granite-4.0-h-small-GGUF]:Q4_K_M mode=native                             | 24 (45%) | 1 (2%)   | 21 (40%) | 4 (8%)   | 3 (6%)    |      53 |
| 🟠 [unsloth/Qwen3-4B-Thinking-2507-GGUF]:Q4_K_M mode=markdown                        | 24 (45%) | 0        | 23 (43%) | 4 (8%)   | 2 (4%)    |      53 |
| 🟠 [qwen3]:32b mode=native                                                           | 23 (43%) | 3 (6%)   | 8 (15%)  | 0        | 19 (36%)  |      53 |
| 🟠 [qwen3-coder]:30b t=2.0 mode=native                                               | 23 (43%) | 1 (2%)   | 29 (55%) | 0        | 0         |      53 |
| 🟠 [unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF]:Q4_K_M mode=native                     | 22 (42%) | 4 (8%)   | 15 (28%) | 5 (9%)   | 7 (13%)   |      53 |
| 🟠 [unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF]:BF16 mode=markdown             | 22 (42%) | 3 (6%)   | 28 (53%) | 0        | 0         |      53 |
| 🟠 [qwen3]:latest mode=native                                                        | 22 (42%) | 2 (4%)   | 26 (49%) | 0        | 3 (6%)    |      53 |
| 🟠 [gpt-oss]:120b mode=native                                                        | 22 (42%) | 1 (2%)   | 21 (40%) | 0        | 9 (17%)   |      53 |
| 🟠 [qwen3-vl]:32b mode=native                                                        | 22 (42%) | 1 (2%)   | 8 (15%)  | 1 (2%)   | 21 (40%)  |      53 |
| 🟠 [NexaAI/qwen3vl-8B-Instruct-4bit-mlx] mode=markdown                               | 16 (41%) | 0        | 23 (59%) | 0        | 0         |      39 |
| 🟠 [qwen3]:14b mode=native                                                           | 21 (40%) | 2 (4%)   | 24 (45%) | 0        | 6 (11%)   |      53 |
| 🟠 [unsloth/MiniMax-M2-GGUF]:Q4_K_M mode=native                                      | 21 (40%) | 1 (2%)   | 14 (26%) | 3 (6%)   | 14 (26%)  |      53 |
| 🟠 [qwen3]:30b mode=native                                                           | 21 (40%) | 0        | 22 (42%) | 0        | 10 (19%)  |      53 |
| 🟠 [NexaAI/qwen3vl-8B-Thinking-4bit-mlx] mode=markdown                               | 15 (38%) | 0        | 23 (59%) | 1 (3%)   | 0         |      39 |
| 🟠 [unsloth/Qwen3-30B-A3B-GGUF]:BF16 mode=markdown                                   | 20 (38%) | 4 (8%)   | 23 (43%) | 3 (6%)   | 3 (6%)    |      53 |
| 🟠 [unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF]:Q4_K_M mode=markdown                   | 20 (38%) | 3 (6%)   | 23 (43%) | 4 (8%)   | 3 (6%)    |      53 |
| 🟠 [qwen3-vl]:8b mode=native                                                         | 20 (38%) | 2 (4%)   | 19 (36%) | 0        | 12 (23%)  |      53 |
| 🟠 [unsloth/gemma-3-12b-it-qat-GGUF]:Q4_K_M mode=native                              | 20 (38%) | 2 (4%)   | 20 (38%) | 1 (2%)   | 10 (19%)  |      53 |
| 🟠 [unsloth/Qwen3-4B-Instruct-2507-GGUF]:Q4_K_M mode=native                          | 20 (38%) | 2 (4%)   | 26 (49%) | 4 (8%)   | 1 (2%)    |      53 |
| 🟠 [qwen3]:4b mode=native                                                            | 20 (38%) | 1 (2%)   | 31 (58%) | 0        | 1 (2%)    |      53 |
| 🟠 [unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF]:Q4_K_M t=1.0 mode=markdown             | 19 (36%) | 4 (8%)   | 18 (34%) | 0        | 12 (23%)  |      53 |
| 🟠 [unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF]:Q4_K_M t=0.0 mode=markdown             | 19 (36%) | 4 (8%)   | 15 (28%) | 0        | 15 (28%)  |      53 |
| 🟠 [unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF]:UD-Q4_K_XL t=0.0 mode=markdown | 19 (36%) | 4 (8%)   | 22 (42%) | 0        | 8 (15%)   |      53 |
| 🟠 [unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF]:UD-Q4_K_XL t=0.5 mode=markdown | 19 (36%) | 4 (8%)   | 22 (42%) | 0        | 8 (15%)   |      53 |
| 🟠 [unsloth/GLM-4.6-GGUF]:Q4_K_M mode=markdown                                       | 19 (36%) | 3 (6%)   | 28 (53%) | 3 (6%)   | 0         |      53 |
| 🔴 [unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF]:UD-Q4_K_XL t=1.5 mode=markdown | 18 (34%) | 4 (8%)   | 28 (53%) | 0        | 3 (6%)    |      53 |
| 🔴 [unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF]:Q4_K_M t=2.0 mode=markdown             | 18 (34%) | 4 (8%)   | 23 (43%) | 1 (2%)   | 7 (13%)   |      53 |
| 🔴 [unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF]:Q4_K_M t=0.5 mode=markdown             | 18 (34%) | 3 (6%)   | 19 (36%) | 4 (8%)   | 9 (17%)   |      53 |
| 🔴 [NexaAI/qwen3vl-4B-Instruct-4bit-mlx]:4BIT mode=markdown                          | 18 (34%) | 3 (6%)   | 14 (26%) | 18 (34%) | 0         |      53 |
| 🔴 [unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF]:Q4_K_M t=1.5 mode=markdown             | 17 (32%) | 4 (8%)   | 23 (43%) | 0        | 9 (17%)   |      53 |
| 🔴 [qwen3-vl]:30b mode=native                                                        | 17 (32%) | 2 (4%)   | 24 (45%) | 0        | 10 (19%)  |      53 |
| 🔴 [qwen3]:1.7b mode=native                                                          | 17 (32%) | 2 (4%)   | 31 (58%) | 0        | 3 (6%)    |      53 |
| 🔴 [unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF]:UD-Q4_K_XL mode=native         | 17 (32%) | 2 (4%)   | 16 (30%) | 1 (2%)   | 17 (32%)  |      53 |
| 🔴 [qwen3]:30b mode=markdown                                                         | 17 (32%) | 1 (2%)   | 27 (51%) | 0        | 8 (15%)   |      53 |
| 🔴 [qwen3]:14b mode=markdown                                                         | 17 (32%) | 1 (2%)   | 30 (57%) | 0        | 5 (9%)    |      53 |
| 🔴 [unsloth/Magistral-Small-2509-GGUF]:UD-Q4_K_XL mode=native                        | 16 (30%) | 4 (8%)   | 28 (53%) | 1 (2%)   | 4 (8%)    |      53 |
| 🔴 [ibm-granite/granite-4.0-h-micro-GGUF]:Q4_K_M mode=native                         | 16 (30%) | 3 (6%)   | 30 (57%) | 4 (8%)   | 0         |      53 |
| 🔴 [unsloth/Qwen3-4B-Instruct-2507-GGUF]:F16 mode=native                             | 16 (30%) | 2 (4%)   | 13 (25%) | 22 (42%) | 0         |      53 |
| 🔴 [qwen3]:32b mode=markdown                                                         | 16 (30%) | 1 (2%)   | 23 (43%) | 0        | 13 (25%)  |      53 |
| 🔴 [NexaAI/qwen3vl-8B-Instruct-4bit-mlx]:4BIT mode=markdown                          | 16 (30%) | 1 (2%)   | 9 (17%)  | 24 (45%) | 3 (6%)    |      53 |
| 🔴 [unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF]:UD-Q4_K_XL t=1.0 mode=markdown | 15 (28%) | 3 (6%)   | 23 (43%) | 0        | 12 (23%)  |      53 |
| 🔴 [granite4]:3b mode=native                                                         | 15 (28%) | 3 (6%)   | 31 (58%) | 4 (8%)   | 0         |      53 |
| 🔴 [qwen3-vl]:4b mode=native                                                         | 15 (28%) | 2 (4%)   | 21 (40%) | 0        | 15 (28%)  |      53 |
| 🔴 [unsloth/Qwen3-4B-Instruct-2507-GGUF]:Q4_K_M mode=markdown                        | 14 (26%) | 2 (4%)   | 33 (62%) | 4 (8%)   | 0         |      53 |
| 🔴 [qwen3]:latest mode=markdown                                                      | 14 (26%) | 1 (2%)   | 36 (68%) | 0        | 2 (4%)    |      53 |
| 🔴 [NexaAI/gpt-oss-20b-MLX-4bit] mode=markdown                                       | 10 (26%) | 4 (10%)  | 23 (59%) | 0        | 2 (5%)    |      39 |
| 🔴 [unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF]:UD-Q4_K_XL t=2.0 mode=markdown | 13 (25%) | 3 (6%)   | 31 (58%) | 0        | 6 (11%)   |      53 |
| 🔴 [unsloth/Qwen3-30B-A3B-GGUF]:Q4_K_M mode=markdown                                 | 13 (25%) | 2 (4%)   | 24 (45%) | 4 (8%)   | 10 (19%)  |      53 |
| 🔴 [unsloth/gpt-oss-20b-GGUF]:Q4_K_M t=1.5 mode=native                               | 13 (25%) | 2 (4%)   | 33 (62%) | 5 (9%)   | 0         |      53 |
| 🔴 [qwen3]:4b mode=markdown                                                          | 13 (25%) | 1 (2%)   | 38 (72%) | 0        | 1 (2%)    |      53 |
| 🔴 [qwen3-coder]:30b mode=markdown                                                   | 13 (25%) | 0        | 40 (75%) | 0        | 0         |      53 |
| 🔴 [qwen2.5vl]:latest mode=markdown                                                  | 13 (25%) | 0        | 40 (75%) | 0        | 0         |      53 |
| 🔴 [gpt-oss]:latest mode=markdown                                                    | 13 (25%) | 0        | 39 (74%) | 1 (2%)   | 0         |      53 |
| 🔴 [llama3.2]:latest mode=native                                                     | 12 (23%) | 2 (4%)   | 39 (74%) | 0        | 0         |      53 |
| 🔴 [llama3]:latest mode=markdown                                                     | 12 (23%) | 0        | 41 (77%) | 0        | 0         |      53 |
| 🔴 [minicpm-v]:latest mode=markdown                                                  | 12 (23%) | 0        | 41 (77%) | 0        | 0         |      53 |
| 🔴 [deepseek-r1]:14b mode=markdown                                                   | 12 (23%) | 0        | 40 (75%) | 0        | 1 (2%)    |      53 |
| 🔴 [NexaAI/qwen3vl-8B-Thinking-4bit-mlx]:4BIT mode=native                            | 11 (21%) | 3 (6%)   | 38 (72%) | 1 (2%)   | 0         |      53 |
| 🔴 [unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF]:BF16 mode=native               | 11 (21%) | 3 (6%)   | 24 (45%) | 2 (4%)   | 13 (25%)  |      53 |
| 🔴 [llama3.2]:latest mode=markdown                                                   | 11 (21%) | 1 (2%)   | 41 (77%) | 0        | 0         |      53 |
| 🔴 [unsloth/Magistral-Small-2509-GGUF]:UD-Q4_K_XL mode=markdown                      | 11 (21%) | 1 (2%)   | 40 (75%) | 0        | 1 (2%)    |      53 |
| 🔴 [llama3.2-vision]:latest mode=markdown                                            | 11 (21%) | 1 (2%)   | 41 (77%) | 0        | 0         |      53 |
| 🔴 [unsloth/granite-4.0-h-small-GGUF]:Q4_K_M mode=markdown                           | 11 (21%) | 1 (2%)   | 36 (68%) | 4 (8%)   | 1 (2%)    |      53 |
| 🔴 [NexaAI/qwen3vl-8B-Instruct-4bit-mlx]:4BIT mode=native                            | 11 (21%) | 0        | 42 (79%) | 0        | 0         |      53 |
| 🔴 [NexaAI/Qwen3-4B-4bit-MLX] mode=markdown                                          | 8 (21%)  | 4 (10%)  | 26 (67%) | 0        | 1 (3%)    |      39 |
| 🔴 [qwen3]:0.6b mode=native                                                          | 10 (19%) | 4 (8%)   | 39 (74%) | 0        | 0         |      53 |
| 🔴 [unsloth/granite-4.0-h-tiny-GGUF]:Q4_K_M mode=markdown                            | 10 (19%) | 4 (8%)   | 17 (32%) | 4 (8%)   | 18 (34%)  |      53 |
| 🔴 [gemma3]:27b mode=markdown                                                        | 10 (19%) | 3 (6%)   | 40 (75%) | 0        | 0         |      53 |
| 🔴 [NexaAI/qwen3vl-4B-Thinking-4bit-mlx]:4BIT mode=native                            | 10 (19%) | 3 (6%)   | 38 (72%) | 2 (4%)   | 0         |      53 |
| 🔴 [unsloth/granite-4.0-h-tiny-GGUF]:Q4_K_M mode=native                              | 10 (19%) | 3 (6%)   | 30 (57%) | 4 (8%)   | 6 (11%)   |      53 |
| 🔴 [llama3.1]:70b mode=markdown                                                      | 10 (19%) | 2 (4%)   | 41 (77%) | 0        | 0         |      53 |
| 🔴 [magistral]:latest mode=markdown                                                  | 10 (19%) | 2 (4%)   | 39 (74%) | 0        | 2 (4%)    |      53 |
| 🔴 [llava-llama3]:latest mode=markdown                                               | 10 (19%) | 1 (2%)   | 42 (79%) | 0        | 0         |      53 |
| 🔴 [ibm-granite/granite-4.0-h-micro-GGUF]:Q4_K_M mode=markdown                       | 10 (19%) | 1 (2%)   | 38 (72%) | 4 (8%)   | 0         |      53 |
| 🔴 [llava]:latest mode=markdown                                                      | 10 (19%) | 0        | 43 (81%) | 0        | 0         |      53 |
| 🔴 [granite3-dense]:latest mode=native                                               | 10 (19%) | 0        | 43 (81%) | 0        | 0         |      53 |
| 🔴 [unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF]:UD-Q4_K_XL mode=markdown       | 9 (17%)  | 4 (8%)   | 39 (74%) | 0        | 1 (2%)    |      53 |
| 🔴 [NexaAI/qwen3vl-4B-Thinking-4bit-mlx]:4BIT mode=markdown                          | 9 (17%)  | 4 (8%)   | 28 (53%) | 12 (23%) | 0         |      53 |
| 🔴 [mistral-small3.2]:24b mode=native                                                | 9 (17%)  | 3 (6%)   | 27 (51%) | 0        | 14 (26%)  |      53 |
| 🔴 [magistral]:latest mode=native                                                    | 9 (17%)  | 3 (6%)   | 41 (77%) | 0        | 0         |      53 |
| 🔴 [llava-phi3]:latest mode=markdown                                                 | 9 (17%)  | 1 (2%)   | 43 (81%) | 0        | 0         |      53 |
| 🔴 [unsloth/GLM-4.6-GGUF]:Q4_K_M mode=native                                         | 9 (17%)  | 0        | 41 (77%) | 3 (6%)   | 0         |      53 |
| 🔴 [unsloth/gpt-oss-20b-GGUF]:F16 mode=markdown                                      | 9 (17%)  | 0        | 41 (77%) | 3 (6%)   | 0         |      53 |
| 🔴 [granite4]:350m mode=native                                                       | 9 (17%)  | 0        | 41 (77%) | 3 (6%)   | 0         |      53 |
| 🔴 [unsloth/GLM-4.5-Air-GGUF]:Q4_K_M mode=native                                     | 9 (17%)  | 0        | 41 (77%) | 3 (6%)   | 0         |      53 |
| 🔴 [LiquidAI/LFM2-8B-A1B-GGUF]:Q4_K_M mode=native                                    | 9 (17%)  | 0        | 32 (60%) | 4 (8%)   | 8 (15%)   |      53 |
| 🔴 [unsloth/gpt-oss-20b-GGUF]:Q4_K_M mode=markdown                                   | 9 (17%)  | 0        | 40 (75%) | 4 (8%)   | 0         |      53 |
| 🔴 [unsloth/gpt-oss-120b-GGUF]:F16 mode=markdown                                     | 9 (17%)  | 0        | 38 (72%) | 6 (11%)  | 0         |      53 |
| 🔴 [NexaAI/Qwen3-4B-4bit-MLX]:4BIT mode=native                                       | 8 (15%)  | 4 (8%)   | 37 (70%) | 4 (8%)   | 0         |      53 |
| 🔴 [NexaAI/qwen3vl-8B-Thinking-4bit-mlx]:4BIT mode=markdown                          | 8 (15%)  | 4 (8%)   | 33 (62%) | 8 (15%)  | 0         |      53 |
| 🔴 [llama2]:7b mode=markdown                                                         | 8 (15%)  | 1 (2%)   | 44 (83%) | 0        | 0         |      53 |
| 🔴 [qwen3]:1.7b mode=markdown                                                        | 8 (15%)  | 1 (2%)   | 43 (81%) | 0        | 1 (2%)    |      53 |
| 🔴 [granite3-dense]:latest mode=markdown                                             | 8 (15%)  | 1 (2%)   | 44 (83%) | 0        | 0         |      53 |
| 🔴 [mistral]:latest mode=markdown                                                    | 8 (15%)  | 1 (2%)   | 44 (83%) | 0        | 0         |      53 |
| 🔴 [qwen3]:0.6b mode=markdown                                                        | 8 (15%)  | 1 (2%)   | 44 (83%) | 0        | 0         |      53 |
| 🔴 [llama2]:latest mode=markdown                                                     | 8 (15%)  | 1 (2%)   | 44 (83%) | 0        | 0         |      53 |
| 🔴 [NexaAI/qwen3vl-4B-Instruct-4bit-mlx]:4BIT mode=native                            | 8 (15%)  | 1 (2%)   | 43 (81%) | 1 (2%)   | 0         |      53 |
| 🔴 [lmstudio-community/Qwen3-Coder-30B-A3B-Instruct-GGUF]:Q4_K_M mode=markdown       | 8 (15%)  | 1 (2%)   | 34 (64%) | 4 (8%)   | 6 (11%)   |      53 |
| 🔴 [gemma3]:latest mode=markdown                                                     | 8 (15%)  | 0        | 45 (85%) | 0        | 0         |      53 |
| 🔴 [gemma3]:12b mode=markdown                                                        | 8 (15%)  | 0        | 45 (85%) | 0        | 0         |      53 |
| 🔴 [unsloth/gpt-oss-120b-GGUF]:Q4_K_M mode=markdown                                  | 8 (15%)  | 0        | 40 (75%) | 5 (9%)   | 0         |      53 |
| 🔴 [gpt-oss]:120b mode=markdown                                                      | 8 (15%)  | 0        | 32 (60%) | 12 (23%) | 1 (2%)    |      53 |
| 🔥 [llama3.1]:70b mode=native                                                        | 7 (14%)  | 0        | 39 (80%) | 0        | 3 (6%)    |      49 |
| 🔥 [granite4]:1b mode=native                                                         | 7 (13%)  | 3 (6%)   | 34 (64%) | 9 (17%)  | 0         |      53 |
| 🔥 [qwen3-vl]:2b mode=native                                                         | 7 (13%)  | 1 (2%)   | 26 (49%) | 0        | 19 (36%)  |      53 |
| 🔥 [unsloth/cogito-v2-preview-llama-70B-GGUF]:Q4_K_M mode=native                     | 7 (13%)  | 0        | 43 (81%) | 3 (6%)   | 0         |      53 |
| 🔥 [ggml-org/Qwen2.5-Coder-7B-Q8_0-GGUF]:Q8_0 mode=markdown                          | 7 (13%)  | 0        | 18 (34%) | 4 (8%)   | 24 (45%)  |      53 |
| 🔥 [NexaAI/gpt-oss-20b-MLX-4bit]:4BIT mode=markdown                                  | 6 (11%)  | 2 (4%)   | 41 (77%) | 4 (8%)   | 0         |      53 |
| 🔥 [NexaAI/gpt-oss-20b-MLX-4bit]:4BIT mode=native                                    | 6 (11%)  | 2 (4%)   | 41 (77%) | 4 (8%)   | 0         |      53 |
| 🔥 [bakllava]:latest mode=markdown                                                   | 6 (11%)  | 1 (2%)   | 46 (87%) | 0        | 0         |      53 |
| 🔥 [unsloth/cogito-v2-preview-llama-405B-GGUF]:Q4_K_M mode=native                    | 6 (11%)  | 1 (2%)   | 36 (68%) | 3 (6%)   | 7 (13%)   |      53 |
| 🔥 [gemma3]:1b mode=markdown                                                         | 6 (11%)  | 1 (2%)   | 42 (79%) | 4 (8%)   | 0         |      53 |
| 🔥 [LiquidAI/LFM2-8B-A1B-GGUF]:Q4_K_M mode=markdown                                  | 6 (11%)  | 0        | 42 (79%) | 4 (8%)   | 1 (2%)    |      53 |
| 🔥 [unsloth/gemma-3-12b-it-qat-GGUF]:Q4_K_M mode=markdown                            | 6 (11%)  | 0        | 43 (81%) | 4 (8%)   | 0         |      53 |
| 🔥 [NexaAI/Qwen3-4B-4bit-MLX]:4BIT mode=markdown                                     | 5 (9%)   | 4 (8%)   | 14 (26%) | 30 (57%) | 0         |      53 |
| 🔥 [mistral]:latest mode=native                                                      | 5 (9%)   | 2 (4%)   | 46 (87%) | 0        | 0         |      53 |
| 🔥 [gemma3]:270m mode=markdown                                                       | 5 (9%)   | 1 (2%)   | 43 (81%) | 4 (8%)   | 0         |      53 |
| 🔥 [deepseek-r1]:latest mode=markdown                                                | 4 (8%)   | 0        | 15 (28%) | 0        | 34 (64%)  |      53 |
| 🔥 [unsloth/gpt-oss-20b-GGUF]:Q4_K_M t=2.0 mode=native                               | 2 (4%)   | 3 (6%)   | 41 (77%) | 5 (9%)   | 2 (4%)    |      53 |

## Task suites by models

| Model                                                                             | [smoketest]     | [hello]       | [basic_answers]   | [debug_fib]   | [smokeimages]   | [crapto]     | [patch_file]   |
|:----------------------------------------------------------------------------------|:----------------|:--------------|:------------------|:--------------|:----------------|:-------------|:---------------|
| [unsloth/gpt-oss-20b-GGUF]:F16 mode=native                                        | 💎 13/13 (100%) | 💎 4/4 (100%) | 🟡 4/5 (80%)      | 🟡 5/6 (83%)  | 🟠 2/5 (40%)    | 🟠 4/8 (50%) | 🟠 6/12 (50%)  |
| [unsloth/gpt-oss-120b-GGUF]:F16 mode=native                                       | 💎 13/13 (100%) | 💎 4/4 (100%) | 🟠 3/5 (60%)      | 💎 6/6 (100%) | 💀 0/5          | 🔴 2/8 (25%) | 🟡 10/12 (83%) |
| [unsloth/Qwen3-VL-235B-A22B-Instruct-GGUF]:Q4_K_M mode=markdown                   | 💎 13/13 (100%) | 💎 4/4 (100%) | 🟠 2/5 (40%)      | 💎 6/6 (100%) | 🟠 3/5 (60%)    | 🟠 4/8 (50%) | 🔴 4/12 (33%)  |
| [unsloth/Qwen3-VL-235B-A22B-Instruct-GGUF]:Q4_K_M mode=native                     | 💎 13/13 (100%) | 🟡 3/4 (75%)  | 🟠 2/5 (40%)      | 🟡 5/6 (83%)  | 🟠 3/5 (60%)    | 🟠 4/8 (50%) | 🟠 5/12 (42%)  |
| [unsloth/gpt-oss-20b-GGUF]:Q4_K_M t=1.0 mode=native                               | 🟢 12/13 (92%)  | 💎 4/4 (100%) | 🟡 4/5 (80%)      | 🟡 4/6 (67%)  | 🔴 1/5 (20%)    | 🟠 4/8 (50%) | 🟠 6/12 (50%)  |
| [unsloth/gpt-oss-20b-GGUF]:Q4_K_M t=0.5 mode=native                               | 🟢 12/13 (92%)  | 💎 4/4 (100%) | 🟡 4/5 (80%)      | 🟡 5/6 (83%)  | 💀 0/5          | 🟠 4/8 (50%) | 🟠 6/12 (50%)  |
| [unsloth/gpt-oss-20b-GGUF]:Q4_K_M mode=native                                     | 💎 13/13 (100%) | 💎 4/4 (100%) | 🟠 2/5 (40%)      | 🟡 4/6 (67%)  | 💀 0/5          | 🟠 3/8 (38%) | 🟡 8/12 (67%)  |
| [unsloth/gpt-oss-120b-GGUF]:Q4_K_M mode=native                                    | 🟢 12/13 (92%)  | 💎 4/4 (100%) | 🟡 4/5 (80%)      | 💎 6/6 (100%) | 🔴 1/5 (20%)    | 🔥 1/8 (12%) | 🟠 6/12 (50%)  |
| [unsloth/gpt-oss-20b-GGUF]:Q4_K_M t=0.0 mode=native                               | 🟡 11/13 (85%)  | 🟡 3/4 (75%)  | 🟡 4/5 (80%)      | 💎 6/6 (100%) | 💀 0/5          | 🟠 4/8 (50%) | 🟠 6/12 (50%)  |
| [unsloth/Qwen3-235B-A22B-Instruct-2507-GGUF]:Q4_K_M mode=native                   | 💎 13/13 (100%) | 💎 4/4 (100%) | 🟠 3/5 (60%)      | 🟡 4/6 (67%)  | 💀 0/5          | 🟡 6/8 (75%) | 🔴 3/12 (25%)  |
| [unsloth/Qwen3-235B-A22B-Instruct-2507-GGUF]:Q4_K_M mode=markdown                 | 💎 13/13 (100%) | 💎 4/4 (100%) | 🟠 2/5 (40%)      | 🟡 4/6 (67%)  | 💀 0/5          | 🟡 6/8 (75%) | 🔴 3/12 (25%)  |
| [unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF]:BF16 mode=native                      | 🟢 12/13 (92%)  | 💎 4/4 (100%) | 🟠 3/5 (60%)      | 🟠 3/6 (50%)  | 💀 0/5          | 🟠 3/8 (38%) | 🟠 7/12 (58%)  |
| [unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF]:Q4_K_M mode=markdown                  | 💎 13/13 (100%) | 🟡 3/4 (75%)  | 🟠 3/5 (60%)      | 🟡 4/6 (67%)  | 💀 0/5          | 🟠 3/8 (38%) | 🟠 5/12 (42%)  |
| [unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF]:BF16 mode=markdown                    | 💎 13/13 (100%) | 🟡 3/4 (75%)  | 🟠 3/5 (60%)      | 🟡 4/6 (67%)  | 💀 0/5          | 🟠 3/8 (38%) | 🟠 5/12 (42%)  |
| [qwen3-coder]:30b t=0.0 mode=native                                               | 💎 13/13 (100%) | 🟡 3/4 (75%)  | 🟠 3/5 (60%)      | 💀 0/6        | 💀 0/5          | 🟠 4/8 (50%) | 🟠 6/12 (50%)  |
| [qwen3-coder]:30b t=0.5 mode=native                                               | 🟢 12/13 (92%)  | 🟡 3/4 (75%)  | 🟡 4/5 (80%)      | 🔴 1/6 (17%)  | 💀 0/5          | 🟠 3/8 (38%) | 🟠 6/12 (50%)  |
| [qwen3-coder]:30b mode=native                                                     | 🟡 11/13 (85%)  | 🟡 3/4 (75%)  | 🟠 3/5 (60%)      | 🔴 1/6 (17%)  | 💀 0/5          | 🟠 4/8 (50%) | 🟠 7/12 (58%)  |
| [unsloth/GLM-4.5-Air-GGUF]:Q4_K_M mode=markdown                                   | 💎 13/13 (100%) | 🟡 3/4 (75%)  | 🟠 2/5 (40%)      | 🟡 4/6 (67%)  | 💀 0/5          | 🔴 2/8 (25%) | 🟠 5/12 (42%)  |
| [unsloth/MiniMax-M2-GGUF]:Q4_K_M mode=markdown                                    | 🟢 12/13 (92%)  | 🟠 2/4 (50%)  | 💎 5/5 (100%)     | 🔴 2/6 (33%)  | 🔴 1/5 (20%)    | 💀 0/8       | 🟠 7/12 (58%)  |
| [qwen3-coder]:30b t=1.5 mode=native                                               | 🟡 10/13 (77%)  | 💎 4/4 (100%) | 🟠 2/5 (40%)      | 🟠 3/6 (50%)  | 🔴 1/5 (20%)    | 🟠 3/8 (38%) | 🟠 5/12 (42%)  |
| [gpt-oss]:latest mode=native                                                      | 💎 13/13 (100%) | 🟡 3/4 (75%)  | 🟠 3/5 (60%)      | 🟠 3/6 (50%)  | 🟠 2/5 (40%)    | 🟠 4/8 (50%) | 💀 0/12        |
| [unsloth/Qwen3-4B-Thinking-2507-GGUF]:F16 mode=native                             | 💎 13/13 (100%) | 💎 4/4 (100%) | 🟡 4/5 (80%)      | 🔴 2/6 (33%)  | 💀 0/5          | 🟠 3/8 (38%) | 🔴 2/12 (17%)  |
| [unsloth/Qwen3-235B-A22B-GGUF]:Q4_K_M mode=native                                 | 🟢 12/13 (92%)  | 💎 4/4 (100%) | 💎 5/5 (100%)     | 🔴 1/6 (17%)  | 💀 0/5          | 🟠 3/8 (38%) | 🔴 3/12 (25%)  |
| [unsloth/cogito-v2-preview-llama-70B-GGUF]:Q4_K_M mode=markdown                   | 💎 13/13 (100%) | 🟡 3/4 (75%)  | 🟠 2/5 (40%)      | 🟡 4/6 (67%)  | 💀 0/5          | 🔴 2/8 (25%) | 🔴 3/12 (25%)  |
| [unsloth/Qwen3-4B-Thinking-2507-GGUF]:F16 mode=markdown                           | 💎 13/13 (100%) | 💎 4/4 (100%) | 💎 5/5 (100%)     | 💀 0/6        | 💀 0/5          | 🟠 3/8 (38%) | 🔴 2/12 (17%)  |
| [unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF]:Q4_K_M mode=native                    | 🟢 12/13 (92%)  | 💎 4/4 (100%) | 🟠 2/5 (40%)      | 🔴 2/6 (33%)  | 💀 0/5          | 🔴 2/8 (25%) | 🔴 4/12 (33%)  |
| [unsloth/Qwen3-30B-A3B-GGUF]:BF16 mode=native                                     | 🟢 12/13 (92%)  | 🟡 3/4 (75%)  | 🟠 3/5 (60%)      | 🟡 4/6 (67%)  | 🔴 1/5 (20%)    | 🟠 3/8 (38%) | 💀 0/12        |
| [unsloth/Qwen3-235B-A22B-GGUF]:Q4_K_M mode=markdown                               | 🟡 11/13 (85%)  | 💎 4/4 (100%) | 🟠 3/5 (60%)      | 🔴 2/6 (33%)  | 💀 0/5          | 🔴 2/8 (25%) | 🔴 4/12 (33%)  |
| [unsloth/Qwen3-4B-Thinking-2507-GGUF]:Q4_K_M mode=native                          | 🟡 11/13 (85%)  | 🟠 2/4 (50%)  | 💎 5/5 (100%)     | 🟠 3/6 (50%)  | 💀 0/5          | 🟠 3/8 (38%) | 🔴 2/12 (17%)  |
| [unsloth/cogito-v2-preview-llama-405B-GGUF]:Q4_K_M mode=markdown                  | 🟡 10/13 (77%)  | 🟡 3/4 (75%)  | 🟠 3/5 (60%)      | 💀 0/6        | 💀 0/5          | 🟠 3/8 (38%) | 🟠 6/12 (50%)  |
| [unsloth/Qwen3-30B-A3B-GGUF]:Q4_K_M mode=native                                   | 🟡 11/13 (85%)  | 💎 4/4 (100%) | 🟠 3/5 (60%)      | 🔴 2/6 (33%)  | 💀 0/5          | 🟠 3/8 (38%) | 🔴 2/12 (17%)  |
| [qwen3-coder]:30b t=1.0 mode=native                                               | 🟢 12/13 (92%)  | 🟡 3/4 (75%)  | 🟠 2/5 (40%)      | 💀 0/6        | 🔴 1/5 (20%)    | 🟠 3/8 (38%) | 🔴 4/12 (33%)  |
| [unsloth/granite-4.0-h-small-GGUF]:Q4_K_M mode=native                             | 🟢 12/13 (92%)  | 💎 4/4 (100%) | 🟡 4/5 (80%)      | 🔴 1/6 (17%)  | 💀 0/5          | 🔥 1/8 (12%) | 🔴 2/12 (17%)  |
| [unsloth/Qwen3-4B-Thinking-2507-GGUF]:Q4_K_M mode=markdown                        | 🟢 12/13 (92%)  | 🟡 3/4 (75%)  | 💎 5/5 (100%)     | 💀 0/6        | 💀 0/5          | 🔥 1/8 (12%) | 🔴 3/12 (25%)  |
| [qwen3]:32b mode=native                                                           | 🟢 12/13 (92%)  | 🟡 3/4 (75%)  | 🟠 2/5 (40%)      | 🔴 1/6 (17%)  | 💀 0/5          | 🔴 2/8 (25%) | 🔴 3/12 (25%)  |
| [qwen3-coder]:30b t=2.0 mode=native                                               | 🟡 10/13 (77%)  | 🟡 3/4 (75%)  | 🟠 2/5 (40%)      | 🔴 1/6 (17%)  | 🔴 1/5 (20%)    | 🟠 3/8 (38%) | 🔴 3/12 (25%)  |
| [unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF]:Q4_K_M mode=native                     | 💎 13/13 (100%) | 🔴 1/4 (25%)  | 🔴 1/5 (20%)      | 🟠 3/6 (50%)  | 💀 0/5          | 🟠 4/8 (50%) | 💀 0/12        |
| [unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF]:BF16 mode=markdown             | 🟡 11/13 (85%)  | 🟠 2/4 (50%)  | 🔴 1/5 (20%)      | 🟠 3/6 (50%)  | 🟠 2/5 (40%)    | 🟠 3/8 (38%) | 💀 0/12        |
| [qwen3]:latest mode=native                                                        | 🟢 12/13 (92%)  | 💎 4/4 (100%) | 🟠 3/5 (60%)      | 💀 0/6        | 🔴 1/5 (20%)    | 🔥 1/8 (12%) | 🔥 1/12 (8%)   |
| [gpt-oss]:120b mode=native                                                        | 🟢 12/13 (92%)  | 🟠 2/4 (50%)  | 🟠 3/5 (60%)      | 💀 0/6        | 🟠 3/5 (60%)    | 🔥 1/8 (12%) | 🔥 1/12 (8%)   |
| [qwen3-vl]:32b mode=native                                                        | 🟠 7/13 (54%)   | 🟡 3/4 (75%)  | 🟠 2/5 (40%)      | 💀 0/6        | 🟡 4/5 (80%)    | 🔴 2/8 (25%) | 🔴 4/12 (33%)  |
| [NexaAI/qwen3vl-8B-Instruct-4bit-mlx] mode=markdown                               | 🟡 11/13 (85%)  | 🟠 2/4 (50%)  | 🟠 3/5 (60%)      |               | 💀 0/5          |              | 💀 0/12        |
| [qwen3]:14b mode=native                                                           | 🟡 10/13 (77%)  | 🟡 3/4 (75%)  | 🟠 3/5 (60%)      | 🔴 1/6 (17%)  | 💀 0/5          | 🔥 1/8 (12%) | 🔴 3/12 (25%)  |
| [unsloth/MiniMax-M2-GGUF]:Q4_K_M mode=native                                      | 🟡 10/13 (77%)  | 🟡 3/4 (75%)  | 🔴 1/5 (20%)      | 🔴 1/6 (17%)  | 💀 0/5          | 🔥 1/8 (12%) | 🟠 5/12 (42%)  |
| [qwen3]:30b mode=native                                                           | 🟡 10/13 (77%)  | 🟡 3/4 (75%)  | 🟠 2/5 (40%)      | 🔴 1/6 (17%)  | 🔴 1/5 (20%)    | 🔴 2/8 (25%) | 🔴 2/12 (17%)  |
| [NexaAI/qwen3vl-8B-Thinking-4bit-mlx] mode=markdown                               | 🟢 12/13 (92%)  | 💀 0/4        | 🟠 2/5 (40%)      |               | 🔴 1/5 (20%)    |              | 💀 0/12        |
| [unsloth/Qwen3-30B-A3B-GGUF]:BF16 mode=markdown                                   | 💎 13/13 (100%) | 💎 4/4 (100%) | 🔴 1/5 (20%)      | 🔴 1/6 (17%)  | 💀 0/5          | 💀 0/8       | 🔥 1/12 (8%)   |
| [unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF]:Q4_K_M mode=markdown                   | 🟢 12/13 (92%)  | 🟠 2/4 (50%)  | 🟠 2/5 (40%)      | 💀 0/6        | 💀 0/5          | 🔴 2/8 (25%) | 🔴 2/12 (17%)  |
| [qwen3-vl]:8b mode=native                                                         | 🟠 6/13 (46%)   | 🟡 3/4 (75%)  | 🟠 3/5 (60%)      | 🔴 1/6 (17%)  | 🟠 2/5 (40%)    | 🔥 1/8 (12%) | 🔴 4/12 (33%)  |
| [unsloth/gemma-3-12b-it-qat-GGUF]:Q4_K_M mode=native                              | 🟢 12/13 (92%)  | 💎 4/4 (100%) | 🟠 3/5 (60%)      | 💀 0/6        | 🔴 1/5 (20%)    | 💀 0/8       | 💀 0/12        |
| [unsloth/Qwen3-4B-Instruct-2507-GGUF]:Q4_K_M mode=native                          | 💎 13/13 (100%) | 🟡 3/4 (75%)  | 🟠 3/5 (60%)      | 💀 0/6        | 💀 0/5          | 🔥 1/8 (12%) | 💀 0/12        |
| [qwen3]:4b mode=native                                                            | 💎 13/13 (100%) | 🟠 2/4 (50%)  | 🟠 2/5 (40%)      | 💀 0/6        | 🔴 1/5 (20%)    | 🔥 1/8 (12%) | 🔥 1/12 (8%)   |
| [unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF]:Q4_K_M t=1.0 mode=markdown             | 🟡 11/13 (85%)  | 🟠 2/4 (50%)  | 💀 0/5            | 🟠 3/6 (50%)  | 💀 0/5          | 🟠 3/8 (38%) | 💀 0/12        |
| [unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF]:Q4_K_M t=0.0 mode=markdown             | 🟠 8/13 (62%)   | 🟡 3/4 (75%)  | 💀 0/5            | 🟡 5/6 (83%)  | 💀 0/5          | 🟠 3/8 (38%) | 💀 0/12        |
| [unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF]:UD-Q4_K_XL t=0.0 mode=markdown | 🟡 11/13 (85%)  | 🟡 3/4 (75%)  | 💀 0/5            | 💀 0/6        | 🟡 4/5 (80%)    | 💀 0/8       | 🔥 1/12 (8%)   |
| [unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF]:UD-Q4_K_XL t=0.5 mode=markdown | 🟡 11/13 (85%)  | 🟡 3/4 (75%)  | 💀 0/5            | 💀 0/6        | 🟠 2/5 (40%)    | 💀 0/8       | 🔴 3/12 (25%)  |
| [unsloth/GLM-4.6-GGUF]:Q4_K_M mode=markdown                                       | 💎 13/13 (100%) | 🟠 2/4 (50%)  | 🟠 2/5 (40%)      | 💀 0/6        | 💀 0/5          | 🔴 2/8 (25%) | 💀 0/12        |
| [unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF]:UD-Q4_K_XL t=1.5 mode=markdown | 🟡 11/13 (85%)  | 💎 4/4 (100%) | 💀 0/5            | 💀 0/6        | 🟠 2/5 (40%)    | 💀 0/8       | 🔥 1/12 (8%)   |
| [unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF]:Q4_K_M t=2.0 mode=markdown             | 🟡 11/13 (85%)  | 🟠 2/4 (50%)  | 💀 0/5            | 🔴 2/6 (33%)  | 💀 0/5          | 🟠 3/8 (38%) | 💀 0/12        |
| [unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF]:Q4_K_M t=0.5 mode=markdown             | 🟢 12/13 (92%)  | 🔴 1/4 (25%)  | 💀 0/5            | 🟡 4/6 (67%)  | 💀 0/5          | 🔥 1/8 (12%) | 💀 0/12        |
| [NexaAI/qwen3vl-4B-Instruct-4bit-mlx]:4BIT mode=markdown                          | 💎 13/13 (100%) | 🔴 1/4 (25%)  | 🔴 1/5 (20%)      | 🔴 1/6 (17%)  | 💀 0/5          | 🔴 2/8 (25%) | 💀 0/12        |
| [unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF]:Q4_K_M t=1.5 mode=markdown             | 🟡 10/13 (77%)  | 🟠 2/4 (50%)  | 💀 0/5            | 🔴 2/6 (33%)  | 💀 0/5          | 🟠 3/8 (38%) | 💀 0/12        |
| [qwen3-vl]:30b mode=native                                                        | 🟡 9/13 (69%)   | 🔴 1/4 (25%)  | 🟠 3/5 (60%)      | 💀 0/6        | 🔴 1/5 (20%)    | 💀 0/8       | 🔴 3/12 (25%)  |
| [qwen3]:1.7b mode=native                                                          | 🟢 12/13 (92%)  | 🟡 3/4 (75%)  | 🟠 2/5 (40%)      | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF]:UD-Q4_K_XL mode=native         | 🟡 10/13 (77%)  | 🔴 1/4 (25%)  | 🔴 1/5 (20%)      | 🟠 3/6 (50%)  | 💀 0/5          | 🔥 1/8 (12%) | 🔥 1/12 (8%)   |
| [qwen3]:30b mode=markdown                                                         | 🟠 8/13 (62%)   | 🟠 2/4 (50%)  | 🟠 2/5 (40%)      | 💀 0/6        | 🔴 1/5 (20%)    | 🔥 1/8 (12%) | 🔴 3/12 (25%)  |
| [qwen3]:14b mode=markdown                                                         | 🟡 11/13 (85%)  | 💀 0/4        | 🟠 3/5 (60%)      | 🔴 1/6 (17%)  | 💀 0/5          | 💀 0/8       | 🔴 2/12 (17%)  |
| [unsloth/Magistral-Small-2509-GGUF]:UD-Q4_K_XL mode=native                        | 🟠 8/13 (62%)   | 🟠 2/4 (50%)  | 🔴 1/5 (20%)      | 🔴 1/6 (17%)  | 🟠 2/5 (40%)    | 🔴 2/8 (25%) | 💀 0/12        |
| [ibm-granite/granite-4.0-h-micro-GGUF]:Q4_K_M mode=native                         | 🟢 12/13 (92%)  | 🟡 3/4 (75%)  | 💀 0/5            | 🔴 1/6 (17%)  | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [unsloth/Qwen3-4B-Instruct-2507-GGUF]:F16 mode=native                             | 🟢 12/13 (92%)  | 💀 0/4        | 🟠 3/5 (60%)      | 💀 0/6        | 💀 0/5          | 💀 0/8       | 🔥 1/12 (8%)   |
| [qwen3]:32b mode=markdown                                                         | 🟡 10/13 (77%)  | 💀 0/4        | 🟠 3/5 (60%)      | 💀 0/6        | 💀 0/5          | 🔴 2/8 (25%) | 🔥 1/12 (8%)   |
| [NexaAI/qwen3vl-8B-Instruct-4bit-mlx]:4BIT mode=markdown                          | 🟠 8/13 (62%)   | 🟡 3/4 (75%)  | 🟠 3/5 (60%)      | 🔴 1/6 (17%)  | 🔴 1/5 (20%)    | 💀 0/8       | 💀 0/12        |
| [unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF]:UD-Q4_K_XL t=1.0 mode=markdown | 🟡 9/13 (69%)   | 🟡 3/4 (75%)  | 💀 0/5            | 🔴 1/6 (17%)  | 💀 0/5          | 💀 0/8       | 🔴 2/12 (17%)  |
| [granite4]:3b mode=native                                                         | 🟡 10/13 (77%)  | 🔴 1/4 (25%)  | 🟠 2/5 (40%)      | 💀 0/6        | 🟠 2/5 (40%)    | 💀 0/8       | 💀 0/12        |
| [qwen3-vl]:4b mode=native                                                         | 🟠 7/13 (54%)   | 🟡 3/4 (75%)  | 🟠 2/5 (40%)      | 💀 0/6        | 🔴 1/5 (20%)    | 🔥 1/8 (12%) | 🔥 1/12 (8%)   |
| [unsloth/Qwen3-4B-Instruct-2507-GGUF]:Q4_K_M mode=markdown                        | 🟡 11/13 (85%)  | 💀 0/4        | 🟠 3/5 (60%)      | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [qwen3]:latest mode=markdown                                                      | 🟡 10/13 (77%)  | 💀 0/4        | 🟠 3/5 (60%)      | 💀 0/6        | 💀 0/5          | 💀 0/8       | 🔥 1/12 (8%)   |
| [NexaAI/gpt-oss-20b-MLX-4bit] mode=markdown                                       | 🟡 10/13 (77%)  | 💀 0/4        | 💀 0/5            |               | 💀 0/5          |              | 💀 0/12        |
| [unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF]:UD-Q4_K_XL t=2.0 mode=markdown | 🟠 5/13 (38%)   | 💎 4/4 (100%) | 💀 0/5            | 💀 0/6        | 🟠 3/5 (60%)    | 💀 0/8       | 🔥 1/12 (8%)   |
| [unsloth/Qwen3-30B-A3B-GGUF]:Q4_K_M mode=markdown                                 | 🟡 9/13 (69%)   | 🔴 1/4 (25%)  | 🟠 2/5 (40%)      | 🔴 1/6 (17%)  | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [unsloth/gpt-oss-20b-GGUF]:Q4_K_M t=1.5 mode=native                               | 🟡 9/13 (69%)   | 🔴 1/4 (25%)  | 🟠 2/5 (40%)      | 💀 0/6        | 🔴 1/5 (20%)    | 💀 0/8       | 💀 0/12        |
| [qwen3]:4b mode=markdown                                                          | 🟠 7/13 (54%)   | 🔴 1/4 (25%)  | 🟠 2/5 (40%)      | 💀 0/6        | 🔴 1/5 (20%)    | 🔥 1/8 (12%) | 🔥 1/12 (8%)   |
| [qwen3-coder]:30b mode=markdown                                                   | 🟡 10/13 (77%)  | 💀 0/4        | 🟠 2/5 (40%)      | 💀 0/6        | 🔴 1/5 (20%)    | 💀 0/8       | 💀 0/12        |
| [qwen2.5vl]:latest mode=markdown                                                  | 🟠 8/13 (62%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 🟡 4/5 (80%)    | 💀 0/8       | 💀 0/12        |
| [gpt-oss]:latest mode=markdown                                                    | 🟡 9/13 (69%)   | 🔴 1/4 (25%)  | 🟠 2/5 (40%)      | 💀 0/6        | 🔴 1/5 (20%)    | 💀 0/8       | 💀 0/12        |
| [llama3.2]:latest mode=native                                                     | 🟡 9/13 (69%)   | 🔴 1/4 (25%)  | 🔴 1/5 (20%)      | 💀 0/6        | 🔴 1/5 (20%)    | 💀 0/8       | 💀 0/12        |
| [llama3]:latest mode=markdown                                                     | 🟠 8/13 (62%)   | 💀 0/4        | 🟠 2/5 (40%)      | 💀 0/6        | 🟠 2/5 (40%)    | 💀 0/8       | 💀 0/12        |
| [minicpm-v]:latest mode=markdown                                                  | 🟠 8/13 (62%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 🟠 3/5 (60%)    | 💀 0/8       | 💀 0/12        |
| [deepseek-r1]:14b mode=markdown                                                   | 🟠 8/13 (62%)   | 💀 0/4        | 🟠 2/5 (40%)      | 💀 0/6        | 🔴 1/5 (20%)    | 💀 0/8       | 🔥 1/12 (8%)   |
| [NexaAI/qwen3vl-8B-Thinking-4bit-mlx]:4BIT mode=native                            | 🟠 8/13 (62%)   | 💀 0/4        | 🟠 2/5 (40%)      | 💀 0/6        | 🔴 1/5 (20%)    | 💀 0/8       | 💀 0/12        |
| [unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF]:BF16 mode=native               | 🟠 6/13 (46%)   | 🟠 2/4 (50%)  | 💀 0/5            | 🔴 1/6 (17%)  | 💀 0/5          | 💀 0/8       | 🔴 2/12 (17%)  |
| [llama3.2]:latest mode=markdown                                                   | 🟡 9/13 (69%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 🔴 1/5 (20%)    | 💀 0/8       | 💀 0/12        |
| [unsloth/Magistral-Small-2509-GGUF]:UD-Q4_K_XL mode=markdown                      | 🟠 7/13 (54%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 🟠 2/5 (40%)    | 💀 0/8       | 🔥 1/12 (8%)   |
| [llama3.2-vision]:latest mode=markdown                                            | 🟠 7/13 (54%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 🟠 3/5 (60%)    | 💀 0/8       | 💀 0/12        |
| [unsloth/granite-4.0-h-small-GGUF]:Q4_K_M mode=markdown                           | 🟠 7/13 (54%)   | 🟠 2/4 (50%)  | 🔴 1/5 (20%)      | 💀 0/6        | 💀 0/5          | 💀 0/8       | 🔥 1/12 (8%)   |
| [NexaAI/qwen3vl-8B-Instruct-4bit-mlx]:4BIT mode=native                            | 🟠 8/13 (62%)   | 💀 0/4        | 🟠 2/5 (40%)      | 💀 0/6        | 🔴 1/5 (20%)    | 💀 0/8       | 💀 0/12        |
| [NexaAI/Qwen3-4B-4bit-MLX] mode=markdown                                          | 🟠 7/13 (54%)   | 💀 0/4        | 🔴 1/5 (20%)      |               | 💀 0/5          |              | 💀 0/12        |
| [qwen3]:0.6b mode=native                                                          | 🟠 8/13 (62%)   | 🔴 1/4 (25%)  | 💀 0/5            | 💀 0/6        | 🔴 1/5 (20%)    | 💀 0/8       | 💀 0/12        |
| [unsloth/granite-4.0-h-tiny-GGUF]:Q4_K_M mode=markdown                            | 🟡 10/13 (77%)  | 💀 0/4        | 💀 0/5            | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [gemma3]:27b mode=markdown                                                        | 🟠 7/13 (54%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 🟠 2/5 (40%)    | 💀 0/8       | 💀 0/12        |
| [NexaAI/qwen3vl-4B-Thinking-4bit-mlx]:4BIT mode=native                            | 🟠 8/13 (62%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 🔴 1/5 (20%)    | 💀 0/8       | 💀 0/12        |
| [unsloth/granite-4.0-h-tiny-GGUF]:Q4_K_M mode=native                              | 🟡 9/13 (69%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [llama3.1]:70b mode=markdown                                                      | 🟠 8/13 (62%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 🔴 1/5 (20%)    | 💀 0/8       | 💀 0/12        |
| [magistral]:latest mode=markdown                                                  | 🟠 8/13 (62%)   | 💀 0/4        | 🟠 2/5 (40%)      | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [llava-llama3]:latest mode=markdown                                               | 🟠 7/13 (54%)   | 💀 0/4        | 💀 0/5            | 💀 0/6        | 🟠 3/5 (60%)    | 💀 0/8       | 💀 0/12        |
| [ibm-granite/granite-4.0-h-micro-GGUF]:Q4_K_M mode=markdown                       | 🟡 9/13 (69%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [llava]:latest mode=markdown                                                      | 🟠 6/13 (46%)   | 💀 0/4        | 💀 0/5            | 💀 0/6        | 🟡 4/5 (80%)    | 💀 0/8       | 💀 0/12        |
| [granite3-dense]:latest mode=native                                               | 🟠 7/13 (54%)   | 💀 0/4        | 🟠 2/5 (40%)      | 💀 0/6        | 🔴 1/5 (20%)    | 💀 0/8       | 💀 0/12        |
| [unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF]:UD-Q4_K_XL mode=markdown       | 🟠 7/13 (54%)   | 💀 0/4        | 💀 0/5            | 💀 0/6        | 🟠 2/5 (40%)    | 💀 0/8       | 💀 0/12        |
| [NexaAI/qwen3vl-4B-Thinking-4bit-mlx]:4BIT mode=markdown                          | 🟠 7/13 (54%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 🔴 1/5 (20%)    | 💀 0/8       | 💀 0/12        |
| [mistral-small3.2]:24b mode=native                                                | 🟠 6/13 (46%)   | 🟠 2/4 (50%)  | 🔴 1/5 (20%)      | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [magistral]:latest mode=native                                                    | 🟠 7/13 (54%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 🔴 1/5 (20%)    | 💀 0/8       | 💀 0/12        |
| [llava-phi3]:latest mode=markdown                                                 | 🟠 6/13 (46%)   | 💀 0/4        | 💀 0/5            | 💀 0/6        | 🟠 3/5 (60%)    | 💀 0/8       | 💀 0/12        |
| [unsloth/GLM-4.6-GGUF]:Q4_K_M mode=native                                         | 🟠 8/13 (62%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [unsloth/gpt-oss-20b-GGUF]:F16 mode=markdown                                      | 🟠 8/13 (62%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [granite4]:350m mode=native                                                       | 🟡 9/13 (69%)   | 💀 0/4        | 💀 0/5            | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [unsloth/GLM-4.5-Air-GGUF]:Q4_K_M mode=native                                     | 🟠 8/13 (62%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [LiquidAI/LFM2-8B-A1B-GGUF]:Q4_K_M mode=native                                    | 🟠 8/13 (62%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [unsloth/gpt-oss-20b-GGUF]:Q4_K_M mode=markdown                                   | 🟠 8/13 (62%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [unsloth/gpt-oss-120b-GGUF]:F16 mode=markdown                                     | 🟠 8/13 (62%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [NexaAI/Qwen3-4B-4bit-MLX]:4BIT mode=native                                       | 🟠 8/13 (62%)   | 💀 0/4        | 💀 0/5            | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [NexaAI/qwen3vl-8B-Thinking-4bit-mlx]:4BIT mode=markdown                          | 🟠 6/13 (46%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 🔴 1/5 (20%)    | 💀 0/8       | 💀 0/12        |
| [llama2]:7b mode=markdown                                                         | 🟠 7/13 (54%)   | 💀 0/4        | 💀 0/5            | 💀 0/6        | 🔴 1/5 (20%)    | 💀 0/8       | 💀 0/12        |
| [qwen3]:1.7b mode=markdown                                                        | 🟠 6/13 (46%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 🔴 1/5 (20%)    | 💀 0/8       | 💀 0/12        |
| [granite3-dense]:latest mode=markdown                                             | 🟠 6/13 (46%)   | 💀 0/4        | 🟠 2/5 (40%)      | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [mistral]:latest mode=markdown                                                    | 🟠 7/13 (54%)   | 💀 0/4        | 💀 0/5            | 💀 0/6        | 🔴 1/5 (20%)    | 💀 0/8       | 💀 0/12        |
| [qwen3]:0.6b mode=markdown                                                        | 🟠 7/13 (54%)   | 💀 0/4        | 💀 0/5            | 💀 0/6        | 🔴 1/5 (20%)    | 💀 0/8       | 💀 0/12        |
| [llama2]:latest mode=markdown                                                     | 🟠 7/13 (54%)   | 💀 0/4        | 💀 0/5            | 💀 0/6        | 🔴 1/5 (20%)    | 💀 0/8       | 💀 0/12        |
| [NexaAI/qwen3vl-4B-Instruct-4bit-mlx]:4BIT mode=native                            | 🟠 7/13 (54%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [lmstudio-community/Qwen3-Coder-30B-A3B-Instruct-GGUF]:Q4_K_M mode=markdown       | 🟠 5/13 (38%)   | 🔴 1/4 (25%)  | 💀 0/5            | 💀 0/6        | 💀 0/5          | 🔴 2/8 (25%) | 💀 0/12        |
| [gemma3]:latest mode=markdown                                                     | 🟠 6/13 (46%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 🔴 1/5 (20%)    | 💀 0/8       | 💀 0/12        |
| [gemma3]:12b mode=markdown                                                        | 🔴 4/13 (31%)   | 💀 0/4        | 💀 0/5            | 💀 0/6        | 🟡 4/5 (80%)    | 💀 0/8       | 💀 0/12        |
| [unsloth/gpt-oss-120b-GGUF]:Q4_K_M mode=markdown                                  | 🟠 8/13 (62%)   | 💀 0/4        | 💀 0/5            | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [gpt-oss]:120b mode=markdown                                                      | 🟠 7/13 (54%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [llama3.1]:70b mode=native                                                        | 🟠 5/13 (38%)   | 💀 0/4        | 💎 1/1 (100%)     | 💀 0/6        | 💀 0/5          | 💀 0/8       | 🔥 1/12 (8%)   |
| [granite4]:1b mode=native                                                         | 🔴 4/13 (31%)   | 🟠 2/4 (50%)  | 🔴 1/5 (20%)      | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [qwen3-vl]:2b mode=native                                                         | 🟠 5/13 (38%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 🔴 1/5 (20%)    | 💀 0/8       | 💀 0/12        |
| [unsloth/cogito-v2-preview-llama-70B-GGUF]:Q4_K_M mode=native                     | 🟠 6/13 (46%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [ggml-org/Qwen2.5-Coder-7B-Q8_0-GGUF]:Q8_0 mode=markdown                          | 🟠 6/13 (46%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [NexaAI/gpt-oss-20b-MLX-4bit]:4BIT mode=markdown                                  | 🟠 6/13 (46%)   | 💀 0/4        | 💀 0/5            | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [NexaAI/gpt-oss-20b-MLX-4bit]:4BIT mode=native                                    | 🟠 6/13 (46%)   | 💀 0/4        | 💀 0/5            | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [bakllava]:latest mode=markdown                                                   | 🔴 3/13 (23%)   | 💀 0/4        | 💀 0/5            | 💀 0/6        | 🟠 3/5 (60%)    | 💀 0/8       | 💀 0/12        |
| [unsloth/cogito-v2-preview-llama-405B-GGUF]:Q4_K_M mode=native                    | 🟠 6/13 (46%)   | 💀 0/4        | 💀 0/5            | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [gemma3]:1b mode=markdown                                                         | 🟠 6/13 (46%)   | 💀 0/4        | 💀 0/5            | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [LiquidAI/LFM2-8B-A1B-GGUF]:Q4_K_M mode=markdown                                  | 🟠 5/13 (38%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [unsloth/gemma-3-12b-it-qat-GGUF]:Q4_K_M mode=markdown                            | 🟠 5/13 (38%)   | 💀 0/4        | 🔴 1/5 (20%)      | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [NexaAI/Qwen3-4B-4bit-MLX]:4BIT mode=markdown                                     | 🟠 5/13 (38%)   | 💀 0/4        | 💀 0/5            | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [mistral]:latest mode=native                                                      | 🟠 5/13 (38%)   | 💀 0/4        | 💀 0/5            | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [gemma3]:270m mode=markdown                                                       | 🟠 5/13 (38%)   | 💀 0/4        | 💀 0/5            | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [deepseek-r1]:latest mode=markdown                                                | 🔴 4/13 (31%)   | 💀 0/4        | 💀 0/5            | 💀 0/6        | 💀 0/5          | 💀 0/8       | 💀 0/12        |
| [unsloth/gpt-oss-20b-GGUF]:Q4_K_M t=2.0 mode=native                               | 🔥 1/13 (8%)    | 💀 0/4        | 💀 0/5            | 💀 0/6        | 🔴 1/5 (20%)    | 💀 0/8       | 💀 0/12        |

## Predicted tokens by models

The average number of predicted tokens per execution that passed (PASS), and per non error execution (!ERROR). Do not compare models that do not share the same tasks. Not all experiments have this information yet.

| Model                                                                 |   tokens/passed |   tokens/nonerror | passed / nonerror   |
|:----------------------------------------------------------------------|----------------:|------------------:|:--------------------|
| [unsloth/gpt-oss-20b-GGUF]:F16 mode=native                            |             869 |              1261 | 38 / 50 (76%)       |
| [unsloth/gpt-oss-120b-GGUF]:F16 mode=native                           |            1047 |              1018 | 38 / 50 (76%)       |
| [unsloth/Qwen3-VL-235B-A22B-Instruct-GGUF]:Q4_K_M mode=native         |             281 |               396 | 35 / 53 (66%)       |
| [unsloth/gpt-oss-20b-GGUF]:Q4_K_M t=1.0 mode=native                   |            1054 |              1129 | 35 / 49 (71%)       |
| [unsloth/gpt-oss-20b-GGUF]:Q4_K_M t=0.5 mode=native                   |             700 |              1522 | 35 / 48 (73%)       |
| [unsloth/gpt-oss-20b-GGUF]:Q4_K_M mode=native                         |             691 |              1217 | 34 / 49 (69%)       |
| [unsloth/gpt-oss-120b-GGUF]:Q4_K_M mode=native                        |             639 |               808 | 34 / 49 (69%)       |
| [unsloth/gpt-oss-20b-GGUF]:Q4_K_M t=0.0 mode=native                   |             571 |              1141 | 34 / 49 (69%)       |
| [unsloth/Qwen3-235B-A22B-Instruct-2507-GGUF]:Q4_K_M mode=native       |             209 |               584 | 33 / 50 (66%)       |
| [qwen3-coder]:30b t=0.0 mode=native                                   |             387 |               528 | 29 / 53 (55%)       |
| [qwen3-coder]:30b t=0.5 mode=native                                   |             340 |               674 | 29 / 53 (55%)       |
| [unsloth/MiniMax-M2-GGUF]:Q4_K_M mode=markdown                        |             399 |               369 | 29 / 50 (58%)       |
| [qwen3-coder]:30b t=1.5 mode=native                                   |             513 |               846 | 28 / 53 (53%)       |
| [unsloth/Qwen3-235B-A22B-GGUF]:Q4_K_M mode=native                     |            1799 |              2654 | 28 / 49 (57%)       |
| [unsloth/Qwen3-30B-A3B-GGUF]:BF16 mode=native                         |            1695 |              2637 | 26 / 49 (53%)       |
| [unsloth/Qwen3-30B-A3B-GGUF]:Q4_K_M mode=native                       |            1563 |              2510 | 25 / 47 (53%)       |
| [qwen3-coder]:30b t=1.0 mode=native                                   |             344 |               721 | 25 / 53 (47%)       |
| [unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF]:Q4_K_M mode=native         |             246 |               842 | 22 / 48 (46%)       |
| [unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF]:BF16 mode=markdown |              66 |               109 | 22 / 53 (42%)       |
| [gpt-oss]:120b mode=native                                            |             310 |               547 | 22 / 53 (42%)       |
| [unsloth/MiniMax-M2-GGUF]:Q4_K_M mode=native                          |            1016 |              2305 | 21 / 50 (42%)       |
| [unsloth/GLM-4.6-GGUF]:Q4_K_M mode=markdown                           |             157 |               306 | 19 / 50 (38%)       |
| [NexaAI/qwen3vl-4B-Instruct-4bit-mlx]:4BIT mode=markdown              |             238 |               201 | 18 / 35 (51%)       |
| [unsloth/Qwen3-4B-Instruct-2507-GGUF]:F16 mode=native                 |             129 |               278 | 16 / 31 (52%)       |
| [granite4]:3b mode=native                                             |             159 |               268 | 15 / 49 (31%)       |
| [unsloth/Qwen3-4B-Instruct-2507-GGUF]:Q4_K_M mode=markdown            |              53 |                62 | 14 / 49 (29%)       |
| [NexaAI/qwen3vl-8B-Thinking-4bit-mlx]:4BIT mode=native                |            1488 |              1874 | 11 / 52 (21%)       |
| [NexaAI/qwen3vl-8B-Instruct-4bit-mlx]:4BIT mode=native                |              73 |               235 | 11 / 53 (21%)       |
| [NexaAI/qwen3vl-4B-Thinking-4bit-mlx]:4BIT mode=native                |            2057 |              2019 | 10 / 51 (20%)       |
| [llama3.1]:70b mode=markdown                                          |             199 |                97 | 10 / 53 (19%)       |
| [NexaAI/qwen3vl-4B-Thinking-4bit-mlx]:4BIT mode=markdown              |            1793 |              2060 | 9 / 41 (22%)        |
| [unsloth/GLM-4.6-GGUF]:Q4_K_M mode=native                             |             221 |               148 | 9 / 50 (18%)        |
| [unsloth/gpt-oss-20b-GGUF]:F16 mode=markdown                          |             165 |               105 | 9 / 50 (18%)        |
| [granite4]:350m mode=native                                           |             158 |               104 | 9 / 50 (18%)        |
| [unsloth/GLM-4.5-Air-GGUF]:Q4_K_M mode=native                         |             171 |               163 | 9 / 50 (18%)        |
| [unsloth/gpt-oss-20b-GGUF]:Q4_K_M mode=markdown                       |             127 |               146 | 9 / 49 (18%)        |
| [unsloth/gpt-oss-120b-GGUF]:F16 mode=markdown                         |             140 |                79 | 9 / 47 (19%)        |
| [NexaAI/Qwen3-4B-4bit-MLX]:4BIT mode=native                           |            1014 |              1077 | 8 / 49 (16%)        |
| [NexaAI/qwen3vl-8B-Thinking-4bit-mlx]:4BIT mode=markdown              |            1007 |              1675 | 8 / 45 (18%)        |
| [NexaAI/qwen3vl-4B-Instruct-4bit-mlx]:4BIT mode=native                |             412 |               701 | 8 / 52 (15%)        |
| [unsloth/gpt-oss-120b-GGUF]:Q4_K_M mode=markdown                      |             132 |                90 | 8 / 48 (17%)        |
| [llama3.1]:70b mode=native                                            |              58 |               100 | 7 / 49 (14%)        |
| [granite4]:1b mode=native                                             |             105 |               131 | 7 / 44 (16%)        |
| [unsloth/cogito-v2-preview-llama-70B-GGUF]:Q4_K_M mode=native         |             243 |               480 | 7 / 50 (14%)        |
| [NexaAI/gpt-oss-20b-MLX-4bit]:4BIT mode=markdown                      |             722 |              1902 | 6 / 49 (12%)        |
| [NexaAI/gpt-oss-20b-MLX-4bit]:4BIT mode=native                        |             739 |              1841 | 6 / 49 (12%)        |
| [gemma3]:1b mode=markdown                                             |              25 |                57 | 6 / 49 (12%)        |
| [NexaAI/Qwen3-4B-4bit-MLX]:4BIT mode=markdown                         |             916 |              1247 | 5 / 23 (22%)        |

## Conversation time by models

The average time in requests with the server. Because we used different servers with different GPU, and different load average, do not think too much about the absolute values.

| Model                                                                       |   s/passed |   s/nonerror | passed / nonerror   |
|:----------------------------------------------------------------------------|-----------:|-------------:|:--------------------|
| [unsloth/gpt-oss-20b-GGUF]:F16 mode=native                                  |          5 |           10 | 38 / 50 (76%)       |
| [unsloth/gpt-oss-120b-GGUF]:F16 mode=native                                 |         11 |           11 | 38 / 50 (76%)       |
| [unsloth/Qwen3-VL-235B-A22B-Instruct-GGUF]:Q4_K_M mode=markdown             |          7 |           10 | 36 / 53 (68%)       |
| [unsloth/Qwen3-VL-235B-A22B-Instruct-GGUF]:Q4_K_M mode=native               |          8 |           11 | 35 / 53 (66%)       |
| [unsloth/gpt-oss-20b-GGUF]:Q4_K_M t=1.0 mode=native                         |         13 |           14 | 35 / 49 (71%)       |
| [unsloth/gpt-oss-20b-GGUF]:Q4_K_M t=0.5 mode=native                         |          7 |           14 | 35 / 48 (73%)       |
| [unsloth/gpt-oss-20b-GGUF]:Q4_K_M mode=native                               |         10 |           17 | 34 / 49 (69%)       |
| [unsloth/gpt-oss-120b-GGUF]:Q4_K_M mode=native                              |          8 |            9 | 34 / 49 (69%)       |
| [unsloth/gpt-oss-20b-GGUF]:Q4_K_M t=0.0 mode=native                         |          5 |           10 | 34 / 49 (69%)       |
| [unsloth/Qwen3-235B-A22B-Instruct-2507-GGUF]:Q4_K_M mode=native             |          5 |           13 | 33 / 50 (66%)       |
| [unsloth/Qwen3-235B-A22B-Instruct-2507-GGUF]:Q4_K_M mode=markdown           |          7 |           18 | 32 / 50 (64%)       |
| [unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF]:Q4_K_M mode=markdown            |          3 |            6 | 31 / 50 (62%)       |
| [unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF]:BF16 mode=markdown              |          7 |           14 | 31 / 50 (62%)       |
| [qwen3-coder]:30b t=0.0 mode=native                                         |          8 |           12 | 29 / 53 (55%)       |
| [qwen3-coder]:30b t=0.5 mode=native                                         |          7 |           12 | 29 / 53 (55%)       |
| [unsloth/MiniMax-M2-GGUF]:Q4_K_M mode=markdown                              |         14 |           14 | 29 / 50 (58%)       |
| [qwen3-coder]:30b t=1.5 mode=native                                         |         10 |           16 | 28 / 53 (53%)       |
| [unsloth/Qwen3-235B-A22B-GGUF]:Q4_K_M mode=native                           |         34 |           50 | 28 / 49 (57%)       |
| [unsloth/Qwen3-4B-Thinking-2507-GGUF]:F16 mode=markdown                     |         30 |           60 | 27 / 50 (54%)       |
| [unsloth/Qwen3-30B-A3B-GGUF]:BF16 mode=native                               |         11 |           18 | 26 / 49 (53%)       |
| [unsloth/Qwen3-30B-A3B-GGUF]:Q4_K_M mode=native                             |         21 |           31 | 25 / 47 (53%)       |
| [qwen3-coder]:30b t=1.0 mode=native                                         |          6 |           14 | 25 / 53 (47%)       |
| [unsloth/Qwen3-4B-Thinking-2507-GGUF]:Q4_K_M mode=markdown                  |         37 |           55 | 24 / 49 (49%)       |
| [qwen3-coder]:30b t=2.0 mode=native                                         |          9 |           15 | 23 / 53 (43%)       |
| [unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF]:Q4_K_M mode=native               |          7 |           26 | 22 / 48 (46%)       |
| [unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF]:BF16 mode=markdown       |          8 |            9 | 22 / 53 (42%)       |
| [gpt-oss]:120b mode=native                                                  |         27 |           55 | 22 / 53 (42%)       |
| [unsloth/MiniMax-M2-GGUF]:Q4_K_M mode=native                                |         42 |           70 | 21 / 50 (42%)       |
| [unsloth/Qwen3-30B-A3B-GGUF]:BF16 mode=markdown                             |         11 |           27 | 20 / 50 (40%)       |
| [unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF]:Q4_K_M mode=markdown             |          3 |           10 | 20 / 49 (41%)       |
| [qwen3-vl]:8b mode=native                                                   |         65 |           75 | 20 / 53 (38%)       |
| [unsloth/GLM-4.6-GGUF]:Q4_K_M mode=markdown                                 |         13 |           17 | 19 / 50 (38%)       |
| [NexaAI/qwen3vl-4B-Instruct-4bit-mlx]:4BIT mode=markdown                    |          8 |            6 | 18 / 35 (51%)       |
| [qwen3-vl]:30b mode=native                                                  |         51 |           72 | 17 / 53 (32%)       |
| [unsloth/Qwen3-4B-Instruct-2507-GGUF]:F16 mode=native                       |          0 |            1 | 16 / 31 (52%)       |
| [NexaAI/qwen3vl-8B-Instruct-4bit-mlx]:4BIT mode=markdown                    |          4 |           22 | 16 / 29 (55%)       |
| [granite4]:3b mode=native                                                   |          3 |            4 | 15 / 49 (31%)       |
| [unsloth/Qwen3-4B-Instruct-2507-GGUF]:Q4_K_M mode=markdown                  |          1 |            1 | 14 / 49 (29%)       |
| [unsloth/Qwen3-30B-A3B-GGUF]:Q4_K_M mode=markdown                           |          7 |           10 | 13 / 49 (27%)       |
| [unsloth/gpt-oss-20b-GGUF]:Q4_K_M t=1.5 mode=native                         |         12 |           41 | 13 / 48 (27%)       |
| [gpt-oss]:latest mode=markdown                                              |          7 |            6 | 13 / 52 (25%)       |
| [NexaAI/qwen3vl-8B-Thinking-4bit-mlx]:4BIT mode=native                      |         26 |           31 | 11 / 52 (21%)       |
| [unsloth/granite-4.0-h-small-GGUF]:Q4_K_M mode=markdown                     |          6 |           15 | 11 / 49 (22%)       |
| [NexaAI/qwen3vl-8B-Instruct-4bit-mlx]:4BIT mode=native                      |          2 |            4 | 11 / 53 (21%)       |
| [NexaAI/qwen3vl-4B-Thinking-4bit-mlx]:4BIT mode=native                      |         25 |           23 | 10 / 51 (20%)       |
| [llama3.1]:70b mode=markdown                                                |         28 |           21 | 10 / 53 (19%)       |
| [unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF]:UD-Q4_K_XL mode=markdown |          2 |            3 | 9 / 53 (17%)        |
| [NexaAI/qwen3vl-4B-Thinking-4bit-mlx]:4BIT mode=markdown                    |         27 |           26 | 9 / 41 (22%)        |
| [unsloth/GLM-4.6-GGUF]:Q4_K_M mode=native                                   |          6 |            4 | 9 / 50 (18%)        |
| [unsloth/gpt-oss-20b-GGUF]:F16 mode=markdown                                |          1 |            0 | 9 / 50 (18%)        |
| [granite4]:350m mode=native                                                 |          1 |            1 | 9 / 50 (18%)        |
| [unsloth/GLM-4.5-Air-GGUF]:Q4_K_M mode=native                               |          2 |            2 | 9 / 50 (18%)        |
| [unsloth/gpt-oss-20b-GGUF]:Q4_K_M mode=markdown                             |          1 |            1 | 9 / 49 (18%)        |
| [unsloth/gpt-oss-120b-GGUF]:F16 mode=markdown                               |          0 |            0 | 9 / 47 (19%)        |
| [NexaAI/Qwen3-4B-4bit-MLX]:4BIT mode=native                                 |         11 |           11 | 8 / 49 (16%)        |
| [NexaAI/qwen3vl-8B-Thinking-4bit-mlx]:4BIT mode=markdown                    |         28 |           31 | 8 / 45 (18%)        |
| [NexaAI/qwen3vl-4B-Instruct-4bit-mlx]:4BIT mode=native                      |          5 |            8 | 8 / 52 (15%)        |
| [unsloth/gpt-oss-120b-GGUF]:Q4_K_M mode=markdown                            |          1 |            1 | 8 / 48 (17%)        |
| [llama3.1]:70b mode=native                                                  |         48 |           38 | 7 / 49 (14%)        |
| [granite4]:1b mode=native                                                   |          2 |            2 | 7 / 44 (16%)        |
| [unsloth/cogito-v2-preview-llama-70B-GGUF]:Q4_K_M mode=native               |          8 |           17 | 7 / 50 (14%)        |
| [NexaAI/gpt-oss-20b-MLX-4bit]:4BIT mode=markdown                            |         10 |           23 | 6 / 49 (12%)        |
| [NexaAI/gpt-oss-20b-MLX-4bit]:4BIT mode=native                              |         10 |           23 | 6 / 49 (12%)        |
| [gemma3]:1b mode=markdown                                                   |          2 |            2 | 6 / 49 (12%)        |
| [unsloth/gemma-3-12b-it-qat-GGUF]:Q4_K_M mode=markdown                      |          6 |           10 | 6 / 49 (12%)        |
| [NexaAI/Qwen3-4B-4bit-MLX]:4BIT mode=markdown                               |          9 |           16 | 5 / 23 (22%)        |
| [unsloth/gpt-oss-20b-GGUF]:Q4_K_M t=2.0 mode=native                         |         60 |           67 | 2 / 48 (4%)         |

## Results by task suites

| Task suite         | PASS       | ALMOST    | FAIL       | ERROR     | TIMEOUT   |   Total |
|:-------------------|:-----------|:----------|:-----------|:----------|:----------|--------:|
| 🟡 [smoketest]     | 1381 (70%) | 0         | 459 (23%)  | 47 (2%)   | 76 (4%)   |    1963 |
| 🟠 [hello]         | 229 (38%)  | 0         | 323 (53%)  | 14 (2%)   | 38 (6%)   |     604 |
| 🔴 [basic_answers] | 242 (32%)  | 245 (33%) | 231 (31%)  | 2 (0%)    | 31 (4%)   |     751 |
| 🔴 [debug_fib]     | 141 (16%)  | 0         | 631 (72%)  | 32 (4%)   | 78 (9%)   |     882 |
| 🔥 [smokeimages]   | 111 (15%)  | 0         | 385 (51%)  | 226 (30%) | 33 (4%)   |     755 |
| 🔥 [crapto]        | 155 (13%)  | 0         | 851 (72%)  | 40 (3%)   | 130 (11%) |    1176 |
| 🔥 [patch_file]    | 211 (12%)  | 0         | 1388 (77%) | 29 (2%)   | 184 (10%) |    1812 |

## Results by tasks

| Task                                | PASS      | ALMOST   | FAIL      | ERROR    | TIMEOUT   |   Total |
|:------------------------------------|:----------|:---------|:----------|:---------|:----------|--------:|
| 🟢 [smoketest] 03                   | 140 (93%) | 0        | 5 (3%)    | 4 (3%)   | 2 (1%)    |     151 |
| 🟢 [smoketest] 05                   | 136 (90%) | 0        | 6 (4%)    | 1 (1%)   | 8 (5%)    |     151 |
| 🟢 [smoketest] 33                   | 135 (89%) | 0        | 12 (8%)   | 0        | 4 (3%)    |     151 |
| 🟢 [smoketest] 04                   | 130 (86%) | 0        | 18 (12%)  | 3 (2%)   | 0         |     151 |
| 🟡 [smoketest] 32                   | 128 (85%) | 0        | 16 (11%)  | 0        | 7 (5%)    |     151 |
| 🟡 [smoketest] 06                   | 124 (82%) | 0        | 15 (10%)  | 5 (3%)   | 7 (5%)    |     151 |
| 🟡 [smoketest] 01                   | 122 (81%) | 0        | 16 (11%)  | 4 (3%)   | 9 (6%)    |     151 |
| 🟠 [smoketest] 02                   | 94 (62%)  | 0        | 29 (19%)  | 11 (7%)  | 17 (11%)  |     151 |
| 🟠 [basic_answers] 0.paris          | 87 (58%)  | 46 (31%) | 9 (6%)    | 0        | 8 (5%)    |     150 |
| 🟠 [smoketest] 12                   | 84 (56%)  | 0        | 60 (40%)  | 5 (3%)   | 2 (1%)    |     151 |
| 🟠 [smoketest] 13                   | 76 (50%)  | 0        | 69 (46%)  | 3 (2%)   | 3 (2%)    |     151 |
| 🟠 [smoketest] 11                   | 76 (50%)  | 0        | 70 (46%)  | 4 (3%)   | 1 (1%)    |     151 |
| 🟠 [basic_answers] 4.fact           | 74 (49%)  | 11 (7%)  | 62 (41%)  | 0        | 4 (3%)    |     151 |
| 🟠 [smoketest] 10                   | 72 (48%)  | 0        | 71 (47%)  | 3 (2%)   | 5 (3%)    |     151 |
| 🟠 [hello] 03git                    | 68 (45%)  | 0        | 73 (48%)  | 2 (1%)   | 8 (5%)    |     151 |
| 🟠 [smoketest] 31                   | 64 (42%)  | 0        | 72 (48%)  | 4 (3%)   | 11 (7%)   |     151 |
| 🟠 [hello] 01world                  | 60 (40%)  | 0        | 84 (56%)  | 4 (3%)   | 3 (2%)    |     151 |
| 🟠 [hello] 02name                   | 57 (38%)  | 0        | 80 (53%)  | 3 (2%)   | 11 (7%)   |     151 |
| 🔴 [crapto] 10-base64               | 50 (34%)  | 0        | 89 (61%)  | 5 (3%)   | 3 (2%)    |     147 |
| 🔴 [smokeimages] 4                  | 49 (32%)  | 0        | 28 (19%)  | 64 (42%) | 10 (7%)   |     151 |
| 🔴 [hello] 04gitignore              | 44 (29%)  | 0        | 86 (57%)  | 5 (3%)   | 16 (11%)  |     151 |
| 🔴 [patch_file] 04ed                | 41 (27%)  | 0        | 94 (62%)  | 1 (1%)   | 15 (10%)  |     151 |
| 🔴 [crapto] 40-xor                  | 39 (27%)  | 0        | 90 (61%)  | 3 (2%)   | 15 (10%)  |     147 |
| 🔴 [crapto] 41-xor-nohint           | 38 (26%)  | 0        | 92 (63%)  | 5 (3%)   | 12 (8%)   |     147 |
| 🔴 [patch_file] 05python            | 38 (25%)  | 0        | 109 (72%) | 1 (1%)   | 3 (2%)    |     151 |
| 🔴 [basic_answers] 1.llme           | 33 (22%)  | 54 (36%) | 55 (37%)  | 0        | 8 (5%)    |     150 |
| 🔴 [patch_file] 00free              | 33 (22%)  | 0        | 111 (74%) | 1 (1%)   | 6 (4%)    |     151 |
| 🔴 [debug_fib] 01                   | 31 (21%)  | 0        | 103 (70%) | 2 (1%)   | 11 (7%)   |     147 |
| 🔴 [debug_fib] 04                   | 31 (21%)  | 0        | 107 (73%) | 4 (3%)   | 5 (3%)    |     147 |
| 🔴 [patch_file] 03patch             | 30 (20%)  | 0        | 102 (68%) | 4 (3%)   | 15 (10%)  |     151 |
| 🔴 [debug_fib] 02b                  | 28 (19%)  | 0        | 102 (69%) | 4 (3%)   | 13 (9%)   |     147 |
| 🔴 [debug_fib] 02                   | 25 (17%)  | 0        | 80 (54%)  | 13 (9%)  | 29 (20%)  |     147 |
| 🔴 [basic_answers] 3.llme           | 25 (17%)  | 66 (44%) | 54 (36%)  | 1 (1%)   | 4 (3%)    |     150 |
| 🔴 [basic_answers] 2.llme           | 23 (15%)  | 68 (45%) | 51 (34%)  | 1 (1%)   | 7 (5%)    |     150 |
| 🔥 [crapto] 20-b64-hex              | 21 (14%)  | 0        | 111 (76%) | 5 (3%)   | 10 (7%)   |     147 |
| 🔥 [smokeimages] 2                  | 19 (13%)  | 0        | 67 (44%)  | 63 (42%) | 2 (1%)    |     151 |
| 🔥 [debug_fib] 03                   | 18 (12%)  | 0        | 111 (76%) | 5 (3%)   | 13 (9%)   |     147 |
| 🔥 [patch_file] 11cat               | 18 (12%)  | 0        | 110 (73%) | 3 (2%)   | 20 (13%)  |     151 |
| 🔥 [smokeimages] 0                  | 18 (12%)  | 0        | 68 (45%)  | 63 (42%) | 2 (1%)    |     151 |
| 🔥 [smokeimages] 1                  | 16 (11%)  | 0        | 96 (64%)  | 35 (23%) | 4 (3%)    |     151 |
| 🔥 [patch_file] 02sed               | 14 (9%)   | 0        | 131 (87%) | 2 (1%)   | 4 (3%)    |     151 |
| 🔥 [patch_file] 01cat               | 10 (7%)   | 0        | 130 (86%) | 2 (1%)   | 9 (6%)    |     151 |
| 🔥 [smokeimages] 3                  | 9 (6%)    | 0        | 126 (83%) | 1 (1%)   | 15 (10%)  |     151 |
| 🔥 [patch_file] 13patch             | 9 (6%)    | 0        | 111 (74%) | 3 (2%)   | 28 (19%)  |     151 |
| 🔥 [debug_fib] 05                   | 8 (5%)    | 0        | 128 (87%) | 4 (3%)   | 7 (5%)    |     147 |
| 🔥 [patch_file] 10free              | 8 (5%)    | 0        | 120 (79%) | 3 (2%)   | 20 (13%)  |     151 |
| 🔥 [patch_file] 15python            | 6 (4%)    | 0        | 131 (87%) | 1 (1%)   | 13 (9%)   |     151 |
| 🔥 [crapto] 42-xor-nokey            | 3 (2%)    | 0        | 102 (69%) | 6 (4%)   | 36 (24%)  |     147 |
| 🔥 [crapto] 31-rot13-b64-hex-nohint | 2 (1%)    | 0        | 129 (88%) | 4 (3%)   | 12 (8%)   |     147 |
| 🔥 [crapto] 30-rot13-b64-hex        | 2 (1%)    | 0        | 123 (84%) | 6 (4%)   | 16 (11%)  |     147 |
| 🔥 [patch_file] 14ed                | 2 (1%)    | 0        | 115 (76%) | 4 (3%)   | 30 (20%)  |     151 |
| 🔥 [patch_file] 12sed               | 2 (1%)    | 0        | 124 (82%) | 4 (3%)   | 21 (14%)  |     151 |
| 💀 [crapto] 43-xor-nokey-nohint     | 0         | 0        | 115 (78%) | 6 (4%)   | 26 (18%)  |     147 |


  [LiquidAI/LFM2-8B-A1B-GGUF]: https://huggingface.co/LiquidAI/LFM2-8B-A1B-GGUF
  [NexaAI/Qwen3-4B-4bit-MLX]: https://huggingface.co/NexaAI/Qwen3-4B-4bit-MLX
  [NexaAI/gpt-oss-20b-MLX-4bit]: https://huggingface.co/NexaAI/gpt-oss-20b-MLX-4bit
  [NexaAI/qwen3vl-4B-Instruct-4bit-mlx]: https://huggingface.co/NexaAI/qwen3vl-4B-Instruct-4bit-mlx
  [NexaAI/qwen3vl-4B-Thinking-4bit-mlx]: https://huggingface.co/NexaAI/qwen3vl-4B-Thinking-4bit-mlx
  [NexaAI/qwen3vl-8B-Instruct-4bit-mlx]: https://huggingface.co/NexaAI/qwen3vl-8B-Instruct-4bit-mlx
  [NexaAI/qwen3vl-8B-Thinking-4bit-mlx]: https://huggingface.co/NexaAI/qwen3vl-8B-Thinking-4bit-mlx
  [bakllava]: https://ollama.com/library/bakllava
  [basic_answers]: tests/basic_answers.sh
  [crapto]: tests/crapto.sh
  [debug_fib]: tests/debug_fib.sh
  [deepseek-r1]: https://ollama.com/library/deepseek-r1
  [gemma3]: https://ollama.com/library/gemma3
  [ggml-org/Qwen2.5-Coder-7B-Q8_0-GGUF]: https://huggingface.co/ggml-org/Qwen2.5-Coder-7B-Q8_0-GGUF
  [gpt-oss]: https://ollama.com/library/gpt-oss
  [granite3-dense]: https://ollama.com/library/granite3-dense
  [granite4]: https://ollama.com/library/granite4
  [hello]: tests/hello.sh
  [ibm-granite/granite-4.0-h-micro-GGUF]: https://huggingface.co/ibm-granite/granite-4.0-h-micro-GGUF
  [llama2]: https://ollama.com/library/llama2
  [llama3]: https://ollama.com/library/llama3
  [llama3.1]: https://ollama.com/library/llama3.1
  [llama3.2]: https://ollama.com/library/llama3.2
  [llama3.2-vision]: https://ollama.com/library/llama3.2-vision
  [llava]: https://ollama.com/library/llava
  [llava-llama3]: https://ollama.com/library/llava-llama3
  [llava-phi3]: https://ollama.com/library/llava-phi3
  [lmstudio-community/Qwen3-Coder-30B-A3B-Instruct-GGUF]: https://huggingface.co/lmstudio-community/Qwen3-Coder-30B-A3B-Instruct-GGUF
  [magistral]: https://ollama.com/library/magistral
  [minicpm-v]: https://ollama.com/library/minicpm-v
  [mistral]: https://ollama.com/library/mistral
  [mistral-small3.2]: https://ollama.com/library/mistral-small3.2
  [patch_file]: tests/patch_file.sh
  [qwen2.5vl]: https://ollama.com/library/qwen2.5vl
  [qwen3]: https://ollama.com/library/qwen3
  [qwen3-coder]: https://ollama.com/library/qwen3-coder
  [qwen3-vl]: https://ollama.com/library/qwen3-vl
  [smokeimages]: tests/smokeimages.sh
  [smoketest]: tests/smoketest.sh
  [unsloth/GLM-4.5-Air-GGUF]: https://huggingface.co/unsloth/GLM-4.5-Air-GGUF
  [unsloth/GLM-4.6-GGUF]: https://huggingface.co/unsloth/GLM-4.6-GGUF
  [unsloth/Magistral-Small-2509-GGUF]: https://huggingface.co/unsloth/Magistral-Small-2509-GGUF
  [unsloth/MiniMax-M2-GGUF]: https://huggingface.co/unsloth/MiniMax-M2-GGUF
  [unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF]: https://huggingface.co/unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF
  [unsloth/Qwen3-235B-A22B-GGUF]: https://huggingface.co/unsloth/Qwen3-235B-A22B-GGUF
  [unsloth/Qwen3-235B-A22B-Instruct-2507-GGUF]: https://huggingface.co/unsloth/Qwen3-235B-A22B-Instruct-2507-GGUF
  [unsloth/Qwen3-30B-A3B-GGUF]: https://huggingface.co/unsloth/Qwen3-30B-A3B-GGUF
  [unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF]: https://huggingface.co/unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF
  [unsloth/Qwen3-4B-Instruct-2507-GGUF]: https://huggingface.co/unsloth/Qwen3-4B-Instruct-2507-GGUF
  [unsloth/Qwen3-4B-Thinking-2507-GGUF]: https://huggingface.co/unsloth/Qwen3-4B-Thinking-2507-GGUF
  [unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF]: https://huggingface.co/unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF
  [unsloth/Qwen3-VL-235B-A22B-Instruct-GGUF]: https://huggingface.co/unsloth/Qwen3-VL-235B-A22B-Instruct-GGUF
  [unsloth/cogito-v2-preview-llama-405B-GGUF]: https://huggingface.co/unsloth/cogito-v2-preview-llama-405B-GGUF
  [unsloth/cogito-v2-preview-llama-70B-GGUF]: https://huggingface.co/unsloth/cogito-v2-preview-llama-70B-GGUF
  [unsloth/gemma-3-12b-it-qat-GGUF]: https://huggingface.co/unsloth/gemma-3-12b-it-qat-GGUF
  [unsloth/gpt-oss-120b-GGUF]: https://huggingface.co/unsloth/gpt-oss-120b-GGUF
  [unsloth/gpt-oss-20b-GGUF]: https://huggingface.co/unsloth/gpt-oss-20b-GGUF
  [unsloth/granite-4.0-h-small-GGUF]: https://huggingface.co/unsloth/granite-4.0-h-small-GGUF
  [unsloth/granite-4.0-h-tiny-GGUF]: https://huggingface.co/unsloth/granite-4.0-h-tiny-GGUF
