{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python312
    pkgs.fish
  ];
  shellHook = ''
    exec ${pkgs.fish}/bin/fish
  '';
}