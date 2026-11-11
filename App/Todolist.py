import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import os
import re
from datetime import datetime
from tkcalendar import Calendar

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- 1. CONFIGURAÇÃO DO BANCO DE DIRETÓRIOS E BANCO DE DADOS LOCAL ---
def conectar_db():
    conn = sqlite3.connect("data.db")
    return conn

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
    
    # Verificação de segurança: Adiciona a coluna 'prioridade' caso o banco antigo não a possua
    cursor.execute("PRAGMA table_info(tarefas)")
    colunas = [col[1] for col in cursor.fetchall()]
    if "prioridade" not in colunas:
        cursor.execute("ALTER TABLE tarefas ADD COLUMN prioridade TEXT DEFAULT 'Baixa'")
        
    conn.commit()
    conn.close()

inicializar_db()

# --- 2. CLASSE PRINCIPAL DA APLICAÇÃO ---
class TodoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ToDoList")
        self.minsize(560, 520)

        # Configuração de peso das linhas da janela principal para redimensionamento fluido
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Variável para rastrear o termo de busca atual e IDs carregados
        self.termo_busca_atual = ""
        self.ids_tarefas_carregadas = []

        # Atalhos de Teclado Globais
        self.bind("<Control-slash>", lambda event: self.abrir_menu_comandos())
        self.bind("<Control-n>", lambda event: self.atalho_focar_nova(event))
        self.bind("<Control-N>", lambda event: self.atalho_focar_nova(event))
        self.bind("<Control-c>", lambda event: self.atalho_abrir_calendario(event))
        self.bind("<Control-C>", lambda event: self.atalho_abrir_calendario(event))
        self.bind("<Control-f>", lambda event: self.atalho_abrir_busca(event))
        self.bind("<Control-F>", lambda event: self.atalho_abrir_busca(event))
        self.bind("<Control-Shift-f>", lambda event: self.atalho_limpar_busca(event))
        self.bind("<Control-Shift-F>", lambda event: self.atalho_limpar_busca(event))
        self.bind("<Control-r>", lambda event: self.atalho_renomear_tarefa(event))
        self.bind("<Control-R>", lambda event: self.atalho_renomear_tarefa(event))
        self.bind("<Control-m>", lambda event: self.atalho_duplicar_tarefa(event))
        self.bind("<Control-M>", lambda event: self.atalho_duplicar_tarefa(event))
        self.bind("<Control-d>", lambda event: self.atalho_excluir_selecionada(event))
        self.bind("<Control-D>", lambda event: self.atalho_excluir_selecionada(event))
        self.bind("<Control-Shift-d>", lambda event: self.atalho_excluir_todas(event))
        self.bind("<Control-Shift-D>", lambda event: self.atalho_excluir_todas(event))
        self.bind("<Control-w>", lambda event: self.atalho_fechar_app(event))
        self.bind("<Control-W>", lambda event: self.atalho_fechar_app(event))
        self.bind("<Control-u>", lambda event: self.atalho_recarregar_app(event))
        self.bind("<Control-U>", lambda event: self.atalho_recarregar_app(event))
        
        # Novo Atalho: Ctrl + K para Concluir/Desfazer a tarefa selecionada
        self.bind("<Control-k>", lambda event: self.atalho_concluir_tarefa(event))
        self.bind("<Control-K>", lambda event: self.atalho_concluir_tarefa(event))

        # Atalhos de Navegação por Setas na Janela Principal
        self.bind("<Up>", lambda event: self.navegar_setas(-1))
        self.bind("<Down>", lambda event: self.navegar_setas(1))

        # Título Principal
        self.titulo_label = ctk.CTkLabel(self, text="To-Do List", font=("Segoe UI", 22, "bold"))
        self.titulo_label.pack(pady=(15, 5))

        # --- BARRA DE ESTATÍSTICAS RÁPIDAS ---
        self.stats_frame = ctk.CTkFrame(self, fg_color="#1f2937", corner_radius=8, height=36)
        self.stats_frame.pack(fill="x", padx=25, pady=(0, 10))
        self.stats_frame.pack_propagate(False)

        self.lbl_stats_total = ctk.CTkLabel(self.stats_frame, text="Total: 0", font=("Segoe UI", 11, "bold"), text_color="#9ca3af")
        self.lbl_stats_total.pack(side="left", padx=12)

        self.lbl_stats_pendentes = ctk.CTkLabel(self.stats_frame, text="Pendentes: 0", font=("Segoe UI", 11, "bold"), text_color="#fbbf24")
        self.lbl_stats_pendentes.pack(side="left", padx=12)

        self.lbl_stats_atrasadas = ctk.CTkLabel(self.stats_frame, text="Atrasadas: 0", font=("Segoe UI", 11, "bold"), text_color="#ef4444")
        self.lbl_stats_atrasadas.pack(side="left", padx=12)

        self.lbl_stats_concluidas = ctk.CTkLabel(self.stats_frame, text="Concluídas: 0", font=("Segoe UI", 11, "bold"), text_color="#34d399")
        self.lbl_stats_concluidas.pack(side="left", padx=12)

        # Container para Input, Seletor de Prioridade, Botão Calendário, Botão Busca e Botão Adicionar
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=25, pady=(0, 10))

        self.entrada_tarefa = ctk.CTkEntry(self.input_frame, placeholder_text="O que você precisa fazer?", font=("Segoe UI", 13), height=42, corner_radius=8)
        self.entrada_tarefa.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entrada_tarefa.bind("<Return>", lambda event: self.adicionar_tarefa())

        # Menu Suspenso de Prioridades
        self.prioridade_var = ctk.StringVar(value="Baixa")
        self.menu_prioridade = ctk.CTkOptionMenu(
            self.input_frame, 
            values=["Baixa", "Média", "Alta"], 
            variable=self.prioridade_var,
            font=("Segoe UI", 11, "bold"),
            width=95,
            height=42,
            corner_radius=8,
            fg_color="#374151",
            button_color="#4b5563",
            button_hover_color="#6b7280"
        )
        self.menu_prioridade.pack(side="left", padx=(0, 8))

        self.btn_calendario = ctk.CTkButton(self.input_frame, text="📅", font=("Segoe UI", 14), width=42, height=42, corner_radius=8, fg_color="#374151", hover_color="#4b5563", command=self.abrir_calendario)
        self.btn_calendario.pack(side="left", padx=(0, 8))

        self.btn_busca = ctk.CTkButton(self.input_frame, text="🔍", font=("Segoe UI", 14), width=42, height=42, corner_radius=8, fg_color="#374151", hover_color="#4b5563", command=self.abrir_janela_busca)
        self.btn_busca.pack(side="left", padx=(0, 8))

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
        self.btn_concluir.pack(side="left", fill="x", expand=True, padx=(0, 3))

        # Botão Editar Global
        self.btn_editar = ctk.CTkButton(self.acoes_frame, text="Editar", font=("Segoe UI", 11, "bold"), fg_color="#4b5563", hover_color="#374151", height=38, corner_radius=6, command=self.renomear_tarefa_global, state="disabled")
        self.btn_editar.pack(side="left", fill="x", expand=True, padx=3)

        # Botão Duplicar Global
        self.btn_duplicar = ctk.CTkButton(self.acoes_frame, text="Duplicar", font=("Segoe UI", 11, "bold"), fg_color="#4b5563", hover_color="#374151", height=38, corner_radius=6, command=self.duplicar_tarefa_selecionada, state="disabled")
        self.btn_duplicar.pack(side="left", fill="x", expand=True, padx=3)

        # Botão Excluir Selecionada Global
        self.btn_excluir_sel = ctk.CTkButton(self.acoes_frame, text="Excluir", font=("Segoe UI", 11, "bold"), fg_color="#4b5563", hover_color="#4b5563", height=38, corner_radius=6, command=self.excluir_tarefa_selecionada, state="disabled")
        self.btn_excluir_sel.pack(side="left", fill="x", expand=True, padx=3)

        # Botão Limpar Tudo Global
        self.btn_excluir_todas = ctk.CTkButton(self.acoes_frame, text="Limpar tudo", font=("Segoe UI", 11, "bold"), fg_color="#4b5563", hover_color="#4b5563", height=38, corner_radius=6, command=self.excluir_todas_tarefas, state="disabled")
        self.btn_excluir_todas.pack(side="right", fill="x", expand=True, padx=(3, 0))

        self.carregar_tarefas()

    def verificar_e_recriar_db(self):
        """Garante que a tabela e colunas existam sempre, recriando se o arquivo foi apagado."""
        inicializar_db()

    def extrair_data_prazo(self, titulo):
        """Extrai o objeto date a partir da tag [Prazo: MM/DD/YY] contida no título."""
        match = re.search(r"\[Prazo:\s*(\d{1,2}/\d{1,2}/\d{2,4})\]", titulo)
        if match:
            str_data = match.group(1)
            for fmt in ("%m/%d/%y", "%m/%d/%Y", "%d/%m/%y", "%d/%m/%Y"):
                try:
                    return datetime.strptime(str_data, fmt).date()
                except ValueError:
                    continue
        return None

    def atualizar_estatisticas(self):
        try:
            self.verificar_e_recriar_db()
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tarefas")
            total = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM tarefas WHERE concluida = 0")
            pendentes = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM tarefas WHERE concluida = 1")
            concluidas = cursor.fetchone()[0]
            
            # Conta atrasadas
            cursor.execute("SELECT titulo FROM tarefas WHERE concluida = 0")
            todas_pendentes = cursor.fetchall()
            conn.close()

            hoje = datetime.now().date()
            atrasadas = 0
            for row in todas_pendentes:
                data_prazo = self.extrair_data_prazo(row[0])
                if data_prazo and data_prazo < hoje:
                    atrasadas += 1

        except sqlite3.OperationalError:
            total, pendentes, concluidas, atrasadas = 0, 0, 0, 0

        self.lbl_stats_total.configure(text=f"Total: {total}")
        self.lbl_stats_pendentes.configure(text=f"Pendentes: {pendentes}")
        self.lbl_stats_atrasadas.configure(text=f"Atrasadas: {atrasadas}")
        self.lbl_stats_concluidas.configure(text=f"Concluídas: {concluidas}")

    def carregar_tarefas(self, termo_busca=""):
        self.termo_busca_atual = termo_busca

        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.frames_tarefas.clear()
        self.ids_tarefas_carregadas.clear()
        self.tarefa_selecionada_id = None
        self.atualizar_estado_botoes_globais()
        self.atualizar_estatisticas()

        if self.termo_busca_atual:
            self.scroll_frame.configure(label_text=f"🔍 Buscando por: \"{self.termo_busca_atual}\" (Ctrl + Shift + F para limpar)")
        else:
            self.scroll_frame.configure(label_text="Tarefas pendentes (Ctrl + / para Comandos)")

        try:
            self.verificar_e_recriar_db()
            conn = conectar_db()
            cursor = conn.cursor()

            if self.termo_busca_atual:
                cursor.execute("""
                    SELECT id, titulo, concluida, detalhes, prioridade 
                    FROM tarefas 
                    WHERE titulo LIKE ?
                """, (f"%{self.termo_busca_atual}%",))
            else:
                cursor.execute("""
                    SELECT id, titulo, concluida, detalhes, prioridade 
                    FROM tarefas
                """)

            registros = cursor.fetchall()
            conn.close()
        except sqlite3.OperationalError:
            registros = []

        # Ordenação Avançada: 
        # 1º Concluídas por último (concluida: 0 antes de 1)
        # 2º Atrasadas primeiro (se data_prazo < hoje)
        # 3º Data de Vencimento mais próxima
        # 4º Prioridade (Alta, Média, Baixa)
        hoje = datetime.now().date()
        mapa_prioridade = {"Alta": 1, "Média": 2, "Baixa": 3}

        def chave_ordenacao(reg):
            concluida = reg[2]
            titulo = reg[1]
            prioridade = reg[4]
            data_prazo = self.extrair_data_prazo(titulo)
            
            # Verifica se está atrasada (0 para sim, 1 para não, garantindo que atrasadas fiquem no topo)
            atrasada = 0 if (concluida == 0 and data_prazo and data_prazo < hoje) else 1
            
            # Valor padrão para datas caso não possua prazo
            data_chave = data_prazo if data_prazo else datetime.max.date()
            
            return (concluida, atrasada, data_chave, mapa_prioridade.get(prioridade, 3))

        registros.sort(key=chave_ordenacao)

        if self.termo_busca_atual:
            frame_limpar_busca = ctk.CTkFrame(self.scroll_frame, fg_color="#1f2937", corner_radius=6, height=36)
            frame_limpar_busca.pack(fill="x", pady=(0, 6), padx=5)
            frame_limpar_busca.pack_propagate(False)

            lbl_info_busca = ctk.CTkLabel(frame_limpar_busca, text=f"Resultados para \"{self.termo_busca_atual}\"", font=("Segoe UI", 12, "bold"), text_color="#60a5fa")
            lbl_info_busca.pack(side="left", padx=10)

            btn_fechar_busca = ctk.CTkButton(
                frame_limpar_busca, 
                text="✖ Limpar Busca", 
                font=("Segoe UI", 11, "bold"), 
                width=100, 
                height=26, 
                fg_color="#b91c1c", 
                hover_color="#991b1b",
                command=lambda: self.carregar_tarefas("")
            )
            btn_fechar_busca.pack(side="right", padx=8)

        if not registros:
            texto_vazio = "Nenhuma tarefa encontrada com esse termo." if self.termo_busca_atual else "Nenhuma tarefa cadastrada."
            lbl_vazio = ctk.CTkLabel(self.scroll_frame, text=texto_vazio, font=("Segoe UI", 12), text_color="gray")
            lbl_vazio.pack(pady=20)
            return

        for indice, reg in enumerate(registros, start=1):
            tarefa_id, titulo, concluida, detalhes, prioridade = reg[0], reg[1], reg[2], reg[3], reg[4]
            
            self.ids_tarefas_carregadas.append((tarefa_id, concluida))

            # Verifica se está atrasada para estilização
            data_prazo = self.extrair_data_prazo(titulo)
            esta_atrasada = (concluida == 0 and data_prazo and data_prazo < hoje)

            row_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#2a2a2a" if concluida == 0 else "#222222", corner_radius=6, height=45)
            row_frame.pack(fill="x", pady=4, padx=5)
            row_frame.pack_propagate(False)
            self.frames_tarefas[tarefa_id] = row_frame

            if esta_atrasada:
                tag_prioridade = "[Atrasada]"
                cor_prioridade = "#ef4444"
                cor_texto = "#ef4444"
                texto_exibicao = f"{indice}. {titulo}  |  {tag_prioridade}"
            else:
                if prioridade == "Alta":
                    tag_prioridade = "[Alta]"
                    cor_prioridade = "#f87171"
                elif prioridade == "Média":
                    tag_prioridade = "[Média]"
                    cor_prioridade = "#fbbf24"
                else:
                    tag_prioridade = "[Baixa]"
                    cor_prioridade = "#34d399"

                if concluida == 1:
                    texto_exibicao = f"✓ {indice}. {titulo}  |  {tag_prioridade}"
                    cor_texto = "#9ca3af"
                else:
                    texto_exibicao = f"{indice}. {titulo}"
                    cor_texto = "#f3f4f6"

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
            btn_linha_notas.pack(side="right", padx=10, pady=7)

            if concluida == 0:
                lbl_tag = ctk.CTkLabel(row_frame, text=tag_prioridade, font=("Segoe UI", 11, "bold"), text_color=cor_prioridade)
                lbl_tag.pack(side="right", padx=5, pady=7)
                lbl_tag.bind("<Button-1>", lambda event, tid=tarefa_id, stat=concluida: self.selecionar_tarefa(tid, stat))

            lbl_texto = ctk.CTkLabel(row_frame, text=texto_exibicao, font=("Segoe UI", 13), text_color=cor_texto, anchor="w")
            lbl_texto.pack(side="left", fill="x", expand=True, padx=12, pady=7)

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

    def navegar_setas(self, direcao):
        """Permite navegar pelas tarefas usando as setas Up e Down do teclado."""
        if not self.ids_tarefas_carregadas:
            return

        lista_ids = [item[0] for item in self.ids_tarefas_carregadas]
        status_dict = {item[0]: item[1] for item in self.ids_tarefas_carregadas}

        if self.tarefa_selecionada_id is None:
            novo_id = lista_ids[0] if direcao > 0 else lista_ids[-1]
        else:
            try:
                indice_atual = lista_ids.index(self.tarefa_selecionada_id)
                novo_indice = (indice_atual + direcao) % len(lista_ids)
                novo_id = lista_ids[novo_indice]
            except ValueError:
                novo_id = lista_ids[0]

        self.selecionar_tarefa(novo_id, status_dict[novo_id])
        return "break"

    def atualizar_estado_botoes_globais(self):
        try:
            self.verificar_e_recriar_db()
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tarefas")
            total_tarefas = cursor.fetchone()[0]
            conn.close()
        except sqlite3.OperationalError:
            total_tarefas = 0

        if self.tarefa_selecionada_id is not None:
            if self.status_selecionado == 1:
                self.btn_concluir.configure(text="Desfazer", fg_color="#ca8a04", hover_color="#a16207", state="normal")
            else:
                self.btn_concluir.configure(text="Concluir", fg_color="#16a34a", hover_color="#15803d", state="normal")

            self.btn_editar.configure(state="normal")
            self.btn_duplicar.configure(fg_color="#2563eb", hover_color="#1d4ed8", state="normal")
            self.btn_excluir_sel.configure(fg_color="#ef4444", hover_color="#dc2626", state="normal")
        else:
            self.btn_concluir.configure(text="Concluir", fg_color="#4b5563", hover_color="#4b5563", state="disabled")
            self.btn_editar.configure(fg_color="#4b5563", hover_color="#4b5563", state="disabled")
            self.btn_duplicar.configure(fg_color="#4b5563", hover_color="#4b5563", state="disabled")
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

    def atalho_abrir_busca(self, event):
        self.abrir_janela_busca()
        return "break"

    def atalho_limpar_busca(self, event):
        if self.termo_busca_atual:
            self.carregar_tarefas("")
        return "break"

    def atalho_renomear_tarefa(self, event):
        self.renomear_tarefa_global()
        return "break"

    def atalho_duplicar_tarefa(self, event):
        self.duplicar_tarefa_selecionada()
        return "break"

    def atalho_excluir_selecionada(self, event):
        self.excluir_tarefa_selecionada()
        return "break"

    def atalho_excluir_todas(self, event):
        self.excluir_todas_tarefas()
        return "break"

    def atalho_fechar_app(self, event):
        self.destroy()
        return "break"

    def atalho_recarregar_app(self, event):
        self.carregar_tarefas(self.termo_busca_atual)
        return "break"

    def atalho_concluir_tarefa(self, event):
        """Atalho Ctrl + K para alternar o status de conclusão da tarefa selecionada."""
        self.alternar_conclusao_global()
        return "break"

    def adicionar_tarefa(self):
        texto = self.entrada_tarefa.get().strip()
        if not texto:
            messagebox.showwarning("Aviso", "Escreva uma tarefa antes de adicionar!")
            return

        prioridade_escolhida = self.prioridade_var.get()

        self.verificar_e_recriar_db()
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tarefas (titulo, concluida, detalhes, prioridade) VALUES (?, 0, '', ?)", (texto, prioridade_escolhida))
        conn.commit()
        conn.close()

        self.entrada_tarefa.delete(0, "end")
        self.prioridade_var.set("Baixa")
        self.carregar_tarefas(self.termo_busca_atual)

    def duplicar_tarefa_selecionada(self):
        if self.tarefa_selecionada_id is None:
            return

        self.verificar_e_recriar_db()
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT titulo, detalhes, prioridade FROM tarefas WHERE id = ?", (self.tarefa_selecionada_id,))
        reg = cursor.fetchone()

        if reg:
            titulo_original, detalhes, prioridade = reg[0], reg[1], reg[2]
            novo_titulo = f"{titulo_original} (Cópia)"

            cursor.execute("INSERT INTO tarefas (titulo, concluida, detalhes, prioridade) VALUES (?, 0, ?, ?)", (novo_titulo, detalhes, prioridade))
            conn.commit()

        conn.close()
        self.carregar_tarefas(self.termo_busca_atual)

    def abrir_menu_comandos(self):
        janela_cmd = ctk.CTkToplevel(self)
        janela_cmd.title("Paleta de Comandos")
        janela_cmd.geometry("440x520")
        janela_cmd.grab_set()

        # Vincula Ctrl+W para fechar esta janela Toplevel
        janela_cmd.bind("<Control-w>", lambda event: janela_cmd.destroy())
        janela_cmd.bind("<Control-W>", lambda event: janela_cmd.destroy())

        lbl_titulo = ctk.CTkLabel(janela_cmd, text="Comandos rápidos e atalhos", font=("Segoe UI", 14, "bold"))
        lbl_titulo.pack(pady=(15, 10), padx=20, anchor="w")

        frame_opcoes = ctk.CTkScrollableFrame(janela_cmd, corner_radius=8)
        frame_opcoes.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        def executar_comando(tipo):
            janela_cmd.destroy()
            if tipo == "focar":
                self.focar_nova_tarefa()
            elif tipo == "calendario":
                self.abrir_calendario()
            elif tipo == "busca":
                self.abrir_janela_busca()
            elif tipo == "limpar_busca":
                self.carregar_tarefas("")
            elif tipo == "renomear":
                self.renomear_tarefa_global()
            elif tipo == "duplicar":
                self.duplicar_tarefa_selecionada()
            elif tipo == "recarregar":
                self.carregar_tarefas(self.termo_busca_atual)
            elif tipo == "excluir_sel":
                self.excluir_tarefa_selecionada()
            elif tipo == "limpar":
                self.excluir_todas_tarefas()
            elif tipo == "fechar":
                self.destroy()

        btn_focar = ctk.CTkButton(frame_opcoes, text="Nova Tarefa  (Ctrl + N)", anchor="w", fg_color="transparent", text_color="#f3f4f6", hover_color="#374151", height=38, command=lambda: executar_comando("focar"))
        btn_focar.pack(fill="x", pady=2)

        btn_cal = ctk.CTkButton(frame_opcoes, text="Abrir Calendário  (Ctrl + C)", anchor="w", fg_color="transparent", text_color="#f3f4f6", hover_color="#374151", height=38, command=lambda: executar_comando("calendario"))
        btn_cal.pack(fill="x", pady=2)

        btn_busca = ctk.CTkButton(frame_opcoes, text="Buscar Tarefas  (Ctrl + F)", anchor="w", fg_color="transparent", text_color="#f3f4f6", hover_color="#374151", height=38, command=lambda: executar_comando("busca"))
        btn_busca.pack(fill="x", pady=2)

        btn_limpar_busca = ctk.CTkButton(frame_opcoes, text="Limpar Filtro de Busca  (Ctrl + Shift + F)", anchor="w", fg_color="transparent", text_color="#60a5fa", hover_color="#374151", height=38, command=lambda: executar_comando("limpar_busca"))
        btn_limpar_busca.pack(fill="x", pady=2)

        btn_renomear = ctk.CTkButton(frame_opcoes, text="Renomear Selecionada  (Ctrl + R)", anchor="w", fg_color="transparent", text_color="#f3f4f6", hover_color="#374151", height=38, command=lambda: executar_comando("renomear"))
        btn_renomear.pack(fill="x", pady=2)

        btn_duplicar = ctk.CTkButton(frame_opcoes, text="Duplicar Selecionada  (Ctrl + M)", anchor="w", fg_color="transparent", text_color="#f3f4f6", hover_color="#374151", height=38, command=lambda: executar_comando("duplicar"))
        btn_duplicar.pack(fill="x", pady=2)

        btn_recarregar = ctk.CTkButton(frame_opcoes, text="Atualizar / Recarregar Estado  (Ctrl + U)", anchor="w", fg_color="transparent", text_color="#60a5fa", hover_color="#374151", height=38, command=lambda: executar_comando("recarregar"))
        btn_recarregar.pack(fill="x", pady=2)

        btn_excluir = ctk.CTkButton(frame_opcoes, text="Excluir Selecionada  (Ctrl + D)", anchor="w", fg_color="transparent", text_color="#fca5a5", hover_color="#7f1d1d", height=38, command=lambda: executar_comando("excluir_sel"))
        btn_excluir.pack(fill="x", pady=2)

        btn_limpar = ctk.CTkButton(frame_opcoes, text="Limpar Todas as Tarefas  (Ctrl + Shift + D)", anchor="w", fg_color="transparent", text_color="#fca5a5", hover_color="#7f1d1d", height=38, command=lambda: executar_comando("limpar"))
        btn_limpar.pack(fill="x", pady=2)

        btn_fechar = ctk.CTkButton(frame_opcoes, text="Fechar Aplicação  (Ctrl + W)", anchor="w", fg_color="transparent", text_color="#fca5a5", hover_color="#7f1d1d", height=38, command=lambda: executar_comando("fechar"))
        btn_fechar.pack(fill="x", pady=2)

    def abrir_janela_busca(self):
        janela_busca = ctk.CTkToplevel(self)
        janela_busca.title("Buscar Tarefas")
        janela_busca.geometry("400x180")
        janela_busca.grab_set()

        # Vincula Ctrl+W para fechar esta janela Toplevel
        janela_busca.bind("<Control-w>", lambda event: janela_busca.destroy())
        janela_busca.bind("<Control-W>", lambda event: janela_busca.destroy())

        lbl_busca = ctk.CTkLabel(janela_busca, text="Digite o termo para pesquisar:", font=("Segoe UI", 13, "bold"))
        lbl_busca.pack(pady=(20, 10), padx=20, anchor="w")

        entrada_termo = ctk.CTkEntry(janela_busca, placeholder_text="Ex: Trabalho, Estudar...", font=("Segoe UI", 13), height=40, corner_radius=8)
        entrada_termo.pack(fill="x", padx=20, pady=(0, 15))
        
        if self.termo_busca_atual:
            entrada_termo.insert(0, self.termo_busca_atual)

        janela_busca.after(100, lambda: entrada_termo.focus_force())

        def executar_busca(event=None):
            termo = entrada_termo.get().strip()
            self.carregar_tarefas(termo)
            janela_busca.destroy()

        entrada_termo.bind("<Return>", executar_busca)

        btn_pesquisar = ctk.CTkButton(janela_busca, text="Pesquisar", font=("Segoe UI", 12, "bold"), fg_color="#1d4ed8", hover_color="#1e40af", height=36, corner_radius=6, command=executar_busca)
        btn_pesquisar.pack(fill="x", padx=20, pady=(0, 20))

    def abrir_calendario(self):
        janela_cal = ctk.CTkToplevel(self)
        janela_cal.title("Calendário de Prazos")
        janela_cal.grab_set()

        # Vincula Ctrl+W para fechar esta janela Toplevel
        janela_cal.bind("<Control-w>", lambda event: janela_cal.destroy())
        janela_cal.bind("<Control-W>", lambda event: janela_cal.destroy())

        lbl_cal = ctk.CTkLabel(janela_cal, text="Selecione uma Data para Prazo:", font=("Segoe UI", 13, "bold"))
        lbl_cal.pack(pady=(15, 10))

        cal = Calendar(janela_cal, selectmode='day', year=2026, month=11, day=11, background='#1f2937', disabledbackground='#2a2a2a', bordercolor='#374151', headersbackground='#374151', normalbackground='#2a2a2a', foreground='white', normalforeground='white', selectbackground='#1d4ed8')
        cal.pack(padx=20, pady=(0, 15), fill="both", expand=True)

        def selecionar_data():
            data_escolhida = cal.get_date()
            self.entrada_tarefa.insert("end", f" [Prazo: {data_escolhida}]")
            janela_cal.destroy()

        btn_confirmar = ctk.CTkButton(janela_cal, text="Inserir Prazo na Tarefa", font=("Segoe UI", 12, "bold"), fg_color="#16a34a", hover_color="#15803d", height=36, corner_radius=6, command=selecionar_data)
        btn_confirmar.pack(fill="x", padx=20, pady=(0, 20))

    def abrir_janela_notas(self, tarefa_id, titulo_tarefa):
        self.verificar_e_recriar_db()
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT detalhes FROM tarefas WHERE id = ?", (tarefa_id,))
        resultado = cursor.fetchone()
        conn.close()
        detalhes_atuais = resultado[0] if resultado and resultado[0] else ""

        janela_notas = ctk.CTkToplevel(self)
        janela_notas.title("Bloco de Notas da Tarefa")
        janela_notas.grab_set()

        # Vincula Ctrl+W para fechar esta janela Toplevel
        janela_notas.bind("<Control-w>", lambda event: janela_notas.destroy())
        janela_notas.bind("<Control-W>", lambda event: janela_notas.destroy())

        lbl_info = ctk.CTkLabel(janela_notas, text=f"Notas para: {titulo_tarefa}", font=("Segoe UI", 13, "bold"))
        lbl_info.pack(pady=(20, 10), padx=20, anchor="w")

        txt_detalhes = ctk.CTkTextbox(janela_notas, font=("Segoe UI", 12), corner_radius=8)
        txt_detalhes.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        txt_detalhes.insert("1.0", detalhes_atuais)

        def salvar_notas():
            novos_detalhes = txt_detalhes.get("1.0", "end-1c").strip()
            
            self.verificar_e_recriar_db()
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

        self.verificar_e_recriar_db()
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE tarefas SET concluida = ? WHERE id = ?", (novo_status, self.tarefa_selecionada_id))
        conn.commit()
        conn.close()
        
        self.carregar_tarefas(self.termo_busca_atual)

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

            self.verificar_e_recriar_db()
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE tarefas SET titulo = ? WHERE id = ?", (novo_texto, self.tarefa_selecionada_id))
            conn.commit()
            conn.close()
            self.carregar_tarefas(self.termo_busca_atual)

    def excluir_tarefa_selecionada(self):
        if self.tarefa_selecionada_id is None:
            return

        self.verificar_e_recriar_db()
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tarefas WHERE id = ?", (self.tarefa_selecionada_id,))
        conn.commit()
        conn.close()
        
        self.carregar_tarefas(self.termo_busca_atual)

    def excluir_todas_tarefas(self, event=None):
        resposta = messagebox.askyesno("Confirmação", "Tem certeza absoluta que deseja apagar TODAS as tarefas?")
        if resposta:
            self.verificar_e_recriar_db()
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tarefas")
            conn.commit()
            conn.close()
            self.carregar_tarefas("")

if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()