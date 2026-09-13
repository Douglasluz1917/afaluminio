import streamlit as st
import sqlite3
import base64
import urllib.parse
from fpdf import FPDF
from datetime import datetime
import pandas as pd
import os
import altair as alt

st.set_page_config(page_title="AF Alumínio - Sistema", layout="wide", page_icon="🏭")

estoque_acessorios = {
    "335": 16.00, "510": 55.00, "511": 32.00, "PARAFUSO ALTO BROCANTE 1'": 0.80,
    "038 IGREJINHA": 3.00, "511 A": 10.00, "570 V/V": 26.00, "571 V/A": 18.00,
    "BAGUETE BOX": 5.00, "BATEDOR BOX NOVO": 0.50, "BRAÇO MAX AR 25cm": 13.00,
    "BRAÇO MAX AR 35cm": 17.00, "BRAÇO MAX AR 55cm": 23.00, "BRAÇO TOLDO 1,50M": 90.00,
    "BRAÇO TOLDO 1M": 60.00, "BROCA 11/64": 6.00, "BROCA 9/64": 4.00, "BUCHA 6": 0.15,
    "BUCHA 8": 0.30, "CANOPLA GRADIL": 3.00, "CAVALETE BOX VELHO": 1.00, "CAVALETE BOX NOVO": 1.00,
    "CHAPA ACRÍLICA CRISTAL": 130.00, "CHAPA ACRÍLICA FUME": 110.00, "CONTROLE MOTOR": 40.00,
    "CREMALHEIRA 1,50MT": 55.00, "DOBRADIÇA BOX": 3.00, "DOBRADIÇA BÚZIO": 9.00,
    "DOBRADIÇA PORTA": 5.00, "FECHADURA CORRER BÚZIO": 75.00, "FECHADURA DE PORTA CORRER": 50.00,
    "FECHADURA DE PORTA GIRO": 75.00, "FECHADURA PORTA 401": 78.00, "FECHADURA BÚZIO GIRO 1/2": 92.00,
    "FECHADURA BÚZIO COMPLETA": 97.00, "FECHADURA ROLETE BÚZIO": 85.00, "FECHADURA ROLETE PORTA": 70.00,
    "FECHADURA GRADE 701": 60.00, "FECHO AVIÃO CROMADO": 6.00, "FECHO AVIÃO NYLON": 5.00,
    "FECHO CONCHA C/ GATILHO": 15.00, "FECHO MAXIM AR": 11.00, "FERROLHO 2'": 8.00,
    "FERROLHO 3'": 9.00, "FERROLHO 4'": 10.00, "FERROLHO 40CM": 20.00, "FERROLHO 20CM": 15.00,
    "FITA ADESIVA 11X4": 10.00, "FITA ADESIVA 11X6": 12.00, "FIXA ESPELHO": 20.00,
    "GUIA BOX VELHO": 0.25, "GUIA BÚZIO": 5.00, "GUIA BÚZIO NYLON": 5.00, "GUIA DE BOX NOVO": 1.00,
    "GUIA JANELA MB": 0.50, "GUIA JANELA MP": 0.50, "GUIA JANELA SUPREMA": 2.00,
    "H PANORAMICO": 4.00, "H POLICARBONATO": 120.00, "JOGO L E CUNHA": 45.00,
    "L. PARA CONTRA MARCO": 2.00, "L. PARA BOX NYLON": 0.60, "L. PARA BOX ALUMÍNIO": 0.60,
    "L. PERFIL DE TELA": 2.00, "MOTOR": 450.00, "ORELHA DE RATO L 25": 7.00,
    "ORELHA  DE RATO MP": 7.00, "PARAFUSO PONTA LISA": 0.30, "POLICARBONATO": 440.00,
    "PONTALETE 30CM": 25.00, "PONTALETE 60CM": 40.00, "PUXADOR BOX SIMPLES": 1.50,
    "PUXADOR BOX DUPLO": 2.50, "POLIETILENO DE 10'": 17.00, "ROLDANA BOX": 1.00,
    "ROLDANA BÚZIO AÇO": 22.00, "ROLDANA BUZIO NYLON": 18.00, "ROLDANA EXCENTRICA": 6.50,
    "ROLDANA JANELA SUPREMA": 6.00, "ROLDANA PORTA SUPREMA": 12.00, "ROLDANA MB": 1.00,
    "ROLDANA MP": 1.50, "ROLDANA MP C/ ROLAMENTO": 5.50, "ROLDANA PORTA MP NYLON": 7.50,
    "ROLDANA PORTA MP ALUMÍNIO": 7.50, "ROLDANA SIMPLES": 3.00, "ROLDANA STANLEY (PAR)": 25.00,
    "SILICONE INCOLOR": 15.00, "SILICONE BC, PT E BZ": 18.00, "SILICONE BRONZE WURTH": 25.00,
    "SPRAY": 25.00, "SUPORTE PARA CORRIMÃO": 9.00, "TAMPA CORRIMÃO BOLEADO": 3.00,
    "TAMPA CORRIMÃO REDONDO": 5.00, "TRANQUETA MAX AR": 11.00, "Z GRADIL": 4.00,
    "SEREGEL 5X5 ROLO 50 METROS": 35.00
}
estoque_borrachas = {"BORRACHA 051": 2.50, "BORRACHA 211": 3.00, "SEREGEL 5X5": 1.00}
estoque_rebites = {"REBITE 325": 15.00, "REBITE 412": 13.00, "REBITE 425": 17.00, "RIBITE 312": 9.00, "TAPA FURO": 10.00}
estoque_pecas= {"CT 002 L.1/2": 25.00, "CT 008 L.3/4": 35.00, "CT 017 L.1'": 45.00, "VZ 280": 72.00}
estoque_perfis = {       
    "MP 357": 3.800/6, "MP 358": 3.600/6, "MP 360": 2.600/6, "MP 300": 2.000/6,
    "MP 309": 2.100/6, "MP 321": 2.800/6, "MP 302": 2.500/6, "BG 202": 0.650/6, 
    "MP 352": 1.100/6, "MP 332": 3.000/6, "25 026": 3.900/6, "AL 019": 1.800/6,
    "JH 072": 7.400/6, "LB 050": 3.100/6, "SU 302": 1.350/6, "AL 032": 0.800/6,
    "BX 157": 3.000/6, "BX 158": 1.000/6, "BX 116": 1.200/6, "BX 156": 1.200/6,
    "BX 159": 1.000/6, "BX 850": 2.200/6, "BX 089": 1.250/6, "BX 085": 1.000/6,
    "BX 087": 1.000/6, "BX 090": 1.000/6, "PC 026": 3.400/6, "AD 001": 3.400/6,
    "AD 004": 2.800/6, "19 652": 4.100/6, "PU 639": 1.700/6, "25 617": 2.000/6,    
    "TG 074": 1.200/6, "TG 004": 2.100/6, "PT 008": 1.000/6, "TR 004": 0.600/6,
    "TR 011": 0.800/6, "TR 038": 1.100/6, "TQ 022": 1.500/6, "TQ 018": 3.300/6,   
    "TR 001": 0.300/6, "TR 018": 0.900/6, "JH 073": 2.100/6, "BG 035": 0.700/6,   
    "25 301": 2.05/6, "25 312": 1.800/6, "25 311": 1.700/6, "MM 375": 2.350/6,
    "MM 376": 3.000/6, "NU 990": 3.250/6, "P 068": 4.500/6, "CG 083": 7.100/6,
    "CG 077": 5.100/6, "CG 075": 3.100/6, "CG 074": 1.600/6, "25 504": 2.660/6,
    "25 002": 1.600/6, "25 508": 4.000/6, "BG 001": 0.650/6, "SU 001": 4.000/6,
    "SU 002": 3.700/6, "SU 003": 3.100/6, "SU 055": 3.100/6, "SU 056": 3.300/6,
    "SU 186": 3.100/6, "TQ 005": 1.200/6, "CM 063": 1.000/6, "30 044": 1.500/6,
    "CG 003": 3.300/6, "RP 610": 4.300/6, "AL 001": 2.700/6, "AL 002": 1.300/6,
    "AL 003": 1.650/6, "AL 027": 0.350/6, "AL 004": 3.300/6, "AL 005": 1.600/6,
    "AL 006": 1.750/6, "AL 007": 0.500/6, "AL 076": 2.200/6, "AL 067": 0.700/6,
    "AL 068": 0.800/6, "CT 026": 4.100/6, "CT 031": 5.200/6, "CT 050": 2.100/6,
    "CT 019": 2.500/6, "BC 002": 0.800/6, "BC 015": 1.000/6, "BC 025": 1.350/6,
    "LB 012": 3.700/6, "VZ 024": 1.500/6, "NPC 006": 4.100/6, "NPC 005": 4.400/6,
    "NL 008": 1.200/6, "25 001": 1.650/6, "ABERTO PORTA L25": 2.500/6
}


def gerar_pdf_3_vias(itens, total, cliente_nome, cliente_telefone="", cliente_endereco="", tipo_doc="VENDA"):
    altura_por_via = 120 + (len(itens) * 5) 
    pdf = FPDF(orientation='P', unit='mm', format=(80, altura_por_via))
    
    pdf.set_margins(left=3, top=5, right=3)
    pdf.set_auto_page_break(auto=False)
    
    data_hora_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    for indice in range(3):
        pdf.add_page()
        
    
        pdf.set_font("Arial", "B", 12)
        pdf.cell(74, 5, "AF ALUMÍNIO", ln=True, align="C")
            
        pdf.set_font("Arial", "", 8)
        pdf.cell(74, 4, "CNPJ: 30.110.561/0001-04", ln=True, align="C")
        pdf.cell(74, 4, "Estr. da Batalha, 717 - Prazeres", ln=True, align="C")
        pdf.cell(74, 4, "Jaboatão dos Guararapes - PE", ln=True, align="C")
        pdf.cell(74, 4, "Tel: (81) 98839-9413", ln=True, align="C")
        
        pdf.ln(2)
        pdf.set_font("Arial", "B", 10)
        if tipo_doc == "ORCAMENTO": pdf.cell(74, 5, "*** ORÇAMENTO ***", ln=True, align="C")
        else: pdf.cell(74, 5, "*** PEDIDO DE VENDA ***", ln=True, align="C")
            
        pdf.set_font("Arial", "B", 8)
        pdf.cell(74, 5, f"Emissão: {data_hora_atual}", ln=True, align="C")
        pdf.set_font("Arial", "B", 9)
        pdf.cell(74, 5, f"Cliente: {cliente_nome}", ln=True, align="C")
        pdf.set_font("Arial", "", 8)
        
        if cliente_telefone: pdf.cell(74, 4, f"Tel: {cliente_telefone}", ln=True, align="C")
        if cliente_endereco: pdf.cell(74, 4, f"End: {cliente_endereco[:40]}", ln=True, align="C")
            
        pdf.cell(74, 3, "-" * 55, ln=True, align="C")
        pdf.set_font("Arial", "B", 8)
        pdf.cell(16, 5, "Qtd", border=0, align="L")
        pdf.cell(38, 5, "Produto/Cor", border=0, align="L")
        pdf.cell(20, 5, "Total", border=0, align="R")
        pdf.ln(5)
        
        pdf.set_font("Arial", "", 8)
        for item in itens:
            qtd_str = str(item.get('Metros', ''))[:10]
            nome_cor = f"{item.get('Perfil', '')[:12]} {item.get('Cor', '')[:6]}"
            valor = f"R$ {item.get('Valor (R$)', 0):.2f}"
            pdf.cell(16, 4, qtd_str, border=0, align="L")
            pdf.cell(38, 4, nome_cor, border=0, align="L")
            pdf.cell(20, 4, valor, border=0, align="R")
            pdf.ln(4)
            
        pdf.cell(74, 3, "-" * 55, ln=True, align="C")
        pdf.set_font("Arial", "B", 10)
        pdf.cell(37, 6, "TOTAL:", border=0, align="L")
        pdf.cell(37, 6, f"R$ {total:.2f}", border=0, align="R")
        pdf.ln(6)
        
        pdf.set_font("Arial", "B", 9)
        pdf.cell(74, 6, "Peso na Balança: _________ kg", border=0, align="C")
        pdf.ln(10) 
        pdf.set_font("Arial", "", 8)
        pdf.cell(74, 4, "Separador: ________________", border=0, align="C")
            
    return pdf.output(dest="S").encode("latin-1")


conn = sqlite3.connect('banco.db', check_same_thread=False)
c = conn.cursor()

def inicializar_banco():
    c.execute('CREATE TABLE IF NOT EXISTS usuarios (usuario TEXT, senha TEXT)')
    c.execute('SELECT * FROM usuarios')
    if not c.fetchall():
        c.execute('INSERT INTO usuarios (usuario, senha) VALUES (?, ?)', ('admin', '1234'))
        c.execute('INSERT INTO usuarios (usuario, senha) VALUES (?, ?)', ('vendedor', '1234'))
        conn.commit()
        
    c.execute('CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, telefone TEXT, tipo TEXT, endereco TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, data_venda TEXT, cliente TEXT, produto TEXT, quantidade TEXT, valor_total REAL)')
    
    c.execute('CREATE TABLE IF NOT EXISTS configuracoes (chave TEXT PRIMARY KEY, valor REAL)')
    c.execute("SELECT * FROM configuracoes WHERE chave='preco_kg_comum'")
    if not c.fetchone():
        c.execute("INSERT INTO configuracoes (chave, valor) VALUES ('preco_kg_comum', 46.00)")
        c.execute("INSERT INTO configuracoes (chave, valor) VALUES ('preco_kg_especial', 52.00)")
        conn.commit()

    c.execute('CREATE TABLE IF NOT EXISTS produtos_db (id INTEGER PRIMARY KEY AUTOINCREMENT, categoria TEXT, nome TEXT, valor_ref REAL)')
    c.execute("SELECT COUNT(*) FROM produtos_db")
    if c.fetchone()[0] == 0:
        for k, v in estoque_acessorios.items(): c.execute("INSERT INTO produtos_db (categoria, nome, valor_ref) VALUES ('Acessórios (Unidade)', ?, ?)", (k, v))
        for k, v in estoque_borrachas.items(): c.execute("INSERT INTO produtos_db (categoria, nome, valor_ref) VALUES ('Borrachas (Metro)', ?, ?)", (k, v))
        for k, v in estoque_rebites.items(): c.execute("INSERT INTO produtos_db (categoria, nome, valor_ref) VALUES ('Rebites (Cento)', ?, ?)", (k, v))
        for k, v in estoque_pecas.items(): c.execute("INSERT INTO produtos_db (categoria, nome, valor_ref) VALUES ('Produtos por Peça', ?, ?)", (k, v))
        for k, v in estoque_perfis.items(): c.execute("INSERT INTO produtos_db (categoria, nome, valor_ref) VALUES ('Perfis (Por Peso)', ?, ?)", (k, v))
        conn.commit()

inicializar_banco()

def verificar_login(usuario, senha):
    c.execute('SELECT * FROM usuarios WHERE usuario=? AND senha=?', (usuario, senha))
    return c.fetchone() is not None

def obter_preco_kg():
    c.execute("SELECT valor FROM configuracoes WHERE chave='preco_kg_comum'")
    comum = c.fetchone()[0]
    c.execute("SELECT valor FROM configuracoes WHERE chave='preco_kg_especial'")
    especial = c.fetchone()[0]
    return comum, especial

if "carrinho" not in st.session_state: st.session_state["carrinho"] = []
if 'logado' not in st.session_state: st.session_state['logado'] = False; st.session_state['usuario_atual'] = ''


if not st.session_state['logado']:
    st.title("🔒 Acesso Restrito - AF Alumínio")
    usuario_input = st.text_input("Usuário:")
    senha_input = st.text_input("Senha:", type="password")
    if st.button("Entrar"):
        if verificar_login(usuario_input, senha_input):
            st.session_state['logado'] = True
            st.session_state['usuario_atual'] = usuario_input
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos!")

else:
    with st.sidebar:
        st.title(f"👤 {st.session_state['usuario_atual'].upper()}")
        
        opcoes_menu = ["🛒 Orçamentos e Vendas", "👥 Cadastro de Clientes", "⚙️ Minha Conta (Senha)"]
        if st.session_state['usuario_atual'] == 'admin':
            opcoes_menu.append("📊 Relatórios e Dashboard")
            opcoes_menu.append("🛠️ Painel de Controle (Admin)")
            
        menu = st.radio("Navegação:", opcoes_menu)
        
        if menu == "🛒 Orçamentos e Vendas":
            st.divider()
            st.header("🛒 Resumo do Pedido")
            valor_pedido = sum(item.get("Valor (R$)", 0.0) for item in st.session_state["carrinho"])
            st.markdown(f"<h3 style='color: #2e7d32; margin-top: 0;'>Total: R$ {valor_pedido:.2f}</h3>", unsafe_allow_html=True)
            
            if len(st.session_state["carrinho"]) == 0:
                st.info("Nenhum item adicionado.")
            else:
                for i, item in enumerate(st.session_state["carrinho"]):
                    col_info, col_del = st.columns([5, 1])
                    with col_info:
                        st.markdown(f"<div style='font-size: 14px; margin-bottom: -10px;'><b>{item.get('Perfil', '')}</b> ({item.get('Cor', '')})</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-size: 13px; color: gray;'>{item.get('Metros', '')} | <b>R$ {item.get('Valor (R$)', 0.0):.2f}</b></div>", unsafe_allow_html=True)
                    with col_del:
                        if st.button("❌", key=f"del_{i}", help="Remover"):
                            st.session_state["carrinho"].pop(i)
                            st.rerun()
                    st.markdown("<hr style='margin-top: 5px; margin-bottom: 5px; opacity: 0.3;'/>", unsafe_allow_html=True)

                st.write("")
                st.info("Finalidade do documento:")
                tipo_registro = st.radio("", ["📝 Apenas Orçamento", "✅ Venda Definitiva"], label_visibility="collapsed")
                
                cliente_para_zap = st.session_state.get('cliente_selecionado', 'Cliente')
                texto_whatsapp = f"*AF ALUMÍNIO*\nCliente: {cliente_para_zap}\n\n"
                for item in st.session_state["carrinho"]:
                    texto_whatsapp += f"▪️ {item.get('Perfil', '')} ({item.get('Cor', '')}) - {item.get('Metros', '')}\n"
                texto_whatsapp += f"\n*TOTAL: R$ {valor_pedido:.2f}*"
                link_whats = f"https://wa.me/?text={urllib.parse.quote(texto_whatsapp)}"

                col_b1, col_b2, col_b3 = st.columns([1.2, 1, 1])
                with col_b1:
                    if st.button("🖨️ Imprimir", use_container_width=True): st.session_state['gerar_pdf_agora'] = tipo_registro
                with col_b2:
                    st.markdown(f'<a href="{link_whats}" target="_blank" style="display: flex; align-items: center; justify-content: center; background-color: #25D366; color: white; height: 38px; border-radius: 8px; text-decoration: none; font-size:12px;">📱 Whats</a>', unsafe_allow_html=True)
                with col_b3:
                    if st.button("🗑️ Limpar", use_container_width=True): st.session_state["carrinho"] = []; st.rerun()

        st.divider()
        if st.button("Sair (Logout)", use_container_width=True): st.session_state['logado'] = False; st.rerun()

    
    if menu == "🛒 Orçamentos e Vendas":
        col_logo, col_titulo = st.columns([1, 6])
        with col_logo:
           
            if os.path.exists("logo.png"): st.image("logo.png", width=130)
        with col_titulo:
            st.title("Sistema de Orçamentos e Vendas")
            
        st.divider()
        c.execute('SELECT nome, telefone, endereco FROM clientes ORDER BY nome ASC')
        lista_clientes_db = c.fetchall()
        dict_clientes_info = {cliente[0]: {"tel": cliente[1], "end": cliente[2]} for cliente in lista_clientes_db}
        opcoes_clientes = ["Consumidor Final (Sem Cadastro)"] + list(dict_clientes_info.keys())
        
        cliente_selecionado = st.selectbox("👤 Selecione o Cliente para a Nota:", opcoes_clientes)
        st.session_state['cliente_selecionado'] = cliente_selecionado 
        
        tel_selecionado = ""
        end_selecionado = ""
        if cliente_selecionado != "Consumidor Final (Sem Cadastro)":
            tel_selecionado = dict_clientes_info[cliente_selecionado]["tel"]
            end_selecionado = dict_clientes_info[cliente_selecionado]["end"]
            
        st.divider()
        st.subheader("📝 Lançar Produto")
        tipo_venda = st.radio("Categoria:", ["Perfis (Por Peso)", "Produtos por Peça", "Acessórios (Unidade)", "Borrachas (Metro)", "Rebites (Cento)"], horizontal=True)
        
        c.execute("SELECT nome, valor_ref FROM produtos_db WHERE categoria=? ORDER BY nome ASC", (tipo_venda,))
        itens_bd = c.fetchall()
        
        if not itens_bd:
            st.warning(f"Nenhum produto cadastrado na categoria '{tipo_venda}'. Vá ao Painel de Controle para adicionar.")
        else:
            dict_produtos_atuais = {item[0]: item[1] for item in itens_bd}
            
            if tipo_venda == "Perfis (Por Peso)":
                c1, c2, c3 = st.columns(3)
                with c1: perfil = st.selectbox("Escolha o Perfil:", list(dict_produtos_atuais.keys()))
                with c2: cor = st.selectbox("Escolha a Cor:", ["Branco", "Fosco", "Preto", "Bronze"], key="cor_perfil")
                with c3: metros = st.number_input("Metragem (m):", min_value=0.0, step=0.5)
                
                if st.button("Adicionar Perfil", type="primary"):
                    preco_comum, preco_especial = obter_preco_kg()
                    peso_metro = dict_produtos_atuais[perfil] 
                    preco_kg = preco_especial if cor in ["Preto", "Bronze"] else preco_comum
                    peso_total = metros * peso_metro
                    st.session_state["carrinho"].append({"Perfil": perfil, "Cor": cor, "Metros": f"{metros} m", "Peso (kg)": round(peso_total, 3), "Valor (R$)": round(peso_total * preco_kg, 2)})
                    st.rerun()

            elif tipo_venda == "Produtos por Peça":
                c1, c2, c3, c4 = st.columns(4)
                with c1: produto_peca = st.selectbox("Escolha o Produto:", list(dict_produtos_atuais.keys()))
                with c2: cor_peca = st.selectbox("Escolha a Cor:", ["Branco", "Fosco", "Preto", "Bronze"], key="cor_peca")
                with c3: tamanho_corte = st.selectbox("Tamanho (m):", [6, 4, 3, 2])
                with c4: qtd_pecas = st.number_input("Quantidade:", min_value=1, step=1) if tamanho_corte == 6 else 1
                
                if st.button("Adicionar Peça", type="primary"):
                    preco_proporcional = (dict_produtos_atuais[produto_peca] / 6) * tamanho_corte
                    medida = f"{qtd_pecas} br(s) 6m" if tamanho_corte == 6 else f"1 pd. {tamanho_corte}m"
                    st.session_state["carrinho"].append({"Perfil": produto_peca, "Cor": cor_peca, "Metros": medida, "Valor (R$)": round(qtd_pecas * preco_proporcional, 2)})
                    st.rerun()

            elif tipo_venda == "Acessórios (Unidade)":
                c1, c2, c3 = st.columns(3)
                with c1: acessorio = st.selectbox("Escolha o Acessório:", list(dict_produtos_atuais.keys()))
                with c2: cor_acessorio = st.selectbox("Cor:", ["Padrão", "Branco", "Fosco", "Preto", "Bronze"], key="cor_acess")
                with c3: qtd_acessorio = st.number_input("Quantidade (Un):", min_value=1, step=1)
                
                if st.button("Adicionar Acessório", type="primary"):
                    st.session_state["carrinho"].append({"Perfil": acessorio, "Cor": cor_acessorio, "Metros": f"{qtd_acessorio} un", "Valor (R$)": round(qtd_acessorio * dict_produtos_atuais[acessorio], 2)})
                    st.rerun()

            elif tipo_venda == "Borrachas (Metro)":
                c1, c2, c3 = st.columns(3)
                with c1: borracha = st.selectbox("Escolha a Borracha:", list(dict_produtos_atuais.keys()))
                with c2: cor_borracha = st.selectbox("Cor:", ["Preto", "Branco", "Cinza", "Transparente"], key="cor_borracha")
                with c3: metros_borracha = st.number_input("Metros:", min_value=0.5, step=0.5)
                
                if st.button("Adicionar Borracha", type="primary"):
                    st.session_state["carrinho"].append({"Perfil": borracha, "Cor": cor_borracha, "Metros": f"{metros_borracha} m", "Valor (R$)": round(metros_borracha * dict_produtos_atuais[borracha], 2)})
                    st.rerun()

            elif tipo_venda == "Rebites (Cento)":
                c1, c2, c3 = st.columns(3)
                with c1: rebite = st.selectbox("Escolha o Rebite:", list(dict_produtos_atuais.keys()))
                with c2: cor_rebite = st.selectbox("Cor:", ["Padrão", "Preto", "Branco", "Fosco", "Bronze"], key="cor_rebite")
                with c3: qtd_rebites = st.number_input("Qtd (Múltiplos 100):", min_value=100, step=100)
                
                if st.button("Adicionar Rebites", type="primary"):
                    st.session_state["carrinho"].append({"Perfil": rebite, "Cor": cor_rebite, "Metros": f"{qtd_rebites} un", "Valor (R$)": round((qtd_rebites / 100) * dict_produtos_atuais[rebite], 2)})
                    st.rerun()

        if 'gerar_pdf_agora' in st.session_state:
            tipo_registro_selecionado = st.session_state['gerar_pdf_agora']
            if tipo_registro_selecionado == "✅ Venda Definitiva":
                tipo_doc_pdf = "VENDA"
                data_atual_bd = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                for item in st.session_state['carrinho']:
                    nome_banco = f"{item.get('Perfil', '')} ({item.get('Cor', '')})"
                    c.execute('INSERT INTO vendas (data_venda, cliente, produto, quantidade, valor_total) VALUES (?, ?, ?, ?, ?)', 
                              (data_atual_bd, cliente_selecionado, nome_banco, item.get('Metros', ''), item.get('Valor (R$)', 0)))
                conn.commit()
                st.success("✅ Venda Registrada no Sistema! A janela de impressão vai abrir.")
            else:
                tipo_doc_pdf = "ORCAMENTO"
                
                valor_pedido = sum(item.get("Valor (R$)", 0.0) for item in st.session_state["carrinho"])
            pdf_bytes = gerar_pdf_3_vias(st.session_state['carrinho'], valor_pedido, cliente_selecionado, tel_selecionado, end_selecionado, tipo_doc=tipo_doc_pdf)
            
            st.info("👇 O documento foi gerado com sucesso! Clique no botão abaixo para abrir.")
            
            st.download_button(
                label="🖨️ ABRIR PDF PARA IMPRESSÃO",
                data=pdf_bytes,
                file_name="AF_Aluminio_Pedido.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )

    
    elif menu == "👥 Cadastro de Clientes":
        st.title("👥 Banco de Clientes")
        with st.form("form_novo_cliente", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1: nome_cliente = st.text_input("Nome Completo / Empresa *"); telefone_cliente = st.text_input("Telefone (WhatsApp)")
            with col2: tipo_cliente = st.selectbox("Categoria", ["Serralheiro", "Consumidor Final"]); endereco_cliente = st.text_input("Endereço (Opcional)")
            if st.form_submit_button("💾 Salvar Cliente") and nome_cliente != "":
                c.execute('INSERT INTO clientes (nome, telefone, tipo, endereco) VALUES (?, ?, ?, ?)', (nome_cliente, telefone_cliente, tipo_cliente, endereco_cliente)); conn.commit(); st.rerun()
        df_clientes = pd.read_sql_query("SELECT id as ID, nome as Nome, telefone as Telefone, tipo as Categoria FROM clientes", conn)
        if not df_clientes.empty: st.dataframe(df_clientes, hide_index=True, use_container_width=True)

        st.divider()
        st.subheader("🗑️ Remover Cliente")
        c.execute("SELECT id, nome, telefone FROM clientes ORDER BY nome ASC")
        clientes_cadastrados = c.fetchall()
        if clientes_cadastrados:
            with st.form("form_excluir_cliente"):
                dict_clientes_excluir = {f"{cli[1]} - {cli[2]}": cli[0] for cli in clientes_cadastrados}
                cliente_a_excluir = st.selectbox("Selecione o cliente:", list(dict_clientes_excluir.keys()))
                if st.form_submit_button("❌ Excluir Cliente"):
                    c.execute("DELETE FROM clientes WHERE id=?", (dict_clientes_excluir[cliente_a_excluir],))
                    conn.commit()
                    st.success("Cliente removido com sucesso!")
                    st.rerun()

    elif menu == "⚙️ Minha Conta (Senha)":
        st.title("⚙️ Alterar Minha Senha")
        with st.form("form_alterar_senha", clear_on_submit=True):
            nova_senha = st.text_input("Digite a Nova Senha:", type="password")
            confirmar_senha = st.text_input("Confirme a Nova Senha:", type="password")
            if st.form_submit_button("💾 Salvar Nova Senha"):
                if nova_senha != "" and nova_senha == confirmar_senha:
                    c.execute('UPDATE usuarios SET senha=? WHERE usuario=?', (nova_senha, st.session_state['usuario_atual'])); conn.commit(); st.success("✅ Senha alterada!")
                else: st.error("Senhas inválidas ou não conferem!")


    elif menu == "📊 Relatórios e Dashboard":
        st.title("📊 Painel Financeiro e Desempenho")
        df_vendas = pd.read_sql_query("SELECT * FROM vendas", conn)
        
        if not df_vendas.empty:
            df_vendas['Data_Real'] = pd.to_datetime(df_vendas['data_venda'], format="%d/%m/%Y %H:%M:%S")
            df_vendas['Mês/Ano'] = df_vendas['Data_Real'].dt.strftime('%m/%Y')
            
            
            meses_disponiveis = ["Todos os Meses"] + list(df_vendas['Mês/Ano'].sort_values().unique())
            mes_selecionado = st.selectbox("📅 Filtrar Dashboard por Período:", meses_disponiveis)
            
            if mes_selecionado != "Todos os Meses":
                df_filtrado = df_vendas[df_vendas['Mês/Ano'] == mes_selecionado].copy()
                titulo_faturamento = f"💰 Faturamento ({mes_selecionado})"
            else:
                df_filtrado = df_vendas.copy()
                titulo_faturamento = "💰 Faturamento Acumulado (Geral)"

            st.divider()

           
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                faturamento_periodo = df_filtrado['valor_total'].sum()
                st.metric(titulo_faturamento, f"R$ {faturamento_periodo:.2f}")
            with col_m2:
                
                qtd_cupons = df_filtrado.groupby(['data_venda', 'cliente']).ngroups
                st.metric("🛒 Cupons Emitidos", f"{qtd_cupons}")
            
            st.divider()
            
            
            st.subheader("📅 Evolução do Faturamento por Mês")
            df_mes = df_vendas.groupby('Mês/Ano')['valor_total'].sum().reset_index()
            df_mes['Data_Sort'] = pd.to_datetime(df_mes['Mês/Ano'], format='%m/%Y')
            df_mes = df_mes.sort_values(by='Data_Sort')
            st.bar_chart(data=df_mes, x='Mês/Ano', y='valor_total')
            
            st.divider()
            
        
            st.subheader("📈 Produtos Mais Vendidos")
            
            metrica = st.radio("Escolha a métrica de análise:", 
                               ["Faturamento (R$)", "Volume de Vendas (Metros, Peças, Centos)"], horizontal=True)
            
            if df_filtrado.empty:
                st.warning(f"Sem vendas registradas para o período selecionado.")
            else:
                if metrica == "Faturamento (R$)":
                    top_produtos = df_filtrado.groupby('produto')['valor_total'].sum().reset_index().sort_values(by='valor_total', ascending=False).head(15)
                    grafico_barras = alt.Chart(top_produtos).mark_bar().encode(
                        x=alt.X('produto:N', sort='-y', title='Produto / Cor'), 
                        y=alt.Y('valor_total:Q', title='Faturamento (R$)'),
                        color=alt.Color('produto:N', legend=None),
                        tooltip=['produto', 'valor_total']
                    )
                else:
                    df_filtrado['qtd_num'] = df_filtrado['quantidade'].str.extract(r'(\d+\.?\d*)', expand=False).astype(float)
                    df_filtrado.loc[df_filtrado['produto'].str.contains('REBITE', case=False, na=False), 'qtd_num'] /= 100
                    
                    top_produtos = df_filtrado.groupby('produto')['qtd_num'].sum().reset_index().sort_values(by='qtd_num', ascending=False).head(15)
                    
                    grafico_barras = alt.Chart(top_produtos).mark_bar().encode(
                        x=alt.X('produto:N', sort='-y', title='Produto / Cor'), 
                        y=alt.Y('qtd_num:Q', title='Volume Total (Metros, Peças ou Centos)'),
                        color=alt.Color('produto:N', legend=None),
                        tooltip=['produto', 'qtd_num']
                    )
                    
                st.altair_chart(grafico_barras, use_container_width=True)
            
            st.divider()
            
        
            st.subheader("📜 Histórico de Vendas (Cupons Fechados)")
            if not df_filtrado.empty:
                df_filtrado['resumo_item'] = df_filtrado['quantidade'].astype(str) + " de " + df_filtrado['produto']
                df_agrupado = df_filtrado.groupby(['data_venda', 'cliente', 'Data_Real']).agg({
                    'resumo_item': lambda x: '  |  '.join(x),
                    'valor_total': 'sum'
                }).reset_index()
                df_agrupado = df_agrupado.sort_values(by='Data_Real', ascending=False)
                df_agrupado = df_agrupado[['data_venda', 'cliente', 'resumo_item', 'valor_total']]
                df_agrupado.columns = ['Data / Hora', 'Cliente', 'Materiais Vendidos (Resumo do Cupom)', 'Valor Total (R$)']
                
                st.dataframe(df_agrupado, hide_index=True, use_container_width=True)
            
        else:
            st.info("Nenhuma venda definitiva registrada ainda.")

    
    elif menu == "🛠️ Painel de Controle (Admin)":
        st.title("🛠️ Painel de Controle Geral")
        
        
        st.subheader("💾 Backup de Segurança")
    
        
        if os.path.exists("banco.db"):
            with open("banco.db", "rb") as f:
                st.download_button(
                    label="⬇️ Fazer Download do Banco de Dados",
                    data=f.read(),
                    file_name=f"backup_af_aluminio_{datetime.now().strftime('%Y%m%d_%H%M')}.db",
                    mime="application/octet-stream",
                    use_container_width=True
                )
        
        st.divider()
        st.subheader("💰 1. Preço do Alumínio (Kg)")
        preco_comum, preco_especial = obter_preco_kg()
        with st.form("form_preco_kg"):
            c1, c2 = st.columns(2)
            with c1: novo_comum = st.number_input("Preço Kg (Branco e Fosco):", min_value=0.0, value=float(preco_comum), format="%.2f")
            with c2: novo_especial = st.number_input("Preço Kg (Preto e Bronze):", min_value=0.0, value=float(preco_especial), format="%.2f")
            if st.form_submit_button("🔄 Atualizar Preços"):
                c.execute("UPDATE configuracoes SET valor=? WHERE chave='preco_kg_comum'", (novo_comum,))
                c.execute("UPDATE configuracoes SET valor=? WHERE chave='preco_kg_especial'", (novo_especial,))
                conn.commit(); st.success("Preços atualizados!"); st.rerun()

        st.divider()
        st.subheader("📦 2. Gestão de Estoque (Adicionar e Alterar Produtos)")
        cat_edit = st.selectbox("Selecione a Categoria para Gerenciar:", 
                               ["Perfis (Por Peso)", "Produtos por Peça", "Acessórios (Unidade)", "Borrachas (Metro)", "Rebites (Cento)"])
        
        if cat_edit == "Perfis (Por Peso)": label_valor = "Peso por Metro (Ex: 2.000/6 = 0.3333)"
        elif cat_edit == "Produtos por Peça": label_valor = "Preço da Barra de 6m (R$)"
        elif cat_edit == "Rebites (Cento)": label_valor = "Preço do Cento (R$)"
        else: label_valor = "Preço Unitário / Por Metro (R$)"

        with st.form("form_add_prod", clear_on_submit=True):
            st.write(f"**Criar novo item em: {cat_edit}**")
            col1, col2 = st.columns(2)
            with col1: novo_nome_prod = st.text_input("Nome do Produto:").upper()
            with col2: novo_valor_prod = st.number_input(label_valor, min_value=0.0000, format="%.4f", step=0.01)
            
            if st.form_submit_button("➕ Adicionar Produto"):
                if novo_nome_prod:
                    c.execute("INSERT INTO produtos_db (categoria, nome, valor_ref) VALUES (?, ?, ?)", (cat_edit, novo_nome_prod, novo_valor_prod))
                    conn.commit(); st.success(f"'{novo_nome_prod}' adicionado!"); st.rerun()

        st.write("")
        c.execute("SELECT id, nome, valor_ref FROM produtos_db WHERE categoria=? ORDER BY nome ASC", (cat_edit,))
        itens_atuais = c.fetchall()
        
        if itens_atuais:
            dict_edicao = {f"{item[1]}": item for item in itens_atuais}
            item_selecionado = st.selectbox("Selecione um item abaixo para Alterar ou Excluir:", list(dict_edicao.keys()))
            id_item = dict_edicao[item_selecionado][0]
            valor_atual = dict_edicao[item_selecionado][2]

            with st.form("form_edit_prod"):
                col_e1, col_e2 = st.columns(2)
                with col_e1: edit_nome = st.text_input("Nome:", value=item_selecionado)
                with col_e2: edit_valor = st.number_input(label_valor, value=float(valor_atual), min_value=0.0000, format="%.4f", step=0.01)

                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    if st.form_submit_button("🔄 Salvar Alteração"):
                        c.execute("UPDATE produtos_db SET nome=?, valor_ref=? WHERE id=?", (edit_nome.upper(), edit_valor, id_item))
                        conn.commit(); st.success("Atualizado!"); st.rerun()
                with col_b2:
                    if st.form_submit_button("❌ Excluir Produto"):
                        c.execute("DELETE FROM produtos_db WHERE id=?", (id_item,))
                        conn.commit(); st.warning("Excluído!"); st.rerun()

        st.divider()
        st.subheader("👥 3. Gestão de Equipe (Vendedores)")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            with st.form("form_novo_usuario", clear_on_submit=True):
                novo_user = st.text_input("Novo Usuário:").lower().strip()
                nova_senha_user = st.text_input("Senha Inicial:", type="password")
                if st.form_submit_button("➕ Criar Vendedor"):
                    c.execute("SELECT * FROM usuarios WHERE usuario=?", (novo_user,))
                    if c.fetchone(): st.error("Usuário já existe!")
                    elif novo_user and nova_senha_user:
                        c.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (novo_user, nova_senha_user)); conn.commit(); st.success(f"Vendedor '{novo_user}' criado!"); st.rerun()
        with col_f2:
            c.execute("SELECT usuario FROM usuarios WHERE usuario != 'admin'")
            lista_vendedores = [u[0] for u in c.fetchall()]
            if lista_vendedores:
                with st.form("form_excluir_usuario"):
                    user_excluir = st.selectbox("Remover Acesso de:", lista_vendedores)
                    if st.form_submit_button("❌ Remover Vendedor"):
                        c.execute("DELETE FROM usuarios WHERE usuario=?", (user_excluir,)); conn.commit(); st.rerun()