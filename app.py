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
        self.geometry("1200x850")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.cor_fundo_sidebar = "#1A1A1A"
        self.cor_hover_botao = "#2B2B2B"
        self.cor_destaque = "#1F6AA5"

        self.criar_sidebar()
        self.criar_telas()
        self.selecionar_tela("Home")

    def criar_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=self.cor_fundo_sidebar)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1) 
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="⚙️ Amigo de\nTodas as Horas", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 30))
        
        self.btn_home = self.criar_botao_menu("🏠 Início", "Home", 1)
        self.btn_blocos = self.criar_botao_menu("🧩 Álgebra de Blocos", "Blocos", 2)
        self.btn_routh = self.criar_botao_menu("📊 Routh-Hurwitz", "Routh", 3)
        self.btn_degrau = self.criar_botao_menu("📈 Resp. ao Degrau", "Degrau", 4)
        self.btn_laplace = self.criar_botao_menu("∫ Laplace Inversa", "Laplace", 5)
        self.btn_erro = self.criar_botao_menu("🎯 Erro e Transitório", "Erro", 6)
        self.btn_formulas = self.criar_botao_menu("📚 Fórmulas", "Formulas", 7)

    def criar_botao_menu(self, texto, nome_tela, linha):
        btn = ctk.CTkButton(self.sidebar_frame, text=texto, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=self.cor_hover_botao, anchor="w", font=ctk.CTkFont(size=15), command=lambda: self.selecionar_tela(nome_tela))
        btn.grid(row=linha, column=0, padx=10, pady=5, sticky="ew")
        return btn

    def criar_telas(self):
        self.telas = {}
        frame_home = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.telas["Home"] = frame_home
        
        ctk.CTkLabel(frame_home, text="BOA NOITE, VIRGINIA", font=ctk.CTkFont(size=36, weight="bold")).pack(pady=(40, 5), anchor="w", padx=40)
        ctk.CTkLabel(frame_home, text="Bem-vinda de volta. Este programa não foi copiado de ninguém, ok?\nSeu ambiente de controlo de sistemas dinâmicos está pronto.", font=ctk.CTkFont(size=16), text_color="gray", justify="left").pack(pady=(0, 20), anchor="w", padx=40)
        
        frame_cards = ctk.CTkFrame(frame_home, fg_color="transparent")
        frame_cards.pack(fill="both", expand=True, padx=40)
        
        self.criar_card(frame_cards, "🧩 Álgebra de Blocos", "Deduza a FT de Malha Fechada", "Blocos", 0, 0)
        self.criar_card(frame_cards, "📊 Tabela de Routh", "Análise de estabilidade e limites", "Routh", 0, 1)
        self.criar_card(frame_cards, "📈 Resposta ao Degrau", "Gráficos de resposta no tempo", "Degrau", 1, 0)
        self.criar_card(frame_cards, "∫ Laplace Inversa", "Transformada F(s) para f(t)", "Laplace", 1, 1)
        self.criar_card(frame_cards, "🎯 Erro e Transitório", "Cálculo de ess, Tipo e Limites de K", "Erro", 2, 0)
        self.criar_card(frame_cards, "📚 Fórmulas Essenciais", "Consulta rápida de controlo", "Formulas", 2, 1)

        for nome in ["Blocos", "Routh", "Degrau", "Laplace", "Erro", "Formulas"]:
            if nome == "Formulas": self.telas[nome] = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
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
        botoes = {"Home": self.btn_home, "Blocos": self.btn_blocos, "Routh": self.btn_routh, "Degrau": self.btn_degrau, "Laplace": self.btn_laplace, "Erro": self.btn_erro, "Formulas": self.btn_formulas}
        for nome, btn in botoes.items():
            btn.configure(fg_color=self.cor_destaque if nome == nome_tela else "transparent")

    # ==========================================
    # MÓDULO DE ERRO (COM SUB-ABAS)
    # ==========================================
    def setup_tab_erro(self, frame):
        ctk.CTkLabel(frame, text="Erro em Regime Permanente e Transitório", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20,5), anchor="w", padx=20)
        
        # Criação das sub-abas
        tabview = ctk.CTkTabview(frame)
        tabview.pack(expand=True, fill="both", padx=20, pady=5)
        
        tab_analise = tabview.add("Análise Geral")
        tab_dim = tabview.add("Dimensionar K")
        
        # --- SUB-ABA 1: ANÁLISE GERAL ---
        ctk.CTkLabel(tab_analise, text="Insira G(s) numérico de ordem n. Exemplo: (s+2)/(s**2 * (s+10))", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=10, pady=5)
        self.entry_G_erro = ctk.CTkEntry(tab_analise, width=650, placeholder_text="Ex: (s+2)/(s*(s+5))")
        self.entry_G_erro.pack(pady=5, anchor="w", padx=10)
        ctk.CTkButton(tab_analise, text="Calcular Parâmetros", command=self.calcular_erro_geral).pack(anchor="w", padx=10, pady=5)
        self.textbox_erro = ctk.CTkTextbox(tab_analise, width=850, height=450, font=("Courier", 13), fg_color="#1A1A1A")
        self.textbox_erro.pack(pady=10, anchor="w", padx=10)

        # --- SUB-ABA 2: DIMENSIONAR K ---
        ctk.CTkLabel(tab_dim, text="Descubra o valor de K para um Erro Alvo (X%)", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=10, pady=10)
        ctk.CTkLabel(tab_dim, text="1. Insira G(s) com a variável (ex: K / (s*(s+4)))").pack(anchor="w", padx=10)
        self.entry_G_dim = ctk.CTkEntry(tab_dim, width=500, placeholder_text="Ex: K / (s*(s+4))")
        self.entry_G_dim.pack(pady=5, anchor="w", padx=10)
        
        linha_inputs = ctk.CTkFrame(tab_dim, fg_color="transparent")
        linha_inputs.pack(anchor="w", padx=10, pady=5)
        
        ctk.CTkLabel(linha_inputs, text="2. Erro Alvo (X% ou dec):").pack(side="left")
        self.entry_erro_alvo = ctk.CTkEntry(linha_inputs, width=120, placeholder_text="Ex: 10% ou 0.1")
        self.entry_erro_alvo.pack(side="left", padx=10)
        
        ctk.CTkLabel(linha_inputs, text="3. Tipo de Entrada:").pack(side="left", padx=(10,5))
        self.combo_entrada = ctk.CTkComboBox(linha_inputs, values=["Degrau", "Rampa", "Parábola"])
        self.combo_entrada.pack(side="left")
        
        ctk.CTkButton(tab_dim, text="Dimensionar Ganho", command=self.calcular_k_erro).pack(anchor="w", padx=10, pady=15)
        self.textbox_dim = ctk.CTkTextbox(tab_dim, width=850, height=350, font=("Courier", 14), fg_color="#1A1A1A")
        self.textbox_dim.pack(pady=10, anchor="w", padx=10)

    def calcular_erro_geral(self):
        try:
            s = sp.Symbol('s'); G = sp.sympify(self.entry_G_erro.get().replace('^', '**'))
            Kp, Kv, Ka = sp.limit(G, s, 0), sp.limit(s*G, s, 0), sp.limit(s**2*G, s, 0)
            
            num, den = sp.fraction(sp.cancel(G)); tipo = 0
            while sp.limit(den / (s**tipo), s, 0) == 0:
                tipo += 1
                if tipo > 10: break

            def fmt(val): return "∞" if val == sp.oo else ("0" if val == 0 else str(round(float(val.evalf()), 6)) if val.is_number else str(sp.simplify(val)))

            res = f"====== ANÁLISE DE ERRO EM REGIME PERMANENTE ======\nG(s) = {G}\nTIPO DO SISTEMA: {tipo}\n\n"
            res += f"Kp = {fmt(Kp)} | Kv = {fmt(Kv)} | Ka = {fmt(Ka)}\n\n"
            res += "+----------------+--------------+--------------+--------------+\n"
            res += "| Entrada        | Tipo 0       | Tipo 1       | Tipo 2       |\n"
            res += "+----------------+--------------+--------------+--------------+\n"
            res += f"| Degrau (1/s)   | {fmt(1/(1+Kp)) if tipo==0 else '0':<12} | 0            | 0            |\n"
            res += f"| Rampa (1/s²)   | ∞            | {fmt(1/Kv) if tipo==1 else ('∞' if tipo==0 else '0'):<12} | 0            |\n"
            res += f"| Parábola (1/s³)| ∞            | ∞            | {fmt(1/Ka) if tipo==2 else ('∞' if tipo<2 else '0'):<12} |\n"
            res += "+----------------+--------------+--------------+--------------+\n\n"

            T = sp.cancel(G / (1 + G)); num_f, den_f = sp.fraction(T)
            res += f"====== RESPOSTA TRANSITÓRIA ======\nMF T(s) = {T}\nPolos em MF:\n"
            for r, m in sp.roots(den_f, s).items(): res += f"  s = {r.evalf(4)} (mult. {m})\n"
            
            den_p = sp.Poly(den_f, s)
            if den_p.degree() == 2:
                c = den_p.all_coeffs()
                wn = sp.sqrt(c[2]/c[0]).evalf()
                zeta = (c[1]/(2*c[0]*wn)).evalf()
                res += f"\nωn = {wn:.4f} rad/s | ζ = {zeta:.4f}\n"
                if zeta < 1:
                    wd = wn * sp.sqrt(1-zeta**2)
                    res += f"tr = {(np.pi-float(sp.acos(zeta)))/float(wd):.4f}s | tp = {np.pi/float(wd):.4f}s\n"
                    res += f"Mp = {float(sp.exp(-(zeta*np.pi)/sp.sqrt(1-zeta**2))*100):.2f}% | ts(2%) = {4/(float(zeta*wn)):.4f}s\n"
            
            self.textbox_erro.delete("0.0", "end"); self.textbox_erro.insert("0.0", res)
        except: messagebox.showerror("Erro", "Erro ao processar a função simbólica.")

    def calcular_k_erro(self):
        try:
            s = sp.Symbol('s')
            # Extrai e formata a função G(s)
            G_str = self.entry_G_dim.get().strip().replace('^', '**')
            G = sp.sympify(G_str)
            
            vars_in_G = G.free_symbols
            vars_in_G.discard(s)
            if not vars_in_G:
                messagebox.showerror("Erro", "A função precisa conter uma variável (ex: K).")
                return
            K_var = list(vars_in_G)[0]

            # Tratamento da entrada do erro alvo
            erro_str = self.entry_erro_alvo.get().strip().replace(',', '.')
            if not erro_str:
                raise ValueError("Campo de erro vazio")
                
            if '%' in erro_str: ess_alvo = float(erro_str.replace('%', '')) / 100.0
            else: ess_alvo = float(erro_str)

            if ess_alvo <= 0:
                messagebox.showerror("Erro Teórico", "O erro alvo deve ser maior que zero para permitir o cálculo algébrico do ganho.")
                return

            entrada = self.combo_entrada.get()
            res = f"====== DIMENSIONAMENTO DO GANHO {K_var} ======\n"
            res += f"G(s) = {G}\nErro Alvo Requisitado: {ess_alvo*100}% ({ess_alvo}) | Entrada: {entrada}\n\n"

            # ---------------------------------------------------------
            # Análise por Tipo de Entrada (Tratamento de Limites Infinitos)
            # ---------------------------------------------------------
            if entrada == "Degrau":
                K_limite = sp.limit(G, s, 0)
                if K_limite == sp.oo or K_limite == -sp.oo:
                    res += "➔ IMPOSSÍVEL DIMENSIONAR K.\nPara um sistema Tipo 1 ou maior, o erro ao Degrau é SEMPRE ZERO, independente do valor de K.\nEscolha a entrada 'Rampa'."
                    solucao = []
                elif ess_alvo >= 1:
                    res += "Erro! Para um Degrau, o erro (ess = 1/(1+Kp)) não pode ser >= 100% se o sistema for funcional (Kp > 0)."
                    solucao = []
                else:
                    const_alvo = (1.0 / ess_alvo) - 1.0
                    res += f"Cálculo: ess = 1 / (1 + Kp)\nKp alvo necessário = {const_alvo:.4f}\nEquação literal extraída: {K_limite} = {const_alvo:.4f}\n\n"
                    solucao = sp.solve(sp.Eq(K_limite, const_alvo), K_var)
            
            elif entrada == "Rampa":
                K_limite = sp.limit(s * G, s, 0)
                if K_limite == sp.oo or K_limite == -sp.oo:
                    res += "➔ IMPOSSÍVEL DIMENSIONAR K.\nPara um sistema Tipo 2 ou maior, o erro à Rampa é SEMPRE ZERO.\nEscolha a entrada 'Parábola'."
                    solucao = []
                elif K_limite == 0:
                    res += "➔ IMPOSSÍVEL DIMENSIONAR K.\nPara um sistema Tipo 0, o erro à Rampa é SEMPRE INFINITO."
                    solucao = []
                else:
                    const_alvo = 1.0 / ess_alvo
                    res += f"Cálculo: ess = 1 / Kv\nKv alvo necessário = {const_alvo:.4f}\nEquação literal extraída: {K_limite} = {const_alvo:.4f}\n\n"
                    solucao = sp.solve(sp.Eq(K_limite, const_alvo), K_var)
                    
            elif entrada == "Parábola":
                K_limite = sp.limit(s**2 * G, s, 0)
                if K_limite == sp.oo or K_limite == -sp.oo:
                    res += "➔ IMPOSSÍVEL DIMENSIONAR K.\nPara um sistema Tipo 3 ou maior, o erro à Parábola é SEMPRE ZERO."
                    solucao = []
                elif K_limite == 0:
                    res += "➔ IMPOSSÍVEL DIMENSIONAR K.\nPara um sistema Tipo 0 ou 1, o erro à Parábola é SEMPRE INFINITO."
                    solucao = []
                else:
                    const_alvo = 1.0 / ess_alvo
                    res += f"Cálculo: ess = 1 / Ka\nKa alvo necessário = {const_alvo:.4f}\nEquação literal extraída: {K_limite} = {const_alvo:.4f}\n\n"
                    solucao = sp.solve(sp.Eq(K_limite, const_alvo), K_var)

            # ---------------------------------------------------------
            # Exibição do Resultado
            # ---------------------------------------------------------
            if solucao:
                res += f"➔ VALOR ENCONTRADO:\n"
                for sol in solucao: 
                    try:
                        res += f"   {K_var} = {sol.evalf(5)}\n"
                    except:
                        res += f"   {K_var} = {sol}\n"
            elif "IMPOSSÍVEL" not in res and "Erro!" not in res:
                res += "➔ Não existe valor algébrico de K que satisfaça este erro.\n"

            self.textbox_dim.delete("0.0", "end")
            self.textbox_dim.insert("0.0", res)
            
        except Exception as e:
            messagebox.showerror("Erro de Formatação", "Expressão inválida ou erro alvo em formato incorreto. Certifique-se de preencher todos os campos.")

    # ==========================================
    # CÓDIGO DAS OUTRAS ABAS (MANTIDO INTACTO)
    # ==========================================
    def setup_tab_blocos(self, f):
        ctk.CTkLabel(f, text="Álgebra de Blocos", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20, padx=30, anchor="w")
        self.entry_G = ctk.CTkEntry(f, width=500, placeholder_text="G(s)"); self.entry_G.pack(padx=30, pady=5, anchor="w")
        self.entry_H = ctk.CTkEntry(f, width=500); self.entry_H.insert(0, "1"); self.entry_H.pack(padx=30, pady=5, anchor="w")
        self.tipo_realimentacao = ctk.StringVar(value="Negativa")
        frame_radio = ctk.CTkFrame(f, fg_color="transparent"); frame_radio.pack(anchor="w", padx=30, pady=10)
        ctk.CTkRadioButton(frame_radio, text="Negativa (-)", variable=self.tipo_realimentacao, value="Negativa").pack(side="left", padx=10)
        ctk.CTkRadioButton(frame_radio, text="Positiva (+)", variable=self.tipo_realimentacao, value="Positiva").pack(side="left", padx=10)
        ctk.CTkButton(f, text="Calcular MF", command=self.calcular_blocos).pack(padx=30, pady=10, anchor="w")
        self.txt_b = ctk.CTkTextbox(f, width=800, height=150); self.txt_b.pack(padx=30, pady=10, anchor="w")

    def calcular_blocos(self):
        try:
            s = sp.Symbol('s'); G, H = sp.sympify(self.entry_G.get().replace('^','**')), sp.sympify(self.entry_H.get().replace('^','**'))
            sinal = 1 if self.tipo_realimentacao.get() == "Negativa" else -1
            T = sp.cancel(G / (1 + sinal * G * H))
            self.txt_b.delete("0.0", "end"); self.txt_b.insert("0.0", f"T(s) = {T}\n\nDenominador: {sp.fraction(T)[1]} = 0")
        except: messagebox.showerror("Erro", "Erro na função.")

    def setup_tab_routh(self, f):
        ctk.CTkLabel(f, text="Routh-Hurwitz", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20, padx=30, anchor="w")
        self.e_r = ctk.CTkEntry(f, width=500, placeholder_text="Ex: 1 18 77 K"); self.e_r.pack(padx=30, pady=5, anchor="w")
        ctk.CTkButton(f, text="Calcular", command=self.calc_r).pack(padx=30, pady=10, anchor="w")
        self.txt_r = ctk.CTkTextbox(f, width=850, height=400); self.txt_r.pack(padx=30, pady=10, anchor="w")

    def calc_r(self):
        try:
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
            
            p_col = [r[i, 0] for i in range(n)]; v = set(); 
            for x in p_col: v.update(x.free_symbols)
            v.discard(eps)
            if len(v)==0:
                sn = [sp.sign(x.evalf()) for x in p_col if x!=0]
                tr = sum(1 for i in range(1, len(sn)) if sn[i]!=sn[i-1])
                res += f"\n➔ ESTÁVEL" if tr==0 else f"\n➔ INSTÁVEL ({tr} SPD)"
            elif len(v)==1:
                var = list(v)[0]
                res += f"\n➔ CONDIÇÃO GERAL DE ESTABILIDADE:\n   {sp.reduce_inequalities([x > 0 for x in p_col], var)}\n"
            self.txt_r.delete("0.0", "end"); self.txt_r.insert("0.0", res)
        except: messagebox.showerror("Erro", "Erro no polinómio.")

    def setup_tab_degrau(self, f):
        ctk.CTkLabel(f, text="Resposta ao Degrau", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20, padx=30, anchor="w")
        f_in = ctk.CTkFrame(f, fg_color="transparent"); f_in.pack(padx=30, pady=5, anchor="w")
        self.e_num = ctk.CTkEntry(f_in, placeholder_text="Num"); self.e_num.pack(side="left", padx=5)
        self.e_den = ctk.CTkEntry(f_in, placeholder_text="Den"); self.e_den.pack(side="left", padx=5)
        ctk.CTkButton(f_in, text="Plot", command=self.plot).pack(side="left", padx=10)
        self.f_g = ctk.CTkFrame(f, fg_color="#1A1A1A"); self.f_g.pack(expand=True, fill="both", padx=30, pady=10)

    def plot(self):
        try:
            t, y = signal.step(signal.TransferFunction([float(x) for x in self.e_num.get().split()], [float(x) for x in self.e_den.get().split()]))
            for w in self.f_g.winfo_children(): w.destroy()
            fig, ax = plt.subplots(figsize=(6, 4), facecolor='#1A1A1A'); ax.set_facecolor('#1A1A1A')
            ax.plot(t, y, '#1F6AA5'); ax.grid(True, color='#333333'); ax.tick_params(colors='white')
            FigureCanvasTkAgg(fig, master=self.f_g).get_tk_widget().pack(expand=True, fill="both")
        except: messagebox.showerror("Erro", "Use apenas números.")

    def setup_tab_laplace(self, f):
        ctk.CTkLabel(f, text="Transformada Inversa de Laplace", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20, padx=30, anchor="w")
        self.e_l = ctk.CTkEntry(f, width=500); self.e_l.pack(padx=30, pady=5, anchor="w")
        ctk.CTkButton(f, text="Inversa", command=self.inv).pack(padx=30, pady=10, anchor="w")
        self.txt_l = ctk.CTkTextbox(f, width=700, height=200); self.txt_l.pack(padx=30, pady=10, anchor="w")

    def inv(self):
        try:
            s, t = sp.Symbol('s'), sp.Symbol('t', positive=True)
            self.txt_l.delete("0.0", "end")
            self.txt_l.insert("0.0", f"f(t) = {sp.simplify(sp.inverse_laplace_transform(sp.sympify(self.e_l.get().replace('^','**')), s, t))}")
        except: messagebox.showerror("Erro", "Erro em Laplace.")

    def setup_tab_formulas(self, f):
        ctk.CTkLabel(f, text="Fórmulas de Controlo", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20, padx=30, anchor="w")
        t = ctk.CTkTextbox(f, width=800, height=500); t.pack(padx=30, pady=10)
        t.insert("0.0", "[ ERRO ESTACIONÁRIO ]\nTipo 0: ess_degrau = 1/(1+Kp)\nTipo 1: ess_rampa = 1/Kv\nTipo 2: ess_parabola = 1/Ka\n\n[ TRANSITÓRIO ]\ntr: subida | tp: pico | ts: acomodação | Mp: sobressinal")
        t.configure(state="disabled")

if __name__ == "__main__":
    app = App(); app.mainloop()