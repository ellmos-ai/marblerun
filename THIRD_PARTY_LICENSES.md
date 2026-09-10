# Third-Party Licenses & Transparency Notice

> **Project:** `ellmos-ai/marblerun` (llmauto)  
> **Audited:** 2026-09-11  
> **Repository License:** [MIT License](LICENSE)  
> **Architecture & Privacy:** 100% Local-First, Zero-Egress by default, Unprivileged User-Mode (`RunAsInvoker`)

---

## Executive Summary & Compliance Assurance

`MarbleRun` (`llmauto`) is engineered with an uncompromising architectural principle: **zero mandatory runtime dependencies**. The entire core agent loop, chain runner, handoff snapshotting, and process lifecycle operate solely on Python standard library modules (`subprocess`, `json`, `pathlib`, `argparse`, `sys`, `time`, `os`, `signal`, `datetime`, `re`, `shutil`, `importlib`).

All direct, optional, and development dependencies utilized across `MarbleRun` are distributed under strictly **permissive open-source licenses** (MIT, Apache-2.0, PSFL). There are **zero copyleft, GPL, or AGPL dependencies**, ensuring maximum flexibility for local development, enterprise automation pipelines, and multi-agent systems.

Furthermore, `MarbleRun` guarantees:
1. **100% Local-First & Zero Egress (INV-LOCAL-01):** Agent orchestration and state handoffs occur entirely within local process boundaries. Zero telemetry, zero external tracking, and zero remote data transmission.
2. **Unprivileged User-Mode (`RunAsInvoker` / INV-SEC-02):** Executes safely in user space without requiring root or administrator elevation.
3. **Multi-Provider Fail-Closed (INV-GATE-03):** Unconfigured external backends fail closed without falling back to insecure endpoints.
4. **Race-Free Parallel Isolation (INV-SYNC-04):** Parallel worker runs use isolated snapshot workspaces to prevent state corruption.
5. **Anti-Starvation Skip Guard (INV-CONT-05):** Protects handoff files from accidental truncation or context overwriting.
6. **Transparent State Persistence (INV-STATE-06):** Human-readable plain text and Markdown state files (`status.txt`, `handoff.md`, `round_counter.txt`) eliminate proprietary lock-in.
7. **Shell-Free Invocation (INV-PROC-07):** Direct argument array execution (`shell=False`) eliminates command injection vulnerabilities.

---

## Runtime Dependency Matrix

| Package | Role / Functional Scope | License | Project Repository / Upstream |
|:---|:---|:---|:---|
| **Python Standard Library** | Core CLI runner, process supervision, handoff snapshots, state persistence, JSON configuration parsing | [PSFL-2.0](https://docs.python.org/3/license.html) | [python/cpython](https://github.com/python/cpython) |

---

## Optional & Provider Dependencies

| Package | Role / Functional Scope | License | Project Repository / Upstream |
|:---|:---|:---|:---|
| **coma** (optional) | Multi-provider LLM CLI orchestrator & adapter framework (Claude, Codex, Agy) | [MIT](https://github.com/dev-bricks/coma/blob/main/LICENSE) | [dev-bricks/coma](https://github.com/dev-bricks/coma) |

---

## Development & Quality Assurance Tooling

| Package | Usage & Purpose | License | Source / Upstream |
|:---|:---|:---|:---|
| **pytest** | Automated test runner, contract verification suites, mock fixtures | [MIT](https://github.com/pytest-dev/pytest/blob/main/LICENSE) | [pytest-dev/pytest](https://github.com/pytest-dev/pytest) |
| **ruff** | High-performance Python linter and code formatting enforcement | [MIT / Apache-2.0](https://github.com/astral-sh/ruff/blob/main/LICENSE-MIT) | [astral-sh/ruff](https://github.com/astral-sh/ruff) |
| **setuptools** | Standard package build backend (PEP 517 / PEP 621 compliant) | [MIT](https://github.com/pypa/setuptools/blob/main/LICENSE) | [pypa/setuptools](https://github.com/pypa/setuptools) |
| **setuptools-scm** | Dynamic version extraction from Git tags / attributes | [MIT](https://github.com/pypa/setuptools-scm/blob/main/LICENSE) | [pypa/setuptools-scm](https://github.com/pypa/setuptools-scm) |

---

## Full License Texts (Excerpts & Notices)

### 1. Python Software Foundation License Version 2 (PSFL-2.0)
Python standard library modules are used under the PSF License Agreement.  
Copyright (c) 2001-2026 Python Software Foundation. All rights reserved.

### 2. MIT License (MIT)
Used by `coma`, `pytest`, `ruff`, `setuptools`, and `setuptools-scm`.

> Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:  
>  
> The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.  
>  
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

### 3. Apache License Version 2.0 (Apache-2.0)
Co-licensed by `ruff`.

> Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at:  
> http://www.apache.org/licenses/LICENSE-2.0  
> Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
