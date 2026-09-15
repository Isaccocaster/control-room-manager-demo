# Sanitizzazione della versione pubblica

La demo è stata costruita come copia separata. Non è una copia del contenuto
operativo con pochi campi oscurati.

Sono stati esclusi:

- repository Git e metadati di sviluppo originali;
- database, backup, cache, log e file generati;
- configurazioni e percorsi locali o di rete;
- fotografie, font e marchi della struttura originale;
- documenti interni, importazioni e script legati ai dati operativi;
- test contenenti esempi provenienti dal contesto originale.

Sono stati sostituiti:

- nome e branding dell'applicazione;
- immagini con sfondi astratti generati localmente;
- esempi e riferimenti identificativi nel codice;
- dataset con record sintetici marcati `DEMO`.

Prima della distribuzione sono previsti controlli su estensioni sensibili,
segreti, percorsi assoluti, riferimenti al branding originale e impronte dei
valori operativi. I database creati a runtime restano esclusi da Git.
