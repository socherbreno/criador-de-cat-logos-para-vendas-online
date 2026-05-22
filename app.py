import streamlit as st
import pandas as pd
import google.generativeai as genai
import time
import io
import requests

# --- CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(page_title="BRScribe - Login", layout="wide")

# --- ROSTO DA EMPRESA (IDENTIDADE VISUAL) ---
import streamlit as st

import streamlit as st
import base64

# --- CABEÇALHO COM LOGO REDONDA E TÍTULO ---
col1, col2 = st.columns([1, 5])

with col1:
    # Lemos o arquivo logobrscribe.png do seu GitHub e convertemos para exibição em HTML
    with open("logobrscribe.png", "rb") as image_file:
        img_base64 = base64.b64encode(image_file.read()).decode()
    
    # Injetamos um CSS simples que força o corte em formato de círculo perfeito
    html_logo = f"""
    <style>
    .img-redonda {{
        border-radius: 50%;
        width: 100%;
        max-width: 120px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }}
    </style>
    <img src="data:image/png;base64,{img_base64}" class="img-redonda">
    """
    st.markdown(html_logo, unsafe_allow_html=True)

with col2:
    st.title("BRScribe")
    st.markdown("**O Gerador Definitivo de Descrições para E-commerce**")
st.subheader("A sua plataforma de otimização de textos para anúncios")
st.markdown("---")

# --- VALIDADOR DINÂMICO DE SENHAS (GOOGLE SHEETS) ---
LINK_DA_PLANILHA_CSV = "COLE_AQUI_O_LINK_DO_PASSO_3"

try:
    # O código lê a planilha em tempo real direto da nuvem
    df_senhas = pd.read_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vSOikx6faAm1unfbbPQNwJgynAiFdbs3rnYyUtj5BMSjF2yYhfbQFWPV8y9r1Emsj3N8VW3_7aEb-yq/pub?output=csv")
    # Transforma a coluna 'Senha' em uma lista de textos limpos
    SENHAS_VALIDAS = df_senhas['Senha'].astype(str).str.strip().tolist()
except:
    # Caso a internet falhe, mantém uma senha de emergência para você não travar
    SENHAS_VALIDAS = ["BRS_master_2026!"]

senha_digitada = st.text_input("🔑 Digite sua Senha de Acesso para começar:", type="password")

if senha_digitada in SENHAS_VALIDAS:
    st.success("✅ Acesso autorizado à plataforma BRScribe!")
    
    # --- CHAVE DA API ---
    api_key = st.text_input("Insira sua Chave de API do Google:", type="password")

    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        # --- UPLOAD DA PLANILHA ---
        uploaded_file = st.file_uploader("Suba sua planilha (.csv ou .xlsx)", type=["csv", "xlsx"])

        if uploaded_file is not None:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='utf-8-sig')
            else:
                df = pd.read_excel(uploaded_file)
            
            st.write("Visualização dos Dados de Entrada:")
            st.dataframe(df.head())

            if st.button("🚀 Iniciar Otimização em Massa"):
                progress_bar = st.progress(0)
                df['TITULO_SEO'] = ""
                df['DESCRICAO_PERSUASIVA'] = ""
                total = len(df)

                for index, row in df.iterrows():
                    prompt =f"""
        Você é o copywriter número 1 de e-commerce da América Latina, especialista nos algoritmos da Amazon e do Mercado Livre (SEO, ranqueamento e gatilhos mentais). 

        Sua missão é criar uma descrição de produto altamente detalhada, persuasiva e longa, baseada EXCLUSIVAMENTE nos dados técnicos fornecidos pelo usuário. 

        REGRAS DE OURO (OBRIGATÓRIAS):
        1. FIDELIDADE ABSOLUTA: Você está PROIBIDO de inventar recursos, dimensões, materiais ou funcionalidades que não estejam nos dados fornecidos. Baseie toda a argumentação apenas no que for real.
        2. DENSIDADE: A descrição deve ser longa e aprofundada. Explore o benefício por trás de cada característica técnica.
        3. FORMATO: Siga rigorosamente a estrutura abaixo.

        DADOS TÉCNICOS FORNECIDOS PELO CLIENTE:
        {dados_do_cliente}

        ESTRUTURA DE SAÍDA EXIGIDA:

        1. TÍTULO OTIMIZADO (SEO)
        Crie um título chamativo com até 150 caracteres contendo: Produto + Marca + Característica Principal + Modelo.

        2. OS 5 BULLET POINTS (Para Amazon)
        Crie 5 tópicos matadores detalhando os maiores benefícios do produto. Use emojis profissionais. Comece cada tópico com um benefício em CAIXA ALTA, seguido de uma explicação baseada nos dados técnicos.

        3. DESCRIÇÃO DETALHADA E PERSUASIVA (Para Mercado Livre)
        Escreva um texto longo (mínimo de 4 parágrafos) usando técnicas de storytelling e copy. 
        - Parágrafo 1: A fisgada (qual problema o produto resolve?).
        - Parágrafo 2 e 3: O aprofundamento (como ele resolve, citando os materiais e a engenharia da peça).
        - Parágrafo 4: A transformação e chamada para ação (Call to Action).

        4. FICHA TÉCNICA (Resumo Rápido)
        Liste todos os dados técnicos originais em um formato de lista clara para facilitar a leitura dinâmica.
        """
                    try:
                        response = model.generate_content(prompt)
                        txt = response.text
                        if "DESCRIÇÃO:" in txt:
                            partes = txt.split("DESCRIÇÃO:")
                            df.at[index, 'TITULO_SEO'] = partes[0].replace("TÍTULO:", "").strip()
                            df.at[index, 'DESCRICAO_PERSUASIVA'] = partes[1].strip()
                        else:
                            df.at[index, 'TITULO_SEO'] = "Erro no formato"
                        time.sleep(2)
                    except Exception as e:
                        df.at[index, 'TITULO_SEO'] = f"Erro: {e}"
                    
                    progress_bar.progress((index + 1) / total)

                st.success("✅ Processamento finalizado com sucesso!")

                # --- EXPORTAÇÃO FORMATADA ---
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Produtos_Otimizados')
                    
                    workbook  = writer.book
                    worksheet = writer.sheets['Produtos_Otimizados']

                    format_body = workbook.add_format({
                        'text_wrap': True, 
                        'valign': 'top', 
                        'font_name': 'Arial',
                        'font_size': 10,
                        'border': 1,
                        'border_color': '#E0E0E0'
                    })

                    format_header = workbook.add_format({
                        'bold': True, 
                        'bg_color': '#4F81BD', 
                        'font_color': 'white',
                        'border': 1,
                        'valign': 'vcenter',
                        'align': 'center'
                    })

                    for col_num, value in enumerate(df.columns.values):
                        worksheet.write(0, col_num, value, format_header)

                    worksheet.set_column('A:E', 18, format_body) 
                    worksheet.set_column('F:F', 45, format_body) 
                    worksheet.set_column('G:G', 85, format_body)

                st.download_button(
                    label="📥 Baixar Catálogo Otimizado (.xlsx)",
                    data=output.getvalue(),
                    file_name='catalogo_profissional.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

elif senha_digitada != "":
    st.error("❌ Acesso Negado. Caso não tenha uma senha ativa, entre em contato com o nosso suporte.")
# --- RODAPÉ DE SUPORTE ---
st.divider() # Cria uma linha horizontal fina e elegante para separar o conteúdo

# Adiciona o texto centralizado com um link clicável que abre o e-mail do cliente automaticamente
rodape = """
<div style="text-align: center; color: #888888; margin-top: 20px;">
    <p>💬 Precisa de ajuda ou encontrou algum problema?</p>
    <p>Entre em contato com o nosso suporte: <a href="mailto:brsenterprisesof28@gmail.com" style="color: #4CAF50; text-decoration: none; font-weight: bold;">brsenterprisesof28@gmail.com</a></p>
</div>
"""
st.markdown(rodape, unsafe_allow_html=True)
