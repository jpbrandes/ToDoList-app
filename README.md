# ToDoList-app

Esse repositório funciona em conjunto com o REA sobre frameworks, o desenvolvimento atual refatora o aplicativo do REA para funcionar de maneira standalone(independente). O Todolist do Recurso Educacional Aberto é extremamente dependente do Uvicorn rodando em segundo plano. Com essa refatoração, o aplicativo já possui uma interface gráfica lógica e funciona de maneira independente e sem internet.

---

# Dependências do projeto

O projeto usa Python e SQLite como ferramentas base, além das dependências que devem ser instaladas com o PIP (gerenciador de pacotes do Python).

```bash
pip install customtkinter tkcalendar
```

# Módulos extras usados no projeto (nativos ou contidos em outros pacotes)

- datetime: responsável pela manipulação de datas e horas.
- re: biblioteca usada para processamento e busca de texto.
- os: usada para comunicação com o sistema operacional, usada principalmente para gerenciar caminhos e diretórios.
- tkinter.messagebox: subconjunto do tkinter, focado em caixas de diálogo.

---

# Empacotar o projeto

Para empacotar o projeto em um executável puro, é necessário instalar o PyInstaller, ele pode ser instalado através do PIP do Python:

```bash
pip install pyinstaller
```

Logo em seguida, é preciso ir até o local onde se encontra o arquivo Todolist.py e rodar o comando:

```bash
pyinstaller --noconsole --onefile Todolist.py
```
Explicação de parâmetros:

- Ao retirar o --noconsole do comando, ao iniciar a aplicação, uma janela de terminal preta acompanharia a execução do programa, o que tornaria a experiência desagradável.
- O parâmetro --onefile empacota o código fonte em um arquivo único para execução.

Após isso, aguarde o processo de compilação, vá até a pasta dist e o executável exe estará lá.
