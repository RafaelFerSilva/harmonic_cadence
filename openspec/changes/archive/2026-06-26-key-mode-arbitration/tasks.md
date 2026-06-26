# Tasks — key-mode-arbitration

## 1. Centro tonal robusto
- [x] 1.1 `_central_pc` (baixo mais frequente + bônus início/fim) substitui
      `_final_tonic_pc` em `detect_mode`.

## 2. Arbitragem
- [x] 2.1 `_mode_refines_key`: modo só refina se concorda na tônica E qualidade.
- [x] 2.2 Gatear o override; anular `mode_info` quando rejeitado (coerência a jusante).

## 3. Verificação
- [x] 3.1 Regressão: Sina-like → Lá maior, modal_analysis None.
- [x] 3.2 Unidade da arbitragem (tônica/qualidade).
- [x] 3.3 Testes modais existentes intactos; suíte completa verde.
