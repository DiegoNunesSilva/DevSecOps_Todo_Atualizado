# Importa bibliotecas necessárias
from flask import Flask, request, jsonify   # Flask para criar API, request/jsonify para lidar com dados JSON
from flask_sqlalchemy import SQLAlchemy     # SQLAlchemy para abstrair o banco de dados
import os                                   # os para ler variáveis de ambiente

# Cria a aplicação Flask
app = Flask(__name__)

# Configuração do banco de dados
# Primeiro tenta usar a variável de ambiente DATABASE_URL (ex.: PostgreSQL)
# Se não existir, usa SQLite local como fallback (útil para testes)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'sqlite:///database.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desativa recurso que gera overhead

# Inicializa o objeto de banco
db = SQLAlchemy(app)

# Define o modelo da tabela "tarefas"
# Cada instância de Tarefa será uma linha no banco
class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)         # chave primária
    titulo = db.Column(db.String(100), nullable=False)   # título da tarefa (obrigatório)
    status = db.Column(db.String(20), default='pendente')# status com valor padrão "pendente"

# Cria as tabelas no banco (se não existirem)
with app.app_context():
    db.create_all()

# ---------------- ROTAS ---------------- #

# Rota para listar todas as tarefas
@app.route("/tarefas", methods=["GET"])
def listar_tarefas():
    tarefas = Tarefa.query.all()  # busca todas as tarefas no banco
    # transforma em lista de dicionários para retornar como JSON
    return jsonify([{"id": t.id, "titulo": t.titulo, "status": t.status} for t in tarefas])

# Rota para adicionar uma nova tarefa
@app.route("/tarefas", methods=["POST"])
def adicionar_tarefa():
    titulo = request.json["titulo"]                     # pega título enviado no corpo da requisição
    status = request.json.get("status", "pendente")     # pega status, se não vier usa "pendente"
    nova = Tarefa(titulo=titulo, status=status)         # cria objeto Tarefa
    db.session.add(nova)                                # adiciona ao banco
    db.session.commit()                                 # salva mudanças
    return jsonify({"mensagem": "Tarefa adicionada com sucesso!"})

# Rota para atualizar uma tarefa existente
@app.route("/tarefas/<int:id>", methods=["PUT"])
def atualizar_tarefa(id):
    tarefa = Tarefa.query.get_or_404(id)                # busca tarefa pelo ID, retorna erro 404 se não existir
    if "titulo" in request.json:                        # se veio título no corpo da requisição
        tarefa.titulo = request.json["titulo"]
    if "status" in request.json:                        # se veio status
        tarefa.status = request.json["status"]
    db.session.commit()                                 # salva mudanças
    return jsonify({"mensagem": "Tarefa atualizada com sucesso!"})

# Rota para remover uma tarefa
@app.route("/tarefas/<int:id>", methods=["DELETE"])
def remover_tarefa(id):
    tarefa = Tarefa.query.get_or_404(id)                # busca tarefa pelo ID
    db.session.delete(tarefa)                           # remove do banco
    db.session.commit()                                 # salva mudanças
    return jsonify({"mensagem": "Tarefa removida com sucesso!"})

# Inicializa a aplicação
if __name__ == "__main__":
    # host=0.0.0.0 permite acesso externo (necessário em Docker)
    # port=5000 define a porta
    app.run(host="0.0.0.0", port=5000, debug=True)
