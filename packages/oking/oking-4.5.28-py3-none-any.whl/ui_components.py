"""
🎨 Componentes UI Reutilizáveis - OKING Hub
Componentes modernos em Tkinter compartilhados entre todas as telas
"""
import tkinter as tk
from tkinter import ttk


# ==================== TEMA ====================

class ModernTheme:
    """Tema moderno centralizado"""
    PRIMARY = "#2563eb"
    PRIMARY_DARK = "#1e40af"
    PRIMARY_LIGHT = "#3b82f6"
    BG_PRIMARY = "#ffffff"
    BG_SECONDARY = "#f8fafc"
    BG_TERTIARY = "#f1f5f9"
    BG_HOVER = "#f0f9ff"
    BG_CODE = "#1e293b"  # Fundo do editor de código
    TEXT_PRIMARY = "#0f172a"
    TEXT_SECONDARY = "#64748b"
    TEXT_TERTIARY = "#94a3b8"
    TEXT_CODE = "#e2e8f0"  # Texto do editor de código
    SUCCESS = "#10b981"
    SUCCESS_BG = "#d1fae5"
    WARNING = "#f59e0b"
    WARNING_BG = "#fef3c7"
    DANGER = "#ef4444"
    DANGER_BG = "#fee2e2"
    INFO = "#3b82f6"
    INFO_BG = "#dbeafe"
    BORDER = "#e2e8f0"
    FONT_FAMILY = "Segoe UI"
    FONT_CODE = "Consolas"  # Fonte monospace para código
    SPACING_SM = 8
    SPACING_MD = 16
    SPACING_LG = 24
    
    @classmethod
    def get_font(cls, size="md", weight="normal", mono=False):
        """Retorna fonte configurada"""
        sizes = {"xs": 8, "sm": 10, "md": 12, "lg": 16, "xl": 22, "xxl": 30}
        family = cls.FONT_CODE if mono else cls.FONT_FAMILY
        return (family, sizes.get(size, 12), weight)


# ==================== COMPONENTES ====================

class Card(tk.Frame):
    """Card moderno com borda e sombra"""
    def __init__(self, parent, theme=None, **kwargs):
        self.theme = theme or ModernTheme()
        config = {
            'bg': self.theme.BG_PRIMARY,
            'relief': 'flat',
            'borderwidth': 1,
            'highlightthickness': 1,
            'highlightbackground': self.theme.BORDER,
        }
        config.update(kwargs)
        super().__init__(parent, **config)
    
    def add_padding(self, padding=None):
        """Adiciona padding interno"""
        p = padding or self.theme.SPACING_MD
        self.configure(padx=p, pady=p)


class ModernButton(tk.Button):
    """Botão moderno com hover"""
    def __init__(self, parent, text="", variant="primary", theme=None, **kwargs):
        self.theme = theme or ModernTheme()
        variants = {
            'primary': {'bg': self.theme.PRIMARY, 'fg': 'white', 'hover': self.theme.PRIMARY_DARK},
            'secondary': {'bg': self.theme.BG_TERTIARY, 'fg': self.theme.TEXT_PRIMARY, 'hover': self.theme.BORDER},
            'success': {'bg': self.theme.SUCCESS, 'fg': 'white', 'hover': '#059669'},
            'danger': {'bg': self.theme.DANGER, 'fg': 'white', 'hover': '#dc2626'},
        }
        v = variants.get(variant, variants['primary'])
        config = {
            'text': text,
            'font': self.theme.get_font("md", "bold"),
            'bg': v['bg'],
            'fg': v['fg'],
            'activebackground': v['hover'],
            'activeforeground': v['fg'],
            'relief': 'flat',
            'borderwidth': 0,
            'padx': 20,
            'pady': 10,
            'cursor': 'hand2',
        }
        config.update(kwargs)
        super().__init__(parent, **config)
        self.default_bg = config['bg']
        self.hover_bg = v['hover']
        self.bind('<Enter>', lambda e: self.configure(bg=self.hover_bg))
        self.bind('<Leave>', lambda e: self.configure(bg=self.default_bg))


class StatusBadge(tk.Label):
    """Badge de status colorido"""
    def __init__(self, parent, text="", status="info", theme=None, **kwargs):
        self.theme = theme or ModernTheme()
        status_colors = {
            'success': {'bg': self.theme.SUCCESS_BG, 'fg': self.theme.SUCCESS},
            'warning': {'bg': self.theme.WARNING_BG, 'fg': self.theme.WARNING},
            'danger': {'bg': self.theme.DANGER_BG, 'fg': self.theme.DANGER},
            'info': {'bg': self.theme.INFO_BG, 'fg': self.theme.INFO},
        }
        colors = status_colors.get(status, status_colors['info'])
        config = {
            'text': text,
            'font': self.theme.get_font("sm", "bold"),
            'bg': colors['bg'],
            'fg': colors['fg'],
            'padx': 12,
            'pady': 4,
            'relief': 'flat',
        }
        config.update(kwargs)
        super().__init__(parent, **config)


class ScrollableFrame(tk.Frame):
    """Frame com scroll automático"""
    def __init__(self, parent, theme=None, **kwargs):
        self.theme = theme or ModernTheme()
        super().__init__(parent, bg=self.theme.BG_SECONDARY, **kwargs)
        
        # Canvas e scrollbar
        self.canvas = tk.Canvas(self, bg=self.theme.BG_SECONDARY, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.theme.BG_SECONDARY)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Bind mousewheel
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind("<MouseWheel>", on_mousewheel)
        
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')
    
    def get_frame(self):
        """Retorna o frame onde adicionar widgets"""
        return self.scrollable_frame


class MetricCard(tk.Frame):
    """Card de métrica com ícone"""
    def __init__(self, parent, icon="", title="", value="", variant="info", theme=None):
        self.theme = theme or ModernTheme()
        super().__init__(
            parent,
            bg=self.theme.BG_PRIMARY,
            relief='flat',
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.theme.BORDER
        )
        
        container = tk.Frame(self, bg=self.theme.BG_PRIMARY)
        container.pack(fill='both', expand=True, padx=20, pady=16)
        
        # Ícone
        icon_colors = {
            'success': self.theme.SUCCESS,
            'warning': self.theme.WARNING,
            'danger': self.theme.DANGER,
            'info': self.theme.INFO,
        }
        
        tk.Label(
            container,
            text=icon,
            font=self.theme.get_font("xxl"),
            fg=icon_colors.get(variant, self.theme.INFO),
            bg=self.theme.BG_PRIMARY
        ).pack(anchor='w', pady=(0, 8))
        
        # Título
        tk.Label(
            container,
            text=title,
            font=self.theme.get_font("sm"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY
        ).pack(anchor='w')
        
        # Valor
        tk.Label(
            container,
            text=value,
            font=self.theme.get_font("xxl", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(anchor='w')


class TabButton(tk.Frame):
    """Botão de aba personalizado"""
    def __init__(self, parent, icon="", text="", theme=None, command=None, is_active=False):
        self.theme = theme or ModernTheme()
        self.command = command
        self.is_active = is_active
        
        super().__init__(
            parent,
            bg=self.theme.PRIMARY if is_active else self.theme.BG_PRIMARY,
            cursor='hand2',
            relief='flat'
        )
        
        container = tk.Frame(
            self,
            bg=self.theme.PRIMARY if is_active else self.theme.BG_PRIMARY
        )
        container.pack(fill='both', expand=True, padx=16, pady=12)
        
        # Ícone
        self.icon_label = tk.Label(
            container,
            text=icon,
            font=self.theme.get_font("lg"),
            fg='white' if is_active else self.theme.TEXT_SECONDARY,
            bg=self.theme.PRIMARY if is_active else self.theme.BG_PRIMARY
        )
        self.icon_label.pack(side='left', padx=(0, 8))
        
        # Texto
        self.text_label = tk.Label(
            container,
            text=text,
            font=self.theme.get_font("md", "bold"),
            fg='white' if is_active else self.theme.TEXT_PRIMARY,
            bg=self.theme.PRIMARY if is_active else self.theme.BG_PRIMARY
        )
        self.text_label.pack(side='left')
        
        self._setup_bindings()
    
    def _setup_bindings(self):
        """Configura eventos de mouse"""
        def on_enter(e):
            if not self.is_active:
                self.configure(bg=self.theme.BG_HOVER)
                for widget in self.winfo_children():
                    widget.configure(bg=self.theme.BG_HOVER)
                    for child in widget.winfo_children():
                        child.configure(bg=self.theme.BG_HOVER)
        
        def on_leave(e):
            if not self.is_active:
                self.configure(bg=self.theme.BG_PRIMARY)
                for widget in self.winfo_children():
                    widget.configure(bg=self.theme.BG_PRIMARY)
                    for child in widget.winfo_children():
                        child.configure(bg=self.theme.BG_PRIMARY)
        
        def on_click(e):
            if self.command:
                self.command()
        
        # Aplica bindings em todos os widgets
        widgets = [self] + list(self.winfo_children())
        for widget in widgets:
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
            widget.bind('<Button-1>', on_click)
            for child in widget.winfo_children():
                child.bind('<Enter>', on_enter)
                child.bind('<Leave>', on_leave)
                child.bind('<Button-1>', on_click)
    
    def set_active(self, active):
        """Define estado ativo/inativo"""
        self.is_active = active
        bg = self.theme.PRIMARY if active else self.theme.BG_PRIMARY
        fg = 'white' if active else self.theme.TEXT_PRIMARY
        fg_icon = 'white' if active else self.theme.TEXT_SECONDARY
        
        self.configure(bg=bg)
        for widget in self.winfo_children():
            widget.configure(bg=bg)
        self.icon_label.configure(bg=bg, fg=fg_icon)
        self.text_label.configure(bg=bg, fg=fg)


class ExpandableMenuItem(tk.Frame):
    """Menu item expansível com subitens"""
    def __init__(self, parent, icon="", text="", theme=None, subitems=None, on_subitem_click=None):
        self.theme = theme or ModernTheme()
        self.subitems = subitems or []
        self.on_subitem_click = on_subitem_click
        self.is_expanded = False
        self.subitem_frames = []
        
        super().__init__(parent, bg=self.theme.BG_PRIMARY)
        
        # Header do menu (clicável para expandir/colapsar)
        self.header = tk.Frame(self, bg=self.theme.BG_PRIMARY, cursor='hand2')
        self.header.pack(fill='x')
        
        header_content = tk.Frame(self.header, bg=self.theme.BG_PRIMARY)
        header_content.pack(fill='x', padx=16, pady=12)
        
        # Ícone de expansão
        self.expand_icon = tk.Label(
            header_content,
            text="▶",
            font=self.theme.get_font("xs"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY
        )
        self.expand_icon.pack(side='left', padx=(0, 8))
        
        # Ícone principal
        tk.Label(
            header_content,
            text=icon,
            font=self.theme.get_font("lg"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left', padx=(0, 8))
        
        # Texto
        tk.Label(
            header_content,
            text=text,
            font=self.theme.get_font("md", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left')
        
        # Badge com contagem
        if self.subitems:
            tk.Label(
                header_content,
                text=str(len(self.subitems)),
                font=self.theme.get_font("xs", "bold"),
                fg='white',
                bg=self.theme.TEXT_SECONDARY,
                padx=6,
                pady=2
            ).pack(side='right')
        
        # Container para subitens (inicialmente escondido)
        self.subitems_container = tk.Frame(self, bg=self.theme.BG_SECONDARY)
        
        # Bindings no header
        for widget in [self.header, header_content, self.expand_icon]:
            widget.bind('<Button-1>', lambda e: self._toggle_expand())
            widget.bind('<Enter>', lambda e: self.header.configure(bg=self.theme.BG_HOVER))
            widget.bind('<Leave>', lambda e: self.header.configure(bg=self.theme.BG_PRIMARY))
    
    def _toggle_expand(self):
        """Expande ou colapsa o menu"""
        self.is_expanded = not self.is_expanded
        
        if self.is_expanded:
            self.expand_icon.configure(text="▼")
            self.subitems_container.pack(fill='x', pady=(0, 4))
            self._build_subitems()
        else:
            self.expand_icon.configure(text="▶")
            self.subitems_container.pack_forget()
    
    def _build_subitems(self):
        """Constrói lista de subitens"""
        # Limpa subitens antigos
        for widget in self.subitems_container.winfo_children():
            widget.destroy()
        self.subitem_frames.clear()
        
        for item in self.subitems:
            subitem = tk.Frame(
                self.subitems_container,
                bg=self.theme.BG_SECONDARY,
                cursor='hand2'
            )
            subitem.pack(fill='x', padx=(32, 0), pady=1)
            
            content = tk.Frame(subitem, bg=self.theme.BG_SECONDARY)
            content.pack(fill='x', padx=12, pady=8)
            
            # Ícone do subitem
            tk.Label(
                content,
                text="📄",
                font=self.theme.get_font("sm"),
                fg=self.theme.TEXT_SECONDARY,
                bg=self.theme.BG_SECONDARY
            ).pack(side='left', padx=(0, 8))
            
            # Nome do job
            tk.Label(
                content,
                text=item.get('job', 'Sem nome'),
                font=self.theme.get_font("sm"),
                fg=self.theme.TEXT_PRIMARY,
                bg=self.theme.BG_SECONDARY,
                anchor='w'
            ).pack(side='left', fill='x', expand=True)
            
            # Badge de status
            status = "✓" if item.get('ativo') == 'S' else "✗"
            status_color = self.theme.SUCCESS if item.get('ativo') == 'S' else self.theme.DANGER
            tk.Label(
                content,
                text=status,
                font=self.theme.get_font("sm"),
                fg=status_color,
                bg=self.theme.BG_SECONDARY
            ).pack(side='right')
            
            # Bindings
            def make_click_handler(job_data):
                return lambda e: self.on_subitem_click(job_data) if self.on_subitem_click else None
            
            for widget in [subitem, content]:
                widget.bind('<Button-1>', make_click_handler(item))
                widget.bind('<Enter>', lambda e, f=subitem: f.configure(bg=self.theme.BG_HOVER))
                widget.bind('<Leave>', lambda e, f=subitem: f.configure(bg=self.theme.BG_SECONDARY))
            
            self.subitem_frames.append(subitem)
    
    def update_subitems(self, subitems):
        """Atualiza lista de subitens dinamicamente"""
        self.subitems = subitems
        if self.is_expanded:
            self._build_subitems()
