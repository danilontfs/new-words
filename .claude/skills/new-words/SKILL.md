---
name: new-words
description: Fluxo diário de estudo de inglês para Anki — recebe a lista de palavras do dia, explica cada uma, sugere opções de frase de exemplo, escreve a planilha-anki.csv com as escolhas e gera os áudios. Use quando o usuário mandar palavras/expressões em inglês pra estudar ou pedir pra processar a "lista do dia".
---

# Palavra do dia (estudo de inglês → Anki)

Este projeto gera diariamente um baralho de Anki com palavras/expressões em inglês.
Formato do arquivo de trabalho `planilha-anki.csv` (raiz do projeto, sem cabeçalho,
separador `;`, 4 colunas): `frase em inglês;definição em português;;`
A 3ª coluna é preenchida depois pelo `generate-audios.py` com `[sound:arquivo.mp3]` —
deixe sempre vazia. A 4ª coluna também fica sempre vazia.

**Nunca use `;` dentro da frase ou da definição** — só como separador de coluna.

O fluxo tem 3 etapas. Não pule etapas nem escreva a planilha antes da etapa 2.

## Etapa 1 — Explicação e opções de frase

Se o usuário não informou a lista de palavras na mensagem que ativou a skill,
**pergunte quais palavras/expressões ele quer estudar hoje** antes de continuar.
Não busque a lista em `InstruçõesChat.txt` — esse arquivo serve só como referência
dos direcionamentos gerais (formato de explicação/significados/exemplos), que já
estão refletidos nesta skill.

Para cada palavra/expressão da lista, nessa ordem, produza:

1. Título com a palavra em destaque (ex: `# Fellow`).
2. Um parágrafo curto (3 a 10 linhas) em português explicando a palavra, cobrindo
   usos formais, informais, regionais e idiomáticos relevantes.
3. Um ou mais **sentidos** (agrupe por sentido/uso quando a palavra tiver mais de um
   significado relevante). Para cada sentido:
   - Uma linha de definição já pronta no formato exato da planilha:
     `Classe gramatical: significado1, significado2, significado3.`
     (classe gramatical pode ser composta, ex: "Expressão/Substantivo".)
   - Exatamente **2 opções de frase de exemplo (A e B)** que usem esse sentido,
     cobrindo nuances diferentes dentro dele. Palavra-alvo em **negrito**, com
     tradução ao lado.

Formato de exemplo (uma palavra com dois sentidos):

```
# Fellow

### Explicação
<parágrafo>

### Sentido 1 — Substantivo: cara, sujeito, colega, camarada.
- A) He's a nice **fellow**. → Ele é um cara legal.
- B) My **fellow** students helped me study. → Meus colegas de turma me ajudaram a estudar.

### Sentido 2 — Adjetivo: companheiro, semelhante.
- A) She spoke to her **fellow** citizens. → Ela falou com seus concidadãos.
- B) I feel for my **fellow** workers. → Eu me solidarizo com meus colegas de trabalho.
```

Depois de mostrar as opções de **todas** as palavras, feche a mensagem com uma
"cola" pronta para o usuário só preencher — um bloco de código com uma linha por
palavra, já com o nome da palavra escrito, faltando só a escolha:

```
fellow: 
typewriters: 
paperback: 
```

Instrua o usuário a preencher cada linha com o sentido (se houver mais de um) e a
letra da opção, ex: `fellow: 1A` ou, se a palavra só tem um sentido, só a letra
(`typewriters: B`). Deixe claro que dá pra colocar mais de uma escolha na mesma
linha, separadas por vírgula, se quiser gerar mais de uma linha na planilha para
aquela palavra (ex: `paperback: 1A, 2A`), e que ele pode responder colando o bloco
de volta já preenchido.

Não escreva na planilha nessa etapa — só apresente as opções e a cola, e aguarde a resposta.

## Etapa 2 — Atualizar a planilha-anki.csv

Quando o usuário responder com as escolhas:

1. Para cada escolha, monte a linha: `{frase escolhida};{todos os sentidos da palavra};;`
   A 2ª coluna sempre leva **todos** os sentidos apresentados na etapa 1 para aquela
   palavra/expressão — não só o sentido da frase escolhida. Concatene as linhas de
   definição de cada sentido, uma após a outra, separadas por espaço (cada uma já
   termina com ponto), ex: `Verbo: ganhar, obter, adquirir (algo gradualmente). Substantivo: ganho, lucro, aumento.`
   Se a palavra tiver só um sentido, a coluna leva só aquela definição.
2. Sobrescreva completamente o `planilha-anki.csv` da raiz do projeto com uma linha
   por escolha, na mesma ordem da lista de palavras original. É um arquivo de
   trabalho do dia — pode substituir o conteúdo anterior sem pedir confirmação.
   O arquivo precisa ficar salvo em UTF-8 **com BOM** (`utf-8-sig`) — sem isso o
   Excel abre os acentos corrompidos. Se escrever o arquivo por outra via que não
   garanta o BOM, rode em seguida:
   ```
   python3 -c "
   path = 'planilha-anki.csv'
   with open(path, encoding='utf-8') as f: content = f.read()
   with open(path, 'w', encoding='utf-8-sig', newline='') as f: f.write(content)
   "
   ```
3. Mostre um resumo curto (palavra → frase escolhida), sem colar o CSV inteiro.

## Etapa 3 — Gerar os áudios

Pergunte o nome da pasta do dia (ex: `lesson-12-01`) caso o usuário ainda não tenha
dito. Depois rode, a partir da raiz do projeto:

```
python3 generate-audios.py <nome-da-pasta>
```

O script sempre cria a pasta dentro de `lessons/`, independente de onde for
chamado. Confirme que rodou sem erro e informe que os áudios e o CSV atualizado
(com os `[sound:...]`) ficaram em `lessons/<nome-da-pasta>/`. Lembre que o
próximo passo — importar esse CSV pro Anki — continua manual.
