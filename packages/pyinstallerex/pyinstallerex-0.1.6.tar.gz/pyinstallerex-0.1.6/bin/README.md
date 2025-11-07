# Binary Launchers Directory

This directory should contain the Go-compiled binary launchers for different platforms.

## Required Files:

- `launcher_windows.exe` - Windows launcher (64-bit)
- `launcher_linux_x86` - Linux x86 launcher (64-bit) 
- `launcher_linux_arm` - Linux ARM launcher (64-bit)

## Building the Launchers:

The launchers should be written in Go and compiled for each target platform. They should:

1. Extract the ZIP section from the combined executable
2. Check if the application is already installed in temp directory
3. If not installed, extract and install
4. Launch the extracted application

## Example Go launcher structure:

```go
package main

import (
    "archive/zip"
    "fmt"
    "io"
    "os"
    "path/filepath"
)

func main() {
    // Implementation details...
}
```