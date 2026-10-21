import customtkinter as ctk
from tkinter import messagebox
import sqlite3

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- 1. CONFIGURAÇÃO DO BANCO DE DADOS LOCAL ---
def conectar_db():
    return sqlite3.connect("data.db")

def inicializar_db():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            concluida INTEGER DEFAULT 0,
            detalhes TEXT DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()

inicializar_db()

# --- 2. CLASSE PRINCIPAL DA APLICAÇÃO ---
class TodoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ToDoList")
        self.minsize(480, 500)

        # Configuração de peso das linhas da janela principal para redimensionamento fluido
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Título Principal
        self.titulo_label = ctk.CTkLabel(self, text="ToDoList", font=("Segoe UI", 22, "bold"))
        self.titulo_label.pack(pady=(20, 10))

        # Container para Input e Botão Adicionar
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=25, pady=(0, 10))

        self.entrada_tarefa = ctk.CTkEntry(self.input_frame, placeholder_text="O que você precisa fazer?", font=("Segoe UI", 13), height=42, corner_radius=8)
        self.entrada_tarefa.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.btn_adicionar = ctk.CTkButton(self.input_frame, text="Adicionar", font=("Segoe UI", 12, "bold"), height=42, corner_radius=8, command=self.adicionar_tarefa)
        self.btn_adicionar.pack(side="right")

        # Área de Rolagem Moderna para listar as tarefas (Expande e contrai dinamicamente sem cobrir os botões)
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Tarefas Pendentes", label_font=("Segoe UI", 12, "bold"), corner_radius=10)
        self.scroll_frame.pack(fill="both", expand=True, padx=25, pady=(0, 10))

        # Container fixo inferior para os botões globais (Garante que nunca sejam cortados)
        self.acoes_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.acoes_frame.pack(fill="x", padx=25, pady=(0, 20))

        self.tarefa_selecionada_id = None
        self.status_selecionado = 0
        self.frames_tarefas = {}

        # Botão Concluir Global
        self.btn_concluir = ctk.CTkButton(self.acoes_frame, text="Concluir", font=("Segoe UI", 11, "bold"), fg_color="#4b5563", hover_color="#4b5563", height=38, corner_radius=6, command=self.alternar_conclusao_global, state="disabled")
        self.btn_concluir.pack(side="left", fill="x", expand=True, padx=(0, 4))

        # Botão Editar Global
        self.btn_editar = ctk.CTkButton(self.acoes_frame, text="Editar", font=("Segoe UI", 11, "bold"), fg_color="#4b5563", hover_color="#374151", height=38, corner_radius=6, command=self.renomear_tarefa_global, state="disabled")
        self.btn_editar.pack(side="left", fill="x", expand=True, padx=4)

        # Botão Excluir Selecionada Global
        self.btn_excluir_sel = ctk.CTkButton(self.acoes_frame, text="Excluir", font=("Segoe UI", 11, "bold"), fg_color="#4b5563", hover_color="#4b5563", height=38, corner_radius=6, command=self.excluir_tarefa_selecionada, state="disabled")
        self.btn_excluir_sel.pack(side="left", fill="x", expand=True, padx=4)

        # Botão Limpar Tudo Global
        self.btn_excluir_todas = ctk.CTkButton(self.acoes_frame, text="Limpar", font=("Segoe UI", 11, "bold"), fg_color="#4b5563", hover_color="#4b5563", height=38, corner_radius=6, command=self.excluir_todas_tarefas, state="disabled")
        self.btn_excluir_todas.pack(side="right", fill="x", expand=True, padx=(4, 0))

        self.carregar_tarefas()

    def carregar_tarefas(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.frames_tarefas.clear()
        self.tarefa_selecionada_id = None
        self.atualizar_estado_botoes_globais()

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, titulo, concluida, detalhes FROM tarefas")
        registros = cursor.fetchall()
        conn.close()

        if not registros:
            lbl_vazio = ctk.CTkLabel(self.scroll_frame, text="Nenhuma tarefa cadastrada.", font=("Segoe UI", 12), text_color="gray")
            lbl_vazio.pack(pady=20)
            return

        for indice, reg in enumerate(registros, start=1):
            tarefa_id, titulo, concluida, detalhes = reg[0], reg[1], reg[2], reg[3]

            row_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#2a2a2a" if concluida == 0 else "#222222", corner_radius=6)
            row_frame.pack(fill="x", pady=4, padx=5)
            self.frames_tarefas[tarefa_id] = row_frame

            if concluida == 1:
                texto_exibicao = f"✓ {indice}. {titulo}"
                cor_texto = "#9ca3af"
            else:
                texto_exibicao = f"{indice}. {titulo}"
                cor_texto = "#f3f4f6"

            lbl_texto = ctk.CTkLabel(row_frame, text=texto_exibicao, font=("Segoe UI", 13), text_color=cor_texto, anchor="w")
            lbl_texto.pack(side="left", fill="x", expand=True, padx=10, pady=8)

            # Botão de Notas (): Laranja com texto preto
            btn_linha_notas = ctk.CTkButton(
                row_frame, 
                text="Notas", # Esse é o ícone presente no botão
                font=("Segoe UI", 12, "bold"), 
                text_color="#FFFFFF",
                width=36, 
                height=30, 
                corner_radius=6, 
                fg_color="#d97706", 
                hover_color="#b45309",
                command=lambda tid=tarefa_id, t_titulo=titulo: self.abrir_janela_notas(tid, t_titulo)
            )
            btn_linha_notas.pack(side="right", padx=(0, 8), pady=5)

            for widget in [row_frame, lbl_texto]:
                widget.bind("<Button-1>", lambda event, tid=tarefa_id, stat=concluida: self.selecionar_tarefa(tid, stat))

    def selecionar_tarefa(self, tarefa_id, status):
        self.tarefa_selecionada_id = tarefa_id
        self.status_selecionado = status

        for tid, frame in self.frames_tarefas.items():
            if tid == tarefa_id:
                frame.configure(fg_color="#1d4ed8")
            else:
                frame.configure(fg_color="#2a2a2a")

        self.atualizar_estado_botoes_globais()

    def atualizar_estado_botoes_globais(self):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tarefas")
        total_tarefas = cursor.fetchone()[0]
        conn.close()

        if self.tarefa_selecionada_id is not None:
            if self.status_selecionado == 1:
                self.btn_concluir.configure(text="Desfazer", fg_color="#ca8a04", hover_color="#a16207", state="normal")
            else:
                self.btn_concluir.configure(text="Concluir", fg_color="#16a34a", hover_color="#15803d", state="normal")

            self.btn_editar.configure(state="normal")
            self.btn_excluir_sel.configure(fg_color="#ef4444", hover_color="#dc2626", state="normal")
        else:
            self.btn_concluir.configure(text="Concluir", fg_color="#4b5563", hover_color="#4b5563", state="disabled")
            self.btn_editar.configure(fg_color="#4b5563", hover_color="#4b5563", state="disabled")
            self.btn_excluir_sel.configure(fg_color="#4b5563", hover_color="#4b5563", state="disabled")

        if total_tarefas > 0:
            self.btn_excluir_todas.configure(fg_color="#991b1b", hover_color="#7f1d1d", state="normal")
        else:
            self.btn_excluir_todas.configure(fg_color="#4b5563", hover_color="#4b5563", state="disabled")

    def adicionar_tarefa(self):
        texto = self.entrada_tarefa.get().strip()
        if not texto:
            messagebox.showwarning("Aviso", "Escreva uma tarefa antes de adicionar!")
            return

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tarefas (titulo, concluida, detalhes) VALUES (?, 0, '')", (texto,))
        conn.commit()
        conn.close()

        self.entrada_tarefa.delete(0, "end")
        self.carregar_tarefas()

    def abrir_janela_notas(self, tarefa_id, titulo_tarefa):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT detalhes FROM tarefas WHERE id = ?", (tarefa_id,))
        resultado = cursor.fetchone()
        conn.close()
        detalhes_atuais = resultado[0] if resultado and resultado[0] else ""

        janela_notas = ctk.CTkToplevel(self)
        janela_notas.title("Bloco de Notas da Tarefa")
        janela_notas.geometry("450x400")
        janela_notas.grab_set()

        lbl_info = ctk.CTkLabel(janela_notas, text=f"Notas para: {titulo_tarefa}", font=("Segoe UI", 13, "bold"))
        lbl_info.pack(pady=(20, 10), padx=20, anchor="w")

        txt_detalhes = ctk.CTkTextbox(janela_notas, font=("Segoe UI", 12), corner_radius=8)
        txt_detalhes.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        txt_detalhes.insert("1.0", detalhes_atuais)

        def salvar_notas():
            novos_detalhes = txt_detalhes.get("1.0", "end-1c").strip()
            
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE tarefas SET detalhes = ? WHERE id = ?", (novos_detalhes, tarefa_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Sucesso", "Anotações salvas com sucesso!")
            janela_notas.destroy()

        btn_salvar = ctk.CTkButton(janela_notas, text="Salvar Notas", font=("Segoe UI", 12, "bold"), fg_color="#16a34a", hover_color="#15803d", height=38, corner_radius=6, command=salvar_notas)
        btn_salvar.pack(fill="x", padx=20, pady=(0, 20))

    def alternar_conclusao_global(self):
        if self.tarefa_selecionada_id is None:
            return

        novo_status = 0 if self.status_selecionado == 1 else 1

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE tarefas SET concluida = ? WHERE id = ?", (novo_status, self.tarefa_selecionada_id))
        conn.commit()
        conn.close()
        
        self.carregar_tarefas()

    def renomear_tarefa_global(self):
        if self.tarefa_selecionada_id is None:
            return

        dialog = ctk.CTkInputDialog(text="Digite o novo nome da tarefa:", title="Renomear Tarefa")
        novo_texto = dialog.get_input()

        if novo_texto is not None:
            novo_texto = novo_texto.strip()
            if not novo_texto:
                messagebox.showwarning("Aviso", "O nome da tarefa não pode ficar vazio!")
                return

            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE tarefas SET titulo = ? WHERE id = ?", (novo_texto, self.tarefa_selecionada_id))
            conn.commit()
            conn.close()
            self.carregar_tarefas()

    def excluir_tarefa_selecionada(self):
        if self.tarefa_selecionada_id is None:
            return

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tarefas WHERE id = ?", (self.tarefa_selecionada_id,))
        conn.commit()
        conn.close()
        
        self.carregar_tarefas()

    def excluir_todas_tarefas(self):
        resposta = messagebox.askyesno("Confirmação", "Tem certeza absoluta que deseja apagar TODAS as tarefas?")
        if resposta:
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tarefas")
            conn.commit()
            conn.close()
            self.carregar_tarefas()

if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()