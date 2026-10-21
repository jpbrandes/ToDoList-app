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
pyinstaller --noconsole --onefile app.py
```