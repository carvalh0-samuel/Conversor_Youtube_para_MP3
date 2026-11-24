# YouTube para MP3 Player

Aplicação desktop em Python com interface gráfica (**Tkinter**) desenvolvida para baixar músicas individuais e playlists completas do YouTube, convertendo-as automaticamente para **MP3 real** com metadados compatíveis com MP3 players físicos.

---

## Por que este projeto existe?

O YouTube entrega fluxos de áudio nativos em contêineres como `.webm` (Opus) e `.m4a` (AAC), formatos que a maioria dos MP3 players dedicados não reconhece. Além disso, arquivos com nomes muito longos ou capas embutidas em alta resolução costumam travar leitores portáteis mais simples.

Este projeto automatiza todo o tratamento necessário para transferir faixas direto para a memória do aparelho:

* **Conversão real para MP3:** Utiliza `yt-dlp` + `FFmpeg` para transcodificar o áudio em `128`, `192` ou `320 kbps`.
* **Ordenação automática de playlists:** Adiciona prefixos numéricos (`01 - `, `02 - `) apenas quando o link é uma playlist, preservando a sequência original das faixas no player.
* **Tags ID3 limpas:** Grava título e artista nos metadados sem embutir miniaturas pesadas que causam erros de leitura em aparelhos antigos.
* **Nomes compatíveis com Windows/FAT32:** Trunca títulos longos (máximo de 100 caracteres) e sanitiza caracteres inválidos para evitar erros de caminho (`MAX_PATH`).
* **Contorno de bloqueio anti-bot:** Suporte integrado à leitura direta de sessão do **Firefox** ou importação de arquivo `cookies.txt`, além de intervalos aleatórios entre requisições.

---

## Pré-requisitos

* **Python 3.10+**
* **Firefox** instalado e logado no YouTube *(recomendado para baixar playlists longas sem bloqueio de bot)*
* **Runtime JavaScript (opcional, recomendado):** [Deno](https://deno.com/) ou Node.js para extração completa de formatos pelo `yt-dlp`.

---

## Instalação

1. Clone este repositório:
   ```bash
   git clone https://github.com/seu-usuario/youtube-mp3-player.git
   cd youtube-mp3-player
   ```

2. Instale as dependências Python (inclui o `yt-dlp` completo e o binário embutido do `FFmpeg`):
   ```bash
   pip install -U "yt-dlp[default]" static-ffmpeg
   ```

3. *(Opcional)* No Windows, instale o Deno para evitar avisos de runtime JavaScript:
   ```powershell
   winget install DenoLand.Deno
   ```

---

## Como Usar

1. Execute a aplicação:
   ```bash
   python yt_mp3_downloader.py
   ```
2. Cole a URL de um vídeo ou playlist do YouTube.
3. Selecione a **pasta de destino** (você pode apontar diretamente para a unidade USB do seu MP3 player).
4. Escolha o método de **Autenticação** (`Firefox (Automático)` por padrão) e a taxa de bits desejada (`192 kbps` oferece o melhor equilíbrio entre qualidade e espaço).
5. Clique em **Baixar Músicas** e acompanhe o progresso e os logs em tempo real.

---

## Estrutura do Projeto

```text
├── yt_mp3_downloader.py   # Interface gráfica (Tkinter) e motor de download/conversão
└── README.md              # Documentação do projeto
```

---

## Aviso Legal

Esta ferramenta foi desenvolvida para fins de estudo e uso pessoal (como backup de áudios livres de direitos autorais ou conteúdo próprio). Respeite os Termos de Serviço do YouTube e as leis de direitos autorais vigentes.