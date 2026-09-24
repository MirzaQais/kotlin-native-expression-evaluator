# Implementation Plan

## Phase 1 — implemented

- selected LLDB frame
- primitive locals/arguments
- restricted side-effect-free Kotlin-like expressions
- host-side evaluation
- unit tests for evaluator behavior

## Phase 2 — Kotlin semantic resolution

- create a Kotlin code fragment in source context
- resolve free identifiers
- resolve calls/receivers
- obtain expression result type
- collect diagnostics
- export a serializable expression plan

## Phase 3 — LLDB frame capture binder

- bind locals/parameters to live values/locations
- support `this` and receivers
- detect optimized-out/unavailable values
- fail explicitly instead of guessing

## Phase 4 — Kotlin/Native compiler bridge

- select compiler version compatible with the target
- generate a synthetic evaluator function
- provide project/KLIB dependencies
- lower with Kotlin/Native
- emit LLVM IR/bitcode
- return result ABI/type metadata

## Phase 5 — target execution

- materialize captures
- relocate/load evaluator code
- execute with LLDB
- enforce timeout/cancellation
- retrieve and render result

## Phase 6 — Kotlin objects/runtime

- strings
- arrays
- nullable references
- object fields
- value classes
- selected collections
- runtime/GC safety

## Phase 7 — performance

- warm compiler service
- expression plan cache
- type/symbol caches
- batched memory reads
- lazy object rendering
- remote-target benchmarks

## Acceptance milestones

**M1** `kexpr x + y * factor` returns the correct primitive result.

**M2** `order.total + tax` is semantically resolved against real source and reports the correct captures.

**M3** the compiler bridge emits native LLVM IR for a synthetic evaluator.

**M4** LLDB executes that evaluator using live frame values and returns a typed result.

**M5** a Kotlin property/function-call expression works under a documented side-effect policy.
