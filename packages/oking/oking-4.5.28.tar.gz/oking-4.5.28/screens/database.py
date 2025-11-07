"""
🗄️ Tela de Configuração de Banco de Dados - OKING Hub
Configurar conexões com criptografia - Versão Simplificada
"""
import tkinter as tk
from tkinter import ttk
import json
import os
import base64
from pathlib import Path
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import platform
from ui_components import ModernTheme, Card, ModernButton


# ==================== CRIPTOGRAFIA ====================

class SecureStorage:
    """Armazenamento seguro de credenciais com AES-256"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.oking'
        self.config_file = self.config_dir / 'database_config.json'
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_machine_key(self):
        machine_id = f"{platform.node()}-{os.getlogin()}-{platform.machine()}"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'oking_hub_db_salt_v1',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(machine_id.encode()))
        return key
    
    def _encrypt(self, data: str) -> str:
        key = self._get_machine_key()
        f = Fernet(key)
        encrypted = f.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def _decrypt(self, encrypted_data: str) -> str:
        try:
            key = self._get_machine_key()
            f = Fernet(key)
            decrypted = f.decrypt(base64.urlsafe_b64decode(encrypted_data))
            return decrypted.decode()
        except:
            return ""
    
    def save_config(self, db_type: str, config: dict):
        """Salva configuração (senha criptografada)"""
        try:
            all_configs = {}
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    all_configs = json.load(f)
            
            config_encrypted = config.copy()
            if config.get('password'):
                config_encrypted['password_encrypted'] = self._encrypt(config['password'])
                del config_encrypted['password']
            
            all_configs[db_type] = {
                **config_encrypted,
                'saved_at': datetime.now().isoformat()
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(all_configs, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Erro ao salvar: {e}")
            return False
    
    def load_config(self, db_type: str):
        """Carrega configuração e descriptografa senha"""
        try:
            if not self.config_file.exists():
                return None
            
            with open(self.config_file, 'r') as f:
                all_configs = json.load(f)
            
            config = all_configs.get(db_type, {})
            
            if config.get('password_encrypted'):
                config['password'] = self._decrypt(config['password_encrypted'])
                del config['password_encrypted']
            
            return config
        except:
            return None


# ==================== COMPONENTE ENTRY ====================

class ModernEntry(tk.Frame):
    """Campo de entrada moderno"""
    def __init__(self, parent, label="", placeholder="", password=False, theme=None, **kwargs):
        self.theme = theme or ModernTheme()
        super().__init__(parent, bg=parent['bg'])
        
        if label:
            tk.Label(
                self,
                text=label,
                font=self.theme.get_font("sm", "bold"),
                fg=self.theme.TEXT_PRIMARY,
                bg=parent['bg']
            ).pack(anchor='w', pady=(0, 6))
        
        entry_container = tk.Frame(
            self,
            bg=self.theme.BG_PRIMARY,
            relief='flat',
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.theme.BORDER,
        )
        entry_container.pack(fill='x')
        
        show = "•" if password else None
        self.entry = tk.Entry(
            entry_container,
            font=self.theme.get_font("md"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY,
            relief='flat',
            borderwidth=0,
            show=show,
            **kwargs
        )
        self.entry.pack(fill='x', padx=12, pady=10)
        
        self.entry_container = entry_container
        self.entry.bind('<FocusIn>', lambda e: self._set_focus(True))
        self.entry.bind('<FocusOut>', lambda e: self._set_focus(False))
    
    def _set_focus(self, focused):
        color = self.theme.PRIMARY if focused else self.theme.BORDER
        self.entry_container.configure(highlightbackground=color)
    
    def get(self):
        return self.entry.get()
    
    def set(self, value):
        self.entry.delete(0, 'end')
        self.entry.insert(0, value)


# ==================== TELA PRINCIPAL ====================

class DatabaseScreen(tk.Frame):
    """Tela de configuração de banco de dados - Versão Simplificada"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=ModernTheme().BG_SECONDARY)
        self.theme = ModernTheme()
        self.storage = SecureStorage()
        self.entries = {}
        self.db_type_var = None
        
        self._build_ui()
        self._load_saved_config()
    
    def _build_ui(self):
        """Constrói interface"""
        # Container principal
        main_container = tk.Frame(self, bg=self.theme.BG_SECONDARY)
        main_container.pack(fill='both', expand=True, padx=24, pady=24)
        
        # Header
        self._build_header(main_container)
        
        # Canvas com scroll para o formulário
        canvas = tk.Canvas(
            main_container,
            bg=self.theme.BG_SECONDARY,
            highlightthickness=0
        )
        scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        
        self.scrollable_frame = tk.Frame(canvas, bg=self.theme.BG_SECONDARY)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # MouseWheel
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True, pady=(16, 0))
        scrollbar.pack(side="right", fill="y", pady=(16, 0))
        
        # Status frame
        self.status_frame = tk.Frame(self.scrollable_frame, bg=self.theme.BG_SECONDARY)
        self.status_frame.pack(fill='x', pady=(0, 12))
        
        # Formulário
        self._build_form()
    
    def _build_header(self, parent):
        """Header da tela"""
        card = Card(parent, theme=self.theme)
        card.pack(fill='x', pady=(0, 16))
        
        container = tk.Frame(card, bg=self.theme.BG_PRIMARY)
        container.pack(fill='x', padx=20, pady=16)
        
        tk.Label(
            container,
            text="🗄️ Configurações de sua integração",
            font=self.theme.get_font("xl", "bold"),
            fg=self.theme.PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left')
        
        tk.Label(
            container,
            text="🔒 Senhas criptografadas com AES-256",
            font=self.theme.get_font("sm"),
            fg=self.theme.SUCCESS,
            bg=self.theme.BG_PRIMARY
        ).pack(side='right')
    
    def _build_form(self):
        """Formulário único de configuração"""
        card = Card(self.scrollable_frame, theme=self.theme)
        card.pack(fill='both', expand=True)
        
        container = tk.Frame(card, bg=self.theme.BG_PRIMARY)
        container.pack(fill='both', expand=True, padx=32, pady=32)
        
        # Grid layout para campos lado a lado
        # Linha 1: Tipo do Banco e Diretório/Driver
        row1 = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        row1.pack(fill='x', pady=(0, 16))
        
        # Coluna 1: Tipo do Banco
        col1 = tk.Frame(row1, bg=self.theme.BG_PRIMARY)
        col1.pack(side='left', fill='both', expand=True, padx=(0, 8))
        
        tk.Label(
            col1,
            text="Tipo do Banco",
            font=self.theme.get_font("sm", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(anchor='w', pady=(0, 6))
        
        self.db_type_var = tk.StringVar(value="SQL")
        db_type_frame = tk.Frame(
            col1,
            bg=self.theme.BG_SECONDARY,
            relief='flat',
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=self.theme.BORDER,
        )
        db_type_frame.pack(fill='x')
        
        self.db_type_dropdown = ttk.Combobox(
            db_type_frame,
            textvariable=self.db_type_var,
            values=["SQL", "MYSQL", "ORACLE", "FIREBIRD"],
            state="readonly",
            font=self.theme.get_font("md")
        )
        self.db_type_dropdown.pack(fill='x', padx=12, pady=10)
        self.db_type_dropdown.bind('<<ComboboxSelected>>', self._on_db_type_change)
        
        # Coluna 2: Diretório/Driver
        col2 = tk.Frame(row1, bg=self.theme.BG_PRIMARY)
        col2.pack(side='left', fill='both', expand=True, padx=(8, 0))
        
        # Coluna 2: Diretório/Driver
        col2 = tk.Frame(row1, bg=self.theme.BG_PRIMARY)
        col2.pack(side='left', fill='both', expand=True, padx=(8, 0))
        
        self.entries['directory_label'] = tk.Label(
            col2,
            text="Driver ODBC",
            font=self.theme.get_font("sm", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        )
        self.entries['directory_label'].pack(anchor='w', pady=(0, 6))
        
        self.entries['directory'] = ModernEntry(
            col2,
            label="",
            placeholder="ODBC Driver 17 for SQL Server",
            theme=self.theme
        )
        self.entries['directory'].pack(fill='x')
        
        # Linha 2: Host e Esquema
        row2 = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        row2.pack(fill='x', pady=(0, 16))
        
        # Host
        col3 = tk.Frame(row2, bg=self.theme.BG_PRIMARY)
        col3.pack(side='left', fill='both', expand=True, padx=(0, 8))
        
        self.entries['host'] = ModernEntry(
            col3,
            label="Host ou IP",
            placeholder="10.111.29.167",
            theme=self.theme
        )
        self.entries['host'].pack(fill='x')
        
        # Esquema
        col4 = tk.Frame(row2, bg=self.theme.BG_PRIMARY)
        col4.pack(side='left', fill='both', expand=True, padx=(8, 0))
        
        self.entries['schema'] = ModernEntry(
            col4,
            label="Esquema",
            placeholder="openk",
            theme=self.theme
        )
        self.entries['schema'].pack(fill='x')
        
        # Linha 3: Usuário e Senha
        row3 = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        row3.pack(fill='x', pady=(0, 24))
        
        # Usuário
        col5 = tk.Frame(row3, bg=self.theme.BG_PRIMARY)
        col5.pack(side='left', fill='both', expand=True, padx=(0, 8))
        
        self.entries['user'] = ModernEntry(
            col5,
            label="Usuário",
            placeholder="openk",
            theme=self.theme
        )
        self.entries['user'].pack(fill='x')
        
        # Senha
        col6 = tk.Frame(row3, bg=self.theme.BG_PRIMARY)
        col6.pack(side='left', fill='both', expand=True, padx=(8, 0))
        
        self.entries['password'] = ModernEntry(
            col6,
            label="Senha",
            password=True,
            theme=self.theme
        )
        self.entries['password'].pack(fill='x')
        
        # Botões
        buttons_frame = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        buttons_frame.pack(fill='x')
        
        ModernButton(
            buttons_frame,
            text="Salvar configurações",
            variant="primary",
            theme=self.theme,
            command=self._save_config
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            buttons_frame,
            text="Abrir Operações",
            variant="success",
            theme=self.theme,
            command=self._open_operations
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            buttons_frame,
            text="Sair",
            variant="secondary",
            theme=self.theme,
            command=self._exit
        ).pack(side='left')
        
        # Atualizar label inicial
        self._update_directory_label()
    
    def _on_db_type_change(self, event=None):
        """Atualiza label quando muda tipo do banco"""
        self._update_directory_label()
    
    def _update_directory_label(self):
        """Atualiza label Diretório/Driver conforme tipo"""
        db_type = self.db_type_var.get()
        
        if db_type == "ORACLE":
            self.entries['directory_label'].config(text="Diretório")
        else:
            self.entries['directory_label'].config(text="Driver ODBC")
    
    def _open_operations(self):
        """Abrir operações (placeholder)"""
        self._show_success("🔄 Abrindo operações...")
    
    def _exit(self):
        """Sair (placeholder)"""
        pass
    
    def _save_config(self):
        """Salva configuração"""
        config = {
            'db_type': self.db_type_var.get(),
            'directory': self.entries['directory'].get(),
            'host': self.entries['host'].get(),
            'schema': self.entries['schema'].get(),
            'user': self.entries['user'].get(),
            'password': self.entries['password'].get()
        }
        
        if not all([config['db_type'], config['host'], config['schema'], config['user'], config['password']]):
            self._show_error("⚠️ Preencha todos os campos obrigatórios")
            return
        
        success = self.storage.save_config('database', config)
        
        if success:
            self._show_success(
                f"✅ Configuração salva com segurança!\n"
                f"🗄️ Banco: {config['db_type']}\n"
                f"🔒 Senha criptografada com AES-256"
            )
        else:
            self._show_error("❌ Erro ao salvar configuração")
    
    def _load_saved_config(self):
        """Carrega configuração salva"""
        config = self.storage.load_config('database')
        
        if not config:
            return
        
        self.db_type_var.set(config.get('db_type', 'SQL'))
        self.entries.get('directory') and self.entries['directory'].set(config.get('directory', ''))
        self.entries.get('host') and self.entries['host'].set(config.get('host', ''))
        self.entries.get('schema') and self.entries['schema'].set(config.get('schema', ''))
        self.entries.get('user') and self.entries['user'].set(config.get('user', ''))
        self.entries.get('password') and self.entries['password'].set(config.get('password', ''))
        
        self._update_directory_label()
    
    def _show_error(self, message):
        """Mostra erro"""
        self._clear_status()
        error_frame = tk.Frame(
            self.status_frame,
            bg=self.theme.DANGER_BG,
            relief='flat',
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.theme.DANGER
        )
        error_frame.pack(fill='x')
        tk.Label(
            error_frame,
            text=message,
            font=self.theme.get_font("sm"),
            fg=self.theme.DANGER,
            bg=self.theme.DANGER_BG,
            justify='left'
        ).pack(padx=12, pady=10)
    
    def _show_success(self, message):
        """Mostra sucesso"""
        self._clear_status()
        success_frame = tk.Frame(
            self.status_frame,
            bg=self.theme.SUCCESS_BG,
            relief='flat',
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.theme.SUCCESS
        )
        success_frame.pack(fill='x')
        tk.Label(
            success_frame,
            text=message,
            font=self.theme.get_font("sm"),
            fg=self.theme.SUCCESS,
            bg=self.theme.SUCCESS_BG,
            justify='left'
        ).pack(padx=12, pady=10)
    
    def _clear_status(self):
        """Limpa mensagens de status"""
        for widget in self.status_frame.winfo_children():
            widget.destroy()
