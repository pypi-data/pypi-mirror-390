# Aristotle SDK

The Aristotle SDK is a Python library that provides tools and utilities for interacting with the Aristotle API, enabling automated theorem proving for Lean projects.


## Installation

```bash
pip install aristotlelib
```

## Quick Start

### 1. Set up your API key

```python
import aristotlelib

# Set your API key
aristotlelib.set_api_key("your-api-key-here")
# Or set it via environment variable
# export ARISTOTLE_API_KEY="your-api-key-here"
```

### 2. Set up the correct Lean Toolchain and Mathlib versions

Aristotle uses the following versions of Lean and Mathlib:

- **Lean Toolchain version**: `leanprover/lean4:v4.20.0-rc5`
- **Mathlib version**: `d62eab0cc36ea522904895389c301cf8d844fd69` (May 9, 2025)

If your project uses a different version of either, it might run into compatibility issues.

### 3. Setup Logging

The SDK uses Python's standard logging module. To see debug and info messages from the SDK, configure logging in your application:

```python
import logging

# Configure logging to see SDK messages
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s"
)

```

This will show helpful messages, like tracking how far along the proof is.

### 4. Prove a theorem from a file

The simplest way to use Aristotle is to prove a theorem from a Lean file:

```python
import asyncio
import aristotlelib

async def main():
    # Prove theorems from a Lean file
    solution_path = await aristotlelib.Project.prove_from_file("path/to/your/file.lean")
    print(f"Solution saved to: {solution_path}")

asyncio.run(main())
```

This will attempt to prove every sorry in your file and give you a file in response. It will automatically import the necessary files from your lean project.

You can also pass in the `output_file_path` to `prove_from_file` to specify where the output should go. There are many other parameters you can use; for more details, see below.

## Command Line Interface

You can also use Aristotle from the command line:

```bash
# Set your API key
export ARISTOTLE_API_KEY="your-api-key-here"

# Prove theorems from a file
aristotle prove-from-file path/to/theorem.lean

# Specify output file
aristotle prove-from-file path/to/theorem.lean --output-file solution.lean

# See all options
aristotle prove-from-file --help
```
There are several options available here, matching the arguments to the prove_from_file function. For more information, run the --help option.

## Features

### Guide Aristotle in English

You can provide natural language hints to guide Aristotle's proof search. Simply include your english proof sketch in the header comment of the theorem, tagged with "PROVIDED SOLUTION:". You can make your sketch as general or detailed as you want.

```lean
/--
  Given x, y ∈ [0, π/2], show that cos(sqrt(x ^ 2 + y ^ 2)) ≤ cos x * cos y.

  PROVIDED SOLUTION:
  Set r := sqrt(x^2 + y^2). If r > π/2, then the inquality holds trivially.
  So consider the case r ≤ π/2. Write x = r cos φ, y = r sin φ.
  Consider the function F(φ) := log(cos(r cos φ)) + log(cos(r sin φ)). Then
  F(0) = F(π/2) = log r, so it suffices to show that for F(φ) ≥ F(0) = F(π/2).
  The derivative of F is F'(φ) = r(sin φ tan(r cos φ) - cos φ tan(r * sin φ)).
  Define G(u) := tan u / u. The derivative of G on (0, π/2) is
  (u - sin u cos u) / (u ^ 2 * (cos u) ^ 2), which is nonnegative on (0, π/2),
  so G is increasing on (0, π/2).

  For φ in [0, π/4], we have r * cos φ ≥ r * sin φ, so by monotonicity of G,
  tan(r * cos φ)/(r * cos φ) ≥ tan(r * sin φ)/(r * sin φ). On [π/4, π/2],
  the inequality is reversed. Multiplying this by r^2 cos φ sin φ gives that
  F' is nonnegative on [0, π/4] and nonpositive on [π/4, π/2]. This means that
  for φ in [0, π/4], F(φ) ≥ F(0), and for φ in [π/4, π/2], F(φ) ≥ F(π/2),
  completing the proof.
-/
theorem final (x y : ℝ) (hx : 0 ≤ x) (hx' : x ≤ Real.pi / 2) (hy : 0 ≤ y) (hy' : y ≤ Real.pi / 2) :
    Real.cos (Real.sqrt (x ^ 2 + y ^ 2)) ≤ Real.cos x * Real.cos y := by
sorry
```

### Find Counterexamples and Negations Automatically

Aristotle can disprove statements and find counterexamples, helping you find logical errors, missed edge cases, or even misformalizations. When a statement is false, Aristotle will leave a comment on the theorem with a the counterexample for you to investigate.

```lean
/-
Aristotle found this block to be false.
Here is a proof of the negation:
theorem my_favorite_theorem (k : ℕ) :
  ∑' n : ℕ, (1 : ℝ) / Nat.choose (n + k + 1) n = 1 + 1 / k := by
    -- Wait, there's a mistake. We can actually prove the opposite.
    negate_state;
    -- Proof starts here:
    use 0; norm_num;
    erw [ tsum_eq_zero_of_not_summable ] <;> norm_num;
    exact_mod_cast mt ( summable_nat_add_iff 1 |> Iff.mp ) Real.not_summable_natCast_inv
-/
theorem my_favorite_theorem (k : ℕ) :
  ∑' n : ℕ, (1 : ℝ) / Nat.choose (n + k + 1) n = 1 + 1 / k := by
sorry
```

You can find code for the custom `negate_state` tactic automatically included in the file header, and below:

```lean
import Mathlib
open Lean Meta Elab Tactic in
elab "revert_all" : tactic => do
  let goals ← getGoals
  let mut newGoals : List MVarId := []
  for mvarId in goals do
    newGoals := newGoals.append [(← mvarId.revertAll)]
  setGoals newGoals

open Lean.Elab.Tactic in
macro "negate_state" : tactic => `(tactic|
  (
    guard_goal_nums 1
    revert_all
    refine @(((by admit) : ∀ {p : Prop}, ¬p → p) ?_)
    try push_neg
  )
)
```


### Integrate Aristotle Seamlessly into your Lean Projects

The simplest way to use Aristotle is to point Aristotle at a file, and let it automatically discover and read dependencies. `Project#prove_from_file` lets you solve in just one line of code.

```python
import asyncio
import aristotlelib

async def main():
    # Prove a theorem from a Lean file
    solution_path = await aristotlelib.Project.prove_from_file("path/to/your/file.lean")
    print(f"Solution saved to: {solution_path}")

asyncio.run(main())
```

For more control over the context available to Aristotle, you can manage dependencies manually. See the code snippet below for the suggested way to orchestrate `Project#create`, `Project#add_context`, and `Project#solve`.

```python
import asyncio
import aristotlelib
from pathlib import Path

async def main():
    # Create a new project
    project = await aristotlelib.Project.create()
    print(f"Created project: {project.project_id}")

    # Manually add files needed for import
    await project.add_context(["path/to/context1.lean", "path/to/context2.lean"])

    # Solve with input content
    await project.solve(input_content="theorem my_theorem : True := trivial")

    # Wait for completion and get solution
    while project.status not in [aristotlelib.ProjectStatus.COMPLETE, aristotlelib.ProjectStatus.FAILED]:
        await asyncio.sleep(30)  # Poll every 30 seconds
        await project.refresh()
        print(f"Status: {project.status}")

    if project.status == aristotlelib.ProjectStatus.COMPLETE:
        solution_path = await project.get_solution()
        print(f"Solution saved to: {solution_path}")

asyncio.run(main())
```

## API Reference

### Project Class

The main class for interacting with Aristotle projects.

#### `Project.create(context_file_paths=None, validate_lean_project_root=True)`

Create a new Aristotle project.

**Parameters:**
- `context_file_paths` (list[Path | str], optional): List of file paths to include for import (up to 10 at a time)
- `validate_lean_project_root` (bool): Whether to validate Lean project structure (recommended: True)

**Returns:** `Project` instance

#### `Project.prove_from_file(input_file_path, auto_add_imports=True, context_file_paths=None, validate_lean_project=True, wait_for_completion=True, polling_interval_seconds=30, max_polling_failures=3, output_file_path=None)`

Convenience method to prove a theorem from a file with automatic import resolution.

**Parameters:**
- `input_file_path` (Path | str): Path to the input Lean file
- `auto_add_imports` (bool): Automatically add imported files as context
- `context_file_paths` (list[Path | str], optional): Manual context files. Cannot be used with `auto_add_imports`.
- `validate_lean_project` (bool): Validate that this is a valid Lean project. Must be true if auto-adding imports.
- `wait_for_completion` (bool): Whether to wait for project completion before returning. If False, you will have to manually query for the status and results.
- `polling_interval_seconds` (int): Seconds to wait between status checks
- `max_polling_failures` (int): Max polling failures before requiring you to manually check for results.
- `output_file_path` (Path | str, optional): Desired path to the output Lean file.

**Returns:** `str` - Path to the solution file (as string), or the project id if wait_for_completion is False

#### `project.add_context(context_file_paths, batch_size=10, validate_lean_project_root=True)`

Add files used as imports to an existing project. You can add up to 10 per request, but can call this as many times as needed. Any time you import a non-standard library (e.g. a local file) it must be added here.

**Parameters:**
- `context_file_paths` (list[Path | str]): Files to add as context
- `batch_size` (int): Files to upload per batch (max 10)
- `validate_lean_project_root` (bool): Validate project structure

#### `project.solve(input_file_path=None, input_content=None)`

Solve the project with either a file or text.

**Parameters:**
- `input_file_path` (Path | str, optional): Path to input file
- `input_content` (str, optional): Text content to solve

**Note:** Exactly one of `input_file_path` or `input_content` must be provided.

#### `project.get_solution(output_path=None)`

Download the solution file, if one exists.

**Parameters:**
- `output_path` (Path | str, optional): Where to save the solution

**Returns:** `Path` to the downloaded solution file

#### `project.refresh()`

Refresh the project status from the API.

### Project Status

```python
class ProjectStatus(Enum):
    NOT_STARTED = "NOT_STARTED"
    QUEUED = "QUEUED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    PENDING_RETRY = "PENDING_RETRY"
```

**Status Descriptions:**

- **`NOT_STARTED`**: The project has been created but no solve request has been submitted yet. You need to call `project.solve()` to begin the theorem proving process.

- **`QUEUED`**: The solve request has been submitted and is waiting in the queue to be processed. The system will automatically start working on it when resources become available.

- **`IN_PROGRESS`**: Aristotle is actively working on proving the theorem. This status indicates that the automated theorem prover is running and attempting to find proofs.

- **`COMPLETE`**: Aristotle has completed your project! You can now call `project.get_solution()` to download the results.

- **`FAILED`**: There was an internal error. The team has already been notified.

- **`PENDING_RETRY`**: Aristotle detected an internal error it thinks should not happen again. These will be re-queued and put in progress again shortly.


### Error Handling

The SDK provides several exception types:

- `AristotleAPIError`: API-related errors
- `LeanProjectError`: Lean project validation errors

## Lean Project Requirements

Aristotle works best with properly structured Lean projects. Your project should have:

- A `lakefile.toml` configuration file or `lakefile.lean` (legacy)
- A `lean-toolchain` file
- Proper import structure

The SDK will automatically:
- Detect your project root
- Validate file paths are within the project
- Resolve imports to include dependencies
- Handle file size limits (100MB max per file)

## Examples

### Basic theorem proving

```python
import asyncio
import aristotlelib
import logging

async def prove_simple_theorem():
    # Set API key
    aristotlelib.set_api_key("your-key")

    # Set logging
    logging.basicConfig(
      level=logging.INFO,
      format="%(levelname)s - %(message)s"
  )

    # Prove a simple theorem and save it to output.lean # LAURA
    await aristotlelib.Project.prove_from_file("examples/simple.lean", output_file_path="examples/output.lean")

asyncio.run(prove_simple_theorem())
```

### Check status of existing projects

```python
import asyncio
import aristotlelib

async def get_project_status():
    # Load an existing project
    project = await aristotlelib.Project.from_id("existing-project-id")

    # Check status
    print(f"Project status: {project.status}")

    if project.status == aristotlelib.ProjectStatus.COMPLETE:
      # if complete, download the solution
      await project.get_solution(output_path="examples/output.lean")

asyncio.run(work_with_existing_project())
```

### Get all your projects

```python
import asyncio
import aristotlelib

async def list_projects():
    projects, pagination_key = await aristotlelib.Project.list_projects(limit=10)

    for project in projects:
        print(f"Project {project.project_id}: {project.status}")

    # Get next page if available
    while pagination_key:
        more_projects, pagination_key = await aristotlelib.Project.list_projects(pagination_key=pagination_key)
        print(f"Found {len(more_projects)} more projects")

asyncio.run(list_projects())
```

## Tips and Tricks

### Replace `sorry` with `admit`

By default, Aristotle attempts to fill in all sorries in a file. If you are only interested in Aristotle filling in one (or a few) `sorry`s, you can replace the others with `admit`. This could be useful if you have `structures` and `defs` that aren't yet complete, or want to get faster results on just one proof.

### Warnings from `aesop`
**Note on `aesop` warnings:** The following warning does not indicate a problem with your proof: `aesop: failed to prove the goal after exhaustive search`

This is expected behavior when `aesop` is used as a non-terminal tactic (i.e., when other tactics follow it). To suppress this warning, use:

```lean
aesop (config := { warnOnNonterminal := false })
```