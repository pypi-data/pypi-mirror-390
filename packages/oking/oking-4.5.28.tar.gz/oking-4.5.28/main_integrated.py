"""
🏢 Dashboard Principal Integrado - OKING Hub
Sistema completo com todas as telas integradas
"""
import tkinter as tk
from tkinter import messagebox
from ui_components import (
    ModernTheme, Card, ModernButton, StatusBadge, 
    MetricCard, TabButton, ScrollableFrame
)

# Importar screens (Settings já está integrado)
try:
    from screens.settings import SettingsScreen
    SETTINGS_AVAILABLE = True
except:
    SETTINGS_AVAILABLE = False

try:
    from screens.help import HelpScreen
    HELP_AVAILABLE = True
except:
    HELP_AVAILABLE = False

try:
    from screens.reports import ReportsScreen
    REPORTS_AVAILABLE = True
except:
    REPORTS_AVAILABLE = False

try:
    from screens.logs import LogsScreen
    LOGS_AVAILABLE = True
except:
    LOGS_AVAILABLE = False

try:
    from screens.jobs import JobsScreen
    JOBS_AVAILABLE = True
except:
    JOBS_AVAILABLE = False

try:
    from screens.database import DatabaseScreen
    DATABASE_AVAILABLE = True
except:
    DATABASE_AVAILABLE = False

try:
    from screens.tokens import TokensScreen
    TOKENS_AVAILABLE = True
except:
    TOKENS_AVAILABLE = False

try:
    from screens.photos import PhotosScreen
    PHOTOS_AVAILABLE = True
except:
    PHOTOS_AVAILABLE = False


# ==================== DASHBOARD PRINCIPAL ====================

class IntegratedDashboard:
    """Dashboard principal com todas as telas integradas"""
    
    def __init__(self, root, shortname="", token_manager=None, jobs_data=None):
        self.root = root
        self.theme = ModernTheme()
        self.current_tab = None
        self.tab_buttons = {}
        self.screen_instances = {}
        self.shortname = shortname
        self.token_manager = token_manager
        self.jobs_data = jobs_data or []
        
        self._setup_window()
        self._build_ui()
        self._switch_tab("overview")
    
    def _setup_window(self):
        self.root.title("OKING Hub - Sistema de Integração")
        w, h = 1400, 900
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        self.root.configure(bg=self.theme.BG_SECONDARY)
    
    def _build_ui(self):
        # Container principal
        main_container = tk.Frame(self.root, bg=self.theme.BG_SECONDARY)
        main_container.pack(fill='both', expand=True)
        
        # Header fixo
        self._build_header(main_container)
        
        # Conteúdo (sidebar + área principal)
        content = tk.Frame(main_container, bg=self.theme.BG_SECONDARY)
        content.pack(fill='both', expand=True)
        
        # Sidebar de navegação
        self._build_sidebar(content)
        
        # Área de conteúdo
        self.content_area = tk.Frame(content, bg=self.theme.BG_SECONDARY)
        self.content_area.pack(side='left', fill='both', expand=True, padx=(0, 24), pady=(0, 24))
    
    def _build_header(self, parent):
        """Cabeçalho fixo"""
        header = Card(parent, theme=self.theme)
        header.pack(fill='x', padx=24, pady=24)
        
        container = tk.Frame(header, bg=self.theme.BG_PRIMARY)
        container.pack(fill='x', padx=20, pady=16)
        
        # Esquerda
        left = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        left.pack(side='left', fill='x', expand=True)
        
        tk.Label(
            left,
            text="🏢 OKING Hub",
            font=self.theme.get_font("xxl", "bold"),
            fg=self.theme.PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left', padx=(0, 16))
        
        # Mostrar shortname se disponível
        if self.shortname:
            tk.Label(
                left,
                text=f"📦 {self.shortname.upper()}",
                font=self.theme.get_font("lg", "bold"),
                fg=self.theme.TEXT_PRIMARY,
                bg=self.theme.BG_PRIMARY
            ).pack(side='left', padx=(0, 16))
        
        # Mostrar token ativo se disponível
        if self.token_manager:
            try:
                active_token = self.token_manager.get_active_token()
                if active_token and 'nome' in active_token:
                    token_frame = tk.Frame(left, bg=self.theme.SUCCESS_BG, relief='flat', bd=1)
                    token_frame.pack(side='left', padx=(0, 8))
                    
                    tk.Label(
                        token_frame,
                        text=f"🔑 Token: {active_token['nome']}",
                        font=self.theme.get_font("sm", "bold"),
                        fg=self.theme.SUCCESS,
                        bg=self.theme.SUCCESS_BG
                    ).pack(padx=12, pady=6)
            except:
                pass
        
        # Direita
        right = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        right.pack(side='right')
        
        ModernButton(
            right,
            text="⚙️ Configurações",
            variant="secondary",
            theme=self.theme,
            command=lambda: self._switch_tab("settings")
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            right,
            text="❓ Ajuda",
            variant="secondary",
            theme=self.theme,
            command=lambda: self._switch_tab("help")
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            right,
            text="🚪 Sair",
            variant="danger",
            theme=self.theme,
            command=self._confirm_exit
        ).pack(side='left')
    
    def _build_sidebar(self, parent):
        """Sidebar de navegação"""
        sidebar = Card(parent, theme=self.theme)
        sidebar.pack(side='left', fill='y', padx=(24, 12), pady=(0, 24))
        sidebar.configure(width=280)
        
        container = tk.Frame(sidebar, bg=self.theme.BG_PRIMARY)
        container.pack(fill='both', expand=True, padx=12, pady=12)
        
        # Título
        tk.Label(
            container,
            text="📋 Navegação",
            font=self.theme.get_font("lg", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(anchor='w', padx=12, pady=(8, 16))
        
        # Abas
        tabs = [
            {"id": "overview", "icon": "🏠", "text": "Visão Geral"},
            {"id": "jobs", "icon": "⚙️", "text": "Configurar Jobs"},
            {"id": "database", "icon": "🗄️", "text": "Banco de Dados"},
            {"id": "tokens", "icon": "🔑", "text": "Tokens"},
            {"id": "photos", "icon": "📸", "text": "Upload de Fotos"},
            {"id": "logs", "icon": "📝", "text": "Logs"},
            {"id": "reports", "icon": "📊", "text": "Relatórios"},
            {"id": "settings", "icon": "🎨", "text": "Tema"},
            {"id": "help", "icon": "❓", "text": "Ajuda"},
        ]
        
        for tab in tabs:
            btn = TabButton(
                container,
                icon=tab["icon"],
                text=tab["text"],
                theme=self.theme,
                command=lambda t=tab["id"]: self._switch_tab(t),
                is_active=(tab["id"] == "overview")
            )
            btn.pack(fill='x', pady=(0, 4))
            self.tab_buttons[tab["id"]] = btn
    
    def _switch_tab(self, tab_id):
        """Troca de aba"""
        if self.current_tab == tab_id:
            return
        
        self.current_tab = tab_id
        
        # Atualiza botões
        for tid, btn in self.tab_buttons.items():
            btn.set_active(tid == tab_id)
        
        # Limpa área de conteúdo
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        # Renderiza conteúdo
        if tab_id == "overview":
            self._render_overview()
        elif tab_id == "jobs":
            self._load_screen("jobs", self._create_jobs_screen)
        elif tab_id == "database":
            self._load_screen("database", self._create_database_screen)
        elif tab_id == "tokens":
            self._load_screen("tokens", self._create_tokens_screen)
        elif tab_id == "photos":
            self._load_screen("photos", self._create_photos_screen)
        elif tab_id == "logs":
            self._load_screen("logs", self._create_logs_screen)
        elif tab_id == "reports":
            self._load_screen("reports", self._create_reports_screen)
        elif tab_id == "settings":
            self._load_screen("settings", self._create_settings_screen)
        elif tab_id == "help":
            self._load_screen("help", self._create_help_screen)
    
    def _load_screen(self, screen_id, creator_func):
        """Carrega ou reutiliza tela"""
        # Cria nova instância toda vez (área de conteúdo já foi limpa)
        screen = creator_func()
        self.screen_instances[screen_id] = screen
        
        # Exibe a tela
        screen.pack(fill='both', expand=True)
    
    # ==================== CRIADORES DE TELAS ====================
    
    def _create_jobs_screen(self):
        """Cria tela de configuração de jobs"""
        if JOBS_AVAILABLE:
            return JobsScreen(self.content_area, shortname=self.shortname, token_manager=self.token_manager)
        return self._create_placeholder("⚙️ Configuração de Jobs", "Configure jobs de sincronização")
    
    def _create_database_screen(self):
        """Cria tela de banco de dados"""
        if DATABASE_AVAILABLE:
            return DatabaseScreen(self.content_area)
        return self._create_placeholder("🗄️ Configuração de Banco de Dados", "Configure conexões Oracle e SQL Server")
    
    def _create_tokens_screen(self):
        """Cria tela de tokens"""
        if TOKENS_AVAILABLE:
            return TokensScreen(self.content_area, token_manager=self.token_manager)
        return self._create_placeholder("🔑 Gerenciamento de Tokens", "Gerencie tokens de API")
    
    def _create_photos_screen(self):
        """Cria tela de fotos"""
        if PHOTOS_AVAILABLE:
            return PhotosScreen(self.content_area)
        return self._create_placeholder("📸 Upload de Fotos", "Envie fotos de produtos")
    
    def _create_logs_screen(self):
        """Cria tela de logs"""
        if LOGS_AVAILABLE:
            return LogsScreen(self.content_area)
        return self._create_placeholder("📝 Logs do Sistema", "Visualize logs de execução")
    
    def _create_reports_screen(self):
        """Cria tela de relatórios"""
        if REPORTS_AVAILABLE:
            return ReportsScreen(self.content_area)
        return self._create_placeholder("📊 Relatórios", "Visualize relatórios de execução")
    
    def _create_settings_screen(self):
        """Cria tela de configurações"""
        if SETTINGS_AVAILABLE:
            return SettingsScreen(self.content_area)
        return self._create_placeholder("🎨 Tema e Aparência", "Personalize a interface")
    
    def _create_help_screen(self):
        """Cria tela de ajuda"""
        if HELP_AVAILABLE:
            return HelpScreen(self.content_area)
        return self._create_placeholder("❓ Ajuda e Documentação", "Documentação e suporte")
    
    def _create_placeholder(self, title, description):
        """Cria placeholder para tela"""
        container = tk.Frame(self.content_area, bg=self.theme.BG_SECONDARY)
        
        card = Card(container, theme=self.theme)
        card.pack(fill='both', expand=True)
        
        content = tk.Frame(card, bg=self.theme.BG_PRIMARY)
        content.pack(fill='both', expand=True, padx=40, pady=40)
        
        tk.Label(
            content,
            text=title,
            font=self.theme.get_font("xxl", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(pady=(40, 16))
        
        tk.Label(
            content,
            text=description,
            font=self.theme.get_font("lg"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY
        ).pack(pady=(0, 40))
        
        ModernButton(
            content,
            text="🚀 Em breve disponível",
            variant="primary",
            theme=self.theme,
            command=lambda: messagebox.showinfo("Info", "Tela em desenvolvimento")
        ).pack()
        
        return container
    
    # ==================== VISÃO GERAL ====================
    
    def _render_overview(self):
        """Renderiza visão geral"""
        scrollable = ScrollableFrame(self.content_area, theme=self.theme)
        scrollable.pack(fill='both', expand=True)
        
        content = scrollable.get_frame()
        
        # Título
        tk.Label(
            content,
            text="📊 Visão Geral do Sistema",
            font=self.theme.get_font("xxl", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_SECONDARY
        ).pack(anchor='w', pady=(0, 20))
        
        # Métricas
        metrics_container = tk.Frame(content, bg=self.theme.BG_SECONDARY)
        metrics_container.pack(fill='x', pady=(0, 24))
        
        metrics = [
            {"icon": "✅", "title": "Jobs Ativos", "value": "12", "variant": "success"},
            {"icon": "⏸️", "title": "Jobs Pausados", "value": "3", "variant": "warning"},
            {"icon": "🔄", "title": "Sincronizações Hoje", "value": "48", "variant": "info"},
            {"icon": "⚠️", "title": "Erros Hoje", "value": "2", "variant": "danger"},
        ]
        
        for i, metric in enumerate(metrics):
            card = MetricCard(
                metrics_container,
                icon=metric["icon"],
                title=metric["title"],
                value=metric["value"],
                variant=metric["variant"],
                theme=self.theme
            )
            card.grid(row=0, column=i, padx=(0, 16) if i < len(metrics)-1 else (0, 0), sticky='ew')
            metrics_container.grid_columnconfigure(i, weight=1)
        
        # Ações rápidas
        tk.Label(
            content,
            text="⚡ Ações Rápidas",
            font=self.theme.get_font("lg", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_SECONDARY
        ).pack(anchor='w', pady=(0, 16))
        
        actions_card = Card(content, theme=self.theme)
        actions_card.pack(fill='x', pady=(0, 24))
        
        actions_container = tk.Frame(actions_card, bg=self.theme.BG_PRIMARY)
        actions_container.pack(fill='x', padx=20, pady=16)
        
        actions = [
            {"icon": "⚙️", "text": "Configurar Jobs", "cmd": lambda: self._switch_tab("jobs")},
            {"icon": "🗄️", "text": "Testar Conexão", "cmd": lambda: self._switch_tab("database")},
            {"icon": "📸", "text": "Upload de Fotos", "cmd": lambda: self._switch_tab("photos")},
            {"icon": "📊", "text": "Ver Relatórios", "cmd": lambda: self._switch_tab("reports")},
        ]
        
        for i, action in enumerate(actions):
            btn = ModernButton(
                actions_container,
                text=f"{action['icon']} {action['text']}",
                variant="secondary",
                theme=self.theme,
                command=action["cmd"]
            )
            btn.grid(row=i//2, column=i%2, padx=8, pady=8, sticky='ew')
            actions_container.grid_columnconfigure(i%2, weight=1)
        
        # Últimas execuções
        tk.Label(
            content,
            text="🕒 Últimas Execuções",
            font=self.theme.get_font("lg", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_SECONDARY
        ).pack(anchor='w', pady=(0, 16))
        
        executions_card = Card(content, theme=self.theme)
        executions_card.pack(fill='x')
        
        exec_container = tk.Frame(executions_card, bg=self.theme.BG_PRIMARY)
        exec_container.pack(fill='x', padx=20, pady=16)
        
        executions = [
            {"job": "Sincronizar Produtos", "time": "10:30", "status": "success"},
            {"job": "Atualizar Preços", "time": "10:15", "status": "success"},
            {"job": "Importar Pedidos", "time": "09:45", "status": "warning"},
            {"job": "Enviar Estoque", "time": "09:30", "status": "success"},
        ]
        
        for i, exec in enumerate(executions):
            exec_frame = tk.Frame(exec_container, bg=self.theme.BG_PRIMARY)
            exec_frame.pack(fill='x', pady=(0, 12) if i < len(executions)-1 else 0)
            
            tk.Label(
                exec_frame,
                text=exec["job"],
                font=self.theme.get_font("md", "bold"),
                fg=self.theme.TEXT_PRIMARY,
                bg=self.theme.BG_PRIMARY
            ).pack(side='left')
            
            tk.Label(
                exec_frame,
                text=exec["time"],
                font=self.theme.get_font("sm"),
                fg=self.theme.TEXT_SECONDARY,
                bg=self.theme.BG_PRIMARY
            ).pack(side='left', padx=(12, 0))
            
            status_text = {"success": "✓ Sucesso", "warning": "⚠ Aviso", "danger": "✗ Erro"}
            StatusBadge(
                exec_frame,
                text=status_text.get(exec["status"], ""),
                status=exec["status"],
                theme=self.theme
            ).pack(side='right')
    
    def _confirm_exit(self):
        """Confirma saída do sistema"""
        if messagebox.askyesno("Confirmar Saída", "Deseja realmente sair do OKING Hub?"):
            self.root.quit()


# ==================== EXECUÇÃO ====================

if __name__ == "__main__":
    root = tk.Tk()
    app = IntegratedDashboard(root)
    root.mainloop()
