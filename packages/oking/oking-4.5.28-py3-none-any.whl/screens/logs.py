"""
📋 Tela de Logs - OKING Hub
Interface moderna em Tkinter para visualizar e filtrar logs
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import random

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from ui_components import ModernTheme, Card, ModernButton, StatusBadge


# ==================== COMPONENTES ====================

class ModernTable(tk.Frame):
    """Tabela moderna com cores alternadas e hover"""
    
    def __init__(self, parent, columns=None, theme=None, on_row_click=None):
        super().__init__(parent, bg=(theme or ModernTheme()).BG_PRIMARY)
        self.theme = theme or ModernTheme()
        self.columns = columns or []
        self.on_row_click = on_row_click
        self.rows = []
        self.row_widgets = []
        
        # Container com scroll
        self.canvas = tk.Canvas(self, bg=self.theme.BG_PRIMARY, highlightthickness=0)
        self.scrollbar_v = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.scrollbar_h = ttk.Scrollbar(self, orient='horizontal', command=self.canvas.xview)
        self.table_frame = tk.Frame(self.canvas, bg=self.theme.BG_PRIMARY)
        
        self.table_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.table_frame, anchor='nw')
        self.canvas.configure(yscrollcommand=self.scrollbar_v.set, xscrollcommand=self.scrollbar_h.set)
        
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar_v.pack(side='right', fill='y')
        self.scrollbar_h.pack(side='bottom', fill='x')
        
        # Criar header
        self._create_header()
    
    def _create_header(self):
        header = tk.Frame(self.table_frame, bg=self.theme.PRIMARY, height=45)
        header.pack(fill='x')
        
        for i, col in enumerate(self.columns):
            label = tk.Label(
                header,
                text=col['title'],
                font=self.theme.get_font("sm", "bold"),
                fg='white',
                bg=self.theme.PRIMARY,
                anchor='w',
                padx=16,
                pady=12
            )
            label.pack(side='left', fill='both', expand=True if col.get('flex') else False)
            
            if not col.get('flex'):
                label.configure(width=col.get('width', 15))
    
    def add_row(self, data, row_data=None):
        """Adiciona uma linha à tabela"""
        row_index = len(self.rows)
        bg_color = self.theme.BG_PRIMARY if row_index % 2 == 0 else self.theme.BG_SECONDARY
        
        row_frame = tk.Frame(self.table_frame, bg=bg_color, cursor='hand2')
        row_frame.pack(fill='x')
        
        # Bind de eventos
        def on_enter(e):
            row_frame.configure(bg=self.theme.BG_HOVER)
            for child in row_frame.winfo_children():
                child.configure(bg=self.theme.BG_HOVER)
        
        def on_leave(e):
            row_frame.configure(bg=bg_color)
            for child in row_frame.winfo_children():
                if not isinstance(child, StatusBadge):
                    child.configure(bg=bg_color)
        
        def on_click(e):
            if self.on_row_click:
                self.on_row_click(row_data or data)
        
        row_frame.bind('<Enter>', on_enter)
        row_frame.bind('<Leave>', on_leave)
        row_frame.bind('<Button-1>', on_click)
        
        # Adicionar células
        for i, col in enumerate(self.columns):
            value = data[i] if i < len(data) else ""
            
            if col.get('type') == 'badge':
                # Badge de status
                status_map = {
                    'success': 'success',
                    'sucesso': 'success',
                    'warning': 'warning',
                    'aviso': 'warning',
                    'error': 'error',
                    'erro': 'error',
                }
                status = status_map.get(str(value).lower(), 'info')
                
                badge_container = tk.Frame(row_frame, bg=bg_color)
                badge_container.pack(side='left', fill='both', padx=16, pady=8)
                badge_container.bind('<Enter>', on_enter)
                badge_container.bind('<Leave>', on_leave)
                badge_container.bind('<Button-1>', on_click)
                
                badge = StatusBadge(badge_container, text=str(value), status=status, theme=self.theme)
                badge.pack()
                badge.bind('<Button-1>', on_click)
            else:
                # Label normal
                cell = tk.Label(
                    row_frame,
                    text=str(value),
                    font=self.theme.get_font("sm"),
                    fg=self.theme.TEXT_PRIMARY,
                    bg=bg_color,
                    anchor='w',
                    padx=16,
                    pady=12
                )
                cell.pack(side='left', fill='both', expand=True if col.get('flex') else False)
                cell.bind('<Enter>', on_enter)
                cell.bind('<Leave>', on_leave)
                cell.bind('<Button-1>', on_click)
                
                if not col.get('flex'):
                    cell.configure(width=col.get('width', 15))
        
        self.rows.append(data)
        self.row_widgets.append(row_frame)
    
    def clear(self):
        """Limpa todas as linhas"""
        for widget in self.row_widgets:
            widget.destroy()
        self.rows = []
        self.row_widgets = []


class Pagination(tk.Frame):
    """Componente de paginação"""
    
    def __init__(self, parent, total_pages=1, current_page=1, on_page_change=None, theme=None):
        self.theme = theme or ModernTheme()
        super().__init__(parent, bg=self.theme.BG_PRIMARY)
        
        self.total_pages = total_pages
        self.current_page = current_page
        self.on_page_change = on_page_change
        
        self._build()
    
    def _build(self):
        # Limpar widgets anteriores
        for widget in self.winfo_children():
            widget.destroy()
        
        # Container
        container = tk.Frame(self, bg=self.theme.BG_PRIMARY)
        container.pack()
        
        # Botão Anterior
        prev_btn = tk.Button(
            container,
            text="← Anterior",
            font=self.theme.get_font("sm"),
            bg=self.theme.BG_TERTIARY if self.current_page > 1 else self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_PRIMARY if self.current_page > 1 else self.theme.TEXT_TERTIARY,
            relief='flat',
            padx=12,
            pady=6,
            cursor='hand2' if self.current_page > 1 else 'arrow',
            state='normal' if self.current_page > 1 else 'disabled',
            command=lambda: self._change_page(self.current_page - 1)
        )
        prev_btn.pack(side='left', padx=(0, 8))
        
        # Números de página
        start = max(1, self.current_page - 2)
        end = min(self.total_pages, start + 4)
        
        if end - start < 4:
            start = max(1, end - 4)
        
        for i in range(start, end + 1):
            is_current = i == self.current_page
            
            page_btn = tk.Button(
                container,
                text=str(i),
                font=self.theme.get_font("sm", "bold" if is_current else "normal"),
                bg=self.theme.PRIMARY if is_current else self.theme.BG_TERTIARY,
                fg='white' if is_current else self.theme.TEXT_PRIMARY,
                relief='flat',
                width=3,
                cursor='hand2' if not is_current else 'arrow',
                command=lambda p=i: self._change_page(p)
            )
            page_btn.pack(side='left', padx=2)
        
        # Botão Próximo
        next_btn = tk.Button(
            container,
            text="Próximo →",
            font=self.theme.get_font("sm"),
            bg=self.theme.BG_TERTIARY if self.current_page < self.total_pages else self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_PRIMARY if self.current_page < self.total_pages else self.theme.TEXT_TERTIARY,
            relief='flat',
            padx=12,
            pady=6,
            cursor='hand2' if self.current_page < self.total_pages else 'arrow',
            state='normal' if self.current_page < self.total_pages else 'disabled',
            command=lambda: self._change_page(self.current_page + 1)
        )
        next_btn.pack(side='left', padx=(8, 0))
    
    def _change_page(self, new_page):
        if 1 <= new_page <= self.total_pages and new_page != self.current_page:
            self.current_page = new_page
            self._build()
            if self.on_page_change:
                self.on_page_change(new_page)
    
    def update_pagination(self, total_pages, current_page):
        self.total_pages = total_pages
        self.current_page = current_page
        self._build()


# ==================== TELA PRINCIPAL ====================

class LogsScreen(tk.Frame):
    """Tela de visualização de logs"""
    
    def __init__(self, parent):
        self.theme = ModernTheme()
        super().__init__(parent, bg=self.theme.BG_SECONDARY)
        
        # Dados
        self.all_logs = self._generate_sample_logs(150)
        self.filtered_logs = self.all_logs.copy()
        self.current_page = 1
        self.logs_per_page = 20
        
        # Filtros
        self.filter_job = tk.StringVar(value="Todos")
        self.filter_status = tk.StringVar(value="Todos")
        self.filter_date = tk.StringVar(value="Hoje")
        self.search_var = tk.StringVar()
        
        self._build_ui()
        self._apply_filters()
    
    def _build_ui(self):
        # Canvas com scroll
        self.canvas = tk.Canvas(self, bg=self.theme.BG_SECONDARY, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.theme.BG_SECONDARY)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Header com título e ações
        self._build_header()
        
        # Filtros
        self._build_filters()
        
        # Estatísticas
        self._build_stats()
        
        # Tabela de logs
        self._build_logs_table()
        
        # Paginação
        self._build_pagination()
    
    def _build_header(self):
        header = Card(self.scrollable_frame, theme=self.theme)
        header.pack(fill='x', padx=24, pady=24)
        header.add_padding(20)
        
        container = tk.Frame(header, bg=self.theme.BG_PRIMARY)
        container.pack(fill='x')
        
        # Título
        tk.Label(
            container,
            text="📋 Logs de Execução",
            font=self.theme.get_font("xl", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left')
        
        # Botões de ação
        actions = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        actions.pack(side='right')
        
        ModernButton(
            actions,
            text="🔄 Atualizar",
            variant="secondary",
            theme=self.theme,
            command=self._refresh_logs
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            actions,
            text="📥 Exportar",
            variant="secondary",
            theme=self.theme,
            command=self._export_logs
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            actions,
            text="🗑️ Limpar Logs",
            variant="danger",
            theme=self.theme,
            command=self._clear_logs
        ).pack(side='left')
    
    def _build_filters(self):
        filters_card = Card(self.scrollable_frame, theme=self.theme)
        filters_card.pack(fill='x', padx=24, pady=(0, 16))
        filters_card.add_padding(20)
        
        # Título
        tk.Label(
            filters_card,
            text="🔍 Filtros",
            font=self.theme.get_font("md", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY,
            anchor='w'
        ).pack(fill='x', pady=(0, 12))
        
        # Container de filtros
        filters_container = tk.Frame(filters_card, bg=self.theme.BG_PRIMARY)
        filters_container.pack(fill='x')
        
        # Job
        job_frame = tk.Frame(filters_container, bg=self.theme.BG_PRIMARY)
        job_frame.pack(side='left', padx=(0, 16))
        
        tk.Label(job_frame, text="Job:", font=self.theme.get_font("sm"),
                fg=self.theme.TEXT_SECONDARY, bg=self.theme.BG_PRIMARY).pack(anchor='w')
        
        job_combo = ttk.Combobox(
            job_frame,
            textvariable=self.filter_job,
            values=["Todos", "Envia Estoque", "Envia Preço", "Envia Produto", "Internaliza Pedidos", "Envia Foto"],
            width=20,
            state='readonly'
        )
        job_combo.pack()
        
        # Status
        status_frame = tk.Frame(filters_container, bg=self.theme.BG_PRIMARY)
        status_frame.pack(side='left', padx=(0, 16))
        
        tk.Label(status_frame, text="Status:", font=self.theme.get_font("sm"),
                fg=self.theme.TEXT_SECONDARY, bg=self.theme.BG_PRIMARY).pack(anchor='w')
        
        status_combo = ttk.Combobox(
            status_frame,
            textvariable=self.filter_status,
            values=["Todos", "Sucesso", "Aviso", "Erro"],
            width=15,
            state='readonly'
        )
        status_combo.pack()
        
        # Data
        date_frame = tk.Frame(filters_container, bg=self.theme.BG_PRIMARY)
        date_frame.pack(side='left', padx=(0, 16))
        
        tk.Label(date_frame, text="Período:", font=self.theme.get_font("sm"),
                fg=self.theme.TEXT_SECONDARY, bg=self.theme.BG_PRIMARY).pack(anchor='w')
        
        date_combo = ttk.Combobox(
            date_frame,
            textvariable=self.filter_date,
            values=["Hoje", "Últimos 7 dias", "Últimos 30 dias", "Todos"],
            width=18,
            state='readonly'
        )
        date_combo.pack()
        
        # Busca
        search_frame = tk.Frame(filters_container, bg=self.theme.BG_PRIMARY)
        search_frame.pack(side='left', padx=(0, 16))
        
        tk.Label(search_frame, text="Buscar:", font=self.theme.get_font("sm"),
                fg=self.theme.TEXT_SECONDARY, bg=self.theme.BG_PRIMARY).pack(anchor='w')
        
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=self.theme.get_font("sm"),
            width=25,
            bg=self.theme.BG_TERTIARY,
            fg=self.theme.TEXT_PRIMARY,
            relief='flat',
            borderwidth=0
        )
        search_entry.pack(ipady=4)
        
        # Botão Aplicar
        ModernButton(
            filters_container,
            text="Aplicar Filtros",
            variant="primary",
            theme=self.theme,
            command=self._apply_filters
        ).pack(side='left')
    
    def _build_stats(self):
        stats_card = Card(self.scrollable_frame, theme=self.theme)
        stats_card.pack(fill='x', padx=24, pady=(0, 16))
        stats_card.add_padding(20)
        
        container = tk.Frame(stats_card, bg=self.theme.BG_PRIMARY)
        container.pack(fill='x')
        
        # Calcular estatísticas
        total = len(self.filtered_logs)
        success = sum(1 for log in self.filtered_logs if log['status'].lower() == 'sucesso')
        warning = sum(1 for log in self.filtered_logs if log['status'].lower() == 'aviso')
        error = sum(1 for log in self.filtered_logs if log['status'].lower() == 'erro')
        
        # Exibir stats
        stats = [
            ("Total de Logs", total, self.theme.INFO),
            ("✓ Sucessos", success, self.theme.SUCCESS),
            ("⚠ Avisos", warning, self.theme.WARNING),
            ("✗ Erros", error, self.theme.DANGER),
        ]
        
        for i, (label, value, color) in enumerate(stats):
            stat_frame = tk.Frame(container, bg=self.theme.BG_PRIMARY)
            stat_frame.pack(side='left', padx=(0, 32 if i < len(stats)-1 else 0))
            
            tk.Label(
                stat_frame,
                text=label,
                font=self.theme.get_font("xs"),
                fg=self.theme.TEXT_SECONDARY,
                bg=self.theme.BG_PRIMARY
            ).pack()
            
            tk.Label(
                stat_frame,
                text=str(value),
                font=self.theme.get_font("xl", "bold"),
                fg=color,
                bg=self.theme.BG_PRIMARY
            ).pack()
    
    def _build_logs_table(self):
        table_card = Card(self.scrollable_frame, theme=self.theme)
        table_card.pack(fill='both', expand=True, padx=24, pady=(0, 16))
        table_card.add_padding(20)
        
        # Colunas da tabela
        columns = [
            {'title': '🕐 Data/Hora', 'width': 18},
            {'title': '📦 Job', 'width': 22},
            {'title': '📊 Status', 'type': 'badge', 'width': 12},
            {'title': '📝 Mensagem', 'flex': True},
            {'title': '⏱ Duração', 'width': 12},
        ]
        
        self.table = ModernTable(
            table_card,
            columns=columns,
            theme=self.theme,
            on_row_click=self._show_log_details
        )
        self.table.pack(fill='both', expand=True)
        
        # Carregar logs da página atual
        self._load_page_logs()
    
    def _build_pagination(self):
        pagination_card = Card(self.scrollable_frame, theme=self.theme)
        pagination_card.pack(fill='x', padx=24, pady=(0, 24))
        pagination_card.add_padding(16)
        
        container = tk.Frame(pagination_card, bg=self.theme.BG_PRIMARY)
        container.pack()
        
        # Info de registros
        start = (self.current_page - 1) * self.logs_per_page + 1
        end = min(self.current_page * self.logs_per_page, len(self.filtered_logs))
        total = len(self.filtered_logs)
        
        self.info_label = tk.Label(
            container,
            text=f"Mostrando {start}-{end} de {total} logs",
            font=self.theme.get_font("sm"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY
        )
        self.info_label.pack(side='left', padx=(0, 32))
        
        # Paginação
        total_pages = max(1, (len(self.filtered_logs) + self.logs_per_page - 1) // self.logs_per_page)
        self.pagination = Pagination(
            container,
            total_pages=total_pages,
            current_page=self.current_page,
            on_page_change=self._on_page_change,
            theme=self.theme
        )
        self.pagination.pack(side='left')
    
    # ========== MÉTODOS DE DADOS ==========
    
    def _generate_sample_logs(self, count):
        """Gera logs de exemplo"""
        jobs = ["Envia Estoque", "Envia Preço", "Envia Produto", "Internaliza Pedidos", "Envia Foto", "Envia Cliente"]
        statuses = ["Sucesso", "Aviso", "Erro"]
        messages = {
            "Sucesso": [
                "Processados 247 registros com sucesso",
                "Sincronização concluída sem erros",
                "Dados enviados para API",
                "Atualização realizada com êxito"
            ],
            "Aviso": [
                "5 registros ignorados por inconsistência",
                "Timeout na API, tentando novamente",
                "Alguns produtos sem estoque disponível",
                "Conexão lenta detectada"
            ],
            "Erro": [
                "Falha na conexão com banco de dados",
                "API retornou código 500",
                "Erro ao processar arquivo XML",
                "Timeout ao conectar com servidor"
            ]
        }
        
        logs = []
        now = datetime.now()
        
        for i in range(count):
            status = random.choice(statuses)
            job = random.choice(jobs)
            
            log = {
                'datetime': (now - timedelta(minutes=random.randint(0, 10080))).strftime('%d/%m/%Y %H:%M'),
                'job': job,
                'status': status,
                'message': random.choice(messages[status]),
                'duration': f"{random.randint(1, 120)}s",
                'details': f"Detalhes completos do log #{i+1}\n\nJob: {job}\nStatus: {status}\nStack trace: ...\nMais informações aqui..."
            }
            logs.append(log)
        
        return sorted(logs, key=lambda x: x['datetime'], reverse=True)
    
    def _apply_filters(self):
        """Aplica filtros aos logs"""
        self.filtered_logs = self.all_logs.copy()
        
        # Filtro por job
        if self.filter_job.get() != "Todos":
            self.filtered_logs = [log for log in self.filtered_logs if log['job'] == self.filter_job.get()]
        
        # Filtro por status
        if self.filter_status.get() != "Todos":
            self.filtered_logs = [log for log in self.filtered_logs if log['status'] == self.filter_status.get()]
        
        # Filtro por busca
        search = self.search_var.get().lower()
        if search:
            self.filtered_logs = [log for log in self.filtered_logs 
                                 if search in log['message'].lower() or search in log['job'].lower()]
        
        # Resetar para página 1
        self.current_page = 1
        
        # Atualizar tabela e paginação
        self._load_page_logs()
        self._update_pagination()
        self._update_stats()
    
    def _load_page_logs(self):
        """Carrega logs da página atual"""
        self.table.clear()
        
        start = (self.current_page - 1) * self.logs_per_page
        end = start + self.logs_per_page
        page_logs = self.filtered_logs[start:end]
        
        for log in page_logs:
            self.table.add_row(
                [log['datetime'], log['job'], log['status'], log['message'], log['duration']],
                row_data=log
            )
    
    def _update_pagination(self):
        """Atualiza controle de paginação"""
        total_pages = max(1, (len(self.filtered_logs) + self.logs_per_page - 1) // self.logs_per_page)
        self.pagination.update_pagination(total_pages, self.current_page)
        
        # Atualizar info
        start = (self.current_page - 1) * self.logs_per_page + 1
        end = min(self.current_page * self.logs_per_page, len(self.filtered_logs))
        total = len(self.filtered_logs)
        self.info_label.configure(text=f"Mostrando {start}-{end} de {total} logs")
    
    def _update_stats(self):
        """Atualiza estatísticas"""
        # Encontrar card de stats e recriar
        for i, child in enumerate(self.scrollable_frame.winfo_children()):
            if i == 2:  # Stats card é o 3º filho (0-indexed)
                child.destroy()
                break
        
        self._build_stats()
    
    def _on_page_change(self, new_page):
        """Callback de mudança de página"""
        self.current_page = new_page
        self._load_page_logs()
        self._update_pagination()
    
    # ========== AÇÕES ==========
    
    def _show_log_details(self, log_data):
        """Mostra detalhes completos do log"""
        details = tk.Toplevel(self.winfo_toplevel())
        details.title(f"Detalhes do Log - {log_data['job']}")
        details.geometry("700x500")
        details.configure(bg=self.theme.BG_SECONDARY)
        
        # Modal
        details.transient(self.winfo_toplevel())
        details.grab_set()
        
        # Header
        header = Card(details, theme=self.theme)
        header.pack(fill='x', padx=20, pady=(20, 0))
        header.add_padding(20)
        
        tk.Label(
            header,
            text=f"📋 {log_data['job']}",
            font=self.theme.get_font("lg", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(anchor='w')
        
        tk.Label(
            header,
            text=f"{log_data['datetime']} • Duração: {log_data['duration']}",
            font=self.theme.get_font("sm"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY
        ).pack(anchor='w', pady=(4, 0))
        
        # Status
        status_map = {
            'sucesso': 'success',
            'aviso': 'warning',
            'erro': 'error'
        }
        StatusBadge(
            header,
            text=log_data['status'],
            status=status_map.get(log_data['status'].lower(), 'info'),
            theme=self.theme
        ).pack(anchor='w', pady=(8, 0))
        
        # Detalhes
        details_card = Card(details, theme=self.theme)
        details_card.pack(fill='both', expand=True, padx=20, pady=(16, 0))
        details_card.add_padding(20)
        
        tk.Label(
            details_card,
            text="Mensagem:",
            font=self.theme.get_font("sm", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY,
            anchor='w'
        ).pack(fill='x', pady=(0, 8))
        
        message_text = tk.Text(
            details_card,
            height=15,
            font=self.theme.get_font("sm"),
            bg=self.theme.BG_TERTIARY,
            fg=self.theme.TEXT_PRIMARY,
            relief='flat',
            borderwidth=0,
            padx=12,
            pady=8,
            wrap='word'
        )
        message_text.pack(fill='both', expand=True)
        message_text.insert('1.0', log_data['details'])
        message_text.configure(state='disabled')
        
        # Botão fechar
        ModernButton(
            details,
            text="Fechar",
            variant="secondary",
            theme=self.theme,
            command=details.destroy
        ).pack(pady=20)
        
        # Centralizar
        details.update_idletasks()
        x = (details.winfo_screenwidth() // 2) - (details.winfo_width() // 2)
        y = (details.winfo_screenheight() // 2) - (details.winfo_height() // 2)
        details.geometry(f"+{x}+{y}")
    
    def _refresh_logs(self):
        """Atualiza logs"""
        messagebox.showinfo("Atualizar", "Logs atualizados com sucesso!")
        self._apply_filters()
    
    def _export_logs(self):
        """Exporta logs para arquivo"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    for log in self.filtered_logs:
                        f.write(f"{log['datetime']} | {log['job']} | {log['status']} | {log['message']}\n")
                messagebox.showinfo("Sucesso", f"Logs exportados para:\n{filename}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar logs:\n{str(e)}")
    
    def _clear_logs(self):
        """Limpa todos os logs"""
        if messagebox.askyesno("Limpar Logs", "Deseja realmente limpar todos os logs?\n\nEsta ação não pode ser desfeita!"):
            self.all_logs = []
            self.filtered_logs = []
            self.current_page = 1
            self._load_page_logs()
            self._update_pagination()
            self._update_stats()
            messagebox.showinfo("Sucesso", "Logs limpos com sucesso!")
