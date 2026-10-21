import tkinter as tk
from tkinter import messagebox
import sqlite3

# 1. Configurar o Banco de Dados SQLite local
def conectar_db():
    conn = sqlite3.connect("tarefas_desktop.db")
    return conn

def inicializar_db():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

inicializar_db()

# 2. Funções de lógica (CRUD)
def carregar_tarefas():
    # Limpa a listbox visual
    lista_tarefas.delete(0, tk.END)
    
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, titulo FROM tarefas")
    registros = cursor.fetchall()
    conn.close()
    
    # Insere cada tarefa na tela
    for reg in registros:
        # reg[0] é o ID, reg[1] é o título
        lista_tarefas.insert(tk.END, f"{reg[0]} - {reg[1]}")

def adicionar_tarefa():
    texto = entrada_tarefa.get().strip()
    if not texto:
        messagebox.showwarning("Aviso", "Digite uma tarefa antes de adicionar!")
        return
    
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tarefas (titulo) VALUES (?)", (texto,))
    conn.commit()
    conn.close()
    
    entrada_tarefa.delete(0, tk.END)
    carregar_tarefas()

def excluir_tarefa():
    try:
        # Pega o item selecionado na lista visual
        selecionado = lista_tarefas.get(lista_tarefas.curselection())
        # Extrai o ID do texto (ex: "1 - Comprar pão" -> pega o "1")
        tarefa_id = selecionado.split(" - ")[0]
        
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,))
        conn.commit()
        conn.close()
        
        carregar_tarefas()
    except Exception:
        messagebox.showwarning("Aviso", "Selecione uma tarefa na lista para excluir!")

# 3. Construção da Interface Gráfica com Tkinter
janela = tk.Tk()
janela.title("To-Do List Standalone (Tkinter)")
janela.geometry("400x450")
janela.config(bg="#f3f4f6")

# Título
titulo_label = tk.Label(janela, text="ToDoList", font=("Segoe UI", 16, "bold"), bg="#f3f4f6", fg="#1f2937")
titulo_label.pack(pady=15)

# Campo de entrada (Input)
entrada_tarefa = tk.Entry(janela, font=("Segoe UI", 12), width=25)
entrada_tarefa.pack(pady=5)

# Botão Adicionar
btn_adicionar = tk.Button(janela, text="Adicionar tarefa", font=("Segoe UI", 10, "bold"), bg="#2563eb", fg="white", command=adicionar_tarefa, width=20)
btn_adicionar.pack(pady=10)

# Lista visual (ListBox)
lista_tarefas = tk.Listbox(janela, font=("Segoe UI", 11), width=32, height=12)
lista_tarefas.pack(pady=10)

# Botão Excluir
btn_excluir = tk.Button(janela, text="Excluir selecionada", font=("Segoe UI", 10, "bold"), bg="#dc2626", fg="white", command=excluir_tarefa, width=20)
btn_excluir.pack(pady=5)

# Carrega as tarefas ao iniciar a janela
carregar_tarefas()

# Mantém o aplicativo rodando
janela.mainloop()