# K Programming installers

## Android Termux / Linux
From a shell:
`bash installers/install.sh`

Requires Python 3 and Git. The installer clones the public repository into
`~/.k-programming` and creates `~/.local/bin/k`.
If needed, add `export PATH="$HOME/.local/bin:$PATH"` to your shell profile.

## Windows
Open PowerShell in the repository folder and run:
`powershell -ExecutionPolicy Bypass -File installers/install.ps1`

Requires Git for Windows and Python 3. Open a new terminal after installation.

## First test
`k examples/hello.k`

The launcher selects the newest available interpreter entry point in its
configured priority order. This is an initial installer, not a claim that
every platform has been independently tested.
