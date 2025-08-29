{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python312
    pkgs.fish
    pkgs.zoxide
    pkgs.tmux
    pkgs.tmate
    pkgs.fzf
    pkgs.docker
    pkgs.docker-compose
  ];
  shellHook = ''
    exec ${pkgs.fish}/bin/fish
  '';
}