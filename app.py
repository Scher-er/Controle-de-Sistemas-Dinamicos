import customtkinter as ctk
from tkinter import messagebox
import sympy as sp
import datetime
import numpy as np
import scipy.signal as signal
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from scipy.optimize import linear_sum_assignment

# ─── Tema ──────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ───────────────────────────────────────────────────────────────────────────────
# Helpers globais
# ───────────────────────────────────────────────────────────────────────────────
def fmt_cplx(c, dec=4):
    """Formata um número complexo de forma legível."""
    if abs(c.imag) < 1e-6:
        return f"{c.real:.{dec}f}"
    sinal = "+" if c.imag >= 0 else "-"
    return f"{c.real:.{dec}f} {sinal} {abs(c.imag):.{dec}f}j"


def _track_branches(num_arr, den_arr, K_vals):
    """
    Calcula as raízes e rastreia os ramos usando o Algoritmo Húngaro
    para evitar saltos ou cruzamentos falsos nos pontos de quebra.
    """
    n = len(den_arr) - 1

    if len(num_arr) > len(den_arr):
        raise ValueError("Sistema impróprio. Verifique os parênteses do denominador.")

    num_pad = np.zeros(len(den_arr))
    num_pad[len(den_arr) - len(num_arr):] = num_arr

    branches = [[] for _ in range(n)]
    prev = None

    for K in K_vals:
        char = den_arr + K * num_pad
        try:
            roots = np.roots(char)
        except Exception:
            continue

        if prev is None:
            idx = np.lexsort((roots.real, roots.imag))
            roots = roots[idx]
        else:
            # Matriz de Custo Global (Evita que as linhas "pulem" nos cruzamentos)
            cost_matrix = np.zeros((n, n))
            for i in range(n):
                for j in range(n):
                    cost_matrix[i, j] = abs(prev[i] - roots[j])
            
            row_ind, col_ind = linear_sum_assignment(cost_matrix)
            new_roots = np.zeros(n, dtype=complex)
            for i, j in zip(row_ind, col_ind):
                new_roots[i] = roots[j]
            roots = new_roots

        prev = roots.copy()
        for i, r in enumerate(roots):
            branches[i].append(r)

    return branches


# ═══════════════════════════════════════════════════════════════════════════════
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Seu Amigo de Todas as Horas  ⚙️")
        self.geometry("1300x920")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.cor_fundo_sidebar = "#1A1A1A"
        self.cor_hover_botao   = "#2B2B2B"
        self.cor_destaque      = "#1F6AA5"
        self.protocol("WM_DELETE_WINDOW", self.fechar_app)
        # Estado compartilhado do LGR
        self._lgr_state = {}

        # Histórico por módulo
        _mods = ["Blocos", "Routh", "Degrau", "Laplace", "Erro", "ErroK", "LGR", "Complexo"]
        self._history    = {m: [] for m in _mods}
        self._hist_frames = {}          # referência ao CTkScrollableFrame de cada painel

        self.criar_sidebar()
        self.criar_telas()
        self.selecionar_tela("Home")

    def fechar_app(self):
        """Mata os processos do Matplotlib no fundo e encerra a janela de vez."""
        plt.close('all')  # Fecha todas as figuras plotadas ocultas
        self.quit()       # Interrompe o loop do CustomTkinter
        self.destroy()    # Destrói os processos da interface


    def isolar_scroll(self, widget_filho, frame_pai):
        """Desativa o scroll do frame pai quando o mouse entra no widget filho."""
        def on_enter(e):
            frame_pai._parent_canvas.unbind_all("<MouseWheel>")
            frame_pai._parent_canvas.unbind_all("<Button-4>")
            frame_pai._parent_canvas.unbind_all("<Button-5>")
            
        def on_leave(e):
            # Restaura a vinculação padrão do CustomTkinter
            frame_pai._parent_canvas.bind_all("<MouseWheel>", frame_pai._mouse_wheel_all, add="+")
            frame_pai._parent_canvas.bind_all("<Button-4>", frame_pai._mouse_wheel_all, add="+")
            frame_pai._parent_canvas.bind_all("<Button-5>", frame_pai._mouse_wheel_all, add="+")

        widget_filho.bind("<Enter>", on_enter)
        widget_filho.bind("<Leave>", on_leave)


    # ── Sidebar ────────────────────────────────────────────────────────────────
    def criar_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0,
                                          fg_color=self.cor_fundo_sidebar)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)

        ctk.CTkLabel(self.sidebar_frame,
                     text="⚙️ Amigo de\nTodas as Horas",
                     font=ctk.CTkFont(size=20, weight="bold")
                     ).grid(row=0, column=0, padx=20, pady=(30, 30))

        self.btn_home     = self._btn_menu("🏠  Início",              "Home",     1)
        self.btn_blocos   = self._btn_menu("🧩  Álgebra de Blocos",   "Blocos",   2)
        self.btn_routh    = self._btn_menu("📊  Routh-Hurwitz",       "Routh",    3)
        self.btn_degrau   = self._btn_menu("📈  Resp. ao Degrau",     "Degrau",   4)
        self.btn_laplace  = self._btn_menu("∫   Laplace Inversa",     "Laplace",  5)
        self.btn_erro     = self._btn_menu("🎯  Erro e Transitório",  "Erro",     6)
        self.btn_lgr      = self._btn_menu("📍  Lugar das Raízes",    "LGR",      7)
        self.btn_complexo = self._btn_menu("📐  Avaliação Complexa",  "Complexo", 8)
        self.btn_formulas = self._btn_menu("📚  Fórmulas",            "Formulas", 9)

    def _btn_menu(self, texto, nome_tela, linha):
        btn = ctk.CTkButton(
            self.sidebar_frame, text=texto, fg_color="transparent",
            text_color=("gray10", "gray90"), hover_color=self.cor_hover_botao,
            anchor="w", font=ctk.CTkFont(size=14),
            command=lambda: self.selecionar_tela(nome_tela))
        btn.grid(row=linha, column=0, padx=10, pady=4, sticky="ew")
        return btn

    # ── Telas ──────────────────────────────────────────────────────────────────
    def criar_telas(self):
        self.telas = {}

        # ── Home ──
        frame_home = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        self.telas["Home"] = frame_home
        ctk.CTkLabel(frame_home, text="BOA NOITE, VIRGINIA",
                     font=ctk.CTkFont(size=36, weight="bold")
                     ).pack(pady=(40, 5), anchor="w", padx=40)
        ctk.CTkLabel(frame_home,
                     text="Bem-vinda de volta ao Seu Amigo de Todas as Horas.\n"
                          "Todas as ferramentas de controle dinâmico estão prontas.",
                     font=ctk.CTkFont(size=16), text_color="gray", justify="left"
                     ).pack(pady=(0, 20), anchor="w", padx=40)

        frame_cards = ctk.CTkFrame(frame_home, fg_color="transparent")
        frame_cards.pack(fill="both", expand=True, padx=40)
        cards = [
            ("🧩 Álgebra de Blocos",  "FT de Malha Fechada",               "Blocos",   0, 0),
            ("📊 Tabela de Routh",    "Estabilidade e limites de K",        "Routh",    0, 1),
            ("📈 Resposta ao Degrau", "Gráficos no domínio do tempo",       "Degrau",   1, 0),
            ("∫ Laplace Inversa",     "F(s) → f(t)",                        "Laplace",  1, 1),
            ("🎯 Erro e Transitório", "ess, Tipo do sistema e K",           "Erro",     2, 0),
            ("📍 Lugar das Raízes",   "LGR completo com gráfico e cálculos","LGR",      2, 1),
            ("📐 Avaliação Complexa", "F(s) em s = σ + jω",                 "Complexo", 3, 0),
            ("📚 Fórmulas",           "Consulta rápida",                    "Formulas", 3, 1),
        ]
        for titulo, desc, nome, r, c in cards:
            self._criar_card(frame_cards, titulo, desc, nome, r, c)

        # ── Outras abas ──
        scrollable = {"Formulas", "LGR"}
        for nome in ["Blocos", "Routh", "Degrau", "Laplace", "Erro", "LGR", "Complexo", "Formulas"]:
            if nome in scrollable:
                self.telas[nome] = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
            else:
                self.telas[nome] = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
            getattr(self, f"setup_tab_{nome.lower()}")(self.telas[nome])

    def _criar_card(self, parent, titulo, desc, nome_tela, row, col):
        card = ctk.CTkFrame(parent, height=115, corner_radius=10,
                            fg_color="#242424", border_width=1, border_color="#333333")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        card.grid_propagate(False)
        ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=17, weight="bold"),
                     text_color=self.cor_destaque).pack(pady=(14, 4))
        ctk.CTkLabel(card, text=desc, font=ctk.CTkFont(size=12),
                     text_color="gray").pack()
        ctk.CTkButton(card, text="Abrir", width=100,
                      command=lambda n=nome_tela: self.selecionar_tela(n)
                      ).pack(side="bottom", pady=12)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)

    def selecionar_tela(self, nome):
        for t in self.telas.values():
            t.grid_forget()
        self.telas[nome].grid(row=0, column=1, sticky="nsew")
        mapa = {
            "Home": self.btn_home, "Blocos": self.btn_blocos, "Routh": self.btn_routh,
            "Degrau": self.btn_degrau, "Laplace": self.btn_laplace, "Erro": self.btn_erro,
            "LGR": self.btn_lgr, "Complexo": self.btn_complexo, "Formulas": self.btn_formulas,
        }
        for n, btn in mapa.items():
            btn.configure(fg_color=self.cor_destaque if n == nome else "transparent")

    # ══════════════════════════════════════════════════════════════════════════
    #  SISTEMA DE HISTÓRICO
    # ══════════════════════════════════════════════════════════════════════════
    def _push_history(self, mod, label, inputs: dict, result_preview: str):
        """Registra uma consulta no histórico e atualiza o painel."""
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        entry = {"ts": ts, "label": label, "inputs": inputs,
                 "preview": result_preview[:220]}
        hist = self._history[mod]
        hist.insert(0, entry)
        if len(hist) > 20:
            hist.pop()
        self._refresh_hist(mod)

    def _build_hist_panel(self, parent, mod):
        """Constrói o painel de histórico para um módulo e retorna o frame raiz."""
        outer = ctk.CTkFrame(parent, fg_color="#161616", corner_radius=8,
                              border_width=1, border_color="#252525")
        outer.pack(padx=30, pady=(4, 22), fill="x", anchor="w")

        # Cabeçalho
        hdr = ctk.CTkFrame(outer, fg_color="transparent")
        hdr.pack(fill="x", padx=12, pady=(8, 4))
        ctk.CTkLabel(hdr, text="📋  Histórico de Consultas",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#666666").pack(side="left")
        ctk.CTkButton(hdr, text="Limpar tudo", width=88, height=22,
                      font=ctk.CTkFont(size=10),
                      fg_color="#2A1A1A", hover_color="#3E2020",
                      command=lambda m=mod: self._clear_hist(m)
                      ).pack(side="right")

        # Lista rolável
        scroll = ctk.CTkScrollableFrame(outer, height=130, fg_color="transparent")
        scroll.pack(fill="x", padx=6, pady=(0, 8))
        self._hist_frames[mod] = scroll

        # Popula vazia
        self._refresh_hist(mod)
        return outer

    def _refresh_hist(self, mod):
        """Redesenha todas as entradas do histórico de um módulo."""
        if mod not in self._hist_frames:
            return
        frame = self._hist_frames[mod]
        for w in frame.winfo_children():
            w.destroy()

        if not self._history[mod]:
            ctk.CTkLabel(frame, text="Nenhuma consulta ainda.",
                         text_color="#484848", font=ctk.CTkFont(size=11)
                         ).pack(anchor="w", padx=8, pady=6)
            return

        for entry in self._history[mod]:
            row = ctk.CTkFrame(frame, fg_color="#1E1E1E", corner_radius=6)
            row.pack(fill="x", pady=2, padx=2)

            ctk.CTkLabel(row, text=entry["ts"], width=62,
                         font=ctk.CTkFont(size=10), text_color="#555555"
                         ).pack(side="left", padx=(8, 2))

            lbl = entry["label"]
            if len(lbl) > 60:
                lbl = lbl[:57] + "…"
            ctk.CTkLabel(row, text=lbl, font=ctk.CTkFont(size=11),
                         text_color="#999999", anchor="w"
                         ).pack(side="left", padx=4, fill="x", expand=True)

            ctk.CTkButton(row, text="↩ Carregar", width=86, height=24,
                          font=ctk.CTkFont(size=10),
                          fg_color="#1A2535", hover_color="#263548",
                          command=lambda e=entry, m=mod: self._load_hist(m, e)
                          ).pack(side="right", padx=6, pady=3)

    def _clear_hist(self, mod):
        self._history[mod].clear()
        self._refresh_hist(mod)

    def _load_hist(self, mod, entry):
        """Restaura os campos de entrada de uma entrada do histórico."""
        inp = entry["inputs"]
        if mod == "Blocos":
            self.entry_G.delete(0, "end"); self.entry_G.insert(0, inp.get("G", ""))
            self.entry_H.delete(0, "end"); self.entry_H.insert(0, inp.get("H", "1"))
            if "tipo" in inp:
                self.tipo_realimentacao.set(inp["tipo"])
        elif mod == "Routh":
            self.e_r.delete(0, "end"); self.e_r.insert(0, inp.get("coefs", ""))
        elif mod == "Degrau":
            self.e_num.delete(0, "end"); self.e_num.insert(0, inp.get("num", ""))
            self.e_den.delete(0, "end"); self.e_den.insert(0, inp.get("den", ""))
        elif mod == "Laplace":
            self.e_l.delete(0, "end"); self.e_l.insert(0, inp.get("F", ""))
        elif mod == "Erro":
            self.e_G_e.delete(0, "end"); self.e_G_e.insert(0, inp.get("G", ""))
        elif mod == "ErroK":
            self.e_G_dim.delete(0, "end"); self.e_G_dim.insert(0, inp.get("G", ""))
            self.e_err_alv.delete(0, "end"); self.e_err_alv.insert(0, inp.get("err", ""))
            if "ent" in inp:
                self.c_ent.set(inp["ent"])
        elif mod == "LGR":
            self.e_lgr.delete(0, "end"); self.e_lgr.insert(0, inp.get("G", ""))
        elif mod == "Complexo":
            self.e_f_comp.delete(0, "end"); self.e_f_comp.insert(0, inp.get("F", ""))
            self.e_s_comp.delete(0, "end"); self.e_s_comp.insert(0, inp.get("s", ""))

    # ══════════════════════════════════════════════════════════════════════════
    #  MÓDULO LGR  ─  Análise Completa do Lugar Geométrico das Raízes
    # ══════════════════════════════════════════════════════════════════════════
    def setup_tab_lgr(self, f):
        ctk.CTkLabel(f, text="📍 Lugar Geométrico das Raízes — Análise Completa",
                     font=ctk.CTkFont(size=22, weight="bold")
                     ).pack(pady=(22, 4), padx=30, anchor="w")

        # ── Bloco de sintaxe ──────────────────────────────────────────────────
        syntax_frame = ctk.CTkFrame(f, fg_color="#1C2333", corner_radius=8,
                                     border_width=1, border_color="#2E4070")
        syntax_frame.pack(padx=30, pady=(6, 4), anchor="w", fill="x")

        ctk.CTkLabel(syntax_frame,
                     text="📖  COMO ESCREVER A FUNÇÃO  G(s)",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#7EB8F7"
                     ).pack(anchor="w", padx=16, pady=(10, 4))

        regras_txt = (
            "  • Multiplicação:  use  *   →   s*(s+2)  não  s(s+2)\n"
            "  • Potência:       use  **  →   s**2     ou   s^2  (^ é convertido automaticamente)\n"
            "  • Divisão:        use  /   →   1 / (s*(s+2))    coloque o denominador entre parênteses\n"
            "  • O ganho K é isolado automaticamente — não precisa escrevê-lo"
        )
        ctk.CTkLabel(syntax_frame, text=regras_txt,
                     font=ctk.CTkFont(size=12), text_color="#AABFDD",
                     justify="left"
                     ).pack(anchor="w", padx=16, pady=(0, 10))

        # ── Exemplos clicáveis ────────────────────────────────────────────────
        ctk.CTkLabel(f, text="  Exemplos  (clique para carregar):",
                     font=ctk.CTkFont(size=12), text_color="gray"
                     ).pack(anchor="w", padx=30, pady=(8, 2))

        EXEMPLOS = [
            ("3 polos reais",         "1 / (s*(s+2)*(s+4))"),
            ("2 polos + 1 zero",      "(s+1) / (s*(s+3)*(s+6))"),
            ("Polos complexos",       "1 / (s*(s**2 + 2*s + 5))"),
            ("4 polos",               "1 / (s*(s+1)*(s+2)*(s+3))"),
            ("2ª ordem",              "1 / (s*(s+4))"),
        ]

        ex_row = ctk.CTkFrame(f, fg_color="transparent")
        ex_row.pack(padx=30, anchor="w", pady=(0, 10))

        def _carregar(expr):
            self.e_lgr.delete(0, "end")
            self.e_lgr.insert(0, expr)

        for rotulo, expr in EXEMPLOS:
            ctk.CTkButton(ex_row,
                          text=rotulo,
                          width=148, height=28,
                          font=ctk.CTkFont(size=11),
                          fg_color="#253050", hover_color="#354570",
                          corner_radius=6,
                          command=lambda e=expr: _carregar(e)
                          ).pack(side="left", padx=3)

        # ── Campo de entrada ──────────────────────────────────────────────────
        row_in = ctk.CTkFrame(f, fg_color="transparent")
        row_in.pack(padx=30, pady=6, anchor="w", fill="x")

        ctk.CTkLabel(row_in, text="G(s) =",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color="#7EB8F7"
                     ).pack(side="left", padx=(0, 8))

        self.e_lgr = ctk.CTkEntry(row_in, width=520,
                                   placeholder_text="1 / (s*(s+2)*(s+4))",
                                   font=ctk.CTkFont(size=14))
        self.e_lgr.pack(side="left", padx=(0, 12))

        ctk.CTkButton(row_in, text="⚙  Calcular",
                      width=170, height=36,
                      font=ctk.CTkFont(size=13),
                      command=self.calc_lgr
                      ).pack(side="left", padx=4)

        ctk.CTkButton(row_in, text="📊  Plotar LGR",
                      width=155, height=36,
                      font=ctk.CTkFont(size=13),
                      fg_color="#2A5E2A", hover_color="#3A7E3A",
                      command=self.plot_lgr
                      ).pack(side="left", padx=4)

        ctk.CTkButton(row_in, text="🗑  Limpar",
                      width=100, height=36,
                      font=ctk.CTkFont(size=12),
                      fg_color="#4A2020", hover_color="#6A3030",
                      command=lambda: (self.e_lgr.delete(0, "end"),
                                       self.txt_lgr.delete("0.0", "end"))
                      ).pack(side="left", padx=4)

        # ── Textbox de resultados ─────────────────────────────────────────────
        self.txt_lgr = ctk.CTkTextbox(f, width=1060, height=510,
                                       font=("Courier New", 13), fg_color="#111111")
        self.txt_lgr.pack(padx=30, pady=(8, 10), anchor="w")
        self.isolar_scroll(self.txt_lgr, f)
        # ── Frame do gráfico ──────────────────────────────────────────────────
        self.lgr_plot_frame = ctk.CTkFrame(f, fg_color="#111111", corner_radius=8)
        self.lgr_plot_frame.pack(padx=30, pady=(0, 30), fill="both", expand=True)
        ctk.CTkLabel(self.lgr_plot_frame,
                     text="Clique em  📊 Plotar LGR  para visualizar o gráfico",
                     text_color="gray", font=ctk.CTkFont(size=14)
                     ).pack(pady=40)

        self._build_hist_panel(f, "LGR")

    # ── Cálculo analítico ──────────────────────────────────────────────────────
    def calc_lgr(self):
        try:
            s = sp.Symbol('s')
            raw = self.e_lgr.get().replace('^', '**').strip()
            if not raw:
                messagebox.showwarning("Aviso", "Insira uma função G(s)H(s).")
                return

            G = sp.sympify(raw)

            # Isola K → substitui qualquer variável que não seja 's' por 1
            for var in list(G.free_symbols):
                if var != s:
                    G = G.subs(var, 1)

            G = sp.cancel(G)
            num_sp, den_sp = sp.fraction(G)
            num_sp = sp.expand(num_sp)
            den_sp = sp.expand(den_sp)

            # ── Polos e zeros ─────────────────────────────────────────────────
            zeros_dict = sp.roots(num_sp, s)
            polos_dict = sp.roots(den_sp, s)

            zeros = []
            for r, mult in zeros_dict.items():
                zeros.extend([complex(r.evalf())] * mult)

            polos = []
            for r, mult in polos_dict.items():
                polos.extend([complex(r.evalf())] * mult)

            n = len(polos)
            m = len(zeros)

            # Validação: sistema deve ser próprio para o LGR
            if m > n:
                diag  = "⚠  SISTEMA IMPRÓPRIO DETECTADO\n"
                diag += "─" * 62 + "\n\n"
                diag += f"  Zeros encontrados (m = {m})  ≥  Polos encontrados (n = {n})\n\n"
                diag += "  O LGR exige n > m (mais polos do que zeros).\n\n"
                diag += "  Causa mais comum: parênteses faltando no denominador.\n\n"
                diag += "  EXPRESSÃO ERRADA:\n"
                diag += "    K*(s+2) / (s+3)*(s**2+2*s+2)\n"
                diag += "    → Python lê como  (s+2)*(s²+2s+2) / (s+3)  ← numerador explode!\n\n"
                diag += "  EXPRESSÃO CORRETA:\n"
                diag += "    K*(s+2) / ((s+3)*(s**2+2*s+2))\n"
                diag += "    → Denominador completo entre parênteses duplos\n\n"
                diag += f"  O que foi identificado como numerador:   N(s) = {num_sp}\n"
                diag += f"  O que foi identificado como denominador: D(s) = {den_sp}\n\n"
                diag += "  Corrija a expressão e tente novamente."
                self.txt_lgr.delete("0.0", "end")
                self.txt_lgr.insert("0.0", diag)
                self._lgr_state = {}
                return

            res = ""
            SEP  = "─" * 62 + "\n"
            SEP2 = "═" * 62 + "\n"

            res += SEP2
            res += "   ANÁLISE COMPLETA DO LUGAR GEOMÉTRICO DAS RAÍZES\n"
            res += SEP2 + "\n"

            # ── Seção 1: Polos e zeros ─────────────────────────────────────
            res += SEP
            res += " 1.  POLOS E ZEROS DE MALHA ABERTA\n"
            res += SEP
            res += f"  N(s) = {num_sp}\n"
            res += f"  D(s) = {den_sp}\n\n"
            res += f"  n = {n}  polo(s)  → {n} ramos no LGR\n"
            for i, p in enumerate(polos):
                star = "  ← COMPLEXO" if abs(p.imag) > 1e-4 else ""
                res += f"    p{i+1} = {fmt_cplx(p)}{star}\n"
            res += f"\n  m = {m}  zero(s) finito(s)\n"
            if m == 0:
                res += f"    (nenhum — todos os {n} ramos vão ao infinito)\n"
            else:
                for i, z in enumerate(zeros):
                    star = "  ← COMPLEXO" if abs(z.imag) > 1e-4 else ""
                    res += f"    z{i+1} = {fmt_cplx(z)}{star}\n"

            assint = n - m
            res += f"\n  Ramos ao infinito (assíntotas): n − m = {n} − {m} = {assint}\n\n"

            # ── Seção 2: Assíntotas ────────────────────────────────────────
            res += SEP
            res += f" 2.  ASSÍNTOTAS  ({assint} ramo(s) ao ∞)\n"
            res += SEP

            if assint <= 0:
                res += "  Todos os ramos terminam em zeros finitos.\n  Não há assíntotas.\n\n"
                centroide = None
            else:
                soma_p = sum(p.real for p in polos)
                soma_z = sum(z.real for z in zeros)
                centroide = (soma_p - soma_z) / assint

                res += "  Centroide (interseção das assíntotas com o eixo real):\n"
                res += f"  σa = (Σ Polos_reais − Σ Zeros_reais) / (n − m)\n"
                res += f"  σa = ( ({' + '.join(f'{p.real:.3f}' for p in polos)})"
                res += f" − ({' + '.join(f'{z.real:.3f}' for z in zeros) if zeros else '0'}) ) / {assint}\n"
                res += f"  σa = ({soma_p:.4f} − {soma_z:.4f}) / {assint}\n"
                res += f"  σa = {centroide:.4f}  ◄\n\n"

                res += "  Ângulos das assíntotas: θ = (2k+1)·180° / (n−m)\n"
                for k in range(assint):
                    ang = (2*k + 1) * 180.0 / assint
                    res += f"    k={k}: θ = (2·{k}+1)·180° / {assint} = {ang:.1f}°\n"
                res += "\n"

            # ── Seção 3: Pontos de Quebra ──────────────────────────────────
            res += SEP
            res += " 3.  PONTOS DE QUEBRA / ENCONTRO\n"
            res += SEP
            res += "  Eq. característica:  1 + K·G(s) = 0\n"
            res += "  → K(s) = −D(s) / N(s)\n\n"

            K_expr = sp.Rational(-1) * den_sp / num_sp
            K_expr_simpl = sp.simplify(K_expr)
            res += f"  K(s) = {K_expr_simpl}\n\n"
            res += "  Condição de ponto de quebra: dK/ds = 0\n"

            dK = sp.diff(K_expr, s)
            numer_dK, _ = sp.fraction(sp.cancel(dK))
            numer_dK = sp.expand(numer_dK)
            res += f"  dK/ds = 0  →  numerador: {numer_dK} = 0\n\n"

            candidatos_sp = sp.solve(numer_dK, s)
            candidatos = []
            for pt in candidatos_sp:
                try:
                    c = complex(pt.evalf())
                    candidatos.append(c)
                except Exception:
                    pass

            quebras_validas = []
            res += "  Candidatos e verificação:\n"
            for c in candidatos:
                if abs(c.imag) > 1e-4:
                    res += f"    s = {fmt_cplx(c)}  →  complexo, ignorado\n"
                    continue
                s_val = c.real
                K_val = float(sp.re(K_expr_simpl.subs(s, s_val).evalf()))

                # Verifica se está no LGR real (nº de polos+zeros à direita é ímpar)
                n_direita = sum(1 for p in polos if p.real > s_val + 1e-8) + \
                            sum(1 for z in zeros if z.real > s_val + 1e-8)
                no_lgr = (n_direita % 2 == 1)

                flag = "✓ VÁLIDO  (ponto de quebra)" if (K_val >= -1e-8 and no_lgr) else \
                       ("✗ K < 0  (não pertence ao LGR positivo)" if K_val < -1e-8 else
                        "✗ Fora do eixo real do LGR")
                res += f"    s = {s_val:.4f}   K = {K_val:.4f}   {flag}\n"
                if K_val >= -1e-8 and no_lgr:
                    quebras_validas.append((s_val, K_val))
            if not candidatos:
                res += "    (dK/ds = 0 sem raízes reais — sem pontos de quebra)\n"
            res += "\n"

           # ── Seção 4: Cruzamento do eixo imaginário ─────────────────────
            res += SEP
            res += " 4.  CRUZAMENTO DO EIXO IMAGINÁRIO\n"
            res += SEP
            res += "  Método: substituição s = jω na equação característica\n"
            res += "  D(jω) + K · N(jω) = 0\n\n"

            K_sym  = sp.Symbol('K', positive=True)
            omega  = sp.Symbol('omega', real=True)

            char_eq = den_sp + K_sym * num_sp
            char_jw = sp.expand(char_eq.subs(s, sp.I * omega))
            r_part  = sp.collect(sp.re(char_jw), omega)
            i_part  = sp.collect(sp.im(char_jw), omega)

            res += f"  Parte Real:  {r_part} = 0\n"
            res += f"  Parte Imag:  {i_part} = 0\n\n"

            # Resolve o sistema Im = 0 e Re = 0 simultaneamente para K e omega
            sistemas_sols = sp.solve([r_part, i_part], (omega, K_sym), dict=True)
            crossings = []

            for sol in sistemas_sols:
                try:
                    w_f = float(sol[omega].evalf())
                    K_f = float(sol[K_sym].evalf())
                except Exception:
                    continue
                
                # Ignora a origem (w=0) e foca em soluções estáveis com K >= 0
                if abs(w_f) > 1e-6 and K_f >= -1e-8:
                    crossings.append((abs(w_f), max(K_f, 0.0)))

            # Remove duplicatas (±w)
            crossings = list(set([(round(w, 4), round(k, 4)) for w, k in crossings]))

            if crossings:
                for w_f, K_f in crossings:
                    res += f"    ω = {w_f:.4f} rad/s  →  K = {K_f:.4f}\n"
                    res += f"    Cruzamento em  s = ±j{w_f:.4f}  com K = {K_f:.4f}  ◄\n"
            else:
                res += "    Nenhum cruzamento com eixo imaginário para K > 0\n"
                res += "    (sistema permanece estável ou instável para todo K > 0)\n"
            res += "\n"

            # ── Seção 5: Ângulos de Partida ────────────────────────────────
            res += SEP
            res += " 5.  ÂNGULOS DE PARTIDA  (polos complexos)\n"
            res += SEP
            res += "  Fórmula: θ_p = Σ∠(p−z_i) − Σ∠(p−p_j) − 180°\n"
            res += "           (ângulos de vetores DESTE polo para cada outro polo/zero)\n\n"

            complexos_sup = [(i, p) for i, p in enumerate(polos) if p.imag > 1e-4]
            departure_angles = {}

            if not complexos_sup:
                res += "  Sistema sem polos complexos — não há ângulos de partida.\n\n"
            else:
                for idx, p in complexos_sup:
                    ang_zeros = [np.degrees(np.angle(p - z)) for z in zeros]
                    ang_polos = [np.degrees(np.angle(p - q))
                                 for j, q in enumerate(polos) if j != idx]
                    soma_z = sum(ang_zeros)
                    soma_p = sum(ang_polos)
                    dep = (soma_z - soma_p - 180.0) % 360.0

                    departure_angles[idx] = dep
                    # Ângulo de partida do polo conjugado = -dep
                    dep_conj = (-dep) % 360.0

                    res += f"  Polo p{idx+1} = {fmt_cplx(p)}\n"
                    if zeros:
                        for i_z, z in enumerate(zeros):
                            res += f"    ∠(p−z{i_z+1}): ∠({fmt_cplx(p - z)}) = {ang_zeros[i_z]:.2f}°\n"
                        res += f"    Σ∠zeros → polo = {soma_z:.2f}°\n"
                    else:
                        res += f"    (sem zeros — contribuição = 0°)\n"

                    for i_q, (ang, (j, q)) in enumerate(
                            zip(ang_polos, [(j,q) for j,q in enumerate(polos) if j != idx])):
                        res += f"    ∠(p−p{j+1}): ∠({fmt_cplx(p - q)}) = {ang:.2f}°\n"
                    res += f"    Σ∠outros polos → polo = {soma_p:.2f}°\n"
                    res += f"    θ_partida = {soma_z:.2f}° − {soma_p:.2f}° − 180° = {dep:.2f}°  ◄\n"
                    res += f"    (polo conjugado p{idx+1}*: θ_partida = {dep_conj:.2f}°)\n\n"

            # ── Seção 6: Resumo ────────────────────────────────────────────
            res += SEP2
            res += " RESUMO\n"
            res += SEP2
            res += f"  Polos: {n}  |  Zeros: {m}  |  Assíntotas: {assint}\n"
            if centroide is not None:
                res += f"  Centroide: σa = {centroide:.4f}\n"
            if quebras_validas:
                res += "  Pontos de quebra: " + \
                       ", ".join(f"s={q[0]:.4f} (K={q[1]:.4f})" for q in quebras_validas) + "\n"
            if crossings:
                res += "  Cruzamentos jω: " + \
                       ", ".join(f"±j{w:.4f} (K={K:.4f})" for w, K in crossings) + "\n"
            if departure_angles:
                res += "  Ângulos partida: " + \
                       ", ".join(f"p{i+1}→{a:.1f}°" for i, a in departure_angles.items()) + "\n"

            # ── Salva estado para o plotter ────────────────────────────────
            self._lgr_state = {
                "polos": polos, "zeros": zeros, "n": n, "m": m,
                "centroide": centroide, "assint": assint,
                "quebras": quebras_validas, "crossings": crossings,
                "departure": departure_angles,
                "num_sp": num_sp, "den_sp": den_sp,
            }

            self.txt_lgr.delete("0.0", "end")
            self.txt_lgr.insert("0.0", res)

            # ── Histórico ─────────────────────────────────────────────────
            preview = f"n={n} polos, m={m} zeros"
            if quebras_validas:
                preview += f" | Quebra: s≈{quebras_validas[0][0]:.3f}"
            if crossings:
                preview += f" | Cruzamento: ±j{crossings[0][0]:.3f}"
            self._push_history("LGR",
                               label=raw[:80],
                               inputs={"G": raw},
                               result_preview=preview)

        except Exception as e:
            msg = str(e)
            # Tenta dar dica específica por tipo de erro
            if "sympify" in msg.lower() or "SyntaxError" in msg or "invalid syntax" in msg.lower():
                dica = (
                    "Não foi possível interpretar a expressão.\n\n"
                    "Dicas:\n"
                    "  • Use * para multiplicar:   s*(s+2)  não  s(s+2)\n"
                    "  • Use ** para potência:     s**2     não  s^2\n"
                    "  • Coloque o denominador entre parênteses:\n"
                    "      1 / ((s+1)*(s+3))  não  1 / (s+1)*(s+3)"
                )
            elif "impróprio" in msg or "broadcast" in msg or "shape" in msg:
                dica = (
                    "Sistema impróprio: mais zeros do que polos.\n\n"
                    "Provavelmente faltam parênteses no denominador.\n\n"
                    "ERRADO:   K*(s+2) / (s+3)*(s**2+2*s+2)\n"
                    "CORRETO:  K*(s+2) / ((s+3)*(s**2+2*s+2))"
                )
            else:
                dica = f"Detalhe técnico: {msg}"
            messagebox.showerror("Erro no cálculo LGR", dica)

    # ── Plotter do LGR ─────────────────────────────────────────────────────────
    def plot_lgr(self):
        # Se estado vazio, tenta calcular primeiro
        if not self._lgr_state:
            self.calc_lgr()
        if not self._lgr_state:
            return

        try:
            st = self._lgr_state
            s = sp.Symbol('s')
            polos    = st["polos"]
            zeros    = st["zeros"]
            n        = st["n"]
            m        = st["m"]
            centroide= st["centroide"]
            assint   = st["assint"]
            quebras  = st["quebras"]
            crossings= st["crossings"]
            dep_ang  = st["departure"]

            # Coeficientes numpy
            def sp_to_np_coeffs(expr):
                try:
                    poly = sp.Poly(expr, s)
                    return np.array([float(c) for c in poly.all_coeffs()], dtype=float)
                except Exception:
                    return np.array([float(expr)], dtype=float)

            num_arr = sp_to_np_coeffs(st["num_sp"])
            den_arr = sp_to_np_coeffs(st["den_sp"])

            # Guarda para diagnóstico antes de chamar _track_branches
            if len(num_arr) > len(den_arr):
                messagebox.showerror(
                    "Sistema impróprio",
                    f"Grau do numerador ({len(num_arr)-1}) ≥ grau do denominador ({len(den_arr)-1}).\n\n"
                    "Verifique os parênteses na expressão.\n\n"
                    "ERRADO:   K*(s+2) / (s+3)*(s**2+2*s+2)\n"
                    "CORRETO:  K*(s+2) / ((s+3)*(s**2+2*s+2))"
                )
                return

           # ── Calcula ramos do LGR ──────────────────────────────────────
            K_vals = np.concatenate([
                np.linspace(0, 0.05, 80),
                np.logspace(-2, 4, 2000),
                [q[1] for q in quebras] # <-- Injeta os K exatos da quebra
            ])
            K_vals = np.sort(K_vals)    # <-- Ordena para o rastreio não bugar
            
            branches = _track_branches(num_arr, den_arr, K_vals)

            # ── Cria figura ───────────────────────────────────────────────
            BG = "#111111"
            plt.rcParams.update({"text.color": "white"})
            fig, ax = plt.subplots(figsize=(10, 7.5), facecolor=BG)
            ax.set_facecolor(BG)
            for sp_ in ax.spines.values():
                sp_.set_color("#444444")
            ax.tick_params(colors="#AAAAAA", labelsize=9)
            ax.set_xlabel("Parte Real  σ", color="#CCCCCC", fontsize=11)
            ax.set_ylabel("Parte Imaginária  jω  [rad/s]", color="#CCCCCC", fontsize=11)
            ax.set_title("Lugar Geométrico das Raízes (LGR)", color="white", fontsize=14, pad=12)
            ax.grid(True, color="#2A2A2A", linestyle="--", alpha=0.7)
            ax.axhline(0, color="#555555", linewidth=0.8)
            ax.axvline(0, color="#555555", linewidth=0.8)

            # ── Ramos ─────────────────────────────────────────────────────
            branch_colors = ["#4FC3F7", "#81C784", "#FFB74D", "#CE93D8",
                             "#F48FB1", "#80CBC4", "#FFCC02", "#FF7043"]
            legend_handles = []

            for i, branch in enumerate(branches):
                if not branch:
                    continue
                reals = [r.real for r in branch]
                imags = [r.imag for r in branch]
                col = branch_colors[i % len(branch_colors)]
                ax.plot(reals, imags, color=col, linewidth=1.8, alpha=0.85, zorder=3)
                # Seta de direção no meio do ramo
                mid = len(reals) // 2
                if mid + 1 < len(reals):
                    ax.annotate("",
                        xy=(reals[mid+1], imags[mid+1]),
                        xytext=(reals[mid], imags[mid]),
                        arrowprops=dict(arrowstyle="->", color=col, lw=1.5),
                        zorder=4)
                if i == 0:
                    legend_handles.append(mpatches.Patch(color=col, label="Ramo do LGR"))

            # ── Polos (×) ─────────────────────────────────────────────────
            for i, p in enumerate(polos):
                ax.plot(p.real, p.imag, marker="x", color="#FF5252",
                        markersize=14, markeredgewidth=2.5, zorder=6)
                ax.annotate(f" p{i+1}", xy=(p.real, p.imag), color="#FF8080",
                            fontsize=9, zorder=7)
            legend_handles.append(
                plt.Line2D([0],[0], marker='x', color='w', markerfacecolor='#FF5252',
                           markeredgecolor='#FF5252', markersize=12, label='Polo (K=0)', lw=0))

            # ── Zeros (○) ─────────────────────────────────────────────────
            for i, z in enumerate(zeros):
                ax.plot(z.real, z.imag, marker="o", color="none",
                        markeredgecolor="#64B5F6", markersize=12,
                        markeredgewidth=2.5, zorder=6)
                ax.annotate(f" z{i+1}", xy=(z.real, z.imag), color="#90CAF9",
                            fontsize=9, zorder=7)
            if zeros:
                legend_handles.append(
                    plt.Line2D([0],[0], marker='o', color='w', markerfacecolor='none',
                               markeredgecolor='#64B5F6', markersize=11,
                               label='Zero (K=∞)', lw=0))

            # ── Assíntotas ────────────────────────────────────────────────
            if centroide is not None and assint > 0:
                # Determina comprimento das assíntotas a partir dos limites atuais
                all_reals = [r.real for b in branches for r in b if b]
                all_imags = [r.imag for b in branches for r in b if b]
                span_r = max(abs(max(all_reals, default=10) - min(all_reals, default=-10)), 10)
                span_i = max(abs(max(all_imags, default=10) - min(all_imags, default=-10)), 10)
                L = max(span_r, span_i) * 1.5

                for k in range(assint):
                    ang_rad = (2*k + 1) * np.pi / assint
                    dx, dy = np.cos(ang_rad) * L, np.sin(ang_rad) * L
                    ax.plot([centroide, centroide + dx], [0, dy],
                            "--", color="#888888", alpha=0.55, linewidth=1.2, zorder=2)
                    deg = np.degrees(ang_rad) % 360
                    ax.annotate(f"{deg:.0f}°", xy=(centroide + dx*0.55, dy*0.55),
                                color="#AAAAAA", fontsize=8, ha="center")

                ax.plot(centroide, 0, marker="+", color="#FFD54F",
                        markersize=14, markeredgewidth=2.5, zorder=7,
                        label=f"Centroide σa={centroide:.3f}")
                legend_handles.append(
                    plt.Line2D([0],[0], marker='+', color='w', markerfacecolor='#FFD54F',
                               markeredgecolor='#FFD54F', markersize=12,
                               label=f'Centroide σa={centroide:.3f}', lw=0))
                legend_handles.append(
                    plt.Line2D([0],[0], linestyle='--', color='#888888',
                               label='Assíntotas'))

            # ── Pontos de Quebra (★) ──────────────────────────────────────
            for q_s, q_K in quebras:
                ax.plot(q_s, 0, marker="*", color="#FFEB3B",
                        markersize=18, zorder=8)
                ax.annotate(f" Quebra\n s={q_s:.3f}\n K={q_K:.3f}",
                            xy=(q_s, 0), color="#FFF176", fontsize=8,
                            xytext=(q_s, 0.4), textcoords='data',
                            arrowprops=dict(arrowstyle='->', color='#FFF176', lw=1))
            if quebras:
                legend_handles.append(
                    plt.Line2D([0],[0], marker='*', color='w', markerfacecolor='#FFEB3B',
                               markeredgecolor='#FFEB3B', markersize=14,
                               label='Ponto de Quebra', lw=0))

            # ── Cruzamentos eixo imaginário (◆) ───────────────────────────
            for w_c, K_c in crossings:
                for pm in [+1, -1]:
                    ax.plot(0, pm * w_c, marker="D", color="#76FF03",
                            markersize=11, zorder=8)
                    ax.annotate(
                        f" s=±j{w_c:.3f}\n K={K_c:.3f}",
                        xy=(0, pm * w_c), color="#CCFF90", fontsize=8,
                        xytext=(0.5, pm * w_c))
            if crossings:
                legend_handles.append(
                    plt.Line2D([0],[0], marker='D', color='w', markerfacecolor='#76FF03',
                               markeredgecolor='#76FF03', markersize=9,
                               label='Cruzamento eixo jω', lw=0))

            # ── Ângulos de Partida (setas) ─────────────────────────────────
            complexos_sup = [(i, p) for i, p in enumerate(polos) if p.imag > 1e-4]
            for idx, p in complexos_sup:
                if idx not in dep_ang:
                    continue
                dep_rad = np.radians(dep_ang[idx])
                L_arr = max(0.3, max(abs(p.real), abs(p.imag)) * 0.18)
                dx = L_arr * np.cos(dep_rad)
                dy = L_arr * np.sin(dep_rad)
                ax.annotate("",
                    xy=(p.real + dx, p.imag + dy),
                    xytext=(p.real, p.imag),
                    arrowprops=dict(arrowstyle="-|>", color="#FF80AB",
                                   lw=2.0, mutation_scale=14),
                    zorder=9)
                ax.annotate(f"θ_p={dep_ang[idx]:.1f}°",
                            xy=(p.real + dx * 1.2, p.imag + dy * 1.2),
                            color="#FF80AB", fontsize=9)
                # Conjugado
                dep_conj_rad = np.radians((-dep_ang[idx]) % 360)
                dx2 = L_arr * np.cos(dep_conj_rad)
                dy2 = L_arr * np.sin(dep_conj_rad)
                ax.annotate("",
                    xy=(p.real + dx2, p.imag - dy + dy2),
                    xytext=(p.real, -p.imag),
                    arrowprops=dict(arrowstyle="-|>", color="#FF80AB",
                                   lw=2.0, mutation_scale=14),
                    zorder=9)

            if complexos_sup:
                legend_handles.append(
                    mpatches.FancyArrow(0, 0, 1, 0, width=0.3,
                                        color='#FF80AB', label='Ângulo de Partida'))

            # ── Legenda & layout ──────────────────────────────────────────
            leg = ax.legend(handles=legend_handles, loc="upper right",
                            facecolor="#1E1E1E", edgecolor="#444444",
                            labelcolor="white", fontsize=9, framealpha=0.9)
            fig.tight_layout(pad=1.5)

            # ── Embutir no frame ──────────────────────────────────────────
            for w in self.lgr_plot_frame.winfo_children():
                w.destroy()

            canvas = FigureCanvasTkAgg(fig, master=self.lgr_plot_frame)
            canvas.draw()
            toolbar = NavigationToolbar2Tk(canvas, self.lgr_plot_frame)
            toolbar.update()
            toolbar.configure(bg="#1A1A1A")
            canvas.get_tk_widget().pack(expand=True, fill="both")

        except Exception as e:
            messagebox.showerror("Erro no Gráfico LGR",
                                 f"Não foi possível plotar.\nDetalhe: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    #  ÁLGEBRA DE BLOCOS
    # ══════════════════════════════════════════════════════════════════════════
    def setup_tab_blocos(self, f):
        ctk.CTkLabel(f, text="🧩 Álgebra de Blocos",
                     font=ctk.CTkFont(size=22, weight="bold")
                     ).pack(pady=20, padx=30, anchor="w")
        ctk.CTkLabel(f, text="Calcula a Função de Transferência de Malha Fechada T(s) = G(s)/(1 ± G(s)H(s))",
                     font=ctk.CTkFont(size=13), text_color="gray"
                     ).pack(anchor="w", padx=30)

        grid = ctk.CTkFrame(f, fg_color="transparent")
        grid.pack(padx=30, pady=12, anchor="w")
        ctk.CTkLabel(grid, text="G(s):").grid(row=0, column=0, sticky="w", pady=6)
        self.entry_G = ctk.CTkEntry(grid, width=480,
                                     placeholder_text="Ex: 10*(s+1) / (s*(s+5)*(s+10))")
        self.entry_G.grid(row=0, column=1, padx=10)
        ctk.CTkLabel(grid, text="H(s):").grid(row=1, column=0, sticky="w", pady=6)
        self.entry_H = ctk.CTkEntry(grid, width=480)
        self.entry_H.insert(0, "1")
        self.entry_H.grid(row=1, column=1, padx=10)

        self.tipo_realimentacao = ctk.StringVar(value="Negativa")
        fr = ctk.CTkFrame(f, fg_color="transparent")
        fr.pack(anchor="w", padx=30, pady=8)
        ctk.CTkRadioButton(fr, text="Realimentação Negativa (−)",
                            variable=self.tipo_realimentacao, value="Negativa"
                            ).pack(side="left", padx=10)
        ctk.CTkRadioButton(fr, text="Realimentação Positiva (+)",
                            variable=self.tipo_realimentacao, value="Positiva"
                            ).pack(side="left", padx=10)

        ctk.CTkButton(f, text="Calcular T(s)", command=self.calcular_blocos
                      ).pack(padx=30, pady=10, anchor="w")
        self.txt_b = ctk.CTkTextbox(f, width=850, height=180,
                                     font=("Courier New", 14), fg_color="#111111")
        self.txt_b.pack(padx=30, pady=10, anchor="w")
        self._build_hist_panel(f, "Blocos")

    def calcular_blocos(self):
        try:
            s = sp.Symbol('s')
            G = sp.sympify(self.entry_G.get().replace('^', '**'))
            H = sp.sympify(self.entry_H.get().replace('^', '**'))
            sinal = 1 if self.tipo_realimentacao.get() == "Negativa" else -1
            T = sp.cancel(G / (1 + sinal * G * H))
            num_T, den_T = sp.fraction(T)
            saida = f"T(s) = {T}\n\n"
            saida += f"Numerador:    {sp.expand(num_T)}\n"
            saida += f"Denominador:  {sp.expand(den_T)}\n\n"
            saida += f"Polos de malha fechada (denominador = 0):\n"
            for r, mult in sp.roots(den_T, s).items():
                saida += f"  s = {complex(r.evalf()):.4f}  (mult. {mult})\n"
            self.txt_b.delete("0.0", "end")
            self.txt_b.insert("0.0", saida)
            self._push_history("Blocos",
                               label=f"G={self.entry_G.get()[:50]}  H={self.entry_H.get()[:20]}",
                               inputs={"G": self.entry_G.get(), "H": self.entry_H.get(),
                                       "tipo": self.tipo_realimentacao.get()},
                               result_preview=saida)
        except Exception as e:
            messagebox.showerror("Erro", f"Verifique as expressões.\nDetalhe: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    #  ROUTH-HURWITZ
    # ══════════════════════════════════════════════════════════════════════════
    def setup_tab_routh(self, f):
        ctk.CTkLabel(f, text="📊 Tabela de Routh-Hurwitz",
                     font=ctk.CTkFont(size=22, weight="bold")
                     ).pack(pady=20, padx=30, anchor="w")
        ctk.CTkLabel(f,
                     text="Coeficientes do polinômio característico (do maior para o menor grau), separados por espaço\n"
                          "Ex para s³+6s²+11s+6  →  1 6 11 6",
                     font=ctk.CTkFont(size=13), text_color="gray", justify="left"
                     ).pack(anchor="w", padx=30)
        self.e_r = ctk.CTkEntry(f, width=600,
                                 placeholder_text="1 6 11 6")
        self.e_r.pack(padx=30, pady=10, anchor="w")
        ctk.CTkButton(f, text="Calcular Tabela", command=self.calc_r
                      ).pack(padx=30, pady=8, anchor="w")
        self.txt_r = ctk.CTkTextbox(f, width=900, height=460,
                                     font=("Courier New", 14), fg_color="#111111")
        self.txt_r.pack(padx=30, pady=10, anchor="w")
        self._build_hist_panel(f, "Routh")

    def calc_r(self):
        try:
            c = [sp.sympify(x) for x in self.e_r.get().split()]
            n = len(c)
            if n < 2:
                messagebox.showerror("Erro", "Insira ao menos 2 coeficientes.")
                return

            r = sp.zeros(n, (n + 1) // 2)
            for i, x in enumerate(c):
                if i % 2 == 0:
                    r[0, i // 2] = x
                else:
                    r[1, i // 2] = x

            eps = sp.Symbol('ε')
            for i in range(2, n):
                for j in range(r.shape[1] - 1):
                    p = r[i-1, 0]
                    if p == 0:
                        p = eps
                        r[i-1, 0] = p
                    r[i, j] = sp.cancel(
                        -(r[i-2, 0]*r[i-1, j+1] - r[i-2, j+1]*p) / p)

            # Monta saída
            res = "TABELA DE ROUTH-HURWITZ\n"
            res += "─" * 50 + "\n"
            max_col_len = max(len(str(r[i, j]))
                              for i in range(n) for j in range(r.shape[1]))

            for i in range(n):
                linha = f"  s^{n-1-i} │ "
                for j in range(r.shape[1]):
                    val = str(sp.simplify(r[i, j]))
                    linha += val.ljust(max_col_len + 3)
                res += linha + "\n"

            # Contagem de mudanças de sinal na 1ª coluna
            primeira_col = [r[i, 0] for i in range(n)]
            # Avalia limite (substitui ε→0+)
            def sinal_val(expr):
                v = sp.limit(expr, eps, 0, "+") if eps in expr.free_symbols else expr
                try:
                    return float(v.evalf())
                except Exception:
                    return None

            sinais = [sinal_val(x) for x in primeira_col]
            mudancas = sum(1 for a, b in zip(sinais, sinais[1:])
                           if a is not None and b is not None and a * b < 0)

            res += "─" * 50 + "\n\n"
            res += f"Mudanças de sinal na 1ª coluna: {mudancas}\n"
            if mudancas == 0:
                res += "✓  SISTEMA ESTÁVEL  (todos os polos no SPE)\n"
            else:
                res += f"✗  SISTEMA INSTÁVEL  — {mudancas} polo(s) no SPD/eixo imaginário\n"

            # Verifica linha zero (ganho marginal)
            for i in range(n):
                if sinais[i] == 0.0 and eps not in primeira_col[i].free_symbols:
                    res += f"\n  ⚠ Linha s^{n-1-i} tem primeiro elemento ZERO "
                    res += "→ estabilidade marginal possível\n"

            self.txt_r.delete("0.0", "end")
            self.txt_r.insert("0.0", res)
            self._push_history("Routh",
                               label=f"Coef: {self.e_r.get()[:60]}",
                               inputs={"coefs": self.e_r.get()},
                               result_preview=res)
        except Exception as e:
            messagebox.showerror("Erro", f"Verifique os coeficientes.\nDetalhe: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    #  RESPOSTA AO DEGRAU
    # ══════════════════════════════════════════════════════════════════════════
    def setup_tab_degrau(self, f):
        ctk.CTkLabel(f, text="📈 Resposta ao Degrau",
                     font=ctk.CTkFont(size=22, weight="bold")
                     ).pack(pady=20, padx=30, anchor="w")
        ctk.CTkLabel(f, text="Coeficientes do numerador e denominador separados por espaço",
                     font=ctk.CTkFont(size=13), text_color="gray"
                     ).pack(anchor="w", padx=30)

        f_in = ctk.CTkFrame(f, fg_color="transparent")
        f_in.pack(padx=30, pady=10, anchor="w")
        ctk.CTkLabel(f_in, text="Num:").pack(side="left")
        self.e_num = ctk.CTkEntry(f_in, placeholder_text="Ex: 4", width=220)
        self.e_num.pack(side="left", padx=6)
        ctk.CTkLabel(f_in, text="Den:").pack(side="left")
        self.e_den = ctk.CTkEntry(f_in, placeholder_text="Ex: 1 2 4", width=220)
        self.e_den.pack(side="left", padx=6)
        ctk.CTkButton(f_in, text="Plotar", command=self.plot_degrau).pack(side="left", padx=10)

        self.f_g = ctk.CTkFrame(f, fg_color="#111111")
        self.f_g.pack(expand=True, fill="both", padx=30, pady=10)
        self._build_hist_panel(f, "Degrau")

    def plot_degrau(self):
        try:
            num_c = [float(x) for x in self.e_num.get().split()]
            den_c = [float(x) for x in self.e_den.get().split()]
            sys = signal.TransferFunction(num_c, den_c)
            t, y = signal.step(sys)

            for w in self.f_g.winfo_children():
                w.destroy()

            BG = "#111111"
            fig, ax = plt.subplots(figsize=(8, 4.5), facecolor=BG)
            ax.set_facecolor(BG)
            for sp_ in ax.spines.values():
                sp_.set_color("#444444")
            ax.tick_params(colors="#AAAAAA")
            ax.set_xlabel("Tempo [s]", color="#CCCCCC")
            ax.set_ylabel("Amplitude", color="#CCCCCC")
            ax.set_title("Resposta ao Degrau Unitário", color="white")

            ax.plot(t, y, "#4FC3F7", linewidth=2, label="y(t)")
            ax.axhline(y[-1], color="#555555", linestyle=":", linewidth=1)

            # Métricas
            y_ss = y[-1]
            if abs(y_ss) > 1e-9:
                Mp = (max(y) - y_ss) / y_ss * 100
                idx_pico = np.argmax(y)
                tp = t[idx_pico]

                mask2 = np.where(np.abs(y - y_ss) <= 0.02 * abs(y_ss))[0]
                ts2 = t[mask2[0]] if len(mask2) > 0 else None

                ax.plot(tp, max(y), "r*", markersize=12, label=f"Pico (tp={tp:.2f}s, Mp={Mp:.1f}%)")
                if ts2:
                    ax.axvline(ts2, color="#FFD54F", linestyle="--", linewidth=1,
                               label=f"ts(2%) ≈ {ts2:.2f}s")
                ax.annotate(f"y∞={y_ss:.3f}", xy=(t[-1]*0.02, y_ss),
                            color="#AAAAAA", fontsize=9)

            ax.legend(facecolor="#1E1E1E", labelcolor="white", fontsize=9)
            ax.grid(True, color="#222222", linestyle="--", alpha=0.6)
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=self.f_g)
            canvas.draw()
            canvas.get_tk_widget().pack(expand=True, fill="both")
            self._push_history("Degrau",
                               label=f"Num:[{self.e_num.get()}]  Den:[{self.e_den.get()}]",
                               inputs={"num": self.e_num.get(), "den": self.e_den.get()},
                               result_preview=f"y∞≈{y[-1]:.4f}")
        except Exception as e:
            messagebox.showerror("Erro", f"Verifique os coeficientes.\nDetalhe: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    #  LAPLACE INVERSA
    # ══════════════════════════════════════════════════════════════════════════
    def setup_tab_laplace(self, f):
        ctk.CTkLabel(f, text="∫ Laplace Inversa",
                     font=ctk.CTkFont(size=22, weight="bold")
                     ).pack(pady=20, padx=30, anchor="w")
        ctk.CTkLabel(f, text="Converte F(s) para f(t) usando frações parciais",
                     font=ctk.CTkFont(size=13), text_color="gray"
                     ).pack(anchor="w", padx=30)
        self.e_l = ctk.CTkEntry(f, width=550,
                                 placeholder_text="Ex: (2*s + 5) / (s**2 + 3*s + 2)")
        self.e_l.pack(padx=30, pady=10, anchor="w")
        ctk.CTkButton(f, text="Calcular Inversa", command=self.inv
                      ).pack(padx=30, pady=8, anchor="w")
        self.txt_l = ctk.CTkTextbox(f, width=750, height=220,
                                     font=("Courier New", 14), fg_color="#111111")
        self.txt_l.pack(padx=30, pady=10, anchor="w")
        self._build_hist_panel(f, "Laplace")

    def inv(self):
        try:
            s, t = sp.Symbol('s'), sp.Symbol('t', positive=True)
            F = sp.sympify(self.e_l.get().replace('^', '**'))
            F_parcial = sp.apart(F, s)
            f = sp.inverse_laplace_transform(F, s, t)
            saida = f"F(s) = {F}\n"
            saida += f"F(s) em frações parciais = {F_parcial}\n\n"
            saida += f"f(t) = {sp.simplify(f)}"
            self.txt_l.delete("0.0", "end")
            self.txt_l.insert("0.0", saida)
            self._push_history("Laplace",
                               label=f"F(s) = {self.e_l.get()[:65]}",
                               inputs={"F": self.e_l.get()},
                               result_preview=saida)
        except Exception as e:
            messagebox.showerror("Erro", f"Expressão inválida.\nDetalhe: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    #  ERRO EM REGIME PERMANENTE + TRANSITÓRIO
    # ══════════════════════════════════════════════════════════════════════════
    def setup_tab_erro(self, frame):
        ctk.CTkLabel(frame, text="🎯 Erro em Regime Permanente e Transitório",
                     font=ctk.CTkFont(size=22, weight="bold")
                     ).pack(pady=(20, 5), anchor="w", padx=20)

        tabview = ctk.CTkTabview(frame)
        tabview.pack(expand=True, fill="both", padx=20, pady=5)
        tab_a = tabview.add("Análise Geral")
        tab_d = tabview.add("Dimensionar K")

        # ── Análise Geral ──
        ctk.CTkLabel(tab_a, text="G(s) do sistema em malha aberta:",
                     font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10, pady=(8,2))
        self.e_G_e = ctk.CTkEntry(tab_a, width=650,
                                   placeholder_text="Ex: 10 / (s*(s+1)*(s+5))")
        self.e_G_e.pack(pady=4, anchor="w", padx=10)
        ctk.CTkButton(tab_a, text="Calcular", command=self.calc_e_geral
                      ).pack(anchor="w", padx=10, pady=6)
        self.t_e = ctk.CTkTextbox(tab_a, width=900, height=460,
                                   font=("Courier New", 13), fg_color="#111111")
        self.t_e.pack(pady=8, anchor="w", padx=10)
        self._build_hist_panel(tab_a, "Erro")

        # ── Dimensionar K ──
        ctk.CTkLabel(tab_d, text="G(s) com a variável K (ganho a dimensionar):",
                     font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10, pady=(8,2))
        self.e_G_dim = ctk.CTkEntry(tab_d, width=500,
                                     placeholder_text="Ex: K / (s*(s+4))")
        self.e_G_dim.pack(pady=4, anchor="w", padx=10)

        l_in = ctk.CTkFrame(tab_d, fg_color="transparent")
        l_in.pack(anchor="w", padx=10, pady=6)
        ctk.CTkLabel(l_in, text="Erro alvo (ex: 0.1 ou 10%):").pack(side="left")
        self.e_err_alv = ctk.CTkEntry(l_in, width=120)
        self.e_err_alv.pack(side="left", padx=8)
        ctk.CTkLabel(l_in, text="Tipo de entrada:").pack(side="left", padx=(12, 4))
        self.c_ent = ctk.CTkComboBox(l_in, values=["Degrau", "Rampa", "Parábola"], width=140)
        self.c_ent.pack(side="left")

        ctk.CTkButton(tab_d, text="Dimensionar K", command=self.calc_k_err
                      ).pack(anchor="w", padx=10, pady=12)
        self.t_dim = ctk.CTkTextbox(tab_d, width=900, height=360,
                                     font=("Courier New", 13), fg_color="#111111")
        self.t_dim.pack(pady=8, anchor="w", padx=10)
        self._build_hist_panel(tab_d, "ErroK")

    def calc_e_geral(self):
        try:
            s = sp.Symbol('s')
            G = sp.sympify(self.e_G_e.get().replace('^', '**'))
            Kp = sp.limit(G, s, 0)
            Kv = sp.limit(s * G, s, 0)
            Ka = sp.limit(s**2 * G, s, 0)

            tipo = 0
            den = sp.fraction(sp.cancel(G))[1]
            while sp.limit(den / s**tipo, s, 0) == 0:
                tipo += 1

            def fmt(v):
                if v == sp.oo or v == -sp.oo:
                    return "∞"
                if v == 0:
                    return "0"
                if v.is_number:
                    return str(round(float(v.evalf()), 6))
                return str(sp.simplify(v))

            def ess(val):
                if val == sp.oo or val == -sp.oo:
                    return "0"
                if val == 0:
                    return "∞"
                try:
                    return str(round(float((1/val).evalf()), 6))
                except Exception:
                    return "?"

            res  = f"G(s) = {G}\n"
            res += "─" * 50 + "\n"
            res += f"Tipo do sistema:    {tipo}\n\n"
            res += f"Constantes de erro:\n"
            res += f"  Kp (posição)  = {fmt(Kp)}\n"
            res += f"  Kv (veloc.)   = {fmt(Kv)}\n"
            res += f"  Ka (aceleração)= {fmt(Ka)}\n\n"
            res += "Erro em regime permanente (ess):\n"
            res += f"  Degrau   (1/s):   ess = {'0' if tipo>=1 else str(round(float((1/(1+Kp)).evalf()),6)) if Kp != sp.oo else '0'}\n"
            res += f"  Rampa    (1/s²):  ess = {'∞' if tipo==0 else '0' if tipo>=2 else ess(Kv)}\n"
            res += f"  Parábola (1/s³):  ess = {'∞' if tipo<2 else '0' if tipo>=3 else ess(Ka)}\n"

            # Polos de malha fechada
            T = sp.cancel(G / (1 + G))
            d_f = sp.fraction(T)[1]
            res += "\n" + "─" * 50 + "\n"
            res += "Polos de Malha Fechada (T(s) = G/(1+G)):\n"
            for r, mu in sp.roots(d_f, s).items():
                res += f"  s = {complex(r.evalf()):.4f}  (mult. {mu})\n"

            d_p = sp.Poly(d_f, s)
            if d_p.degree() == 2:
                co = d_p.all_coeffs()
                wn = float(sp.sqrt(co[2] / co[0]).evalf())
                zeta = float((co[1] / (2 * co[0] * wn)))
                wd = wn * np.sqrt(max(1 - zeta**2, 0))
                res += "\n" + "─" * 50 + "\n"
                res += "Parâmetros de 2ª ordem:\n"
                res += f"  ωn = {wn:.4f} rad/s\n"
                res += f"  ζ  = {zeta:.4f}\n"
                if 0 < zeta < 1:
                    Mp = np.exp(-zeta * np.pi / np.sqrt(1 - zeta**2)) * 100
                    tp = np.pi / wd if wd > 0 else float('inf')
                    ts = 4 / (zeta * wn) if zeta * wn > 0 else float('inf')
                    beta = np.arccos(zeta)
                    tr = (np.pi - beta) / wd if wd > 0 else float('inf')
                    res += f"  ωd = {wd:.4f} rad/s\n"
                    res += f"  Mp = {Mp:.2f}%\n"
                    res += f"  tp = {tp:.4f} s\n"
                    res += f"  tr = {tr:.4f} s\n"
                    res += f"  ts(2%) = {ts:.4f} s\n"
                elif zeta >= 1:
                    res += "  Sistema Criticamente Amortecido ou Superamortecido\n"
                else:
                    res += "  Sistema Instável (ζ < 0)\n"

            self.t_e.delete("0.0", "end")
            self.t_e.insert("0.0", res)
            self._push_history("Erro",
                               label=f"G(s) = {self.e_G_e.get()[:65]}",
                               inputs={"G": self.e_G_e.get()},
                               result_preview=res)
        except Exception as e:
            messagebox.showerror("Erro", f"Verifique a expressão.\nDetalhe: {e}")

    def calc_k_err(self):
        try:
            s = sp.Symbol('s')
            G = sp.sympify(self.e_G_dim.get().replace('^', '**'))
            v_G = G.free_symbols
            v_G.discard(s)
            if not v_G:
                messagebox.showerror("Erro", "Não encontrei variável K na expressão.")
                return
            K_v = list(v_G)[0]
            err_txt = self.e_err_alv.get().replace(',', '.')
            e_a = float(err_txt.replace('%', '')) / 100.0 if '%' in err_txt else float(err_txt)
            ent = self.c_ent.get()
            res = f"G(s) = {G}\nErro alvo: {e_a}\nEntrada: {ent}\n\n"
            sol = []

            if ent == "Degrau":
                L = sp.limit(G, s, 0)
                if L in [sp.oo, -sp.oo] or e_a >= 1:
                    res += "Impossível: Sistema ≥ Tipo 1 ou erro ≥ 100%."
                else:
                    c_a = (1.0 / e_a) - 1
                    sol = sp.solve(sp.Eq(L, c_a), K_v)
            elif ent == "Rampa":
                L = sp.limit(s * G, s, 0)
                if L in [sp.oo, -sp.oo, 0]:
                    res += "Impossível: Tipo incompatível com Rampa."
                else:
                    sol = sp.solve(sp.Eq(L, 1.0 / e_a), K_v)
            else:
                L = sp.limit(s**2 * G, s, 0)
                if L in [sp.oo, -sp.oo, 0]:
                    res += "Impossível: Tipo incompatível com Parábola."
                else:
                    sol = sp.solve(sp.Eq(L, 1.0 / e_a), K_v)

            if sol:
                for sv in sol:
                    res += f"K = {sv.evalf(6)}\n"

            self.t_dim.delete("0.0", "end")
            self.t_dim.insert("0.0", res)
            self._push_history("ErroK",
                               label=f"G={self.e_G_dim.get()[:40]}  err={self.e_err_alv.get()}  {self.c_ent.get()}",
                               inputs={"G": self.e_G_dim.get(),
                                       "err": self.e_err_alv.get(),
                                       "ent": self.c_ent.get()},
                               result_preview=res)
        except Exception as e:
            messagebox.showerror("Erro", f"Verifique as entradas.\nDetalhe: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    #  AVALIAÇÃO COMPLEXA
    # ══════════════════════════════════════════════════════════════════════════
    def setup_tab_complexo(self, f):
        ctk.CTkLabel(f, text="📐 Avaliação Complexa de F(s)",
                     font=ctk.CTkFont(size=22, weight="bold")
                     ).pack(pady=20, padx=30, anchor="w")
        ctk.CTkLabel(f, text="Avalie módulo e fase de F(s) em qualquer ponto complexo s = σ + jω",
                     font=ctk.CTkFont(size=13), text_color="gray"
                     ).pack(anchor="w", padx=30)

        grid = ctk.CTkFrame(f, fg_color="transparent")
        grid.pack(padx=30, pady=12, anchor="w")
        ctk.CTkLabel(grid, text="F(s):").grid(row=0, column=0, sticky="w", pady=6)
        self.e_f_comp = ctk.CTkEntry(grid, width=520,
                                      placeholder_text="Ex: (s+2)*(s+4) / (s*(s+3)*(s+6))")
        self.e_f_comp.grid(row=0, column=1, padx=10)
        ctk.CTkLabel(grid, text="Ponto s:").grid(row=1, column=0, sticky="w", pady=6)
        self.e_s_comp = ctk.CTkEntry(grid, width=260,
                                      placeholder_text="Ex: -1 + 3j")
        self.e_s_comp.grid(row=1, column=1, padx=10, sticky="w")

        ctk.CTkButton(f, text="Calcular Módulo e Fase", command=self.calc_complexo
                      ).pack(padx=30, pady=10, anchor="w")
        self.txt_comp = ctk.CTkTextbox(f, width=820, height=340,
                                        font=("Courier New", 14), fg_color="#111111")
        self.txt_comp.pack(padx=30, pady=10, anchor="w")
        self._build_hist_panel(f, "Complexo")

    def calc_complexo(self):
        try:
            s = sp.Symbol('s')
            F = sp.sympify(self.e_f_comp.get().replace('^', '**'))
            s_str = self.e_s_comp.get().replace('j', 'I').replace('i', 'I')
            s_val = sp.sympify(s_str)

            res_math  = F.subs(s, s_val).evalf()
            real_part = float(sp.re(res_math))
            imag_part = float(sp.im(res_math))
            modulo    = float(sp.Abs(res_math))
            fase_deg  = float(np.degrees(float(sp.arg(res_math))))
            sinal     = "+" if imag_part >= 0 else "−"

            saida  = "====== AVALIAÇÃO COMPLEXA ======\n\n"
            saida += f"F(s) avaliada em  s = {s_str.replace('I','j')}\n\n"
            saida += "Resultado Cartesiano:\n"
            saida += f"  Real:    {real_part:.6f}\n"
            saida += f"  Imag:    {imag_part:.6f} j\n"
            saida += f"  Formato: {real_part:.6f} {sinal} {abs(imag_part):.6f}j\n\n"
            saida += "Resultado Polar:\n"
            saida += f"  |F(s)| = {modulo:.6f}\n"
            saida += f"  ∠F(s)  = {fase_deg:.4f}°\n"
            saida += f"  Formato: {modulo:.6f} ∠ {fase_deg:.4f}°\n\n"
            saida += "Critério do Ângulo (LGR):\n"
            saida += f"  ∠F(s) = {fase_deg:.2f}°  "
            diff = abs((fase_deg % 360) - 180)
            saida += "→ ✓ Pertence ao LGR  (∠ = ±180°)" if diff < 1.0 else \
                     f"→ ✗ Não pertence ao LGR  (falta {diff:.2f}° para ±180°)"

            self.txt_comp.delete("0.0", "end")
            self.txt_comp.insert("0.0", saida)
            self._push_history("Complexo",
                               label=f"F={self.e_f_comp.get()[:40]}  s={self.e_s_comp.get()}",
                               inputs={"F": self.e_f_comp.get(), "s": self.e_s_comp.get()},
                               result_preview=saida)
        except Exception as e:
            messagebox.showerror("Erro", f"Expressão inválida.\nDetalhe: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    #  FÓRMULAS ESSENCIAIS
    # ══════════════════════════════════════════════════════════════════════════
    def setup_tab_formulas(self, f):
        ctk.CTkLabel(f, text="📚 Fórmulas de Controle Dinâmico",
                     font=ctk.CTkFont(size=22, weight="bold")
                     ).pack(pady=20, padx=30, anchor="w")
    
        texto = """
 ══════════════════════════════════════════════════════════════════════
  1.  SISTEMAS DE 2ª ORDEM  —  G(s) = ωn² / (s² + 2ζωns + ωn²)
 ══════════════════════════════════════════════════════════════════════

  ωd = ωn·√(1−ζ²)          Frequência natural amortecida
  σ  = ζ·ωn                 Fator de atenuação (abscissa dos polos)
  β  = arccos(ζ)            Ângulo dos polos complexos

  Tempo de subida:   tr = (π − β) / ωd
  Instante de pico:  tp = π / ωd
  Sobressinal:       Mp = exp(−ζπ / √(1−ζ²)) × 100  [%]
  Tempo acomodação:  ts(2%) = 4 / (ζ·ωn)
                     ts(5%) = 3 / (ζ·ωn)

 ══════════════════════════════════════════════════════════════════════
  2.  ERRO EM REGIME PERMANENTE  (sistema unitário, malha fechada)
 ══════════════════════════════════════════════════════════════════════

  Tipo do sistema = nº de integradores puros em G(s) (polos em s=0)

  Constante de posição:    Kp = lim[s→0]  G(s)
  Constante de velocidade: Kv = lim[s→0] s·G(s)
  Constante de aceleração: Ka = lim[s→0] s²·G(s)

  ┌──────────┬────────────────┬────────────────┬────────────────┐
  │ Entrada  │    Tipo 0      │    Tipo 1      │    Tipo 2      │
  ├──────────┼────────────────┼────────────────┼────────────────┤
  │ Degrau   │ 1/(1+Kp)       │     0          │     0          │
  │ Rampa    │    ∞           │ 1/Kv           │     0          │
  │ Parábola │    ∞           │    ∞           │ 1/Ka           │
  └──────────┴────────────────┴────────────────┴────────────────┘

 ══════════════════════════════════════════════════════════════════════
  3.  ÁLGEBRA DE BLOCOS
 ══════════════════════════════════════════════════════════════════════

  T(s) = G(s) / (1 ± G(s)·H(s))

  ✦ (+) no denominador → realimentação NEGATIVA
  ✦ (−) no denominador → realimentação POSITIVA

 ══════════════════════════════════════════════════════════════════════
  4.  LUGAR GEOMÉTRICO DAS RAÍZES (LGR)  —  1 + K·G(s)H(s) = 0
 ══════════════════════════════════════════════════════════════════════

  Regras básicas:
  • n ramos, começam nos polos (K=0) e terminam nos zeros (K→∞)
  • Ramos ao infinito: n − m  (n=polos, m=zeros)
  • Eixo real: pertencem ao LGR se Σ(polos+zeros à direita) for ímpar

  Centroide das assíntotas:
  σa = (Σ Re[polos] − Σ Re[zeros]) / (n − m)

  Ângulos das assíntotas:
  θk = (2k+1)·180° / (n−m)    k = 0, 1, …, (n−m−1)

  Pontos de quebra/encontro:
  K(s) = −D(s)/N(s)    →    dK/ds = 0

  Cruzamento do eixo imaginário (método s = jω):
  Substituir s = jω na eq. característica:
  D(jω) + K·N(jω) = 0
  → Separar parte real e imaginária
  → Resolver Im = 0 para ω, depois Re = 0 para K

  Ângulo de partida de polo complexo p_k:
  θ_partida = Σ∠(p_k − z_i) − Σ∠(p_k − p_j) − 180°
              ↑ soma todos zeros     ↑ soma todos outros polos

  Ângulo de chegada em zero complexo z_k:
  θ_chegada = Σ∠(z_k − p_j) − Σ∠(z_k − z_i) + 180°

 ══════════════════════════════════════════════════════════════════════
  5.  ROUTH-HURWITZ  —  Estabilidade Absoluta
 ══════════════════════════════════════════════════════════════════════

  Para  a_n·sⁿ + a_(n-1)·sⁿ⁻¹ + … + a_1·s + a_0 = 0:

  1. Montar tabela com n+1 linhas (s^n até s^0)
  2. Preencher usando:
       rᵢ,ⱼ = (rᵢ₋₁,₀ · rᵢ₋₂,ⱼ₊₁ − rᵢ₋₂,₀ · rᵢ₋₁,ⱼ₊₁) / rᵢ₋₁,₀
  3. Mudanças de sinal na 1ª coluna = nº de polos no SPD
  4. Sistema estável ↔ todos os elementos da 1ª coluna > 0

  Casos especiais:
  • 1º elemento da linha = 0 → substituir por ε→0⁺
  • Linha inteiramente zero → sistema possui raízes simétricas
    ↳ Derivar o polinômio auxiliar (linha anterior)

 ══════════════════════════════════════════════════════════════════════
  6.  TRANSFORMADA DE LAPLACE  —  Pares Comuns
 ══════════════════════════════════════════════════════════════════════

  δ(t)      ↔  1
  u(t)      ↔  1/s
  t·u(t)    ↔  1/s²
  e^(at)    ↔  1/(s−a)
  sin(ωt)   ↔  ω / (s² + ω²)
  cos(ωt)   ↔  s / (s² + ω²)
  t·e^(at)  ↔  1/(s−a)²

  Teorema do valor final:  lim[t→∞] f(t) = lim[s→0] s·F(s)
  Teorema do valor inicial: lim[t→0⁺] f(t) = lim[s→∞] s·F(s)
"""

        tb = ctk.CTkTextbox(f, width=1000, height=660,
                             font=("Courier New", 13), fg_color="#111111")
        tb.pack(padx=30, pady=10, anchor="w")
        self.isolar_scroll(tb, f)
        tb.insert("0.0", texto)
        tb.configure(state="disabled")


# ─── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
