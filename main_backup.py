import trio
import requests
import json
import os

ARQUIVO_MENSAGENS = "mensagens.json"


def carregar_mensagens():

    try:

        resposta = requests.get(
            FIREBASE_MONITOR,
            timeout=10
        )

        dados = resposta.json() or {}

        return dados.get(
            "mensagens",
            {}
        )

    except Exception as e:

        print(
            "Erro carregando mensagens:",
            e
        )

        return {
            "online_message_id": None,
            "dia_message_id": None,
            "semana_message_id": None
        }


def salvar_mensagens(dados):

    try:

        requests.patch(
            FIREBASE_MONITOR,
            json={
                "mensagens": dados
            },
            timeout=10
        )

    except Exception as e:

        print(
            "Erro salvando mensagens:",
            e
        )

from samp_query import Client
from datetime import datetime, timedelta, timezone

FUSO_BRASIL = timezone(timedelta(hours=-3))

def agora():
    return datetime.now(FUSO_BRASIL)

HOST = "ip1.brasilplayshox.com.br"
PORT = 7777

WEBHOOK_ONLINE = "https://discord.com/api/webhooks/1509136993186222152/G-AK46fpOJnIwhkMXqNL47xMbx4qwE8ECrZgHIehS4DGk9jYcNpijcUR9b5A_N2o3CXW"
WEBHOOK_DIA = "https://discord.com/api/webhooks/1509137293489864706/Q-ShKKetj0k-SAXkbh5m5wZLpz_Hx_oS_qdjBo3PlrDoq-HwPwV4Yv5OQbGo6QtqPRbP"
WEBHOOK_SEMANA = "https://discord.com/api/webhooks/1509137422892404777/sv7swMsSA_1HNKGoBdnPSo-aB1AHGYQLkiq-RncgOtK8HT2H-UeBox6JcLJ4WNk_zLIo"

FIREBASE_ONLINE = (
    "https://monitor-mt-default-rtdb.firebaseio.com/online.json"
)

FIREBASE_MONITOR = (
    "https://monitor-mt-default-rtdb.firebaseio.com/discord_monitor.json"
)

FIREBASE_MONITORES = (
    "https://monitor-mt-default-rtdb.firebaseio.com/monitores.json"
)

ULTIMOS_ONLINE = set()

ARQUIVO_DIA = "ativos_dia.json"
ARQUIVO_SEMANA = "ativos_semana.json"

ARQUIVO_DATA_ATUAL = "data_atual.txt"
ARQUIVO_SEMANA_ATUAL = "semana_atual.txt"

def formatar_tempo(minutos):

    horas = minutos // 60

    minutos_restantes = minutos % 60

    if horas > 0:

        return f"{horas}h{minutos_restantes:02d}m"

    return f"{minutos_restantes}m"


def carregar_lista(arquivo):

    if os.path.exists(arquivo):

        with open(arquivo, "r") as f:
            return set(json.load(f))

    return set()


def salvar_lista(arquivo, lista):

    with open(arquivo, "w") as f:
        json.dump(list(lista), f)

def ler_firebase_online():

    try:

        resposta = requests.get(
            FIREBASE_ONLINE,
            timeout=15
        )

        if resposta.status_code != 200:

            print(
                "Firebase retornou:",
                resposta.status_code
            )

            return None

        dados = resposta.json()

        membros = dados.get("membros", [])

        return membros

    except Exception as e:

        print("Erro Firebase:", e)

        return None


def enviar_discord(webhook, mensagem):

    data = {
        "content": mensagem
    }

    requests.post(webhook, json=data)

def obter_historico_firebase():

    try:

        dados = requests.get(
            "https://monitor-mt-default-rtdb.firebaseio.com/historico.json",
            timeout=10
        ).json()

        if not dados:
            return []

        return dados.get("players", [])

    except Exception as e:

        print("Erro Firebase Historico:", e)

        return []

def atualizar_status_monitor(origem):

    try:

        requests.patch(
            FIREBASE_MONITOR,
            json={
                "status": "online",
                "origem": origem,
                "ultima_execucao": agora().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            },
            timeout=10
        )

    except Exception as e:

        print(
            "Erro ao atualizar monitor:",
            e
        )

def atualizar_monitor_nome(nome_monitor):

    try:

        requests.patch(
            FIREBASE_MONITORES,
            json={
                nome_monitor: {
                    "status": "online",
                    "ultima_vez": agora().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                }
            },
            timeout=10
        )

    except Exception as e:

        print(
            "Erro atualizando monitor:",
            e
        )

def verificar_sentinelas_offline():

    try:

        resposta = requests.get(
            FIREBASE_MONITOR,
            timeout=10
        )

        dados = resposta.json() or {}

        sentinelas = dados.get(
            "sentinelas",
            {}
        )

        alterou = False

        momento_atual = agora()

        for nome, info in sentinelas.items():

            ultima_vez = info.get(
                "ultima_vez",
                ""
            )

            if not ultima_vez:
                continue

            try:

                horario = datetime.strptime(
                    ultima_vez,
                    "%Y-%m-%d %H:%M:%S"
                ).replace(
                    tzinfo=FUSO_BRASIL
                )

                diferenca = (
                    momento_atual - horario
                ).total_seconds()

                if diferenca > 2100:

                    if info.get("status") != "offline":

                        info["status"] = "offline"

                        alterou = True

            except:
                pass

        if alterou:

            requests.patch(
                FIREBASE_MONITOR,
                json={
                    "sentinelas": sentinelas
                },
                timeout=10
            )

            print(
                "Sentinelas offline atualizados."
            )

    except Exception as e:

        print(
            "Erro verificando sentinelas:",
            e
        )

def verificar_monitores_offline():

    try:

        resposta = requests.get(
            FIREBASE_MONITORES,
            timeout=10
        )

        monitores = resposta.json() or {}

        alterou = False

        momento_atual = agora()

        for nome, info in monitores.items():

            ultima_vez = info.get(
                "ultima_vez",
                ""
            )

            if not ultima_vez:
                continue

            try:

                horario = datetime.strptime(
                    ultima_vez,
                    "%Y-%m-%d %H:%M:%S"
                ).replace(
                    tzinfo=FUSO_BRASIL
                )

                diferenca = (
                    momento_atual - horario
                ).total_seconds()

                if diferenca > 600:

                    if info.get("status") != "offline":

                        info["status"] = "offline"

                        alterou = True

            except:
                pass

        if alterou:

            requests.put(
                FIREBASE_MONITORES,
                json=monitores,
                timeout=10
            )

            print(
                "Monitores offline atualizados."
            )

    except Exception as e:

        print(
            "Erro verificando monitores:",
            e
        )

def carregar_controle():

    try:

        resposta = requests.get(
            FIREBASE_MONITOR,
            timeout=10
        )

        dados = resposta.json() or {}

        return dados.get(
            "controle",
            {}
        )

    except Exception as e:

        print(
            "Erro carregando controle:",
            e
        )

        return {}

def registrar_reinicio():

    try:

        resposta = requests.get(
            FIREBASE_MONITOR,
            timeout=10
        )

        dados = resposta.json() or {}

        reinicios = dados.get(
            "reinicios",
            0
        )

        reinicios += 1

        requests.patch(
            FIREBASE_MONITOR,
            json={
                "reinicios": reinicios
            },
            timeout=10
        )

        print(
            f"Reinício registrado: {reinicios}"
        )

    except Exception as e:

        print(
            "Erro registrando reinício:",
            e
        )

def salvar_controle(
    data_atual,
    semana_atual
):

    try:

        requests.patch(
            FIREBASE_MONITOR,
            json={
                "controle": {
                    "data_atual": data_atual,
                    "semana_atual": semana_atual
                }
            },
            timeout=10
        )

    except Exception as e:

        print(
            "Erro salvando controle:",
            e
        )

def atualizar_online(webhook, mensagem):

    dados = carregar_mensagens()

    message_id = dados.get("online_message_id")

    if not message_id:

        resposta = requests.post(
            webhook + "?wait=true",
            json={"content": mensagem}
        )

        if resposta.status_code in (200, 201):

            dados["online_message_id"] = resposta.json()["id"]
            salvar_mensagens(dados)

            print("Mensagem ONLINE criada.")

        else:

            print("Erro ao criar mensagem ONLINE:", resposta.text)

        return

    webhook_base = webhook.split("/webhooks/")[1]

    partes = webhook_base.split("/")

    webhook_id = partes[0]
    webhook_token = partes[1]

    url = (
        f"https://discord.com/api/webhooks/"
        f"{webhook_id}/{webhook_token}"
        f"/messages/{message_id}"
    )

    resposta = requests.patch(
        url,
        json={"content": mensagem}
    )

    if resposta.status_code != 200:

        print("Erro ao editar mensagem ONLINE:", resposta.text)

def atualizar_dia(webhook, mensagem):

    dados = carregar_mensagens()

    message_id = dados.get("dia_message_id")

    if not message_id:

        resposta = requests.post(
            webhook + "?wait=true",
            json={"content": mensagem}
        )

        if resposta.status_code in (200, 201):

            dados["dia_message_id"] = resposta.json()["id"]
            salvar_mensagens(dados)

            print("Mensagem DIA criada.")

        else:

            print("Erro ao criar mensagem DIA:", resposta.text)

        return

    webhook_base = webhook.split("/webhooks/")[1]

    partes = webhook_base.split("/")

    webhook_id = partes[0]
    webhook_token = partes[1]

    url = (
        f"https://discord.com/api/webhooks/"
        f"{webhook_id}/{webhook_token}"
        f"/messages/{message_id}"
    )

    resposta = requests.patch(
        url,
        json={"content": mensagem}
    )

    if resposta.status_code != 200:

        print("Erro ao editar mensagem DIA:", resposta.text)

def atualizar_semana(webhook, mensagem):

    dados = carregar_mensagens()

    message_id = dados.get("semana_message_id")

    if not message_id:

        resposta = requests.post(
            webhook + "?wait=true",
            json={"content": mensagem}
        )

        if resposta.status_code in (200, 201):

            dados["semana_message_id"] = resposta.json()["id"]
            salvar_mensagens(dados)

            print("Mensagem SEMANA criada.")

        else:

            print("Erro ao criar mensagem SEMANA:", resposta.text)

        return

    webhook_base = webhook.split("/webhooks/")[1]

    partes = webhook_base.split("/")

    webhook_id = partes[0]
    webhook_token = partes[1]

    url = (
        f"https://discord.com/api/webhooks/"
        f"{webhook_id}/{webhook_token}"
        f"/messages/{message_id}"
    )

    resposta = requests.patch(
        url,
        json={"content": mensagem}
    )

    if resposta.status_code != 200:

        print("Erro ao editar mensagem SEMANA:", resposta.text)


async def verificar_players():

    global ULTIMOS_ONLINE

    ativos_dia = carregar_lista(ARQUIVO_DIA)
    ativos_semana = carregar_lista(ARQUIVO_SEMANA)

    controle = carregar_controle()

    data_salva = controle.get(
        "data_atual",
        ""
    )

    semana_salva = controle.get(
        "semana_atual",
        ""
    )


    atualizar_monitor_nome(
        "github_backup"
    )

    client = Client(HOST, PORT)

    try:

        verificar_sentinelas_offline()

        verificar_monitores_offline()

        hoje = agora().strftime("%Y-%m-%d")

        semana_atual = agora().strftime("%G-W%V")

        if data_salva != hoje:

            ativos_dia = set()

            dados = carregar_mensagens()

            dados["dia_message_id"] = None

            salvar_mensagens(dados)

            data_salva = hoje

            salvar_controle(
                data_salva,
                semana_salva
            )

            print("Novo dia detectado.")

        if semana_salva != semana_atual:

            ativos_semana = set()

            dados = carregar_mensagens()

            dados["semana_message_id"] = None

            salvar_mensagens(dados)

            semana_salva = semana_atual

            salvar_controle(
                data_salva,
                semana_salva
            )

            print("Nova semana detectada.")

        print("Consultando servidor...")

        with trio.move_on_after(10) as timeout:

            info = await client.info()
            print(f"Players informados pelo servidor: {info.players}")

        if timeout.cancelled_caught:

            print("TIMEOUT em client.info()")
            return

        print("Info recebida.")

        historico = obter_historico_firebase()

        ler_firebase_online()

        with trio.move_on_after(20) as timeout:

            players = await client.players()

        if timeout.cancelled_caught:

            print("TIMEOUT em client.players()")

            fonte_dados = "sentinela"

            membros_mt = ler_firebase_online()

            if not membros_mt:

                print("Firebase também falhou.")

                return

            print("Usando dados do Firebase.")

            atualizar_status_monitor(
                "Sentinela"
            )

        else:

            print("Lista de players recebida.")

            atualizar_status_monitor(
                "Query SAMP"
            )

            fonte_dados = "Query SAMP"

            membros_mt = []

            for player in players.players:

                nome = player.name

                if "$MT" in nome.upper():
                    membros_mt.append(nome)

        membros_atuais = set(membros_mt)

        entraram = membros_atuais - ULTIMOS_ONLINE

        for nome in membros_atuais:
            ativos_dia.add(nome)
            ativos_semana.add(nome)

        salvar_lista(ARQUIVO_DIA, ativos_dia)
        salvar_lista(ARQUIVO_SEMANA, ativos_semana)

        hora_atual = agora().strftime("%H:%M:%S")

        mensagem_online = (
            f"🟢 MEMBROS ONLINE\n\n"
            + "\n".join([f"• {nome}" for nome in membros_mt])
            + f"\n\nTotal Online: {len(membros_mt)}"
            + f"\nAtualização: {fonte_dados} • {hora_atual}"
        )

        hoje = agora().strftime("%Y-%m-%d")

        linhas_dia = []

        for player in historico:

            nome = player["nome"]

            minutos = (
                player
                .get("dias", {})
                .get(hoje, 0)
            )

            if minutos > 0:

                linhas_dia.append(
                    (
                        minutos,
                        f"{nome} - {formatar_tempo(minutos)}"
                    )
                )

        linhas_dia.sort(
            reverse=True,
            key=lambda x: x[0]
        )

        texto_dia = []

        for posicao, (_, texto) in enumerate(
            linhas_dia,
            start=1
        ):

            texto_dia.append(
                f"{posicao}º {texto}"
            )

        mensagem_dia = (
            f"📅 ATIVOS {agora().strftime('%d/%m/%Y')}\n\n"
            + "\n".join(texto_dia)
            + f"\n\nTotal ativos: {len(texto_dia)}"
        )

        semana_atual = agora().strftime("%G-W%V")

        linhas_semana = []

        for player in historico:

            nome = player["nome"]

            minutos_semana = (
                player
                .get("semanas", {})
                .get(semana_atual, 0)
            )

            dias_ativos = len(
                player.get("dias", {})
            )

            if minutos_semana > 0:

                linhas_semana.append(
                    (
                        minutos_semana,
                        f"{nome} - "
                        f"{formatar_tempo(minutos_semana)} "
                        f"| {dias_ativos} dias"
                    )
                )

        linhas_semana.sort(
            reverse=True,
            key=lambda x: x[0]
        )

        texto_semana = []

        for posicao, (_, texto) in enumerate(
            linhas_semana,
            start=1
        ):

            texto_semana.append(
                f"{posicao}º {texto}"
            )

        mensagem_semana = (
            f"📊 ATIVOS DA SEMANA\n"
            f"Semana: {semana_atual}\n\n"
            + "\n".join(texto_semana)
            + f"\n\nTotal ativos: {len(texto_semana)}"
        )

        atualizar_online(
            WEBHOOK_ONLINE,
            mensagem_online
        )

        atualizar_dia(
            WEBHOOK_DIA,
            mensagem_dia
        )

        atualizar_semana(
            WEBHOOK_SEMANA,
            mensagem_semana
        )

        print(f"\n[{hora_atual}] Atualizado com sucesso.")

        if entraram:

            print("Entraram:")

            for nome in entraram:
                print(f"+ {nome}")

        ULTIMOS_ONLINE = membros_atuais

    except Exception as e:

        print("ERRO Query:", e)

        membros_mt = ler_firebase_online()

        if membros_mt:

            print("Fallback para Sentinela.")

            hora_atual = agora().strftime("%H:%M:%S")

            mensagem_online = (
                f"🟢 MEMBROS ONLINE\n\n"
                + "\n".join([f"• {nome}" for nome in membros_mt])
                + f"\n\nTotal Online: {len(membros_mt)}"
                + f"\nAtualização: Sentinela • {hora_atual}"
            )

            atualizar_online(
                WEBHOOK_ONLINE,
                mensagem_online
            )

        else:

            print("Firebase também falhou.")



registrar_reinicio()

trio.run(verificar_players)

           