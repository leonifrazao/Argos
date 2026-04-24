{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "Argos";

  buildInputs = with pkgs; [
    python312
    uv

    # Dependências de sistema pro NumPy + OpenCV
    zlib
    libGL
    glib
    stdenv.cc.cc.lib

    # X11 / xcb (necessário pro OpenCV via pip)
    xorg.libX11
    xorg.libXext
    xorg.libXrender
    xorg.libxcb
    xorg.libXau
    xorg.libXdmcp
    xorg.xcbutilwm
    xorg.xcbutilimage
    xorg.xcbutilkeysyms
    xorg.xcbutilrenderutil

    # Qt xcb plugin deps (usado pelo OpenCV)
    libxkbcommon
    fontconfig
    freetype
    dbus
  ];

  shellHook = ''
    echo "Ambiente Nix ativo — Python $(python3 --version | cut -d' ' -f2) + uv"

    # Garante que o OpenCV encontre as libs de sistema
    export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [
      pkgs.zlib
      pkgs.libGL
      pkgs.glib
      pkgs.stdenv.cc.cc.lib
      pkgs.xorg.libX11
      pkgs.xorg.libXext
      pkgs.xorg.libXrender
      pkgs.xorg.libxcb
      pkgs.xorg.libXau
      pkgs.xorg.libXdmcp
      pkgs.xorg.xcbutilwm
      pkgs.xorg.xcbutilimage
      pkgs.xorg.xcbutilkeysyms
      pkgs.xorg.xcbutilrenderutil
      pkgs.libxkbcommon
      pkgs.fontconfig
      pkgs.freetype
      pkgs.dbus
    ]}:$LD_LIBRARY_PATH"

    # Cria/atualiza o venv e instala dependências automaticamente
    echo "Sincronizando dependências..."
    uv sync --no-dev

    # Ativa o venv
    source .venv/bin/activate
    echo "Pronto! Rode: python main.py"
  '';
}
