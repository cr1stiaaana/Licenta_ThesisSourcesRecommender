# Dezvoltare asistată de AI — Experiență și Concluzii

## 1. Cum s-a desfășurat procesul

Dezvoltarea proiectului a fost realizată în colaborare directă cu un asistent AI (Kiro), care a participat activ în toate etapele ciclului de viață al aplicației: definirea specificațiilor, proiectarea arhitecturii, implementarea codului, scrierea testelor, configurarea pipeline-ului CI/CD, analiza de performanță, și redactarea documentației tehnice.

Fluxul de lucru tipic a urmat un model conversațional iterativ: dezvoltatorul formula o cerință sau o întrebare, asistentul propunea o soluție (cod, arhitectură, sau text), dezvoltatorul evalua și solicita ajustări, iar asistentul rafina rezultatul. Acest ciclu se repeta până când ambele părți considerau soluția satisfăcătoare. Deciziile finale au aparținut întotdeauna dezvoltatorului — asistentul a funcționat ca un partener tehnic, nu ca un automat care livrează cod fără supraveghere.

## 2. Beneficii observate

**Viteză de implementare** — Componentele care ar fi necesitat ore de cercetare și implementare manuală (configurarea schemathesis, scrierea benchmark-ului de performanță, integrarea OpenAPI validator în CI) au fost realizate în minute. Asistentul avea deja cunoștințele necesare și le-a aplicat direct pe structura existentă a proiectului.

**Consistență tehnică** — Codul generat a respectat convențiile deja existente în proiect (naming, structura importurilor, stilul docstring-urilor, tipul de error handling) fără a fi nevoie de instrucțiuni explicite la fiecare iterație. Asistentul a citit codul existent și s-a adaptat.

**Explorare rapidă a alternativelor** — Întrebări de tipul „ce alte metode de criptare există?" sau „cum se poate îmbunătăți scalabilitatea?" au primit răspunsuri structurate cu comparații, compromisuri, și recomandări contextualizate la proiect, nu răspunsuri generice.

**Documentare simultană** — Documentația tehnică (TESTE_PERFORMANTA.md, CONCLUZII_DIRECTII_VIITOARE.md) a fost redactată în paralel cu implementarea, nu retroactiv. Acest lucru a asigurat că documentația reflectă exact starea reală a sistemului.

**Reducerea barierei de intrare** — Concepte complexe (property-based testing, contract testing, FAISS indexing, RRF fusion) au fost explicate și implementate fără a necesita studiu individual extensiv din partea dezvoltatorului.

## 3. Dezavantaje și limitări

**Necesitatea validării umane** — Codul generat nu a fost întotdeauna corect din prima încercare (ex: apelul ContentVerifier cu parametri greșiți în benchmark). Dezvoltatorul trebuie să înțeleagă suficient codul pentru a detecta erorile, altfel le propagă fără să le observe.

**Risc de supradependență** — Există tentația de a delega decizii arhitecturale asistentului fără a le înțelege complet. Aceasta poate duce la un proiect pe care dezvoltatorul nu-l poate menține independent.

**Context limitat** — Asistentul nu cunoaște istoricul complet al deciziilor anterioare decât dacă sunt documentate explicit. La reluarea unei conversații, contextul trebuie reconstruit parțial.

**Tendința de over-engineering** — Asistentul poate propune soluții mai complexe decât necesarul (ex: adăugarea de metrici p95 și stdev când media era suficientă pentru scopul lucrării), necesitând direcționare activă din partea dezvoltatorului.

**Cod funcțional, nu întotdeauna optim** — Soluțiile generate funcționează corect dar nu sunt mereu cele mai eficiente. Optimizarea necesită tot intervenție umană cu cunoștințe de domeniu.

## 4. Concluzii privind modelul de colaborare

Colaborarea om-AI s-a dovedit eficientă atunci când dezvoltatorul a menținut rolul de **arhitect și decident**, iar asistentul a servit ca **implementator rapid și consilier tehnic**. Modelul funcționează optim când:

- Dezvoltatorul știe *ce* vrea, iar asistentul ajută cu *cum* se face
- Fiecare output al asistentului este evaluat critic, nu acceptat automat
- Documentația e scrisă în paralel, nu delegată complet
- Conceptele noi sunt înțelese, nu doar copiate

Această abordare nu înlocuiește competența tehnică a dezvoltatorului — o amplifică. Un dezvoltator care înțelege arhitectura și poate valida soluțiile obține rezultate semnificativ mai bune decât unul care folosește asistentul ca o cutie neagră.
