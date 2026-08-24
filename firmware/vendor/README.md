# Dependências vendorizadas do firmware

`platform-native` reproduz a versão 1.2.1 da plataforma oficial PlatformIO,
commit `7df81639bc84474e9b1812d241762cffad9c69e7`, sob Apache-2.0. Apenas o
manifesto e o builder necessários ao HIL nativo foram preservados. Isso evita
que o build de segurança dependa do registro remoto do PlatformIO.
