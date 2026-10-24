# ToDoList-app

Esse repositório funciona em conjunto com o REA sobre frameworks, o aplicativo em desenvolvimento refatora o aplicativo para funcionar de maneira standalone.

---

# Compilar o projeto

Para compilar o projeto, é necessário instalar o Pyinstaller, ele pode ser instalado atráves do pip do Python:

```bash
pip install pyinstaller
```

Logo em seguida, é preciso ir até local onde se encontra o arquivo app.py e rodar o comando:

```bash
pyinstaller --onefile Todolist.py
```

Após isso, vá até a pasta dist e o executável exe estará lá.

---

# Dependências do projeto

O projeto usa as seguintes dependências:

```bash
pip install customtkinter tkcalendar pillow
```

Isso sem contar o SQLite e Python como linguagem base.