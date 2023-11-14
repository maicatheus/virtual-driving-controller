"""
README para VirtualCarController

Visão Geral:
------------
VirtualCarController é um programa em Python que permite aos usuários controlar um carro virtual usando gestos de mão. Este software utiliza técnicas de visão computacional e emulação de gamepad para traduzir movimentos de mão em comandos de controle do carro.

Dependências:
-------------
- Python 3.x
- OpenCV (cv2): Para processamento de imagens e tarefas de visão computacional.
- MediaPipe (mediapipe): Uma estrutura para auxiliar a identificar objetos pela web.
- vgamepad (vgamepad): Uma biblioteca para emular um gamepad do Xbox 360.

Instalação:
-----------
1. Instale o Python 3.x pelo site oficial.
2. Instale os pacotes necessários usando o pip:

```bash
pip install opencv-python mediapipe vgamepad
```
Instruções de Controle:
-----------------------
- Acelerar: Levante o pelgar da direita gradualmente para acelerar.
- Frear: Levante o polegar da esquerda gradualmente para freiar.
- Direção: Mova as mãos para a esquerda ou direita para controlar a direção. O ângulo entre as mãos é utilizado para determinar a direção do volante.

Características:
----------------
- Detecção de gestos de mão para controle do carro.
- Cálculo em tempo real da velocidade e do ângulo.
- Feedback visual na tela.
- Emulação de gamepad para compatibilidade com diversos jogos de simulação de carro.

Uso:
----
1. Execute o script `main.py`.
2. Posicione suas mãos em frente à webcam.
3. Faça gestos com as mãos para controlar a velocidade e a direção do carro virtual.
"""

