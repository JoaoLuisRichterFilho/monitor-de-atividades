# PythonLogger

O projeto monitora o tempo de uso das janelas no Windows e registra as trocas
em um arquivo CSV chamado `logger_AAAA-MM-DD.csv`, criado na pasta em que o
programa for iniciado.

Quando o mouse permanece parado por dois minutos, o CSV recebe um registro de
possível ausência. O monitor pode ser pausado com `Ctrl + K` e encerrado com
`Ctrl + C`.

Para iniciar:

```shell
python main.py
```