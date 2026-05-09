import json, os

MULT = {'DVD': 220, 'D': 220, 'S': 48, 'Q': 24, 'M': 12, 'T': 4, 'A': 1}

arquivos = ['PEDRO_ARTHUR.json', 'LUCIANA_SIMAS_.json', 'LUCAS_GABRIEL_DA_SILVA_SANTANA.json', 'MOACIR_JÚNIOR.json']

for nome_arq in arquivos:
    caminho = f'dados/{nome_arq}'
    if not os.path.exists(caminho):
        print(f'Nao encontrado: {caminho}')
        continue
    with open(caminho, encoding='utf-8') as f:
        d = json.load(f)
    nome = d.get('colaborador') or nome_arq
    print(f'\n=== {nome} ===')
    sugs = d.get('tabelas', {}).get('sugestoes', [])
    for s in sugs:
        texto = str(s.get('Sugestao', s.get('Sugestão', ''))).strip()
        if not texto:
            continue
        h    = str(s.get('Horas',    '0')).replace('h',   '').strip()
        m    = str(s.get('Minutos',  '0')).replace('min', '').strip()
        freq = str(s.get('Frequencia', s.get('Frequência', 'M'))).upper().strip()
        try:
            h_val = float(h or 0)
            m_val = float(m or 0)
            mult  = MULT.get(freq, 12)
            h_ano = (h_val + m_val / 60) * mult
            rs    = h_ano * 35
            print(f'  Sugestao : {texto[:70]}')
            print(f'  H:{h_val} M:{m_val} Freq:{freq} Mult:{mult}')
            print(f'  H/ano:{h_ano:.1f} | R$:{rs:.2f}')
            print()
        except Exception as e:
            print(f'  Erro: {e}')