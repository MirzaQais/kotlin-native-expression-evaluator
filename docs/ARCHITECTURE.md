# Architecture

## Production direction

```mermaid
flowchart TB
    USER["Kotlin expression"]
    SOURCE["Source context at stopped line"]
    LLDB["LLDB StackFrame + DWARF"]
    PSI["Kotlin code fragment / PSI"]
    ANALYZE["Kotlin semantic analysis<br/>symbols / calls / types / diagnostics"]
    CAPTURE["Capture planner<br/>free symbols -> frame values"]
    MODE{"Evaluation mode"}
    HOST["Safe host evaluator"]
    COMPILER["Version-matched Kotlin/Native compiler service"]
    WRAP["Synthetic evaluator function"]
    BITCODE["LLVM IR / bitcode"]
    MATERIALIZE["LLDB materializer"]
    TARGET["Stopped target process"]
    VALUE["Typed result"]

    USER --> PSI
    SOURCE --> PSI
    PSI --> ANALYZE
    LLDB --> CAPTURE
    ANALYZE --> CAPTURE
    CAPTURE --> MODE
    MODE -- simple/pure --> HOST
    MODE -- full Kotlin --> WRAP
    WRAP --> COMPILER
    COMPILER --> BITCODE
    BITCODE --> MATERIALIZE
    CAPTURE --> MATERIALIZE
    MATERIALIZE <--> TARGET
    HOST --> VALUE
    MATERIALIZE --> VALUE
```

## Recommended compiler boundary

```text
LLDB plugin / debugger core (C++)
            |
            | IPC
            v
Kotlin Expression Compiler Service
            |
            +-- K2 / Analysis API semantic resolution
            +-- Kotlin/Native backend
            +-- compiler-version-specific runtime knowledge
            |
            v
LLVM IR / bitcode + result metadata
```

## Frame binding

For:

```kotlin
order.total + tax
```

semantic analysis identifies the source-level symbols and types, while LLDB owns the live values/locations. The capture planner maps the two representations.

## LLDB integration direction

LLDB documents language-specific expression evaluation as part of a `TypeSystem` implementation. A Kotlin production path would conceptually use:

```text
TypeSystem
  -> UserExpression
       -> ExpressionParser
            -> Kotlin compiler bridge
                 -> generated LLVM IR
                      -> LLDB execution
```

Exact C++ signatures must be matched to the LLDB version being integrated.

## Version compatibility

Compiler-backed evaluation must be version-aware. The Kotlin/Native compiler/runtime internals should not be treated as a stable debugger ABI.
