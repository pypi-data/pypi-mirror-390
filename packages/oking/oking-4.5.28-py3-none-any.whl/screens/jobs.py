"""
⚙️ Tela de Configuração de Jobs - OKING Hub
Lista dinâmica de jobs carregados da API com editor individual
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import re
import json
import urllib.request
import urllib.error
from ui_components import ModernTheme, Card, ModernButton


# ==================== COMPONENTES ====================

class SQLEditor(tk.Frame):
    """Editor SQL com numeração de linhas e syntax highlighting"""
    
    def __init__(self, parent, theme=None, height=15, **kwargs):
        super().__init__(parent, bg=(theme or ModernTheme()).BG_CODE)
        self.theme = theme or ModernTheme()
        
        # Frame principal
        editor_frame = tk.Frame(self, bg=self.theme.BG_CODE)
        editor_frame.pack(fill='both', expand=True, padx=1, pady=1)
        
        # Numeração de linhas
        self.line_numbers = tk.Text(
            editor_frame,
            width=4,
            padx=4,
            pady=5,
            bg=self.theme.BG_CODE,
            fg=self.theme.TEXT_SECONDARY,
            font=self.theme.get_font("sm", mono=True),
            state='disabled',
            wrap='none',
            cursor='arrow'
        )
        self.line_numbers.pack(side='left', fill='y')
        
        # Área de código
        self.code_area = scrolledtext.ScrolledText(
            editor_frame,
            height=height,
            wrap='none',
            font=self.theme.get_font("sm", mono=True),
            bg=self.theme.BG_CODE,
            fg=self.theme.TEXT_CODE,
            insertbackground='white',
            selectbackground=self.theme.PRIMARY,
            relief='flat',
            padx=8,
            pady=5,
            **kwargs
        )
        self.code_area.pack(side='left', fill='both', expand=True)
        
        # Tags de syntax highlighting
        self.code_area.tag_config('keyword', foreground='#c792ea')
        self.code_area.tag_config('string', foreground='#c3e88d')
        self.code_area.tag_config('comment', foreground='#546e7a')
        self.code_area.tag_config('number', foreground='#f78c6c')
        
        # Eventos
        self.code_area.bind('<KeyRelease>', self._on_change)
        self.code_area.bind('<MouseWheel>', self._sync_scroll)
        
        self._update_line_numbers()
    
    def _on_change(self, event=None):
        """Atualiza numeração e highlighting"""
        self._update_line_numbers()
        self._highlight_syntax()
    
    def _update_line_numbers(self):
        """Atualiza numeração de linhas"""
        line_count = int(self.code_area.index('end-1c').split('.')[0])
        line_numbers_string = "\n".join(str(i) for i in range(1, line_count + 1))
        
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')
        self.line_numbers.insert('1.0', line_numbers_string)
        self.line_numbers.config(state='disabled')
    
    def _sync_scroll(self, event):
        """Sincroniza scroll entre numeração e código"""
        self.line_numbers.yview_moveto(self.code_area.yview()[0])
    
    def _highlight_syntax(self):
        """Aplica syntax highlighting SQL"""
        # Remove tags antigas
        for tag in ['keyword', 'string', 'comment', 'number']:
            self.code_area.tag_remove(tag, '1.0', 'end')
        
        code = self.code_area.get('1.0', 'end')
        
        # Keywords SQL
        keywords = r'\b(SELECT|FROM|WHERE|JOIN|INNER|LEFT|RIGHT|OUTER|ON|AND|OR|GROUP BY|ORDER BY|HAVING|LIMIT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|TABLE|INDEX|VIEW|AS|IN|NOT|NULL|IS|LIKE|BETWEEN|CASE|WHEN|THEN|ELSE|END|DISTINCT|TOP|WITH|CAST|COALESCE|COUNT|SUM|AVG|MAX|MIN)\b'
        for match in re.finditer(keywords, code, re.IGNORECASE):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.code_area.tag_add('keyword', start, end)
        
        # Strings
        for match in re.finditer(r"'[^']*'", code):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.code_area.tag_add('string', start, end)
        
        # Comentários
        for match in re.finditer(r'--[^\n]*', code):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.code_area.tag_add('comment', start, end)
        
        # Números
        for match in re.finditer(r'\b\d+\b', code):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.code_area.tag_add('number', start, end)
    
    def get(self):
        """Retorna conteúdo"""
        return self.code_area.get('1.0', 'end-1c')
    
    def set(self, content):
        """Define conteúdo"""
        self.code_area.delete('1.0', 'end')
        self.code_area.insert('1.0', content)
        self._update_line_numbers()
        self._highlight_syntax()
    
    def clear(self):
        """Limpa editor"""
        self.set('')


class ToggleSwitch(tk.Canvas):
    """Switch ON/OFF customizado"""
    
    def __init__(self, parent, theme=None, callback=None):
        self.theme = theme or ModernTheme()
        self.callback = callback
        self.state = False
        
        super().__init__(
            parent,
            width=60,
            height=30,
            bg=parent['bg'],
            highlightthickness=0,
            cursor='hand2'
        )
        
        # Background
        self.bg_rect = self.create_rectangle(
            5, 5, 55, 25,
            fill='#e2e8f0',
            outline='',
            tags='bg'
        )
        
        # Circle
        self.circle = self.create_oval(
            7, 7, 23, 23,
            fill='white',
            outline='',
            tags='circle'
        )
        
        self.bind('<Button-1>', lambda e: self._toggle())
    
    def _toggle(self):
        """Alterna estado"""
        self.state = not self.state
        self._animate()
        if self.callback:
            self.callback(self.state)
    
    def _animate(self):
        """Anima transição"""
        if self.state:
            self.itemconfig(self.bg_rect, fill=self.theme.SUCCESS)
            self.coords(self.circle, 39, 7, 55, 23)
        else:
            self.itemconfig(self.bg_rect, fill='#e2e8f0')
            self.coords(self.circle, 7, 7, 23, 23)
    
    def get_state(self):
        """Retorna estado atual"""
        return self.state
    
    def set_state(self, state):
        """Define estado"""
        self.state = state
        self._animate()


# ==================== TELA PRINCIPAL ====================

class JobsScreen(tk.Frame):
    """Tela de configuração de jobs com lista dinâmica"""
    
    def __init__(self, parent, shortname=None, token_manager=None):
        super().__init__(parent, bg=ModernTheme().BG_SECONDARY)
        self.theme = ModernTheme()
        self.shortname = shortname
        self.token_manager = token_manager
        self.jobs_data = []
        self.current_job = None
        self.editor_expanded = False  # Estado de expansão do editor
        
        self._build_ui()
        self._load_jobs_from_api()
    
    def _build_ui(self):
        """Constrói interface"""
        # Container principal dividido
        self.main_container = tk.Frame(self, bg=self.theme.BG_SECONDARY)
        self.main_container.pack(fill='both', expand=True, padx=24, pady=24)
        
        # PAINEL ESQUERDO: Lista de Jobs
        self.left_panel = tk.Frame(self.main_container, bg=self.theme.BG_SECONDARY)
        self.left_panel.pack(side='left', fill='both', expand=False, padx=(0, 12))
        self.left_panel.pack_propagate(False)
        self.left_panel.configure(width=350)
        
        self._build_jobs_list(self.left_panel)
        
        # PAINEL DIREITO: Editor do Job (SEM padding, o Card já tem)
        self.right_panel = tk.Frame(self.main_container, bg=self.theme.BG_SECONDARY)
        self.right_panel.pack(side='left', fill='both', expand=True)
        
        self._show_empty_state()
    
    def _build_jobs_list(self, parent):
        """Constrói lista de jobs"""
        # Header
        header_card = Card(parent, theme=self.theme)
        header_card.pack(fill='x', pady=(0, 6))  # REDUZIDO: 12 → 6
        
        header_container = tk.Frame(header_card, bg=self.theme.BG_PRIMARY)
        header_container.pack(fill='x', padx=20, pady=16)
        
        tk.Label(
            header_container,
            text="📋 Lista de Jobs",
            font=self.theme.get_font("lg", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left')
        
        # Botão refresh
        ModernButton(
            header_container,
            text="🔄",
            variant="secondary",
            theme=self.theme,
            command=self._load_jobs_from_api
        ).pack(side='right')
        
        # Lista scrollável
        list_card = Card(parent, theme=self.theme)
        list_card.pack(fill='both', expand=True)
        
        # Canvas + Scrollbar
        canvas = tk.Canvas(
            list_card,
            bg=self.theme.BG_PRIMARY,
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(list_card, orient='vertical', command=canvas.yview)
        
        self.jobs_list_frame = tk.Frame(canvas, bg=self.theme.BG_PRIMARY)
        
        canvas.create_window((0, 0), window=self.jobs_list_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True, padx=12, pady=12)
        scrollbar.pack(side='right', fill='y')
        
        # Configurar scroll region
        self.jobs_list_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        # ADICIONAR MOUSEWHEEL SCROLL
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    def _show_empty_state(self):
        """Mostra estado vazio (sem job selecionado)"""
        # Resetar estado de expansão
        self.editor_expanded = False
        
        # Garantir que lista esteja visível ao voltar
        if not self.left_panel.winfo_ismapped():
            self.left_panel.pack(side='left', fill='both', padx=(0, 12), before=self.right_panel)
            self.left_panel.pack_propagate(False)
            self.left_panel.configure(width=350)
        
        # Limpar painel direito
        for widget in self.right_panel.winfo_children():
            widget.destroy()
        
        empty_card = Card(self.right_panel, theme=self.theme)
        empty_card.pack(fill='both', expand=True)
        
        container = tk.Frame(empty_card, bg=self.theme.BG_PRIMARY)
        container.pack(expand=True, padx=40, pady=40)
        
        tk.Label(
            container,
            text="📄",
            font=self.theme.get_font("xxl"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY
        ).pack(pady=(0, 16))
        
        tk.Label(
            container,
            text="Selecione um job para editar",
            font=self.theme.get_font("lg"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY
        ).pack()
    
    def _load_jobs_from_api(self):
        """Carrega jobs da API"""
        try:
            # Verificar se temos token e shortname
            if not self.shortname or not self.token_manager:
                print("[WARN] JobsScreen: shortname ou token_manager não fornecidos, usando dados de exemplo")
                self._load_sample_jobs()
                return
            
            # Obter token ativo
            active_token = self.token_manager.get_active_token()
            if not active_token:
                print("[WARN] JobsScreen: Nenhum token ativo, usando dados de exemplo")
                self._load_sample_jobs()
                return
            
            token_value = active_token.get('token', '')
            
            # Montar URL da API
            api_url = f"https://{self.shortname}.oking.openk.com.br/api/consulta/oking_hub/filtros?token={token_value}"
            
            print(f"[INFO] JobsScreen: Carregando jobs da API: {self.shortname}")
            
            # Fazer requisição
            with urllib.request.urlopen(api_url, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                self.jobs_data = data.get('modulos', [])
                print(f"[INFO] JobsScreen: {len(self.jobs_data)} jobs carregados com sucesso!")
                self._populate_jobs_list()
                
        except urllib.error.URLError as e:
            print(f"[ERROR] JobsScreen: Erro de conexão com API: {e}")
            messagebox.showerror(
                "Erro de Conexão",
                f"Não foi possível conectar à API:\n{str(e)}\n\nUsando dados de exemplo."
            )
            # Dados de exemplo para desenvolvimento
            self._load_sample_jobs()
        except Exception as e:
            print(f"[ERROR] JobsScreen: Erro ao carregar jobs: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror(
                "Erro",
                f"Erro ao carregar jobs:\n{str(e)}\n\nUsando dados de exemplo."
            )
            self._load_sample_jobs()
    
    def _load_sample_jobs(self):
        """Carrega jobs de exemplo (fallback)"""
        self.jobs_data = [
            {
                "job": "envia_cliente_job",
                "nome_job": "Enviar Clientes para Hub",  # Nome amigável
                "ativo": "S",
                "comando_sql": "SELECT * FROM CLIENTES",
                "tempo_execucao": 30,
                "unidade_tempo": "M",
                "tamanho_pacote": 100  # Compatibilidade
            },
            {
                "job": "sincroniza_estoque_job",
                "nome_job": "Sincronizar Estoque",  # Nome amigável
                "ativo": "N",
                "comando_sql": "SELECT * FROM ESTOQUE",
                "tempo_execucao": 15,
                "unidade_tempo": "M",
                "tamanho_pacote": 50  # Compatibilidade
            }
        ]
        self._populate_jobs_list()
    
    def _populate_jobs_list(self):
        """Popula lista de jobs na UI"""
        # Limpa lista atual
        for widget in self.jobs_list_frame.winfo_children():
            widget.destroy()
        
        if not self.jobs_data:
            tk.Label(
                self.jobs_list_frame,
                text="Nenhum job encontrado",
                font=self.theme.get_font("md"),
                fg=self.theme.TEXT_SECONDARY,
                bg=self.theme.BG_PRIMARY
            ).pack(pady=20)
            return
        
        # Cria item para cada job
        for idx, job in enumerate(self.jobs_data):
            self._create_job_item(job, idx)
    
    def _create_job_item(self, job, index):
        """Cria item visual para um job"""
        item = tk.Frame(
            self.jobs_list_frame,
            bg=self.theme.BG_SECONDARY,
            cursor='hand2'
        )
        item.pack(fill='x', padx=8, pady=2)  # REDUZIDO: pady=4 → 2
        
        content = tk.Frame(item, bg=self.theme.BG_SECONDARY, cursor='hand2')
        content.pack(fill='x', padx=12, pady=8)  # REDUZIDO: pady=12 → 8
        
        # Ícone
        icon_label = tk.Label(
            content,
            text="⚙️",
            font=self.theme.get_font("md"),  # REDUZIDO: lg → md
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_SECONDARY,
            cursor='hand2'
        )
        icon_label.pack(side='left', padx=(0, 12))
        
        # Info
        info_frame = tk.Frame(content, bg=self.theme.BG_SECONDARY, cursor='hand2')
        info_frame.pack(side='left', fill='x', expand=True)
        
        # USAR nome_job se existir, senão usa job (compatibilidade com versões antigas)
        job_display_name = job.get('nome_job') or job.get('job', 'Sem nome')
        
        name_label = tk.Label(
            info_frame,
            text=job_display_name,
            font=self.theme.get_font("sm", "bold"),  # REDUZIDO: md → sm (-2px)
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_SECONDARY,
            anchor='w',
            cursor='hand2'
        )
        name_label.pack(fill='x')
        
        # Intervalo
        interval_text = f"{job.get('tempo_execucao', 0)} min"
        interval_label = tk.Label(
            info_frame,
            text=interval_text,
            font=self.theme.get_font("xs"),  # REDUZIDO: sm → xs (-2px)
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_SECONDARY,
            anchor='w',
            cursor='hand2'
        )
        interval_label.pack(fill='x')
        
        # Status badge
        status = "ATIVO" if job.get('ativo') == 'S' else "INATIVO"
        status_color = self.theme.SUCCESS if job.get('ativo') == 'S' else self.theme.DANGER
        
        status_label = tk.Label(
            content,
            text=status,
            font=self.theme.get_font("xs", "bold"),
            fg='white',
            bg=status_color,
            padx=8,
            pady=4,
            cursor='hand2'
        )
        status_label.pack(side='right')
        
        # Click handler
        def on_click(e):
            self._select_job(job, index)
        
        # Hover
        def on_enter(e):
            item.configure(bg=self.theme.BG_HOVER)
            content.configure(bg=self.theme.BG_HOVER)
            info_frame.configure(bg=self.theme.BG_HOVER)
            icon_label.configure(bg=self.theme.BG_HOVER)
            name_label.configure(bg=self.theme.BG_HOVER)
            interval_label.configure(bg=self.theme.BG_HOVER)
        
        def on_leave(e):
            item.configure(bg=self.theme.BG_SECONDARY)
            content.configure(bg=self.theme.BG_SECONDARY)
            info_frame.configure(bg=self.theme.BG_SECONDARY)
            icon_label.configure(bg=self.theme.BG_SECONDARY)
            name_label.configure(bg=self.theme.BG_SECONDARY)
            interval_label.configure(bg=self.theme.BG_SECONDARY)
        
        # Aplicar bindings em TODOS os widgets
        all_widgets = [item, content, info_frame, icon_label, name_label, interval_label, status_label]
        for widget in all_widgets:
            widget.bind('<Button-1>', on_click)
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
    
    def _select_job(self, job, index):
        """Seleciona um job para edição"""
        self.current_job = {'data': job, 'index': index}
        self.editor_expanded = False  # Reset expansão ao trocar de job
        # Garantir que lista esteja visível ao selecionar novo job
        if not self.left_panel.winfo_ismapped():
            self.left_panel.pack(side='left', fill='both', padx=(0, 12), before=self.right_panel)
            self.left_panel.pack_propagate(False)
            self.left_panel.configure(width=350)
        self._show_job_editor()
    
    def _toggle_editor_expansion(self):
        """Alterna entre editor expandido/normal"""
        self.editor_expanded = not self.editor_expanded
        
        if self.editor_expanded:
            # Esconde lista de jobs
            self.left_panel.pack_forget()
            # Remove padding do main_container para ocupar 100% (esquerda e direita)
            self.main_container.pack_configure(padx=0, pady=0)
        else:
            # Mostra lista de jobs NA MESMA POSIÇÃO (side='left', ANTES do right_panel)
            self.left_panel.pack(side='left', fill='both', padx=(0, 12), before=self.right_panel)
            self.left_panel.pack_propagate(False)
            self.left_panel.configure(width=350)
            # Restaura padding do main_container
            self.main_container.pack_configure(padx=24, pady=24)
        
        # Recarrega editor com novo tamanho
        self._show_job_editor()
    
    def _show_job_editor(self):
        """Mostra editor do job selecionado"""
        # Limpa painel direito
        for widget in self.right_panel.winfo_children():
            widget.destroy()
        
        job = self.current_job['data']
        
        # Container scrollável
        canvas = tk.Canvas(
            self.right_panel,
            bg=self.theme.BG_SECONDARY,
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(self.right_panel, orient='vertical', command=canvas.yview)
        
        editor_container = tk.Frame(canvas, bg=self.theme.BG_SECONDARY)
        
        canvas.create_window((0, 0), window=editor_container, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        editor_container.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        # ADICIONAR MOUSEWHEEL SCROLL NO EDITOR
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # HEADER
        self._build_job_header(editor_container, job)
        
        # STATUS
        self._build_job_status(editor_container, job)
        
        # SQL EDITOR
        self._build_job_sql_editor(editor_container, job)
        
        # CONFIGURAÇÕES
        self._build_job_config(editor_container, job)
        
        # AÇÕES
        self._build_job_actions(editor_container, job)
    
    def _build_job_header(self, parent, job):
        """Header do editor"""
        card = Card(parent, theme=self.theme)
        card.pack(fill='x', pady=(0, 16))
        
        container = tk.Frame(card, bg=self.theme.BG_PRIMARY)
        container.pack(fill='x', padx=20, pady=16)
        
        # USAR nome_job se existir, senão usa job (compatibilidade com versões antigas)
        job_display_name = job.get('nome_job') or job.get('job', 'Job')
        
        tk.Label(
            container,
            text=f"⚙️ {job_display_name}",
            font=self.theme.get_font("xl", "bold"),
            fg=self.theme.PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left')
        
        # Botões à direita
        buttons_frame = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        buttons_frame.pack(side='right')
        
        # Botão expandir/retrair (AGORA NO HEADER - SEMPRE VISÍVEL)
        expand_icon = "⬜" if self.editor_expanded else "⬛"
        expand_text = "Retrair" if self.editor_expanded else "Expandir"
        ModernButton(
            buttons_frame,
            text=f"{expand_icon} {expand_text}",
            variant="secondary",
            theme=self.theme,
            command=self._toggle_editor_expansion
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            buttons_frame,
            text="← Voltar",
            variant="secondary",
            theme=self.theme,
            command=self._show_empty_state
        ).pack(side='left')
    
    def _build_job_status(self, parent, job):
        """Status do job"""
        card = Card(parent, theme=self.theme)
        card.pack(fill='x', pady=(0, 16))
        
        container = tk.Frame(card, bg=self.theme.BG_PRIMARY)
        container.pack(fill='x', padx=20, pady=16)
        
        tk.Label(
            container,
            text="Status:",
            font=self.theme.get_font("md", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left', padx=(0, 12))
        
        # Toggle switch
        self.status_switch = ToggleSwitch(container, theme=self.theme)
        self.status_switch.set_state(job.get('ativo') == 'S')
        self.status_switch.pack(side='left', padx=(0, 12))
        
        self.status_label = tk.Label(
            container,
            text="LIGADO" if job.get('ativo') == 'S' else "DESLIGADO",
            font=self.theme.get_font("md", "bold"),
            fg=self.theme.SUCCESS if job.get('ativo') == 'S' else self.theme.DANGER,
            bg=self.theme.BG_PRIMARY
        )
        self.status_label.pack(side='left')
    
    def _build_job_sql_editor(self, parent, job):
        """Editor SQL"""
        card = Card(parent, theme=self.theme)
        card.pack(fill='x', pady=(0, 16))
        
        container = tk.Frame(card, bg=self.theme.BG_PRIMARY)
        container.pack(fill='both', expand=True, padx=20, pady=16)
        
        # Título do editor
        tk.Label(
            container,
            text="📝 Query SQL:",
            font=self.theme.get_font("md", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(anchor='w', pady=(0, 8))
        
        # Editor SQL (altura dinâmica baseada no estado de expansão)
        editor_height = 25 if self.editor_expanded else 12
        self.sql_editor = SQLEditor(container, theme=self.theme, height=editor_height)
        self.sql_editor.pack(fill='both', expand=True)
        self.sql_editor.set(job.get('comando_sql', ''))
    
    def _build_job_config(self, parent, job):
        """Configurações do job"""
        card = Card(parent, theme=self.theme)
        card.pack(fill='x', pady=(0, 16))
        
        container = tk.Frame(card, bg=self.theme.BG_PRIMARY)
        container.pack(fill='x', padx=20, pady=16)
        
        tk.Label(
            container,
            text="⏱️ Configurações:",
            font=self.theme.get_font("md", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(anchor='w', pady=(0, 12))
        
        # Intervalo
        interval_frame = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        interval_frame.pack(fill='x', pady=(0, 8))
        
        tk.Label(
            interval_frame,
            text="Intervalo de execução:",
            font=self.theme.get_font("md"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left', padx=(0, 12))
        
        self.interval_entry = tk.Entry(
            interval_frame,
            font=self.theme.get_font("md"),
            width=10
        )
        self.interval_entry.insert(0, str(job.get('tempo_execucao', 0)))
        self.interval_entry.pack(side='left', padx=(0, 8))
        
        tk.Label(
            interval_frame,
            text="minutos",
            font=self.theme.get_font("md"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left')
    
    def _build_job_actions(self, parent, job):
        """Ações do job"""
        card = Card(parent, theme=self.theme)
        card.pack(fill='x', pady=(0, 16))
        
        container = tk.Frame(card, bg=self.theme.BG_PRIMARY)
        container.pack(fill='x', padx=20, pady=16)
        
        ModernButton(
            container,
            text="💾 Salvar Configuração",
            variant="primary",
            theme=self.theme,
            command=self._save_job_config
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            container,
            text="▶️ Testar Query",
            variant="success",
            theme=self.theme,
            command=self._test_query
        ).pack(side='left')
    
    def _save_job_config(self):
        """Salva configuração do job na API"""
        if not self.current_job:
            return
        
        job = self.current_job['data']
        
        # Verificar se temos token e shortname
        if not self.shortname or not self.token_manager:
            messagebox.showerror(
                "Erro",
                "Não é possível salvar: shortname ou token não disponíveis"
            )
            return
        
        # Obter token ativo
        active_token = self.token_manager.get_active_token()
        if not active_token:
            messagebox.showerror(
                "Erro",
                "Nenhum token ativo encontrado"
            )
            return
        
        token_value = active_token.get('token', '')
        
        # Coleta dados do formulário
        try:
            sql_comando = self.sql_editor.get()
            tempo_exec = int(self.interval_entry.get() or 0)
            status_ativo = 'S' if self.status_switch.get_state() else 'N'
            
            # Preparar payload para API
            dados = {
                'comando': sql_comando,  # JSON já faz escape automaticamente
                'intervalo': tempo_exec,
                'observacao': job.get('observacao', ''),
                'job': job.get('job'),
                'ativo': status_ativo,
                'token': token_value
            }
            
            print(f"[INFO] JobsScreen: Salvando job '{job.get('job')}'...")
            print(f"[DEBUG] Payload: {dados}")
            
            # Enviar para API
            import urllib.request
            import json
            
            api_url = f"https://{self.shortname}.oking.openk.com.br/api/tarefa"
            
            req = urllib.request.Request(
                api_url,
                data=json.dumps(dados).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if result.get('sucesso'):
                    # Atualizar dados locais
                    config = {
                        'job': job.get('job'),
                        'ativo': status_ativo,
                        'comando_sql': sql_comando,
                        'tempo_execucao': tempo_exec,
                        'unidade_tempo': job.get('unidade_tempo', 'M')
                    }
                    self.jobs_data[self.current_job['index']].update(config)
                    
                    # Atualizar lista visual
                    self._populate_jobs_list()
                    
                    print(f"[INFO] JobsScreen: Job '{job.get('job')}' salvo com sucesso!")
                    
                    messagebox.showinfo(
                        "✅ Sucesso",
                        f"Configuração do job salva com sucesso!\n\n"
                        f"Job: {job.get('nome_job') or job.get('job')}\n"
                        f"Status: {'ATIVO ✅' if status_ativo == 'S' else 'INATIVO ❌'}\n"
                        f"Intervalo: {tempo_exec} minutos"
                    )
                else:
                    raise Exception(result.get('mensagem', 'Erro desconhecido'))
                    
        except ValueError as e:
            messagebox.showerror(
                "Erro de Validação",
                f"Intervalo deve ser um número válido: {e}"
            )
        except urllib.error.URLError as e:
            print(f"[ERROR] JobsScreen: Erro de conexão ao salvar job: {e}")
            messagebox.showerror(
                "Erro de Conexão",
                f"Não foi possível conectar à API:\n{str(e)}"
            )
        except Exception as e:
            print(f"[ERROR] JobsScreen: Erro ao salvar job: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror(
                "Erro ao Salvar",
                f"Erro ao salvar configuração:\n{str(e)}"
            )
    
    def _test_query(self):
        """Testa query SQL na API"""
        query = self.sql_editor.get()
        
        if not query.strip():
            messagebox.showwarning("Aviso", "Query SQL está vazia!")
            return
        
        # Verificar se temos token e shortname
        if not self.shortname or not self.token_manager:
            messagebox.showerror(
                "Erro",
                "Não é possível testar: shortname ou token não disponíveis"
            )
            return
        
        # Obter token ativo
        active_token = self.token_manager.get_active_token()
        if not active_token:
            messagebox.showerror(
                "Erro",
                "Nenhum token ativo encontrado"
            )
            return
        
        token_value = active_token.get('token', '')
        
        try:
            print(f"[INFO] JobsScreen: Testando query SQL...")
            
            # Preparar payload para teste
            import urllib.request
            import json
            
            dados = {
                'comando': query,
                'token': token_value
            }
            
            # Endpoint de teste (pode ser necessário ajustar conforme API)
            api_url = f"https://{self.shortname}.oking.openk.com.br/api/testar_comando"
            
            req = urllib.request.Request(
                api_url,
                data=json.dumps(dados).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=15) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if result.get('sucesso'):
                    registros = result.get('registros', 0)
                    tempo = result.get('tempo', 0)
                    
                    messagebox.showinfo(
                        "✅ Query Validada",
                        f"Query executada com sucesso!\n\n"
                        f"Registros encontrados: {registros}\n"
                        f"Tempo de execução: {tempo}s"
                    )
                else:
                    raise Exception(result.get('mensagem', 'Erro ao executar query'))
                    
        except urllib.error.HTTPError as e:
            # Se endpoint não existir, fazer validação simples
            if e.code == 404:
                print("[WARN] JobsScreen: Endpoint de teste não disponível, validando sintaxe básica")
                self._validate_sql_syntax(query)
            else:
                messagebox.showerror(
                    "Erro HTTP",
                    f"Erro ao testar query (HTTP {e.code}):\n{str(e)}"
                )
        except urllib.error.URLError as e:
            print(f"[ERROR] JobsScreen: Erro de conexão ao testar query: {e}")
            messagebox.showerror(
                "Erro de Conexão",
                f"Não foi possível conectar à API:\n{str(e)}"
            )
        except Exception as e:
            print(f"[ERROR] JobsScreen: Erro ao testar query: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror(
                "Erro ao Testar",
                f"Erro ao testar query:\n{str(e)}"
            )
    
    def _validate_sql_syntax(self, query):
        """Validação básica de sintaxe SQL (fallback)"""
        query_upper = query.upper().strip()
        
        # Verificações básicas
        if not query_upper:
            messagebox.showerror("Erro", "Query está vazia!")
            return
        
        # Comandos SQL válidos
        valid_commands = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'EXEC', 'EXECUTE', 'CALL']
        
        if not any(query_upper.startswith(cmd) for cmd in valid_commands):
            messagebox.showerror(
                "Erro de Sintaxe",
                "Query deve começar com SELECT, INSERT, UPDATE, DELETE, EXEC ou CALL"
            )
            return
        
        # Verificar parênteses balanceados
        if query.count('(') != query.count(')'):
            messagebox.showwarning(
                "Aviso de Sintaxe",
                "Parênteses podem estar desbalanceados"
            )
            return
        
        messagebox.showinfo(
            "✅ Sintaxe Válida",
            "Sintaxe SQL aparenta estar correta!\n\n"
            f"Comando: {query_upper.split()[0]}\n"
            f"Tamanho: {len(query)} caracteres\n\n"
            "⚠️ Validação completa só é possível executando na API"
        )
