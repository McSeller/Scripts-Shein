import xlwings as xw
from datetime import datetime

ARQUIVO_DETALHES = "detalhes_spu.xlsx"
ARQUIVO_MASTER = r"C:\Users\Windows\3D Objects\Shein\Tabela Master\Tabela de Preco Master Shein.xlsx"
NOME_LOG = f"log_atualizacao_precos_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"

def atualizar_precos_ctrl_L_com_log():
    app = xw.App(visible=False)
    log = []

    try:
        wb_detalhes = app.books.open(ARQUIVO_DETALHES)
        wb_master = app.books.open(ARQUIVO_MASTER)

        sht_detalhes = wb_detalhes.sheets[0]
        sht_master = wb_master.sheets[0]

        ultima_detalhes = sht_detalhes.range("B" + str(sht_detalhes.cells.last_cell.row)).end("up").row
        alteracoes = 0

        for linha in range(2, ultima_detalhes + 1):
            titulo = sht_detalhes.range(f"B{linha}").value
            if not titulo:
                continue

            log.append(f"[{linha}] Pesquisando título: {repr(titulo)}")

            celula_master = sht_master.api.Cells.Find(
                What=str(titulo),
                LookIn=-4163,    # xlValues
                LookAt=1,        # xlWhole
                SearchOrder=1,   # xlByRows
                SearchDirection=1,  # xlNext
                MatchCase=False
            )

            if celula_master:
                linha_master = celula_master.Row
                preco_base_master = sht_master.range(f"C{linha_master}").value
                promocao_master  = sht_master.range(f"D{linha_master}").value
                preco_base_atual = sht_detalhes.range(f"D{linha}").value

                log.append(f"      → ENCONTRADO NA MASTER (linha {linha_master}): Preço Base Master = '{preco_base_master}', Promoção Master = '{promocao_master}', BasePrice Atual = '{preco_base_atual}'")

                try:
                    pbm = float(preco_base_master)
                    pba = float(preco_base_atual)
                except Exception as e:
                    log.append(f"      ❌ Erro ao converter preços para float: master='{preco_base_master}' | atual='{preco_base_atual}' | Erro: {str(e)}")
                    continue

                if pba >= pbm:
                    # Só atualiza SPECIALPRICE
                    sht_detalhes.range(f"E{linha}").value = promocao_master
                    log.append(f"      → Atualizou SPECIALPRICE (E{linha}) para '{promocao_master}'. (BasePrice {pba} >= PreçoBaseMaster {pbm})")
                else:
                    # Atualiza basePrice e SPECIALPRICE
                    sht_detalhes.range(f"D{linha}").value = pbm
                    sht_detalhes.range(f"E{linha}").value = promocao_master
                    log.append(f"      → Atualizou BASEPRICE (D{linha}) para '{pbm}' e SPECIALPRICE (E{linha}) para '{promocao_master}'. (BasePrice {pba} < PreçoBaseMaster {pbm})")
                alteracoes += 1
            else:
                preco_base_atual = sht_detalhes.range(f"D{linha}").value
                try:
                    pba = float(preco_base_atual)
                    specialprice = round(pba * 0.95, 2)
                    sht_detalhes.range(f"E{linha}").value = specialprice
                    log.append(f"      → NÃO ENCONTRADO NA MASTER. Aplicado -5% em BasePrice: {pba} → SPECIALPRICE (E{linha}) = {specialprice}")
                    alteracoes += 1
                except Exception as e:
                    log.append(f"      ❌ NÃO ENCONTRADO NA MASTER e erro ao calcular -5%: basePrice='{preco_base_atual}' | Erro: {str(e)}")


        wb_detalhes.save(ARQUIVO_DETALHES)
        log.append(f"\n✅ Atualização concluída. {alteracoes} linhas alteradas.")

    finally:
        with open(NOME_LOG, "w", encoding="utf-8") as f:
            f.write("\n".join(log))
        wb_master.close()
        wb_detalhes.close()
        app.quit()
        print(f"Log salvo em {NOME_LOG}")

if __name__ == "__main__":
    atualizar_precos_ctrl_L_com_log()
