{
  pkgs,
  lib,
  config,
  inputs,
  ...
}: {
  languages.rust.enable = true;
  languages.nix.enable = true;
  languages.python = {
    enable = true;
    version = "3.12";
    uv = {
      enable = true;
      sync.enable = true;
      sync.allExtras = true;
    };
    venv.enable = true;
    venv.quiet = false;
  };
}
