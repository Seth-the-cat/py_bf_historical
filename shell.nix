{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
    pname = "py-bf-historical-shell";
    buildInputs = [
        pkgs.python3
        pkgs.python3Packages.flask
        pkgs.python3Packages.requests
        pkgs.python3Packages.bleach
        pkgs.python3Packages.beautifulsoup4
        pkgs.python3Packages.aiohttp
        pkgs.sqlite
    ];

    shellHook = ''
        export PYTHONPATH="${toString ./.}:$PYTHONPATH"
        export FLASK_APP=main.py
        export FLASK_ENV=development
        export PYTHONNOUSERSITE=1
        echo "Entered nix shell for py_bf_historical — run: flask run"
    '';
}