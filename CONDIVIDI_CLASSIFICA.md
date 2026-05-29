# 🌐 Come condividere la classifica online (link pubblico)

## Metodo più semplice: Netlify Drop

1. Vai su → https://app.netlify.com/drop
2. Trascina la cartella `data/output/` nella pagina
3. Netlify ti dà subito un link tipo:
   `https://funny-name-123456.netlify.app`
4. Condividi questo link con tutti i partecipanti

### Per aggiornare la classifica:
- Riesegui `run.bat` (genera nuovo `index.html`)
- Torna su Netlify → clicca sul tuo sito → "Deploys"
- Trascina di nuovo la cartella `data/output/`
- Il link rimane lo stesso, la classifica è aggiornata ✅

---

## Metodo alternativo: GitHub Pages (gratuito, link stabile)

1. Crea account su https://github.com (gratis)
2. Crea un nuovo repository pubblico (es. `totomondiale2026`)
3. Carica solo il file `data/output/index.html`
4. Vai su Settings → Pages → Branch: main → Save
5. Il link sarà: `https://tuonome.github.io/totomondiale2026/`

### Per aggiornare:
- Sostituisci `index.html` nel repository con la versione aggiornata
