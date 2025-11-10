{
  description = "Demo flake for using redun_psij";
  inputs = {
    # nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    nixpkgs.url = "github:NixOS/nixpkgs/25.05"; # until eRI supports later than Nix 2.17 😢

    flake-utils.url = "github:numtide/flake-utils";
    redun = {
      url = "github:AgResearch/redun.nix/main";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    redun-psij = {
      # url = "github:AgResearch/redun_psij/main";
      url = "./..";
      inputs = {
        nixpkgs.follows = "nixpkgs";
        redun.follows = "redun";
      };
    };
  };

  outputs = inputs:
    inputs.flake-utils.lib.eachDefaultSystem
      (system:
        let
          pkgs = import inputs.nixpkgs {
            inherit system;
          };

          flakePkgs = {
            redun = inputs.redun.packages.${system}.default;
            redun-psij = inputs.redun-psij.packages.${system}.default;
          };

          python-dependencies =
            [
              flakePkgs.redun
              flakePkgs.redun-psij
            ];

          fastq_generator =
            let
              src = pkgs.fetchFromGitHub {
                owner = "johanzi";
                repo = "fastq_generator";
                rev = "8bf8d68d0c8dc07c7e4b8c5a53068aef15b40aa6";
                hash = "sha256-XABzYER54zOipEnELhYIcOssd2GYHaKjU5K2jMt9/xc=";
              };
            in
            (pkgs.writeScriptBin "fastq_generator" (builtins.readFile "${src}/fastq_generator.py")).overrideAttrs (old: {
              buildInputs = [ pkgs.python3 ];
              buildCommand = "${old.buildCommand}\n patchShebangs $out";
            });

        in
        with pkgs;
        {
          devShells = {
            default = mkShell
              {
                buildInputs =
                  let
                    python-with-dependencies = (pkgs.python3.withPackages (ps: python-dependencies));

                  in
                  [
                    bashInteractive
                    python-with-dependencies
                    jsonnet
                    fastq_generator
                    fastqc
                    multiqc
                  ];

                shellHook = ''
                  export PYTHONPATH=$(pwd)/src:$PYTHONPATH
                  export PSIJ_EXECUTOR_CONFIG_PATH=$(pwd)/config
                '';
              };
          };
        }
      );
}
