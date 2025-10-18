import streamlit as st
import pandas as pd

st.set_page_config(page_title='Fanfarras Score', page_icon='🥁', layout='centered')

# Estado de sessão
if 'indice_atual' not in st.session_state:
    st.session_state.indice_atual = 0
if 'mensagem_salvar' not in st.session_state:
    st.session_state.mensagem_salvar = ''
if 'df' not in st.session_state:
    st.session_state.df = None

# Upload CSV
arquivo = st.file_uploader("Carregar arquivo CSV", type=['csv'])
if arquivo:
    if st.session_state.df is None:
        df = pd.read_csv(arquivo)
        if 'index' not in df.columns:
            df.insert(0, 'index', range(len(df)))
        df.set_index('index', inplace=True)
        st.session_state.df = df
    else:
        df = st.session_state.df

    lista_corp = df['corporacao'].tolist()

    # Funções de navegação
    def ir_anterior():
        if st.session_state.indice_atual > 0:
            st.session_state.indice_atual -= 1

    def ir_proxima():
        if st.session_state.indice_atual < len(lista_corp) - 1:
            st.session_state.indice_atual += 1

    # Navegação
    col_anterior, col_atual, col_proxima = st.columns([1, 2, 1])
    with col_anterior:
        st.button('⬅️ Anterior', on_click=ir_anterior)
    with col_atual:
        selecao = st.selectbox(
            'Escolha a corporação:',
            options=lista_corp,
            index=st.session_state.indice_atual,
            key='select_corp',
            label_visibility='collapsed'
        )
        st.session_state.indice_atual = lista_corp.index(selecao)
    with col_proxima:
        st.button('➡️ Próximo', on_click=ir_proxima)

    # Mensagem de salvamento
    if st.session_state.mensagem_salvar:
        st.info(st.session_state.mensagem_salvar)

    # Dados da corporação
    idx = st.session_state.indice_atual
    dados = df.iloc[idx]

    st.markdown(f"#### {dados['corporacao']} - {dados['municipio']}/{dados['uf']} ####")
    st.write(f"###### {dados['modalidade']} - {dados['categoria']} ######")

    # Critérios
    lista_criterios = [
        'nota_uniformidade', 'nota_pelotao', 'nota_corpo_coreografico',
        'nota_mor_baliza', 'nota_staff', 'nota_marcha', 'nota_evolucao',
        'nota_percussao', 'nota_sopro', 'nota_apresentacao', 'nota_execucao'
    ]

    notas = {}
    soma_final = 0
    divisor = len(lista_criterios)

    for criterio in lista_criterios:
        st.divider()
        nome_exibicao = (
            criterio.replace('nota_', '').replace('_', ' ').title()
            .replace('Corpo Coreografico', 'Corpo Coreográfico')
            .replace('Mor Baliza', 'Mor e Balizas')
            .replace('Percussao', 'Percussão')
        )

        with st.container():
            col1, col2, col3 = st.columns([0.85, 0.1, 0.05])

            # Valor atual do DataFrame
            valor_atual = int(dados[criterio]) if pd.notna(dados[criterio]) and str(dados[criterio]).isdigit() else 1

            # Checkbox S/N
            sem_nota = col2.checkbox('S/N', value=False, key=f"{criterio}_sn_{idx}")

            # Slider
            if sem_nota:
                nota = 0
                col1.slider(
                    label=f"{nome_exibicao.upper()}",
                    min_value=1,
                    max_value=5,
                    value=1,
                    key=f"{criterio}_slider_{idx}",
                    disabled=True
                )
            else:
                nota = col1.slider(
                    label=f"{nome_exibicao.upper()}",
                    min_value=1,
                    max_value=5,
                    value=valor_atual,
                    key=f"{criterio}_slider_{idx}"
                )

            if nota == 0:
                divisor -= 1
            soma_final += nota
            col3.markdown(f'### {nota} ###')
            notas[criterio] = nota

    # Observações
    st.divider()
    st.markdown('Observações')
    obs_texto = st.text_area(
        'Observações',
        value=dados['obs'] if 'obs' in df.columns and pd.notna(dados['obs']) else '',
        height=80,
        key=f'obs_{idx}'
    )

    # Nota final
    nota_final = soma_final / divisor if divisor > 0 else 0

    # Botão Atualizar
    col_botao, col_nota_final = st.columns([0.85, 0.15])
    with col_botao:
        if st.button('💾 Atualizar Avaliação'):
            for criterio, nota in notas.items():
                df.at[df.index[idx], criterio] = nota
            df.at[df.index[idx], 'obs'] = obs_texto
            df.at[df.index[idx], 'total'] = round(nota_final, 3)
            st.session_state.mensagem_salvar = "✅ Avaliação atualizada com sucesso!"
            st.success(st.session_state.mensagem_salvar)

    with col_nota_final:
        st.text('Nota Final:')
        st.markdown(f'### {nota_final:.3f} ###')

    st.divider()
    st.download_button(
        label="📥 Baixar CSV atualizado",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name='viii_goianao_atualizado.csv',
        mime='text/csv'
    )

    final = st.expander('Resultado parcial', expanded=False)
    final.write(df)

else:
    st.info("Por favor, carregue um arquivo CSV para começar.")
