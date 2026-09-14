import streamlit as st
import sqlite3
import pandas as pd
import altair as alt
from datetime import datetime
import streamlit.components.v1 as components
import os
import shutil


st.set_page_config(page_title="AF Alumínio - Sistema", page_icon="🏢", layout="wide")


conn = sqlite3.connect('banco.db', check_same_thread=False)
c = conn.cursor()

def criar_tabelas():
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT UNIQUE, senha TEXT, perfil TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS produtos (id INTEGER PRIMARY KEY AUTOINCREMENT, categoria TEXT, perfil TEXT, cor TEXT, peso_metro REAL, preco_kg REAL, preco_metro REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, telefone TEXT, endereco TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, data_venda TEXT, cliente TEXT, produto TEXT, quantidade REAL, valor_total REAL, vendedor TEXT)''')
    
    try:
        c.execute("ALTER TABLE produtos ADD COLUMN categoria TEXT DEFAULT 'Perfil'")
        conn.commit()
    except:
        pass
    
    c.execute("SELECT * FROM usuarios WHERE usuario='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO usuarios (usuario, senha, perfil) VALUES ('admin', '123', 'admin')")
        c.execute("INSERT INTO usuarios (usuario, senha, perfil) VALUES ('vendedor', '123', 'vendedor')")
        
    
    c.execute("SELECT COUNT(*) FROM produtos")
    if c.fetchone()[0] == 0:
        estoque_acessorios = {
           "335": 16.00, "510": 55.00, "511": 32.00, "PARAFUSO ALTO BROCANTE 1'": 0.80,
           "038 IGREJINHA": 3.00, "511 A": 10.00, "570 V/V": 26.00, "571 V/A": 18.00,
           "BAGUETE BOX": 5.00, "BATEDOR BOX NOVO": 0.50, "BRAÇO MAX AR 25cm": 13.00,
           "BRAÇO MAX AR 35cm": 17.00, "BRAÇO MAX AR 55cm": 23.00, "BRAÇO TOLDO 1,50M": 90.00,
           "BRAÇO TOLDO 1M": 60.00, "BROCA 11/64": 6.00, "BROCA 9/64": 4.00, "BUCHA 6": 0.15,
           "BUCHA 8": 0.30, "CANOPLA GRADIL": 3.00, "CAVALETE BOX VELHO": 1.00,
           "CAVALETE BOX NOVO": 1.00, "CHAPA ACRÍLICA CRISTAL": 130.00, "CHAPA ACRÍLICA FUME": 110.00,
           "CONTROLE MOTOR": 40.00, "CREMALHEIRA 1,50MT": 55.00, "DOBRADIÇA BOX": 3.00,
           "DOBRADIÇA BÚZIO": 9.00, "DOBRADIÇA PORTA": 5.00, "FECHADURA CORRER BÚZIO": 75.00,
           "FECHADURA DE PORTA CORRER": 50.00, "FECHADURA DE PORTA GIRO": 75.00,
           "FECHADURA PORTA 401": 78.00, "FECHADURA BÚZIO GIRO 1/2": 92.00,
           "FECHADURA BÚZIO COMPLETA": 97.00, "FECHADURA ROLETE BÚZIO": 85.00,
           "FECHADURA ROLETE PORTA": 70.00, "FECHADURA GRADE 701": 60.00, "FECHO AVIÃO CROMADO": 6.00,
           "FECHO AVIÃO NYLON": 5.00, "FECHO CONCHA C/ GATILHO": 15.00, "FECHO MAXIM AR": 11.00,
           "FERROLHO 2'": 8.00, "FERROLHO 3'": 9.00, "FERROLHO 4'": 10.00, "FERROLHO 40CM": 20.00,
           "FERROLHO 20CM": 15.00, "FITA ADESIVA 11X4": 10.00, "FITA ADESIVA 11X6": 12.00,
           "FIXA ESPELHO": 20.00, "GUIA BOX VELHO": 0.25, "GUIA BÚZIO": 5.00, "GUIA BÚZIO NYLON": 5.00,
           "GUIA DE BOX NOVO": 1.00, "GUIA JANELA MB": 0.50, "GUIA JANELA MP": 0.50,
           "GUIA JANELA SUPREMA": 2.00, "H PANORAMICO": 4.00, "H POLICARBONATO": 120.00,
           "JOGO L E CUNHA": 45.00, "L. PARA CONTRA MARCO": 2.00, "L. PARA BOX NYLON": 0.60,
           "L. PARA BOX ALUMÍNIO": 0.60, "L. PERFIL DE TELA": 2.00, "MOTOR": 450.00,
           "ORELHA DE RATO L 25": 7.00, "ORELHA  DE RATO MP": 7.00, "PARAFUSO PONTA LISA": 0.30,
           "POLICARBONATO": 440.00, "PONTALETE 30CM": 25.00, "PONTALETE 60CM": 40.00,
           "PUXADOR BOX SIMPLES": 1.50, "PUXADOR BOX DUPLO": 2.50, "POLIETILENO DE 10'": 17.00,
           "ROLDANA BOX": 1.00, "ROLDANA BÚZIO AÇO": 22.00, "ROLDANA BUZIO NYLON": 18.00,
           "ROLDANA EXCENTRICA": 6.50, "ROLDANA JANELA SUPREMA": 6.00, "ROLDANA PORTA SUPREMA": 12.00,
           "ROLDANA MB": 1.00, "ROLDANA MP": 1.50, "ROLDANA MP C/ ROLAMENTO": 5.50,
           "ROLDANA PORTA MP NYLON": 7.50, "ROLDANA PORTA MP ALUMÍNIO": 7.50, "ROLDANA SIMPLES": 3.00,
           "ROLDANA STANLEY (PAR)": 25.00, "SILICONE INCOLOR": 15.00, "SILICONE BC, PT E BZ": 18.00,
           "SILICONE BRONZE WURTH": 25.00, "SPRAY": 25.00, "SUPORTE PARA CORRIMÃO": 9.00,
           "TAMPA CORRIMÃO BOLEADO": 3.00, "TAMPA CORRIMÃO REDONDO": 5.00, "TRANQUETA MAX AR": 11.00,
           "Z GRADIL": 4.00, "SEREGEL 5X5 ROLO 50 METROS": 35.00
        }

        estoque_borrachas = { "BORRACHA 051": 2.50, "BORRACHA 211": 3.00, "SEREGEL 5X5": 1.00 }
        estoque_rebites = { "REBITE 325": 15.00, "REBITE 412": 13.00, "REBITE 425": 17.00, "RIBITE 312": 9.00, "TAPA FURO": 10.00 }
        estoque_pecas = { "CT 002 L.1/2": 25.00, "CT 008 L.3/4": 35.00, "CT 017 L.1'": 45.00, "VZ 280": 72.00 }

        estoque_perfis = {       
            "MP 357": 3.800/6, "MP 358": 3.600/6, "MP 360": 2.600/6, "MP 300": 2.000/6, "MP 309": 2.100/6,
            "MP 321": 2.800/6, "MP 302": 2.500/6, "BG 202": 0.650/6, "MP 352": 1.100/6, "MP 332": 3.000/6,
            "25 026": 3.900/6, "AL 019": 1.800/6, "JH 072": 7.400/6, "LB 050": 3.100/6, "SU 302": 1.350/6,
            "AL 032": 0.800/6, "BX 157": 3.000/6, "BX 158": 1.000/6, "BX 116": 1.200/6, "BX 156": 1.200/6,
            "BX 159": 1.000/6, "BX 850": 2.200/6, "BX 089": 1.250/6, "BX 085": 1.000/6, "BX 087": 1.000/6,
            "BX 090": 1.000/6, "PC 026": 3.400/6, "AD 001": 3.400/6, "AD 004": 2.800/6, "19 652": 4.100/6,
            "PU 639": 1.700/6, "25 617": 2.000/6, "TG 074": 1.200/6, "TG 004": 2.100/6, "PT 008": 1.000/6,
            "TR 004": 0.600/6, "TR 011": 0.800/6, "TR 038": 1.100/6, "TQ 022": 1.500/6, "TQ 018": 3.300/6,
            "TR 001": 0.300/6, "TR 018": 0.900/6, "JH 073": 2.100/6, "BG 035": 0.700/6, "25 301": 2.05/6,
            "25 312": 1.800/6, "25 311": 1.700/6, "MM 375": 2.350/6, "MM 376": 3.000/6, "NU 990": 3.250/6,
            "P 068": 4.500/6, "CG 083": 7.100/6, "CG 077": 5.100/6, "CG 075": 3.100/6, "CG 074": 1.600/6,
            "25 504": 2.660/6, "25 002": 1.600/6, "25 508": 4.000/6, "BG 001": 0.650/6, "SU 001": 4.000/6,
            "SU 002": 3.700/6, "SU 003": 3.100/6, "SU 055": 3.100/6, "SU 056": 3.300/6, "SU 186": 3.100/6,
            "TQ 005": 1.200/6, "CM 063": 1.000/6, "30 044": 1.500/6, "CG 003": 3.300/6, "RP 610": 4.300/6,
            "AL 001": 2.700/6, "AL 002": 1.300/6, "AL 003": 1.650/6, "AL 027": 0.350/6, "AL 004": 3.300/6,
            "AL 005": 1.600/6, "AL 006": 1.750/6, "AL 007": 0.500/6, "AL 076": 2.200/6, "AL 067": 0.700/6,
            "AL 068": 0.800/6, "CT 026": 4.100/6, "CT 031": 5.200/6, "CT 050": 2.100/6, "CT 019": 2.500/6,
            "BC 002": 0.800/6, "BC 015": 1.000/6, "BC 025": 1.350/6, "LB 012": 3.700/6, "VZ 024": 1.500/6,
            "NPC 006": 4.100/6, "NPC 005": 4.400/6, "NL 008": 1.200/6, "25 001": 1.650/6, "ABERTO PORTA L25": 2.500/6
        }

       
        for nome, preco in estoque_acessorios.items():
            c.execute('INSERT INTO produtos (categoria, perfil, cor, peso_metro, preco_kg, preco_metro) VALUES (?, ?, ?, ?, ?, ?)', ("Acessório", nome, "N/A", 0, 0, preco))
        for nome, preco in estoque_borrachas.items():
            c.execute('INSERT INTO produtos (categoria, perfil, cor, peso_metro, preco_kg, preco_metro) VALUES (?, ?, ?, ?, ?, ?)', ("Acessório", nome, "N/A", 0, 0, preco))
        for nome, preco in estoque_rebites.items():
            c.execute('INSERT INTO produtos (categoria, perfil, cor, peso_metro, preco_kg, preco_metro) VALUES (?, ?, ?, ?, ?, ?)', ("Acessório", nome, "N/A", 0, 0, preco))
        for nome, preco in estoque_pecas.items():
            c.execute('INSERT INTO produtos (categoria, perfil, cor, peso_metro, preco_kg, preco_metro) VALUES (?, ?, ?, ?, ?, ?)', ("Acessório", nome, "N/A", 0, 0, preco))
            
        
        preco_kg_padrao = 35.00  
        for nome, peso_metro in estoque_perfis.items():
            preco_metro = peso_metro * preco_kg_padrao
            c.execute('INSERT INTO produtos (categoria, perfil, cor, peso_metro, preco_kg, preco_metro) VALUES (?, ?, ?, ?, ?, ?)', ("Perfil", nome, "Fosco", peso_metro, preco_kg_padrao, preco_metro))
            
    conn.commit()

criar_tabelas()


if 'logado' not in st.session_state:
    st.session_state['logado'] = False
if 'usuario_atual' not in st.session_state:
    st.session_state['usuario_atual'] = ""
if 'perfil_atual' not in st.session_state:
    st.session_state['perfil_atual'] = ""
if 'carrinho' not in st.session_state:
    st.session_state['carrinho'] = []


if not st.session_state['logado']:
    st.title("🔒 Login - AF Alumínio")
    with st.form("form_login"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        submit_login = st.form_submit_button("Entrar")
        
        if submit_login:
            c.execute("SELECT perfil FROM usuarios WHERE usuario=? AND senha=?", (usuario, senha))
            resultado = c.fetchone()
            if resultado:
                st.session_state['logado'] = True
                st.session_state['usuario_atual'] = usuario
                st.session_state['perfil_atual'] = resultado[0]
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos!")
    st.stop() 


def gerar_html_3_vias(itens, total, cliente_nome, cliente_telefone="", cliente_endereco="", tipo_doc="VENDA"):
    data_hora_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    vendedor_nome = st.session_state['usuario_atual']
    
    linhas_itens = ""
    for item in itens:
        qtd_str = str(item.get('Qtd', ''))[:10]
        nome_cor = f"{item.get('Produto', '')[:12]} {item.get('Cor', '')[:6]}"
        valor = f"R$ {item.get('Valor (R$)', 0):.2f}"
        linhas_itens += f"<tr><td>{qtd_str}</td><td>{nome_cor}</td><td class='right'>{valor}</td></tr>"

    via_html = f"""
    <div class="via">
        <div class="center bold" style="font-size: 16px; margin-bottom: 5px;">AF ALUMÍNIO</div>
        <div class="center">CNPJ: 30.110.561/0001-04<br>
        Estr. da Batalha, 717 - Prazeres<br>
        Jaboatão dos Guararapes - PE<br>
        Tel: (81) 98839-9413</div>
        <div class="line"></div>
        <div class="center bold" style="font-size: 14px;">*** { 'PEDIDO DE VENDA' if tipo_doc == 'VENDA' else 'ORÇAMENTO' } ***</div>
        <div class="center bold">Emissão: {data_hora_atual}</div>
        <div class="center bold" style="font-size: 13px;">Cliente: {cliente_nome}</div>
        <div class="center">
            {'Tel: ' + cliente_telefone + '<br>' if cliente_telefone else ''}
            {'End: ' + cliente_endereco[:40] if cliente_endereco else ''}
        </div>
        <div class="center bold" style="margin-top: 3px;">Vend: {vendedor_nome.upper()}</div>
        <div class="line"></div>
        <table>
            <tr><td class="bold">Qtd</td><td class="bold">Produto</td><td class="bold right">Total</td></tr>
            {linhas_itens}
        </table>
        <div class="line"></div>
        <table>
            <tr><td class="bold" style="font-size:14px;">TOTAL:</td><td class="bold right" style="font-size:14px;">R$ {total:.2f}</td></tr>
        </table>
        <br>
        <div class="center bold">Peso na Balança: _________ kg</div>
        <br><br>
        <div class="center">Separador: ________________</div>
    </div>
    """
    
    html_completo = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @media print {{
            @page {{ margin: 0; }}
            body {{ margin: 0; padding: 0; }}
            .quebra {{ page-break-after: always; }}
            .tela-aviso {{ display: none; }}
        }}
        body {{ font-family: 'Courier New', Courier, monospace; font-size: 12px; width: 280px; margin: 0 auto; color: black; }}
        .center {{ text-align: center; }}
        .bold {{ font-weight: bold; }}
        .line {{ border-bottom: 1px dashed #000; margin: 5px 0; }}
        table {{ width: 100%; font-size: 12px; border-collapse: collapse; }}
        td {{ padding: 2px 0; vertical-align: top; }}
        td.right {{ text-align: right; }}
        .via {{ margin-bottom: 30px; }}
        .tela-aviso {{ background: #e0f7fa; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 10px; cursor: pointer; border: 1px solid #0097a7; }}
    </style>
    </head>
    <body>
        <div class="tela-aviso" onclick="window.print()">🖨️ Clique aqui se a tela de impressão não abriu automaticamente</div>
        {via_html}
        <div class="quebra" style="border-bottom: 2px solid black; margin: 20px 0;"></div>
        {via_html}
        <div class="quebra" style="border-bottom: 2px solid black; margin: 20px 0;"></div>
        {via_html}
        <script>
            window.onload = function() {{
                window.focus();
                window.print();
            }}
        </script>
    </body>
    </html>
    """
    return html_completo


with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
        
    st.write(f"👤 Olá, **{st.session_state['usuario_atual']}**")
    
    opcoes_menu = ["🛒 Orçamentos e Vendas", "👥 Cadastro de Clientes"]
    if st.session_state['perfil_atual'] == 'admin':
        opcoes_menu.extend(["📦 Cadastro de Produtos", "📊 Relatórios"])
        
    menu = st.radio("Navegação", opcoes_menu)
    st.markdown("---")
    
    st.subheader("🛒 Carrinho Atual")
    if not st.session_state["carrinho"]:
        st.info("Carrinho vazio.")
    else:
        total_carrinho = 0
        for i, item in enumerate(st.session_state["carrinho"]):
            st.write(f"{item['Qtd']}x {item['Produto']} ({item['Cor']}) - R$ {item['Valor (R$)']:.2f}")
            total_carrinho += item['Valor (R$)']
        st.markdown(f"**Total: R$ {total_carrinho:.2f}**")
        
        col_b1, col_b2, col_b3 = st.columns([1,1,1])
        with col_b3:
            if st.button("🗑️ Limpar", use_container_width=True): 
                st.session_state["carrinho"] = []
                if 'gerar_pdf_agora' in st.session_state:
                    del st.session_state['gerar_pdf_agora']
                st.rerun()

    st.markdown("---")
    
    if st.session_state['perfil_atual'] == 'admin':
        if st.button("💾 Fazer Backup do Banco"):
            nome_backup = f'banco_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
            shutil.copy2('banco.db', nome_backup)
            st.success(f"Backup salvo como: {nome_backup}")

    if st.button("🚪 Sair"):
        st.session_state['logado'] = False
        st.session_state['usuario_atual'] = ""
        st.session_state['perfil_atual'] = ""
        st.rerun()


if menu == "🛒 Orçamentos e Vendas":
    st.header("Novo Atendimento")
    
    c.execute('SELECT nome, telefone, endereco FROM clientes')
    clientes_db = c.fetchall()
    lista_clientes = ["Consumidor Final"] + [c[0] for c in clientes_db] if clientes_db else ["Consumidor Final"]
    
    cliente_selecionado = st.selectbox("Selecione o Cliente", lista_clientes)
    
    tel_selecionado = end_selecionado = ""
    if cliente_selecionado != "Consumidor Final":
        for cli in clientes_db:
            if cli[0] == cliente_selecionado:
                tel_selecionado, end_selecionado = cli[1], cli[2]
    
    st.markdown("### Adicionar Produtos")
    c.execute('SELECT categoria, perfil, cor, preco_metro FROM produtos ORDER BY categoria, perfil')
    produtos_db = c.fetchall()
    
    if not produtos_db:
        st.warning("Nenhum produto cadastrado!")
    else:
        lista_produtos = [f"[{p[0]}] {p[1]} - {p[2]} (R$ {p[3]:.2f})" for p in produtos_db]
        produto_selecionado = st.selectbox("Produto / Acessório", lista_produtos)
        
        idx = lista_produtos.index(produto_selecionado)
        prod_categoria = produtos_db[idx][0]
        prod_nome = produtos_db[idx][1]
        prod_cor = produtos_db[idx][2]
        preco_unitario = produtos_db[idx][3]
        
        col1, col2 = st.columns(2)
        with col1:
            if prod_categoria == "Acessório":
                quantidade = st.number_input("Quantidade (Unidades)", min_value=1.0, value=1.0, step=1.0)
            else:
                quantidade = st.number_input("Quantidade (Metros)", min_value=0.1, value=1.0, step=0.1)
                
        with col2:
            valor_calculado = quantidade * preco_unitario
            st.info(f"Valor a adicionar: **R$ {valor_calculado:.2f}**")
            
        if st.button("➕ Adicionar ao Carrinho"):
            st.session_state["carrinho"].append({
                "Categoria": prod_categoria,
                "Produto": prod_nome,
                "Cor": prod_cor,
                "Qtd": quantidade,
                "Valor (R$)": valor_calculado
            })
            st.success("Adicionado!")
            st.rerun()

    st.markdown("---")
    
    if st.session_state["carrinho"]:
        st.markdown("### Resumo do Pedido")
        df_carrinho = pd.DataFrame(st.session_state["carrinho"])
        st.dataframe(df_carrinho, use_container_width=True)
        
        col_fim1, col_fim2 = st.columns(2)
        with col_fim1:
            tipo_registro = st.radio("Finalidade:", ["📄 Orçamento Simples", "✅ Venda Definitiva"])
        with col_fim2:
            if st.button("🖨️ Imprimir Pedido (Térmica)", use_container_width=True):
                st.session_state['gerar_pdf_agora'] = tipo_registro
                st.rerun()
        
        if 'gerar_pdf_agora' in st.session_state:
            tipo_registro_selecionado = st.session_state['gerar_pdf_agora']
            
            if tipo_registro_selecionado == "✅ Venda Definitiva":
                tipo_doc_pdf = "VENDA"
                data_atual_bd = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                for item in st.session_state['carrinho']:
                    nome_banco = f"{item['Produto']} ({item['Cor']})"
                    c.execute('INSERT INTO vendas (data_venda, cliente, produto, quantidade, valor_total, vendedor) VALUES (?, ?, ?, ?, ?, ?)', 
                              (data_atual_bd, cliente_selecionado, nome_banco, item['Qtd'], item['Valor (R$)'], st.session_state['usuario_atual']))
                conn.commit()
            else:
                tipo_doc_pdf = "ORCAMENTO"
                
            valor_pedido = sum(item["Valor (R$)"] for item in st.session_state["carrinho"])
            
            html_recibo = gerar_html_3_vias(
                st.session_state['carrinho'], 
                valor_pedido, 
                cliente_selecionado, 
                tel_selecionado, 
                end_selecionado, 
                tipo_doc=tipo_doc_pdf
            )
            
            st.success("✅ Documento gerado e enviado para impressão!")
            components.html(html_recibo, height=450, scrolling=True)
            del st.session_state['gerar_pdf_agora']


elif menu == "📦 Cadastro de Produtos" and st.session_state['perfil_atual'] == 'admin':
    st.header("Cadastro de Materiais")
    
    with st.form("form_produto"):
        categoria = st.radio("Categoria", ["Perfil", "Acessório"])
        
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do Material (Perfil, Roldana, etc)")
            cor = st.selectbox("Cor / Acabamento", ["Branco", "Fosco", "Bronze", "Preto", "Amadeirado", "Brilhante", "N/A"])
        with col2:
            if categoria == "Perfil":
                peso_metro = st.number_input("Peso por Metro (Kg)", min_value=0.00, value=0.00, step=0.01)
                preco_kg = st.number_input("Preço do Kg (R$)", min_value=0.0, value=0.0, step=0.5)
            else:
                preco_unidade = st.number_input("Preço Unitário (R$)", min_value=0.0, value=0.0, step=0.5)
        
        submit = st.form_submit_button("💾 Salvar Material")
        
        if submit:
            if nome:
                if categoria == "Perfil":
                    preco_final = peso_metro * preco_kg
                    c.execute('INSERT INTO produtos (categoria, perfil, cor, peso_metro, preco_kg, preco_metro) VALUES (?, ?, ?, ?, ?, ?)', 
                              (categoria, nome, cor, peso_metro, preco_kg, preco_final))
                else:
                    c.execute('INSERT INTO produtos (categoria, perfil, cor, peso_metro, preco_kg, preco_metro) VALUES (?, ?, ?, ?, ?, ?)', 
                              (categoria, nome, cor, 0, 0, preco_unidade))
                conn.commit()
                st.success(f"{categoria} '{nome}' salvo com sucesso!")
            else:
                st.error("O nome do material é obrigatório.")
                
    st.markdown("### Estoque Cadastrado")
    df_prod = pd.read_sql_query("SELECT * FROM produtos", conn)
    st.dataframe(df_prod, use_container_width=True)

elif menu == "👥 Cadastro de Clientes":
    st.header("Cadastro de Clientes")
    
    with st.form("form_cliente"):
        nome_cli = st.text_input("Nome / Empresa")
        tel_cli = st.text_input("Telefone / WhatsApp")
        end_cli = st.text_input("Endereço Completo")
        
        submit_cli = st.form_submit_button("💾 Salvar Cliente")
        
        if submit_cli:
            if nome_cli:
                c.execute('INSERT INTO clientes (nome, telefone, endereco) VALUES (?, ?, ?)', (nome_cli, tel_cli, end_cli))
                conn.commit()
                st.success(f"Cliente {nome_cli} cadastrado!")
            else:
                st.error("O nome do cliente é obrigatório.")

    st.markdown("### Clientes Cadastrados")
    df_cli = pd.read_sql_query("SELECT * FROM clientes", conn)
    st.dataframe(df_cli, use_container_width=True)

elif menu == "📊 Relatórios" and st.session_state['perfil_atual'] == 'admin':
    st.header("Painel de Vendas")
    
    df_vendas = pd.read_sql_query("SELECT * FROM vendas", conn)
    
    if df_vendas.empty:
        st.info("Nenhuma venda registrada ainda.")
    else:
        faturamento_total = df_vendas['valor_total'].sum()
        st.metric("Faturamento Total", f"R$ {faturamento_total:.2f}")
        
        st.markdown("### Histórico de Vendas")
        st.dataframe(df_vendas, use_container_width=True)
        
        st.markdown("### Vendas por Produto")
        vendas_agrupadas = df_vendas.groupby('produto')['valor_total'].sum().reset_index()
        grafico = alt.Chart(vendas_agrupadas).mark_bar().encode(
            x=alt.X('produto', title='Produto'),
            y=alt.Y('valor_total', title='Total Vendido (R$)'),
            color='produto'
        ).properties(height=400)
        st.altair_chart(grafico, use_container_width=True)