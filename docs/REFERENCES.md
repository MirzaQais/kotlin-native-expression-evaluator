# References

Primary first-party references:

- Kotlin — Debugging Kotlin/Native  
  https://kotlinlang.org/docs/native-debugging.html

- LLDB — Adding Programming Language Support  
  https://lldb.llvm.org/resources/addinglanguagesupport.html

- Kotlin Analysis API  
  https://kotlin.github.io/analysis-api/

- Kotlin Analysis API — File Compilation  
  https://kotlin.github.io/analysis-api/file-compilation.html

Key design facts reflected in this repository:

- Kotlin/Native debugging uses DWARF-compatible debug information.
- Kotlin documents debugger expression evaluation as unsupported.
- LLDB exposes language-specific expression support through its language/type-system architecture.
- Kotlin Analysis API provides semantic source analysis.
- The currently documented Analysis API in-memory compilation target is JVM, so native expression code generation needs a Kotlin/Native-specific bridge.
