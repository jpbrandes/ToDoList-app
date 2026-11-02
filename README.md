# ToDoList-app

Esse repositório funciona em conjunto com o REA sobre frameworks, o desenvolvimento atual refatora o aplicativo do REA para funcionar de maneira standalone(indepentente). O Todolist do Recurso Educacional Aberto é extremamente dependente do Uvicorn rodando em segundo plano. Com essa refatoração, o aplicativo já possui uma interface gráfica lógica e funciona de maneira independente e sem internet.

---

# Empacotar o projeto

Para empacotar o projeto em um executável puro, é necessário instalar o Pyinstaller, ele pode ser instalado através do pip do Python:

```bash
pip install pyinstaller
```

Logo em seguida, é preciso ir até local onde se encontra o arquivo Todolist.py e rodar o comando:

```bash
pyinstaller --noconsole --onefile Todolist.py
```

Após isso, vá até a pasta dist e o executável exe estará lá.

---

# Dependências do projeto

O projeto usa as seguintes dependências:

```bash
pip install customtkinter tkcalendar pillow
```

Isso sem contar o SQLite como banco de dados e Python como linguagem base.
