import streamlit as st
import pandas as pd
import google.generativeai as genai
import time
import io

# --- CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(page_title="Gerador de Catálogo Pro", layout="wide")
st.title("⚡ Automação de Cadastros - Versão Design Pro")

# --- CHAVE DA API ---
api_key = st.text_input("Insira sua Chave de API:", type="password")

if api_key:
    genai.configure(api_key=api_key)
    # Usando o modelo atualizado e com os espaços perfeitamente alinhados
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

        if st.button("🚀 Gerar Catálogo com Design"):
            progress_bar = st.progress(0)
            df['TITULO_SEO'] = ""
            df['DESCRICAO_PERSUASIVA'] = ""
            total = len(df)

            for index, row in df.iterrows():
                # Prompt refinado para evitar falhas de formatação
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

            st.success("✅ Geração concluída com sucesso!")

            # --- MÁGICA DA FORMATAÇÃO E DESIGN ---
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Produtos_Otimizados')
                
                workbook  = writer.book
                worksheet = writer.sheets['Produtos_Otimizados']

                # 1. Formato Principal: Quebra de texto + Alinhamento no TOPO
                format_body = workbook.add_format({
                    'text_wrap': True, 
                    'valign': 'top', 
                    'font_name': 'Arial',
                    'font_size': 10,
                    'border': 1,
                    'border_color': '#E0E0E0'
                })

                # 2. Formato do Cabeçalho: Negrito + Cor de Fundo + Centralizado
                format_header = workbook.add_format({
                    'bold': True, 
                    'bg_color': '#4F81BD', 
                    'font_color': 'white',
                    'border': 1,
                    'valign': 'vcenter',
                    'align': 'center'
                })

                # Aplicar cabeçalho manual para garantir o estilo
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, format_header)

                # Aplicar o formato de corpo (Top Align) em todas as colunas
                # Colunas A até E (Originais)
                worksheet.set_column('A:E', 18, format_body) 
                # Coluna F (Título)
                worksheet.set_column('F:F', 45, format_body) 
                # Coluna G (Descrição - Mais larga e com quebra)
                worksheet.set_column('G:G', 85, format_body)

            st.download_button(
                label="📥 Baixar Planilha Profissional",
                data=output.getvalue(),
                file_name='catalogo_pronto_v1.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )