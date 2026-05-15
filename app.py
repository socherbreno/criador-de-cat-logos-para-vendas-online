import streamlit as st
import pandas as pd
import google.generativeai as genai
import time
import io

# --- CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(page_title="BRScribe - Login", layout="wide")

# --- ROSTO DA EMPRESA (IDENTIDADE VISUAL) ---
st.title("🚀 BRScribe")
st.subheader("A sua plataforma de otimização de textos para anúncios")
st.markdown("---") # Linha divisória para separar a marca do formulário

# --- CADEADO DE SEGURANÇA ---
SENHA_CORRETA = "VENDAS2026" 
senha_digitada = st.text_input("🔑 Digite sua Senha de Acesso para começar:", type="password")

if senha_digitada == SENHA_CORRETA:
    st.success("✅ Bem-vindo ao painel de controle da BRScribe!")
    
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
                    prompt = f"Aja como copywriter. Gere TÍTULO (60 chars) e DESCRIÇÃO (bullet points) para: {row['Produto']}, Marca: {row['Marca/Modelo']}, Material: {row['Material']}. Retorne no formato: TÍTULO: [texto] DESCRIÇÃO: [texto]"
                    
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
