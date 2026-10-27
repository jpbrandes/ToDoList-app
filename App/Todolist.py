import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from tkcalendar import Calendar

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

        # Atalhos de Teclado Globais
        self.bind("<Control-slash>", lambda event: self.abrir_menu_comandos())
        self.bind("<Control-n>", lambda event: self.atalho_focar_nova(event))
        self.bind("<Control-N>", lambda event: self.atalho_focar_nova(event))
        self.bind("<Control-c>", lambda event: self.atalho_abrir_calendario(event))
        self.bind("<Control-C>", lambda event: self.atalho_abrir_calendario(event))
        self.bind("<Control-d>", lambda event: self.atalho_excluir_selecionada(event))
        self.bind("<Control-D>", lambda event: self.atalho_excluir_selecionada(event))
        self.bind("<Control-Shift-d>", lambda event: self.atalho_excluir_todas(event))
        self.bind("<Control-Shift-D>", lambda event: self.atalho_excluir_todas(event))

        # Título Principal
        self.titulo_label = ctk.CTkLabel(self, text="To-Do List", font=("Segoe UI", 22, "bold"))
        self.titulo_label.pack(pady=(20, 10))

        # Container para Input, Botão Adicionar e Botão Calendário
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=25, pady=(0, 10))

        self.entrada_tarefa = ctk.CTkEntry(self.input_frame, placeholder_text="O que você precisa fazer?", font=("Segoe UI", 13), height=42, corner_radius=8)
        self.entrada_tarefa.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.btn_calendario = ctk.CTkButton(self.input_frame, text="📅", font=("Segoe UI", 14), width=42, height=42, corner_radius=8, fg_color="#374151", hover_color="#4b5563", command=self.abrir_calendario)
        self.btn_calendario.pack(side="left", padx=(0, 8))

        self.btn_adicionar = ctk.CTkButton(self.input_frame, text="Adicionar", font=("Segoe UI", 12, "bold"), height=42, corner_radius=8, command=self.adicionar_tarefa)
        self.btn_adicionar.pack(side="right")

        # Área de Rolagem Moderna para listar as tarefas
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Tarefas pendentes (Ctrl + / para Comandos)", label_font=("Segoe UI", 11, "bold"), corner_radius=10)
        self.scroll_frame.pack(fill="both", expand=True, padx=25, pady=(0, 10))

        # Container fixo inferior para os botões globais
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

            btn_linha_notas = ctk.CTkButton(
                row_frame, 
                text="📝", 
                font=("Segoe UI", 12, "bold"), 
                text_color="#000000",
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

    def focar_nova_tarefa(self):
        self.entrada_tarefa.focus()

    def atalho_focar_nova(self, event):
        self.focar_nova_tarefa()
        return "break"

    def atalho_abrir_calendario(self, event):
        self.abrir_calendario()
        return "break"

    def atalho_excluir_selecionada(self, event):
        self.excluir_tarefa_selecionada()
        return "break"

    def atalho_excluir_todas(self, event):
        self.excluir_todas_tarefas()
        return "break"

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

    def abrir_menu_comandos(self):
        janela_cmd = ctk.CTkToplevel(self)
        janela_cmd.title("Paleta de Comandos")
        janela_cmd.grab_set()

        lbl_titulo = ctk.CTkLabel(janela_cmd, text="Comandos Rápidos & Atalhos", font=("Segoe UI", 13, "bold"))
        lbl_titulo.pack(pady=(15, 10), padx=20, anchor="w")

        frame_opcoes = ctk.CTkScrollableFrame(janela_cmd, corner_radius=8)
        frame_opcoes.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        def executar_comando(tipo):
            janela_cmd.destroy()
            if tipo == "focar":
                self.focar_nova_tarefa()
            elif tipo == "calendario":
                self.abrir_calendario()
            elif tipo == "excluir_sel":
                self.excluir_tarefa_selecionada()
            elif tipo == "limpar":
                self.excluir_todas_tarefas()

        btn_focar = ctk.CTkButton(frame_opcoes, text="Nova Tarefa  (Ctrl + N)", anchor="w", fg_color="transparent", text_color="#f3f4f6", hover_color="#374151", height=36, command=lambda: executar_comando("focar"))
        btn_focar.pack(fill="x", pady=2)

        btn_cal = ctk.CTkButton(frame_opcoes, text="Abrir Calendário  (Ctrl + C)", anchor="w", fg_color="transparent", text_color="#f3f4f6", hover_color="#374151", height=36, command=lambda: executar_comando("calendario"))
        btn_cal.pack(fill="x", pady=2)

        btn_excluir = ctk.CTkButton(frame_opcoes, text="Excluir Selecionada  (Ctrl + D)", anchor="w", fg_color="transparent", text_color="#fca5a5", hover_color="#7f1d1d", height=36, command=lambda: executar_comando("excluir_sel"))
        btn_excluir.pack(fill="x", pady=2)

        btn_limpar = ctk.CTkButton(frame_opcoes, text="Limpar Todas as Tarefas  (Ctrl + Shift + D)", anchor="w", fg_color="transparent", text_color="#fca5a5", hover_color="#7f1d1d", height=36, command=lambda: executar_comando("limpar"))
        btn_limpar.pack(fill="x", pady=2)

    def abrir_calendario(self):
        janela_cal = ctk.CTkToplevel(self)
        janela_cal.title("Calendário de Prazos")
        janela_cal.grab_set()

        lbl_cal = ctk.CTkLabel(janela_cal, text="Selecione uma Data para Prazo:", font=("Segoe UI", 13, "bold"))
        lbl_cal.pack(pady=(15, 10))

        cal = Calendar(janela_cal, selectmode='day', year=2026, month=10, day=24, background='#1f2937', disabledbackground='#2a2a2a', bordercolor='#374151', headersbackground='#374151', normalbackground='#2a2a2a', foreground='white', normalforeground='white', selectbackground='#1d4ed8')
        cal.pack(padx=20, pady=(0, 15), fill="both", expand=True)

        def selecionar_data():
            data_escolhida = cal.get_date()
            self.entrada_tarefa.insert("end", f" [Prazo: {data_escolhida}]")
            janela_cal.destroy()

        btn_confirmar = ctk.CTkButton(janela_cal, text="Inserir Prazo na Tarefa", font=("Segoe UI", 12, "bold"), fg_color="#16a34a", hover_color="#15803d", height=36, corner_radius=6, command=selecionar_data)
        btn_confirmar.pack(fill="x", padx=20, pady=(0, 20))

    def abrir_janela_notas(self, tarefa_id, titulo_tarefa):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT detalhes FROM tarefas WHERE id = ?", (tarefa_id,))
        resultado = cursor.fetchone()
        conn.close()
        detalhes_atuais = resultado[0] if resultado and resultado[0] else ""

        janela_notas = ctk.CTkToplevel(self)
        janela_notas.title("Bloco de Notas da Tarefa")
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