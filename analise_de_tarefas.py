                # --- LISTA DE RELATOS RECENTES ---
                st.subheader("🔍 Últimos Relatos do Campo")
                st.table(df_ultimos[['colaborador', 'kpi_nome', 'relato_do_auditor']].tail(5))

                
 
                # --- DETALHAMENTO ISOLADO ---
                st.markdown("---")
                st.subheader("🎯 Diagnóstico por Indicador")
                
                for kpi in df_ultimos['kpi_nome'].unique():
                    dados_kpi = df_ultimos[df_ultimos['kpi_nome'] == kpi].iloc[-1]
                    
                    nota = dados_kpi['percentual_alcance']
                    cor = "green" if nota >= 80 else "orange" if nota >= 50 else "red"
                    
                    with st.expander(f"🔍 Detalhes: {kpi} - :{cor}[{nota:.1f}%]"):
                        c1, c2 = st.columns([1, 2])
                        with c1:
                            st.write("**Veredito Técnico:**")
                            st.write(f"Status: `{dados_kpi['status_pericial']}`")
                        with c2:
                            st.write("**Análise do Auditor (IA):**")
                            st.info(dados_kpi['analise_critica'])
                            if dados_kpi.get('gap_de_conformidade'):
                                st.warning("**O que faltou para 100%:**")
                                for item in dados_kpi['gap_de_conformidade']:
                                    st.write(f"• {item}")

            else:
                st.info("Sincronize os dados para carregar o dashboard.")

        except Exception as e:
            st.error(f"Erro no Dashboard T2: {e}")

        # 👇 FORA do try/except, mas ainda dentro do with t2
        if all_data:

            if st.button("📥 Gerar Relatório HTML Completo", key="btn_html_relatorio"):

                html_kpis = df_kpi.to_html(index=False)
                html_relatos = df_ultimos[['colaborador', 'kpi_nome', 'relato_do_auditor']].tail(5).to_html(index=False)

                grafico_bar_html = fig_bar.to_html(full_html=False, include_plotlyjs='cdn')
                grafico_pie_html = fig_pie.to_html(full_html=False, include_plotlyjs=False)

                html_final = f"""
                <html>
                    <head>
                        <meta charset="UTF-8">
                        <title>Relatório de Auditoria</title>
                        <style>
                            body {{
                                font-family: Arial;
                                background-color: #f4f6f8;
                                padding: 30px;
                            }}
                            h1, h2 {{
                                color: #1e3a8a;
                            }}
                            table {{
                                border-collapse: collapse;
                                width: 100%;
                                margin-bottom: 30px;
                            }}
                            th, td {{
                                border: 1px solid #ccc;
                                padding: 8px;
                                text-align: left;
                            }}
                            th {{
                                background-color: #1e3a8a;
                                color: white;
                            }}
                            .card {{
                                background: white;
                                padding: 20px;
                                border-radius: 10px;
                                margin-bottom: 20px;
                                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                            }}
                        </style>
                    </head>
                    <body>

                        <h1>📊 Relatório de Auditoria de KPIs</h1>

                        <div class="card">
                            <h2>Métricas Gerais</h2>
                            <p><b>Eficiência Média:</b> {media_alcance:.1f}%</p>
                            <p><b>Total de KPIs:</b> {len(df_ultimos)}</p>
                            <p><b>KPI Crítico:</b> {pior_kpi_nome}</p>
                        </div>

                        <div class="card">
                            <h2>Média por Indicador</h2>
                            {grafico_bar_html}
                        </div>

                        <div class="card">
                            <h2>Volume de Auditorias</h2>
                            {grafico_pie_html}
                        </div>

                        <div class="card">
                            <h2>Tabela de KPIs</h2>
                            {html_kpis}
                        </div>

                        <div class="card">
                            <h2>Últimos Relatos</h2>
                            {html_relatos}
                        </div>

                    </body>
                </html>
                """

                st.download_button(
                    label="⬇️ Baixar Relatório HTML",
                    data=html_final,
                    file_name="relatorio_auditoria.html",
                    mime="text/html"
                )
    

                            

                                            
                
                
    with t3:
        st.header("🏆 Ranking Global de Produtividade")
        
        try:
            g = Github(DB_TOKEN)
            repo = g.get_repo(REPO_NAME)
            contents = repo.get_contents("auditorias")
            all_data = []

            # 1. BUSCA TODOS OS ARQUIVOS
            with st.spinner("Calculando posições..."):
                for content_file in contents:
                    if content_file.type == "dir":
                        subdir_files = repo.get_contents(content_file.path)
                        for file in subdir_files:
                            if file.name.endswith(".json"):
                                data = json.loads(file.decoded_content)
                                all_data.append(data)

            if all_data:
                df_ranking = pd.DataFrame(all_data)

                # --- CORREÇÃO DA CHAVE AQUI ---
                # Usando 'colaborador' (como sai no seu JSON) e 'percentual_alcance'
                # Se o campo de nota no seu JSON tiver outro nome, mude 'percentual_alcance' abaixo
                df_ranking = pd.DataFrame(all_data)

                df_ranking = df_ranking.drop_duplicates(
                    subset=['colaborador', 'kpi_nome'],
                    keep='last'
                )

                ranking = df_ranking.groupby("colaborador")["percentual_alcance"].sum().reset_index().sort_values(by="percentual_alcance",    ascending=False).reset_index(drop=True)

                ranking["percentual_alcance"] = ranking["percentual_alcance"] / 5

                ranking.index = ranking.index + 1
                ranking.columns = ["Colaborador", "Média de Eficiência"]


                # --- EXIBIÇÃO DO PÓDIO ---
                c1, c2, c3 = st.columns(3)
                if len(ranking) >= 1:
                    c1.metric("🥇 1º", ranking.iloc[0]["Colaborador"], f"{ranking.iloc[0]['Média de Eficiência']:.1f}%")
                if len(ranking) >= 2:
                    c2.metric("🥈 2º", ranking.iloc[1]["Colaborador"], f"{ranking.iloc[1]['Média de Eficiência']:.1f}%")
                if len(ranking) >= 3:
                    c3.metric("🥉 3º", ranking.iloc[2]["Colaborador"], f"{ranking.iloc[2]['Média de Eficiência']:.1f}%")

                st.divider()

                # Tabela estilizada
                st.subheader("Tabela de Classificação")
                st.dataframe(
                    ranking.style.format({"Média de Eficiência": "{:.1f}%"}),
                    use_container_width=True
                )
            else:
                st.info("Nenhuma auditoria encontrada para gerar o ranking.")

        except Exception as e:
            st.error(f"Erro ao processar ranking: {e}")

if __name__ == "__main__":
    aba_produtividade_inteligente()
