# ToDoList-app

Esse repositório funciona em conjunto com o REA sobre frameworks (https://github.com/jpbrandes/REARepository), o ToDoList atual refatora a versão antiga presente no REA para funcionar de maneira standalone. O Todolist do Recurso Educacional Aberto é uma versão dependente do Uvicorn rodando em segundo plano. Com essa refatoração, o aplicativo já possui uma interface gráfica e funciona de maneira independente e sem internet, exatamente como um aplicativo desktop padrão.

## Dependências do projeto

O projeto usa Python e SQLite como ferramentas base, além das dependências que devem ser instaladas com o PIP:

```bash
pip install customtkinter tkcalendar
```
- **customtkinter**: é a biblioteca usada para criar a interface da aplicação.
- **tkcalendar**: é um módulo do tkinter original que adiciona suporte a um calendário.

## Módulos extras usados no projeto

- **datetime**: responsável pela manipulação de datas e horas.
- **re**: biblioteca usada para processamento e busca de texto.
- **os**: usada para comunicação com o sistema operacional, usada principalmente para gerenciar caminhos e diretórios.
- **tkinter.messagebox**: subconjunto do tkinter, focado em caixas de diálogo.
- **sys**: nativo do Python, usado diretamente para obter informações sobre a execução do programa.
- **csv**: fornece suporte a arquivos csv, para exportar e importar.
- **filedialog**: diálogo usado para o sistema salvar algum arquivo em determinado diretório do sistema.

## Empacotar o projeto

Para empacotar o projeto em um executável puro, é necessário usar o PyInstaller, ele pode ser instalado através do PIP:

```bash
pip install pyinstaller
```

Logo em seguida, é preciso ir até o local onde se encontra o arquivo Todolist.py e rodar o comando:

```bash
pyinstaller --noconsole --onefile Todolist.py
```
Explicação de parâmetros:

- Ao retirar o **--noconsole** do comando, ao iniciar a aplicação, uma janela de terminal preta acompanharia a execução do programa, o que tornaria a experiência desagradável.
- O parâmetro **--onefile** empacota o código fonte em um arquivo único para execução.

Após isso, aguarde o processo de compilação, vá até a pasta dist e o executável exe estará lá.
