import customtkinter as ctk
from tkinter import messagebox
import sympy as sp
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Configuração do Tema Moderno
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Seu Amigo de Todas as Horas")
        self.geometry("1250x900")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.cor_fundo_sidebar = "#1A1A1A"
        self.cor_hover_botao = "#2B2B2B"
        self.cor_destaque = "#1F6AA5"

        self.criar_sidebar()
        self.criar_telas()
        self.selecionar_tela("Home")

    def criar_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=self.cor_fundo_sidebar)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1) 
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="⚙️ Amigo de\nTodas as Horas", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 30))
        
        self.btn_home = self.criar_botao_menu("🏠 Início", "Home", 1)
        self.btn_blocos = self.criar_botao_menu("🧩 Álgebra de Blocos", "Blocos", 2)
        self.btn_routh = self.criar_botao_menu("📊 Routh-Hurwitz", "Routh", 3)
        self.btn_degrau = self.criar_botao_menu("📈 Resp. ao Degrau", "Degrau", 4)
        self.btn_laplace = self.criar_botao_menu("∫ Laplace Inversa", "Laplace", 5)
        self.btn_erro = self.criar_botao_menu("🎯 Erro e Transitório", "Erro", 6)
        self.btn_lgr = self.criar_botao_menu("📍 Lugar das Raízes", "LGR", 7)
        self.btn_complexo = self.criar_botao_menu("📐 Avaliação Complexa", "Complexo", 8)
        self.btn_formulas = self.criar_botao_menu("📚 Fórmulas", "Formulas", 9)

    def criar_botao_menu(self, texto, nome_tela, linha):
        btn = ctk.CTkButton(self.sidebar_frame, text=texto, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=self.cor_hover_botao, anchor="w", font=ctk.CTkFont(size=15), command=lambda: self.selecionar_tela(nome_tela))
        btn.grid(row=linha, column=0, padx=10, pady=5, sticky="ew")
        return btn

    def criar_telas(self):
        self.telas = {}
        frame_home = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        self.telas["Home"] = frame_home
        
        ctk.CTkLabel(frame_home, text="BOA NOITE, VIRGINIA", font=ctk.CTkFont(size=36, weight="bold")).pack(pady=(40, 5), anchor="w", padx=40)
        ctk.CTkLabel(frame_home, text="Bem-vinda de volta ao Seu Amigo de Todas as Horas.\nTodas as ferramentas de controle dinâmico estão prontas e operacionais.", font=ctk.CTkFont(size=16), text_color="gray", justify="left").pack(pady=(0, 20), anchor="w", padx=40)
        
        frame_cards = ctk.CTkFrame(frame_home, fg_color="transparent")
        frame_cards.pack(fill="both", expand=True, padx=40)
        
        self.criar_card(frame_cards, "🧩 Álgebra de Blocos", "Deduza a FT de Malha Fechada", "Blocos", 0, 0)
        self.criar_card(frame_cards, "📊 Tabela de Routh", "Estabilidade e limites de K", "Routh", 0, 1)
        self.criar_card(frame_cards, "📈 Resposta ao Degrau", "Gráficos no tempo", "Degrau", 1, 0)
        self.criar_card(frame_cards, "∫ Laplace Inversa", "F(s) para f(t)", "Laplace", 1, 1)
        self.criar_card(frame_cards, "🎯 Erro e Transitório", "Cálculo de ess, Tipo e Dimensionar K", "Erro", 2, 0)
        self.criar_card(frame_cards, "📍 Lugar das Raízes", "Assíntotas, Centroide, Polos e Zeros", "LGR", 2, 1)
        self.criar_card(frame_cards, "📐 Avaliação Complexa", "F(s) em s=a+bj (Módulo e Fase)", "Complexo", 3, 0)
        self.criar_card(frame_cards, "📚 Fórmulas Essenciais", "Consulta rápida", "Formulas", 3, 1)

        for nome in ["Blocos", "Routh", "Degrau", "Laplace", "Erro", "LGR", "Complexo", "Formulas"]:
            if nome == "Formulas" or nome == "LGR": self.telas[nome] = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
            else: self.telas[nome] = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
            getattr(self, f"setup_tab_{nome.lower()}")(self.telas[nome])

    def criar_card(self, parent, titulo, desc, nome_tela, row, col):
        card = ctk.CTkFrame(parent, height=110, corner_radius=10, fg_color="#242424", border_width=1, border_color="#333333")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        card.grid_propagate(False)
        ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=18, weight="bold"), text_color=self.cor_destaque).pack(pady=(15, 5))
        ctk.CTkLabel(card, text=desc, font=ctk.CTkFont(size=12), text_color="gray").pack()
        ctk.CTkButton(card, text="Abrir", width=100, command=lambda: self.selecionar_tela(nome_tela)).pack(side="bottom", pady=15)
        parent.grid_columnconfigure(0, weight=1); parent.grid_columnconfigure(1, weight=1)

    def selecionar_tela(self, nome_tela):
        for tela in self.telas.values(): tela.grid_forget()
        self.telas[nome_tela].grid(row=0, column=1, sticky="nsew")
        botoes = {"Home": self.btn_home, "Blocos": self.btn_blocos, "Routh": self.btn_routh, "Degrau": self.btn_degrau, "Laplace": self.btn_laplace, "Erro": self.btn_erro, "LGR": self.btn_lgr, "Complexo": self.btn_complexo, "Formulas": self.btn_formulas}
        for nome, btn in botoes.items():
            btn.configure(fg_color=self.cor_destaque if nome == nome_tela else "transparent")

    # ==========================================
    # LUGAR GEOMÉTRICO DAS RAÍZES (LGR) (Falta Homologar!)
    # ==========================================
    def setup_tab_lgr(self, f):
        ctk.CTkLabel(f, text="Análise do Lugar das Raízes (LGR)", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20, padx=30, anchor="w")
        ctk.CTkLabel(f, text="Insira a Função de Malha Aberta G(s)H(s) para extrair os parâmetros analíticos.", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=30)
        self.e_lgr = ctk.CTkEntry(f, width=650, placeholder_text="Ex: K / (s*(s+2)*(s+4))")
        self.e_lgr.pack(padx=30, pady=15, anchor="w")
        ctk.CTkButton(f, text="Extrair Parâmetros LGR", command=self.calc_lgr).pack(padx=30, pady=5, anchor="w")
        self.txt_lgr = ctk.CTkTextbox(f, width=850, height=450, font=("Courier", 14), fg_color="#1A1A1A")
        self.txt_lgr.pack(padx=30, pady=20, anchor="w")

    def calc_lgr(self):
        try:
            s = sp.Symbol('s')
            G_str = self.e_lgr.get().replace('^', '**')
            G = sp.sympify(G_str)
            
            # Remover K para achar raízes
            for var in G.free_symbols:
                if var != s: G = G.subs(var, 1)

            num, den = sp.fraction(sp.cancel(G))
            
            # Raízes
            zeros_dict = sp.roots(num, s)
            polos_dict = sp.roots(den, s)
            
            zeros = []
            for raiz, mult in zeros_dict.items():
                zeros.extend([complex(raiz.evalf())] * mult)
            
            polos = []
            for raiz, mult in polos_dict.items():
                polos.extend([complex(raiz.evalf())] * mult)

            n = len(polos)
            m = len(zeros)

            def fmt_cplx(c):
                if abs(c.imag) < 1e-6: return f"{c.real:.3f}"
                sinal = "+" if c.imag > 0 else "-"
                return f"{c.real:.3f} {sinal} {abs(c.imag):.3f}j"

            res = "====== PARÂMETROS DO LUGAR DAS RAÍZES ======\n\n"
            res += f"Número de Ramos (Polos, n): {n}\n"
            for p in polos: res += f"  ➔ s = {fmt_cplx(p)}\n"
            
            res += f"\nNúmero de Zeros Finitos (m): {m}\n"
            for z in zeros: res += f"  ➔ s = {fmt_cplx(z)}\n"
            if m == 0: res += "  ➔ Nenhum zero finito.\n"

            res += f"\nRamos indo para o infinito (Assíntotas) = n - m = {n - m}\n"

            if n > m:
                # Centroide
                soma_p = sum(p.real for p in polos)
                soma_z = sum(z.real for z in zeros)
                centroide = (soma_p - soma_z) / (n - m)
                res += f"\n➔ CENTROIDE (Interseção das Assíntotas):\n   σa = {centroide:.4f}\n"

                # Ângulos
                res += f"\n➔ ÂNGULOS DAS ASSÍNTOTAS (θa):\n"
                for k in range(n - m):
                    angulo_rad = (2 * k + 1) * np.pi / (n - m)
                    angulo_deg = np.degrees(angulo_rad) % 360
                    res += f"   k={k}: {angulo_deg:.1f}°\n"
            
            # Ponto de quebra aproximado
            K_expr = -den / num
            dK_ds = sp.diff(K_expr, s)
            break_dict = sp.roots(sp.numer(dK_ds), s)
            
            quebras_validas = []
            for pt, mult in break_dict.items():
                if pt.is_real: quebras_validas.append(float(pt.evalf()))
            
            if quebras_validas:
                res += f"\n➔ PONTOS CRÍTICOS / QUEBRA NO EIXO REAL (Avaliando dK/ds = 0):\n"
                for q in set(quebras_validas):
                    res += f"   s ≈ {q:.4f} (Verifique se pertence ao LGR)\n"

            self.txt_lgr.delete("0.0", "end")
            self.txt_lgr.insert("0.0", res)
        except Exception as e:
            messagebox.showerror("Erro", "Expressão inválida. Verifique os parênteses.")

    # ==========================================
    # AVALIAÇÃO COMPLEXA
    # ==========================================
    def setup_tab_complexo(self, f):
        ctk.CTkLabel(f, text="Avaliação Complexa de F(s)", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20, padx=30, anchor="w")
        ctk.CTkLabel(f, text="Avalie o ganho/fase de um sistema num ponto s específico.", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=30)
        
        frame_in = ctk.CTkFrame(f, fg_color="transparent")
        frame_in.pack(padx=30, pady=10, anchor="w", fill="x")
        
        ctk.CTkLabel(frame_in, text="Função F(s):").grid(row=0, column=0, sticky="w", pady=5)
        self.e_f_comp = ctk.CTkEntry(frame_in, width=500, placeholder_text="Ex: (s+2)*(s+4) / (s*(s+3)*(s+6))")
        self.e_f_comp.grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkLabel(frame_in, text="Ponto s (com j):").grid(row=1, column=0, sticky="w", pady=5)
        self.e_s_comp = ctk.CTkEntry(frame_in, width=250, placeholder_text="Ex: -7 + 9j")
        self.e_s_comp.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        ctk.CTkButton(f, text="Calcular Módulo e Fase", command=self.calc_complexo).pack(padx=30, pady=10, anchor="w")
        self.txt_comp = ctk.CTkTextbox(f, width=800, height=300, font=("Courier", 14), fg_color="#1A1A1A")
        self.txt_comp.pack(padx=30, pady=10, anchor="w")

    def calc_complexo(self):
        try:
            s = sp.Symbol('s')
            F_str = self.e_f_comp.get().replace('^', '**')
            F = sp.sympify(F_str)

            s_str = self.e_s_comp.get().replace('j', 'I').replace('i', 'I')
            s_val = sp.sympify(s_str)

            res_math = F.subs(s, s_val).evalf()
            
            real_part = float(sp.re(res_math))
            imag_part = float(sp.im(res_math))
            
            modulo = float(sp.Abs(res_math))
            fase_rad = float(sp.arg(res_math))
            fase_deg = np.degrees(fase_rad)

            sinal = "+" if imag_part >= 0 else "-"

            saida = "====== RESULTADO DA AVALIAÇÃO COMPLEXA ======\n\n"
            saida += f"Avaliando F(s) em s = {s_str.replace('I', 'j')}\n\n"
            
            saida += "➔ COORDENADA CARTESIANA:\n"
            saida += f"   Real: {real_part:.6f}\n"
            saida += f"   Imag: {imag_part:.6f} j\n"
            saida += f"   Formato: {real_part:.6f} {sinal} {abs(imag_part):.6f}j\n\n"
            
            saida += "➔ COORDENADA POLAR:\n"
            saida += f"   Módulo (Magnitude): {modulo:.6f}\n"
            saida += f"   Fase (Ângulo):      {fase_deg:.4f}°\n"
            saida += f"   Formato: {modulo:.6f} ∠ {fase_deg:.4f}°\n"

            self.txt_comp.delete("0.0", "end")
            self.txt_comp.insert("0.0", saida)
        except Exception as e:
            messagebox.showerror("Erro", "Expressão inválida. Use 'j' para imaginário e verifique a função matemática.")

    # ==========================================
    # FUNÇÕES DOS OUTROS MÓDULOS 
    # ==========================================
    # (O código de Erro, Blocos, Routh, Laplace, Degrau, etc )
    
    def setup_tab_erro(self, frame):
        ctk.CTkLabel(frame, text="Erro em Regime Permanente e Transitório", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20,5), anchor="w", padx=20)
        tabview = ctk.CTkTabview(frame)
        tabview.pack(expand=True, fill="both", padx=20, pady=5)
        tab_analise = tabview.add("Análise Geral")
        tab_dim = tabview.add("Dimensionar K")
        ctk.CTkLabel(tab_analise, text="Insira G(s) numérico de ordem n.", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=10, pady=5)
        self.e_G_e = ctk.CTkEntry(tab_analise, width=650); self.e_G_e.pack(pady=5, anchor="w", padx=10)
        ctk.CTkButton(tab_analise, text="Calcular", command=self.calc_e_geral).pack(anchor="w", padx=10, pady=5)
        self.t_e = ctk.CTkTextbox(tab_analise, width=850, height=450); self.t_e.pack(pady=10, anchor="w", padx=10)
        ctk.CTkLabel(tab_dim, text="1. Insira G(s) com a variável K:").pack(anchor="w", padx=10)
        self.e_G_dim = ctk.CTkEntry(tab_dim, width=500); self.e_G_dim.pack(pady=5, anchor="w", padx=10)
        l_in = ctk.CTkFrame(tab_dim, fg_color="transparent"); l_in.pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(l_in, text="2. Erro Alvo:").pack(side="left")
        self.e_err_alv = ctk.CTkEntry(l_in, width=120); self.e_err_alv.pack(side="left", padx=10)
        ctk.CTkLabel(l_in, text="3. Entrada:").pack(side="left", padx=(10,5))
        self.c_ent = ctk.CTkComboBox(l_in, values=["Degrau", "Rampa", "Parábola"]); self.c_ent.pack(side="left")
        ctk.CTkButton(tab_dim, text="Dimensionar", command=self.calc_k_err).pack(anchor="w", padx=10, pady=15)
        self.t_dim = ctk.CTkTextbox(tab_dim, width=850, height=350); self.t_dim.pack(pady=10, anchor="w", padx=10)

    def calc_e_geral(self):
        try:
            s = sp.Symbol('s'); G = sp.sympify(self.e_G_e.get().replace('^', '**'))
            Kp, Kv, Ka = sp.limit(G, s, 0), sp.limit(s*G, s, 0), sp.limit(s**2*G, s, 0)
            tipo = 0; den = sp.fraction(sp.cancel(G))[1]
            while sp.limit(den / (s**tipo), s, 0) == 0: tipo += 1
            def fmt(v): return "∞" if v == sp.oo else ("0" if v == 0 else str(round(float(v.evalf()), 6)) if v.is_number else str(sp.simplify(v)))
            res = f"G(s) = {G}\nTIPO: {tipo}\nKp = {fmt(Kp)} | Kv = {fmt(Kv)} | Ka = {fmt(Ka)}\n"
            res += f"Degrau: {fmt(1/(1+Kp)) if tipo==0 else '0'} | Rampa: {fmt(1/Kv) if tipo==1 else ('∞' if tipo==0 else '0')} | Parábola: {fmt(1/Ka) if tipo==2 else ('∞' if tipo<2 else '0')}\n"
            T = sp.cancel(G / (1 + G)); d_f = sp.fraction(T)[1]
            res += f"\nPolos MF:\n"
            for r, m in sp.roots(d_f, s).items(): res += f"  s = {r.evalf(4)}\n"
            d_p = sp.Poly(d_f, s)
            if d_p.degree() == 2:
                c = d_p.all_coeffs(); wn = sp.sqrt(c[2]/c[0]).evalf(); z = (c[1]/(2*c[0]*wn)).evalf()
                res += f"ωn = {wn:.4f} | ζ = {z:.4f}\n"
            self.t_e.delete("0.0", "end"); self.t_e.insert("0.0", res)
        except: messagebox.showerror("Erro", "Erro ao processar.")

    def calc_k_err(self):
        try:
            s = sp.Symbol('s'); G = sp.sympify(self.e_G_dim.get().replace('^', '**')); v_G = G.free_symbols; v_G.discard(s)
            K_v = list(v_G)[0]; err = self.e_err_alv.get().replace(',','.')
            e_a = float(err.replace('%',''))/100.0 if '%' in err else float(err)
            ent = self.c_ent.get(); res = f"G(s) = {G}\nErro: {e_a}\n"
            if ent == "Degrau":
                L = sp.limit(G, s, 0)
                if L in [sp.oo, -sp.oo] or e_a >= 1: res += "Impossível/Erro: Sistema >= Tipo 1 ou Erro >= 100%."; sol = []
                else: c_a = (1.0/e_a)-1; sol = sp.solve(sp.Eq(L, c_a), K_v)
            elif ent == "Rampa":
                L = sp.limit(s*G, s, 0)
                if L in [sp.oo, -sp.oo, 0]: res += "Impossível: Tipo incompatível com Rampa."; sol = []
                else: sol = sp.solve(sp.Eq(L, 1.0/e_a), K_v)
            else:
                L = sp.limit(s**2*G, s, 0)
                if L in [sp.oo, -sp.oo, 0]: res += "Impossível: Tipo incompatível com Parábola."; sol = []
                else: sol = sp.solve(sp.Eq(L, 1.0/e_a), K_v)
            if sol:
                for sol_v in sol: res += f"K = {sol_v.evalf(5)}\n"
            self.t_dim.delete("0.0", "end"); self.t_dim.insert("0.0", res)
        except: messagebox.showerror("Erro", "Verifique as entradas.")

    def setup_tab_blocos(self, f):
        ctk.CTkLabel(f, text="Álgebra de Blocos", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20, padx=30, anchor="w")
        self.entry_G = ctk.CTkEntry(f, width=500, placeholder_text="G(s)"); self.entry_G.pack(padx=30, pady=5, anchor="w")
        self.entry_H = ctk.CTkEntry(f, width=500); self.entry_H.insert(0, "1"); self.entry_H.pack(padx=30, pady=5, anchor="w")
        self.tipo_realimentacao = ctk.StringVar(value="Negativa")
        fr = ctk.CTkFrame(f, fg_color="transparent"); fr.pack(anchor="w", padx=30, pady=10)
        ctk.CTkRadioButton(fr, text="Negativa (-)", variable=self.tipo_realimentacao, value="Negativa").pack(side="left", padx=10)
        ctk.CTkRadioButton(fr, text="Positiva (+)", variable=self.tipo_realimentacao, value="Positiva").pack(side="left", padx=10)
        ctk.CTkButton(f, text="Calcular MF", command=self.calcular_blocos).pack(padx=30, pady=10, anchor="w")
        self.txt_b = ctk.CTkTextbox(f, width=800, height=150); self.txt_b.pack(padx=30, pady=10, anchor="w")

    def calcular_blocos(self):
        s = sp.Symbol('s'); G, H = sp.sympify(self.entry_G.get().replace('^','**')), sp.sympify(self.entry_H.get().replace('^','**'))
        sin = 1 if self.tipo_realimentacao.get() == "Negativa" else -1
        T = sp.cancel(G / (1 + sin * G * H)); self.txt_b.delete("0.0", "end"); self.txt_b.insert("0.0", f"T(s) = {T}\nDenom: {sp.fraction(T)[1]} = 0")

    def setup_tab_routh(self, f):
        ctk.CTkLabel(f, text="Routh-Hurwitz", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20, padx=30, anchor="w")
        self.e_r = ctk.CTkEntry(f, width=500); self.e_r.pack(padx=30, pady=5, anchor="w")
        ctk.CTkButton(f, text="Calcular", command=self.calc_r).pack(padx=30, pady=10, anchor="w")
        self.txt_r = ctk.CTkTextbox(f, width=850, height=400); self.txt_r.pack(padx=30, pady=10, anchor="w")

    def calc_r(self):
        c = [sp.sympify(x) for x in self.e_r.get().split()]; n = len(c); r = sp.zeros(n, (n+1)//2)
        for i, x in enumerate(c):
            if i%2==0: r[0, i//2]=x
            else: r[1, i//2]=x
        eps = sp.Symbol('ε') 
        for i in range(2, n):
            for j in range(r.shape[1]-1):
                p = r[i-1, 0]; 
                if p==0: p=eps; r[i-1, 0]=p
                r[i, j] = sp.cancel(-(r[i-2, 0]*r[i-1, j+1] - r[i-2, j+1]*p)/p)
        res = "TABELA:\n"; 
        for i in range(n): res += f"s^{n-1-i} | " + "  ".join([str(x) for x in r[i,:]]) + "\n"
        self.txt_r.delete("0.0", "end"); self.txt_r.insert("0.0", res)

    def setup_tab_degrau(self, f):
        ctk.CTkLabel(f, text="Resposta ao Degrau", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20, padx=30, anchor="w")
        f_in = ctk.CTkFrame(f, fg_color="transparent"); f_in.pack(padx=30, pady=5, anchor="w")
        self.e_num = ctk.CTkEntry(f_in, placeholder_text="Num"); self.e_num.pack(side="left", padx=5)
        self.e_den = ctk.CTkEntry(f_in, placeholder_text="Den"); self.e_den.pack(side="left", padx=5)
        ctk.CTkButton(f_in, text="Plot", command=self.plot).pack(side="left", padx=10)
        self.f_g = ctk.CTkFrame(f, fg_color="#1A1A1A"); self.f_g.pack(expand=True, fill="both", padx=30, pady=10)

    def plot(self):
        t, y = signal.step(signal.TransferFunction([float(x) for x in self.e_num.get().split()], [float(x) for x in self.e_den.get().split()]))
        for w in self.f_g.winfo_children(): w.destroy()
        fig, ax = plt.subplots(figsize=(6, 4), facecolor='#1A1A1A'); ax.set_facecolor('#1A1A1A')
        ax.plot(t, y, '#1F6AA5'); ax.grid(True, color='#333333'); ax.tick_params(colors='white')
        FigureCanvasTkAgg(fig, master=self.f_g).get_tk_widget().pack(expand=True, fill="both")

    def setup_tab_laplace(self, f):
        ctk.CTkLabel(f, text="Laplace Inversa", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20, padx=30, anchor="w")
        self.e_l = ctk.CTkEntry(f, width=500); self.e_l.pack(padx=30, pady=5, anchor="w")
        ctk.CTkButton(f, text="Inversa", command=self.inv).pack(padx=30, pady=10, anchor="w")
        self.txt_l = ctk.CTkTextbox(f, width=700, height=200); self.txt_l.pack(padx=30, pady=10, anchor="w")

    def inv(self):
        s, t = sp.Symbol('s'), sp.Symbol('t', positive=True)
        f = sp.inverse_laplace_transform(sp.sympify(self.e_l.get().replace('^','**')), s, t)
        self.txt_l.delete("0.0", "end"); self.txt_l.insert("0.0", f"f(t) = {sp.simplify(f)}")

    def setup_tab_formulas(self, f):
        ctk.CTkLabel(f, text="Fórmulas de Controle Dinâmico", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20, padx=30, anchor="w")
        
        texto_formulas = """
        === GUIA RÁPIDO DE ENGENHARIA DE CONTROLE ===

        [ 1. SISTEMAS DE 2ª ORDEM ]
        Forma Padrão: G(s) = ωn² / (s² + 2ζωns + ωn²)

        • Frequência Natural Amortecida: ωd = ωn * √(1 - ζ²)
        • Fator de Atenuação:            σ = ζ * ωn
        • Tempo de Subida (tr):          tr = (π - β) / ωd   (β = arccos(ζ) em rad)
        • Instante de Pico (tp):         tp = π / ωd
        • Sobressinal Máximo (Mp%):      Mp = exp( -(ζ*π) / √(1 - ζ²) ) * 100
        • Tempo de Acomodação (ts 2%):   ts = 4 / (ζ * ωn)
        • Tempo de Acomodação (ts 5%):   ts = 3 / (ζ * ωn)

        -------------------------------------------------------------------------
        [ 2. ERRO EM REGIME PERMANENTE E TIPO DE SISTEMA ]
        O 'Tipo' é o número de integradores puros (polos na origem, s^n).

        • Constante de Posição:    Kp = lim(s->0) G(s)
        • Constante de Velocidade: Kv = lim(s->0) sG(s)
        • Constante de Aceleração: Ka = lim(s->0) s²G(s)

        Erros Estacionários (ess):
        • Entrada Degrau (1/s):    ess = 1 / (1 + Kp)   (Zero para Tipo >= 1)
        • Entrada Rampa (1/s²):    ess = 1 / Kv         (Zero para Tipo >= 2)
        • Entrada Parábola (1/s³): ess = 1 / Ka         (Zero para Tipo >= 3)

        -------------------------------------------------------------------------
        [ 3. ÁLGEBRA DE BLOCOS ]
        • Função de Malha Fechada T(s) = G(s) / (1 ± G(s)H(s))
          Use sinal (+) no denominador para realimentação NEGATIVA.
          Use sinal (-) no denominador para realimentação POSITIVA.

        -------------------------------------------------------------------------
        [ 4. LUGAR GEOMÉTRICO DAS RAÍZES (LGR) ]
        Seja n = número de polos e m = número de zeros.

        • Ramos no infinito (Assíntotas) = n - m
        • Centroide das Assíntotas (σa):
          σa = ( Σ Polos_reais - Σ Zeros_reais ) / (n - m)

        • Ângulos das Assíntotas (θa):
          θa = [ (2k + 1) * 180° ] / (n - m)    para k = 0, 1, 2... (n-m-1)

        • Pontos de Quebra / Encontro (Breakaway points):
          Encontrados pelas raízes da derivada dK/ds = 0
        """
        
        textbox = ctk.CTkTextbox(f, width=850, height=550, font=("Courier", 14), fg_color="#1A1A1A")
        textbox.pack(padx=30, pady=10, anchor="w")
        textbox.insert("0.0", texto_formulas)
        textbox.configure(state="disabled") # Trava para não ser editável pelo usuário

if __name__ == "__main__":
    app = App(); app.mainloop()
