# Energia Gandu — ODS 7

Plataforma educativa sobre energia e sustentabilidade em Gandu (BA), criada com Flask.

## Executar localmente

```bash
python -m venv venv
# Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abra http://127.0.0.1:5000 no navegador.

## Estrutura

- `app.py`: aplicação Flask, rotas e simulador
- `templates/`: páginas HTML
- `data/gandu.json`: dados exibidos na plataforma
- `requirements.txt`: dependências

**Atenção:** os resultados do simulador são estimativas educativas, não propostas comerciais. Confirme tarifas, dados públicos, metodologia e regras de compensação com as fontes oficiais antes de utilizar em decisões financeiras.
