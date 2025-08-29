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
    if [ ! -d env ]; then
      python3 -m venv env
    fi
    exec ${pkgs.fish}/bin/fish -C 'source ./env/bin/activate.fish; pip install --upgrade pip; pip3 install -r ./requirements.txt'
  '';
}