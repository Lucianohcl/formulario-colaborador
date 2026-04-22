
    # --- CHAMADA E EXIBIÇÃO ---

    # 1. Verifica se 't' existe e se é um dicionário antes de tentar o .get()
    t_valida = locals().get('t')

    if isinstance(t_valida, dict):
        # Agora é seguro usar o .get()
        lista_dif = locals().get('t', {}).get('dificuldades', [])
        h_v = locals().get('h_total', 0)

        res_dificuldades = analisar_dificuldades_rigoroso(lista_dif, t_valida, h_v)

        if res_dificuldades:
            st.table(res_dificuldades)
        else:
            st.info("ℹ️ Nenhuma dificuldade encontrada para este colaborador.")
    else:
        # Se 't' não existe ou não é dicionário, mostra o seu alerta amarelo
        st.info("⚠️ ATENÇÃO ACIMA ☝️")


import pandas as pd

def motor_pericia_ultra(tabelas, dificuldades, sugestoes):
    todas_atv = tabelas.get('alta', []) + tabelas.get('normal', []) + tabelas.get('baixa', [])
    contexto_atv = " ".join([a.get('Atividade', '').lower() for a in todas_atv])
    
    analise_detalhada = []

    for sug in sugestoes:
        texto_sug = sug.get('Sugestão', '').lower()
        if texto_sug in ["nenhuma", "nada", "n/a", "", "nenhuma melhoria"]: continue

        freq = sug.get('Frequência', 'D').upper()
        m = int(str(sug.get('Minutos', '0')).replace(' min', '') or 0)
        h = int(str(sug.get('Horas', '0')).replace(' h', '') or 0)
        tempo_min_atual = (h * 60) + m
        
        # --- INTELIGÊNCIA ARTIFICIAL DE CLASSIFICAÇÃO ---
        # Analisa a viabilidade técnica da sugestão
        if any(w in texto_sug for w in ['sistema', 'automação', 'ia', 'integrar', 'digitalizar', 'api', 'robô', 'python']):
            potencial = 0.85  # Tecnologia de ponta reduz drasticamente a carga manual
            categoria = "🤖 TRANSFORMÇÃO DIGITAL"
            cor_status = "🔥 ALTO IMPACTO"
        elif any(w in texto_sug for w in ['padronizar', 'checklist', 'treinamento', 'pop', 'manual', 'procedimento']):
            potencial = 0.45  # Organização de fluxo elimina desperdício
            categoria = "📈 OTIMIZAÇÃO DE PROCESSO"
            cor_status = "✅ ESTRUTURAL"
        else:
            potencial = 0.20  # Melhorias pontuais
            categoria = "💡 MELHORIA INCREMENTAL"
            cor_status = "🟡 OPERACIONAL"

        # --- ENGENHARIA DE VALOR (ROI ANUALIZADO) ---
        # Baseamos em 220 dias úteis/ano para frequência Diária
        mult = {'D': 220, 'S': 48, 'M': 12, 'T': 4, 'A': 1}.get(freq, 1)
        h_ano_atual = (tempo_min_atual * mult) / 60
        h_poupadas = h_ano_atual * potencial
        
        # Valor financeiro (Base R$ 65,00/h técnica - valor de mercado consultoria)
        valor_financeiro = h_poupadas * 65 

        analise_detalhada.append({
            "🎯 ESTRATÉGIA": categoria,
            "💡 SUGESTÃO ANALISADA": sug.get('Sugestão').upper(),
            "⏱️ CARGA ATUAL (ANO)": f"{h_ano_atual:.1f} h",
            "🚀 ECONOMIA PROJETADA": f"− {h_poupadas:.1f} h/ano",
            "💰 VALOR RECUPERÁVEL": f"R$ {valor_financeiro:,.2f}",
            "🔍 PARECER DO PERITO": cor_status
        })
    
    return pd.DataFrame(analise_detalhada)



# --- EXIBIÇÃO NO DASHBOARD (VERSÃO LIMPA E BLINDADA) ---
if st.session_state.get("pagina") == "analise":
    st.markdown("---")

    with st.status("Processando análise pericial...", expanded=True):
        st.header("🔬 Central de Inteligência e Auditoria de Processos")

        t_base = locals().get('t')

        if isinstance(t_base, dict):
            sug_lista = t_base.get('sugestoes', [])
            dif_lista = t_base.get('dificuldades', [])
            
            if sug_lista:
                sug_primeira = str(sug_lista[0].get('Sugestão', '')).lower().strip()
                if sug_primeira in ["nenhuma", "nada", "n/a", ""]:
                    st.error("🚨 ALERTA: Colaborador não sugeriu melhorias.")
                else:
                    st.subheader(f"📊 Business Case: {t_base.get('colaborador', 'Consultor')}")
                    df_analise = motor_pericia_ultra(t_base, dif_lista, sug_lista)
                    
                    if not df_analise.empty:
                        # CÁLCULOS PARA BATER TUDO (REDUZ MARGEM DE ERRO)
                        h_extraidas = df_analise['🚀 ECONOMIA PROJETADA'].str.replace(',', '.').str.extract(r'(\d+\.?\d*)').astype(float)
                        total_h_ano = h_extraidas.sum().iloc[0]
                        total_valor = total_h_ano * 65 
                        
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Capacidade Recuperada", f"{total_h_ano:.1f} h/ano", "GANHO REAL")
                        c2.metric("ROI Operacional Est.", f"R$ {total_valor:,.2f}", "REDUÇÃO CUSTO")
                        c3.metric("Impacto em Dias", f"{total_h_ano/8:.1f} dias", "OFFLOAD")

                        st.info(f"📌 Conclusão: Foram detectadas {len(df_analise)} oportunidades.")
                        st.table(df_analise)
            else:
                st.info("⚠️ Nenhuma sugestão encontrada.")
        else:
            st.info("☝️ Selecione um colaborador.")



    # --- CHAMADA E EXIBIÇÃO ---

    # 1. Verifica se 't' existe e se é um dicionário antes de tentar o .get()
    t_valida = locals().get('t')

    if isinstance(t_valida, dict):
        # Agora é seguro usar o .get()
        lista_dif = locals().get('t', {}).get('dificuldades', [])
        h_v = locals().get('h_total', 0)

        res_dificuldades = analisar_dificuldades_rigoroso(lista_dif, t_valida, h_v)

        if res_dificuldades:
            st.table(res_dificuldades)
        else:
            st.info("ℹ️ Nenhuma dificuldade encontrada para este colaborador.")
    else:
        # Se 't' não existe ou não é dicionário, mostra o seu alerta amarelo
        st.info("⚠️ ATENÇÃO ACIMA ☝️")


import pandas as pd

def motor_pericia_ultra(tabelas, dificuldades, sugestoes):
    todas_atv = tabelas.get('alta', []) + tabelas.get('normal', []) + tabelas.get('baixa', [])
    contexto_atv = " ".join([a.get('Atividade', '').lower() for a in todas_atv])
    
    analise_detalhada = []

    for sug in sugestoes:
        texto_sug = sug.get('Sugestão', '').lower()
        if texto_sug in ["nenhuma", "nada", "n/a", "", "nenhuma melhoria"]: continue

        freq = sug.get('Frequência', 'D').upper()
        m = int(str(sug.get('Minutos', '0')).replace(' min', '') or 0)
        h = int(str(sug.get('Horas', '0')).replace(' h', '') or 0)
        tempo_min_atual = (h * 60) + m
        
        # --- INTELIGÊNCIA ARTIFICIAL DE CLASSIFICAÇÃO ---
        # Analisa a viabilidade técnica da sugestão
        if any(w in texto_sug for w in ['sistema', 'automação', 'ia', 'integrar', 'digitalizar', 'api', 'robô', 'python']):
            potencial = 0.85  # Tecnologia de ponta reduz drasticamente a carga manual
            categoria = "🤖 TRANSFORMÇÃO DIGITAL"
            cor_status = "🔥 ALTO IMPACTO"
        elif any(w in texto_sug for w in ['padronizar', 'checklist', 'treinamento', 'pop', 'manual', 'procedimento']):
            potencial = 0.45  # Organização de fluxo elimina desperdício
            categoria = "📈 OTIMIZAÇÃO DE PROCESSO"
            cor_status = "✅ ESTRUTURAL"
        else:
            potencial = 0.20  # Melhorias pontuais
            categoria = "💡 MELHORIA INCREMENTAL"
            cor_status = "🟡 OPERACIONAL"

        # --- ENGENHARIA DE VALOR (ROI ANUALIZADO) ---
        # Baseamos em 220 dias úteis/ano para frequência Diária
        mult = {'D': 220, 'S': 48, 'M': 12, 'T': 4, 'A': 1}.get(freq, 1)
        h_ano_atual = (tempo_min_atual * mult) / 60
        h_poupadas = h_ano_atual * potencial
        
        # Valor financeiro (Base R$ 65,00/h técnica - valor de mercado consultoria)
        valor_financeiro = h_poupadas * 65 

        analise_detalhada.append({
            "🎯 ESTRATÉGIA": categoria,
            "💡 SUGESTÃO ANALISADA": sug.get('Sugestão').upper(),
            "⏱️ CARGA ATUAL (ANO)": f"{h_ano_atual:.1f} h",
            "🚀 ECONOMIA PROJETADA": f"− {h_poupadas:.1f} h/ano",
            "💰 VALOR RECUPERÁVEL": f"R$ {valor_financeiro:,.2f}",
            "🔍 PARECER DO PERITO": cor_status
        })
    
    return pd.DataFrame(analise_detalhada)



# --- EXIBIÇÃO NO DASHBOARD (VERSÃO LIMPA E BLINDADA) ---
if st.session_state.get("pagina") == "analise":
    st.markdown("---")

    with st.status("Processando análise pericial...", expanded=True):
        st.header("🔬 Central de Inteligência e Auditoria de Processos")

        t_base = locals().get('t')

        if isinstance(t_base, dict):
            sug_lista = t_base.get('sugestoes', [])
            dif_lista = t_base.get('dificuldades', [])
            
            if sug_lista:
                sug_primeira = str(sug_lista[0].get('Sugestão', '')).lower().strip()
                if sug_primeira in ["nenhuma", "nada", "n/a", ""]:
                    st.error("🚨 ALERTA: Colaborador não sugeriu melhorias.")
                else:
                    st.subheader(f"📊 Business Case: {t_base.get('colaborador', 'Consultor')}")
                    df_analise = motor_pericia_ultra(t_base, dif_lista, sug_lista)
                    
                    if not df_analise.empty:
                        # CÁLCULOS PARA BATER TUDO (REDUZ MARGEM DE ERRO)
                        h_extraidas = df_analise['🚀 ECONOMIA PROJETADA'].str.replace(',', '.').str.extract(r'(\d+\.?\d*)').astype(float)
                        total_h_ano = h_extraidas.sum().iloc[0]
                        total_valor = total_h_ano * 65 
                        
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Capacidade Recuperada", f"{total_h_ano:.1f} h/ano", "GANHO REAL")
                        c2.metric("ROI Operacional Est.", f"R$ {total_valor:,.2f}", "REDUÇÃO CUSTO")
                        c3.metric("Impacto em Dias", f"{total_h_ano/8:.1f} dias", "OFFLOAD")

                        st.info(f"📌 Conclusão: Foram detectadas {len(df_analise)} oportunidades.")
                        st.table(df_analise)
            else:
                st.info("⚠️ Nenhuma sugestão encontrada.")
        else:
            st.info("☝️ Selecione um colaborador.")