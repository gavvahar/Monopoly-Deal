{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python312
    pkgs.fish
    pkgs.gh
    pkgs.zoxide
    pkgs.tmux
    pkgs.tmate
  ];
  shellHook = ''
    exec ${pkgs.fish}/bin/fish
  '';
}