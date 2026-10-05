from flask import Flask, jsonify, request
from datetime import datetime
import uuid

app = Flask(__name__)

# =========================
# BANCO TEMPORÁRIO DA V17
# =========================

tarefas = []
agentes = []


# =========================
# FUNÇÕES
# =========================

def agora():
    return datetime.now().isoformat()


def criar_id():
    return str(uuid.uuid4())[:8]


# =========================
# INÍCIO / PAINEL
# =========================

@app.route("/")
def inicio():
    concluidas = sum(
        1 for tarefa in tarefas
        if tarefa["status"] == "concluida"
    )

    erros = sum(
        1 for tarefa in tarefas
        if tarefa["status"] == "erro"
    )

    pendentes = sum(
        1 for tarefa in tarefas
        if tarefa["status"] == "pendente"
    )

    return jsonify({
        "sistema": "V17 1.000 Tarefas",
        "versao": "1.0",
        "status": "ONLINE",
        "hora": agora(),
        "estatisticas": {
            "total_tarefas": len(tarefas),
            "concluidas": concluidas,
            "pendentes": pendentes,
            "erros": erros,
            "agentes": len(agentes)
        }
    })


# =========================
# STATUS DO SISTEMA
# =========================

@app.route("/status")
def status():
    return jsonify({
        "sistema": "V17 1.000 Tarefas",
        "status": "ONLINE",
        "hora": agora(),
        "tarefas": len(tarefas),
        "agentes": len(agentes)
    })


# =========================
# CRIAR TAREFA
# =========================

@app.route("/tarefas", methods=["POST"])
def criar_tarefa():

    dados = request.get_json(silent=True) or {}

    nome = dados.get("nome", "Tarefa sem nome")
    descricao = dados.get("descricao", "")

    tarefa = {
        "id": criar_id(),
        "nome": nome,
        "descricao": descricao,
        "status": "pendente",
        "criada_em": agora(),
        "atualizada_em": agora()
    }

    tarefas.append(tarefa)

    return jsonify({
        "mensagem": "Tarefa criada com sucesso",
        "tarefa": tarefa
    }), 201


# =========================
# LISTAR TAREFAS
# =========================

@app.route("/tarefas", methods=["GET"])
def listar_tarefas():

    return jsonify({
        "total": len(tarefas),
        "tarefas": tarefas
    })


# =========================
# CONCLUIR TAREFA
# =========================

@app.route("/tarefas/<tarefa_id>/concluir", methods=["POST"])
def concluir_tarefa(tarefa_id):

    for tarefa in tarefas:

        if tarefa["id"] == tarefa_id:

            tarefa["status"] = "concluida"
            tarefa["atualizada_em"] = agora()

            return jsonify({
                "mensagem": "Tarefa concluída",
                "tarefa": tarefa
            })

    return jsonify({
        "erro": "Tarefa não encontrada"
    }), 404


# =========================
# COLOCAR TAREFA EM ERRO
# =========================

@app.route("/tarefas/<tarefa_id>/erro", methods=["POST"])
def erro_tarefa(tarefa_id):

    for tarefa in tarefas:

        if tarefa["id"] == tarefa_id:

            tarefa["status"] = "erro"
            tarefa["atualizada_em"] = agora()

            return jsonify({
                "mensagem": "Tarefa marcada como erro",
                "tarefa": tarefa
            })

    return jsonify({
        "erro": "Tarefa não encontrada"
    }), 404


# =========================
# CRIAR AGENTE
# =========================

@app.route("/agentes", methods=["POST"])
def criar_agente():

    dados = request.get_json(silent=True) or {}

    nome = dados.get("nome", "Agente V17")
    especialidade = dados.get(
        "especialidade",
        "geral"
    )

    agente = {
        "id": criar_id(),
        "nome": nome,
        "especialidade": especialidade,
        "status": "ativo",
        "criado_em": agora()
    }

    agentes.append(agente)

    return jsonify({
        "mensagem": "Agente criado com sucesso",
        "agente": agente
    }), 201


# =========================
# LISTAR AGENTES
# =========================

@app.route("/agentes", methods=["GET"])
def listar_agentes():

    return jsonify({
        "total": len(agentes),
        "agentes": agentes
    })


# =========================
# EXECUTAR TAREFA
# =========================

@app.route("/executar/<tarefa_id>", methods=["POST"])
def executar_tarefa(tarefa_id):

    for tarefa in tarefas:

        if tarefa["id"] == tarefa_id:

            if tarefa["status"] == "concluida":
                return jsonify({
                    "mensagem": "Essa tarefa já foi concluída"
                })

            tarefa["status"] = "executando"
            tarefa["atualizada_em"] = agora()

            return jsonify({
                "mensagem": "Tarefa enviada para execução",
                "tarefa": tarefa
            })

    return jsonify({
        "erro": "Tarefa não encontrada"
    }), 404


# =========================
# ESTATÍSTICAS
# =========================

@app.route("/estatisticas")
def estatisticas():

    total = len(tarefas)

    concluidas = sum(
        1 for t in tarefas
        if t["status"] == "concluida"
    )

    executando = sum(
        1 for t in tarefas
        if t["status"] == "executando"
    )

    pendentes = sum(
        1 for t in tarefas
        if t["status"] == "pendente"
    )

    erros = sum(
        1 for t in tarefas
        if t["status"] == "erro"
    )

    taxa = 0

    if total > 0:
        taxa = round(
            (concluidas / total) * 100,
            2
        )

    return jsonify({
        "total": total,
        "concluidas": concluidas,
        "executando": executando,
        "pendentes": pendentes,
        "erros": erros,
        "taxa_conclusao": f"{taxa}%"
    })


# =========================
# INICIAR SERVIDOR
# =========================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
