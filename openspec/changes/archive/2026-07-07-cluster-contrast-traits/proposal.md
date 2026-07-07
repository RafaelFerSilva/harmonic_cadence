## Why

O clustering v1 descreve cada família pelos seus traços **absolutos** (top funções/cadências). Mas
no dado real (`k=8`) TODA família grande mostra "T, SD, D" — porque essas funções dominam o corpus
inteiro. O traço absoluto é quase inútil para distinguir famílias: ele conta o que é comum, não o
que é característico. O conserto honesto é o **contraste**: descrever a família pelo que ela tem **a
mais** que a média do corpus (lift), revelando o dialeto (`Emp`, `Dsec`, `Dim`…) que a define.

## What Changes

- Os traços de família passam de **absolutos** para **por contraste**: para cada função/cadência,
  o lift = participação média na família − participação média no corpus. Os traços salientes são os
  de maior lift **positivo** (sobre-representados), com o valor do lift **visível** (denominador).
- O `harmonic corpus clusters` mostra, por família, os traços que a distinguem do corpus (e sinaliza
  quando uma família não tem nada acima da média — "é o próprio baseline").
- Puro descritivo, sem placar; sem dependência nova; não toca coder/gates.

## Capabilities

### New Capabilities
<!-- Nenhuma. -->

### Modified Capabilities
- `harmonic-corpus-clustering`: o requisito "Consulta de famílias na CLI" passa a definir os traços
  salientes por **contraste com o corpus** (lift), não em valor absoluto.

## Impact

- **Código:** `overlay/clustering.py` (`cluster_traits` vira contraste; baseline do corpus computado
  uma vez); ajuste da saída da CLI (`corpus clusters`); testes.
- **Banco:** nenhuma mudança de schema (traço é computado na consulta, não materializado).
- **Não toca:** os 3 gates duros (293/293), `detect_key`, coder, persistência base. Mede contra
  `songbook_baseline.py` ao vivo.
- **Sem dependência nova.**
