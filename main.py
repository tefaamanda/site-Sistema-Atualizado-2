from flask import Flask, render_template, redirect, url_for, flash, request, session
import fdb
from datetime import datetime
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'grupo2'

host = 'localhost'
database = r'C:\Users\Aluno\Downloads\siteFinanceiroBanco\BANCODADOS.FDB'
user = 'SYSDBA'
password = 'sysdba'

# Conexão
con = fdb.connect(host=host, database=database, user=user, password=password)

class Usuario:
    def __init__(self, id_usuario, nome, email, senha):
        self.id = id_usuario
        self.nome = nome
        self.email = email
        self.senha = senha

class Despesa:
    def __init__(self, id_usuario, id_despesa, nome, valor, data_despesa, descricao):
        self.id_usuario = id_usuario
        self.id_despesa = id_despesa
        self.nome = nome
        self.valor = valor
        self.data_despesa = data_despesa
        self.descricao = descricao


class Receita:
    def __init__(self, id_usuario, id_receita, nome, valor, data_receita, descricao):
        self.id_usuario = id_usuario
        self.id_receita = id_receita
        self.nome = nome
        self.valor = valor
        self.data_receita = data_receita
        self.descricao = descricao



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/abrir_login')
def abrir_login():
    return render_template('login.html')


@app.route('/abrir_cad_despesa')
def abrir_cad_despesa():
    if 'id_usuario' not in session:
        flash('Você precisa estar logado para acessar a página.')
        return redirect(url_for('login'))

    return render_template('cadastroDespesa.html')


@app.route('/abrir_cad_receita')
def abrir_cad_receita():
    if 'id_usuario' not in session:
        flash('Você precisa estar logado para acessar a página')
        return redirect(url_for('login'))
    return render_template('cadastroReceita.html')

@app.route('/excluirDespesa/<int:id>')
def excluirDespesa(id):
    if 'id_usuario' not in session:
        flash('Você precisa estar logado para acessar a página')
        return redirect(url_for('login'))

    # Recuperar a receita do banco de dados
    cursor = con.cursor()
    cursor.execute('SELECT * FROM despesa WHERE id_despesa = ?', (id,))
    despesa = cursor.fetchone()
    cursor.close()

    # Se a receita não for encontrada, exibe um erro
    if despesa is None:
        flash('Erro ao encontrar despesa.', 'error')
        return redirect(url_for('listaDespesa'))

    # Passando a variável receita para o template
    return render_template('excluirDespesa.html', despesa=despesa)


@app.route('/excluirReceita/<int:id>', methods=['GET'])
def excluirReceita(id):
    if 'id_usuario' not in session:
        flash('Você precisa estar logado para acessar a página')
        return redirect(url_for('login'))

    # Recuperar a receita do banco de dados
    cursor = con.cursor()
    cursor.execute('SELECT * FROM receita WHERE id_receita = ?', (id,))
    receita = cursor.fetchone()
    cursor.close()

    # Se a receita não for encontrada, exibe um erro
    if receita is None:
        flash('Erro ao encontrar receita.', 'error')
        return redirect(url_for('listaReceita'))

    # Passando a variável receita para o template
    return render_template('excluirReceita.html', receita=receita)


@app.route('/listaDespesa')
def listaDespesa():

    if 'id_usuario' not in session:
        flash('Você precisa estar logado para acessar a página')
        return redirect(url_for('login'))


    id_usuario = session['id_usuario']
    cursor = con.cursor()
    cursor.execute("SELECT d.ID_DESPESA , d.NOME, d.VALOR, d.DATA_DESPESA, d.DESCRICAO FROM DESPESA d WHERE d.ID_USUARIO  = ?", (id_usuario,))
    despesas = cursor.fetchall()
    return render_template('listaDespesa.html', despesas=despesas)

@app.route('/listaReceita')
def listaReceita():
    if 'id_usuario' not in session:
        flash('Você precisa estar logado para acessar a página')
        return redirect(url_for('login'))

    id_usuario = session['id_usuario']
    cursor = con.cursor()
    cursor.execute("SELECT r.ID_RECEITA ,r.NOME, r.VALOR, r.DATA_RECEITA, r.DESCRICAO FROM RECEITA r WHERE r.ID_USUARIO  = ?", (id_usuario,))
    receitas = cursor.fetchall()

    return render_template('listaReceita.html', receitas=receitas)

@app.route('/inicial')
def inicial():

    if 'id_usuario' not in session:
        flash('Você precisa estar logado para acessar a página')
        return redirect(url_for('login'))

    cursor = con.cursor()

    id_usuario = session['id_usuario']

    # Buscar as despesas e receitas para exibição
    cursor.execute("SELECT ID_DESPESA, NOME, VALOR, DATA_DESPESA, DESCRICAO FROM DESPESA WHERE ID_USUARIO = ?" ,(id_usuario,))
    despesas = cursor.fetchall()
    cursor.execute("SELECT ID_RECEITA, NOME, VALOR, DATA_RECEITA, DESCRICAO FROM RECEITA WHERE ID_USUARIO = ?", (id_usuario,))
    receitas = cursor.fetchall()

    # Variáveis para os totais
    total_receita = 0
    total_despesa = 0

    # Verifique se o usuário está logado
    if 'id_usuario' not in session:
        flash('Você precisa estar logado no sistema.')
        return redirect(url_for('login'))

    id_usuario = session['id_usuario']

    # Logs para depuração
    print(f"ID Usuário na sessão: {id_usuario}")

    # Cria um novo cursor para calcular os totais
    try:
        # Consulta para somar receitas
        cursor.execute('SELECT coalesce(VALOR, 0) FROM RECEITA WHERE id_usuario = ?', (id_usuario,))
        receitas_db = cursor.fetchall()  # Obtém todos os valores de receita
        print(f"Valores das receitas: {receitas_db}")

        for row in receitas_db:
            total_receita += row[0]

        # Consulta para somar despesas
        cursor.execute('SELECT coalesce(VALOR, 0) FROM DESPESA WHERE id_usuario = ?', (id_usuario,))
        despesas_db = cursor.fetchall()  # Obtém todos os valores de despesa
        print(f"Valores das despesas: {despesas_db}")

        for row in despesas_db:
            total_despesa += row[0]

        total_perda_lucro = total_receita - total_despesa

    except Exception as e:
        total_receita = 0
        total_despesa = 0
        total_perda_lucro = 0
        print(f"Erro ao buscar totais: {str(e)}")
        print(f"Tipo do erro: {type(e)}")

    # Fecha o cursor após as operações
    cursor.close()

    # Formata os totais para exibição
    total_receita = f"{total_receita:.2f}"
    total_despesa = f"{total_despesa:.2f}"
    total_perda_lucro = f"{total_perda_lucro:.2f}"

    # Renderiza o template com os valores calculados
    return render_template('inicial.html', despesas=despesas, receitas=receitas, total_receita=total_receita, total_despesa=total_despesa, total_perda_lucro=total_perda_lucro)


@app.route('/cadastroDespesa')
def cadastroDespesa():

    if 'id_usuario' not in session:
        flash('Você precisa estar logado para acessar a página')
        return redirect(url_for('login'))

    cursor = con.cursor()
    cursor.execute("SELECT ID_DESPESA, NOME, VALOR, DATA_DESPESA, DESCRICAO FROM DESPESA")
    despesa = cursor.fetchall()
    cursor.close()
    return render_template('cadastroDespesa.html', despesa=despesa)


@app.route('/cadastroReceita')
def cadastroReceita():

    if 'id_usuario' not in session:
        flash('Você precisa estar logado para acessar a página')
        return redirect(url_for('login'))

    cursor = con.cursor()
    cursor.execute("SELECT ID_RECEITA, NOME, VALOR, DATA_RECEITA, DESCRICAO FROM RECEITA")
    receita = cursor.fetchall()
    cursor.close()
    return render_template('cadastroReceita.html', receita=receita)

@app.route('/criarDespesa', methods=['POST'])
def criarDespesa():

    if 'id_usuario' not in session:
        flash('Você precisa estar logado para acessar a página')
        return redirect(url_for('login'))

    nome = request.form['nome']
    valor = request.form['valor']
    data_despesa = request.form['data_despesa']
    descricao = request.form['descricao']
    cursor = con.cursor()
    id_usuario = session['id_usuario']
    try:
        cursor.execute("SELECT 1 FROM despesa WHERE VALOR = ? and DATA_DESPESA = ?", (valor,data_despesa))
        if cursor.fetchone():
            flash('Erro: O valor da despesa já foi cadastrado neste dia!', "error")
            return redirect(url_for('cadastroDespesa'))  # Corrigido aqui
        cursor.execute("INSERT INTO despesa (NOME, VALOR, DATA_DESPESA, DESCRICAO, ID_USUARIO) VALUES (?, ?, ?, ?,?)",
                       (nome, valor, data_despesa, descricao, id_usuario))
        con.commit()
        print(id_usuario)
    except Exception as e:
        flash(f"Erro ao criar despesa: {e}", "error")
        return redirect(url_for('cadastroDespesa'))  # Corrigido aqui
    finally:
        cursor.close()
        flash("Despesa cadastrada com sucesso!", "success")
        return redirect(url_for('listaDespesa'))  # Corrigido aqui

@app.route('/criarReceita', methods=['POST'])
def criarReceita():

    if 'id_usuario' not in session:
        flash('Você precisa estar logado para acessar a página')
        return redirect(url_for('login'))

    nome = request.form['nome']
    valor = request.form['valor']
    data_receita = request.form['data_receita']
    descricao = request.form['descricao']
    cursor = con.cursor()
    id_usuario = session['id_usuario']
    try:
        cursor.execute("SELECT 1 FROM receita WHERE VALOR = ? AND DATA_RECEITA = ?", (valor, data_receita))
        if cursor.fetchone():
            flash('Erro: O valor da receita já foi cadastrado neste dia!', "error")
            return redirect(url_for('cadastroReceita'))  # Corrigido aqui
        cursor.execute("INSERT INTO receita (NOME, VALOR, DATA_RECEITA, DESCRICAO, ID_USUARIO) VALUES (?, ?, ?, ?, ?)",
                       (nome, valor, data_receita, descricao, id_usuario))
        con.commit()
        print(id_usuario)
    except Exception as e:
        flash(f"Erro ao criar receita: {e}", "error")
        return redirect(url_for('cadastroReceita'))  # Corrigido aqui
    finally:
        cursor.close()
        flash("Receita cadastrada com sucesso!", "success")
        return redirect(url_for('listaReceita'))  # Corrigido aqui

@app.route('/editarDespesa/<int:id>', methods=['GET', 'POST'])
def editarDespesa(id):

    if 'id_usuario' not in session:
        flash('Você precisa estar logado para acessar a página')
        return redirect(url_for('login'))

    cursor = con.cursor()
    cursor.execute("SELECT id_despesa, nome, valor, data_despesa, descricao FROM despesa WHERE id_despesa = ?", (id,))
    despesa = cursor.fetchone()
    if not despesa:
        cursor.close()
        flash("Despesa não encontrada", "error")
        return redirect(url_for('index'))  # Corrigido aqui
    if request.method == 'POST':
        nome = request.form['nome']
        valor = request.form['valor']
        data_despesa = request.form['data_despesa']
        descricao = request.form['descricao']
        cursor.execute("UPDATE despesa SET nome = ?, valor = ?, data_despesa = ?, descricao = ? WHERE id_despesa = ?",
                       (nome, valor, data_despesa, descricao, id))
        con.commit()
        cursor.close()
        flash("Despesa atualizada com sucesso!", "success")
        return redirect(url_for('listaDespesa'))  # Corrigido aqui
    cursor.close()
    return render_template('editarDespesa.html', despesa=despesa, valor='Editar Despesa')

@app.route('/editarReceita/<int:id>', methods=['GET', 'POST'])
def editarReceita(id):

    if 'id_usuario' not in session:
        flash('Você precisa estar logado para acessar a página')
        return redirect(url_for('login'))

    cursor = con.cursor()
    cursor.execute("SELECT id_receita, nome, valor, data_receita, descricao FROM receita WHERE id_receita = ?", (id,))
    receita = cursor.fetchone()
    if not receita:
        cursor.close()
        flash("Receita não encontrada", "error")
        return redirect(url_for('index'))  # Corrigido aqui
    if request.method == 'POST':
        nome = request.form['nome']
        valor = request.form['valor']
        data_receita = request.form['data_receita']
        descricao = request.form['descricao']
        cursor.execute("UPDATE receita SET nome = ?, valor = ?, data_receita = ?, descricao = ? WHERE id_receita = ?",
                       (nome, valor, data_receita, descricao, id))
        con.commit()
        cursor.close()
        flash("Receita atualizada com sucesso!", "success")
        return redirect(url_for('listaReceita'))  # Corrigido aqui
    cursor.close()
    return render_template('editarReceita.html', receita=receita, valor='Editar Receita')

@app.route('/deletarDespesa/<int:id>', methods=['POST'])
def deletarDespesa(id):

    if 'id_usuario' not in session:
        flash('Você precisa estar logado para acessar a página')
        return redirect(url_for('login'))


    cursor = con.cursor()
    try:
        cursor.execute('DELETE FROM despesa WHERE id_despesa = ?', (id,))
        con.commit()
        flash("Despesa excluída com sucesso!", "success")
    except Exception as e:
        con.rollback()
        flash('Erro ao excluir despesa.', 'error')
    finally:
        cursor.close()
    return redirect(url_for('listaDespesa'))

@app.route('/deletarReceita/<int:id>', methods=['POST'])
def deletarReceita(id):

    if 'id_usuario' not in session:
        flash('Você precisa estar logado para acessar a página')
        return redirect(url_for('login'))


    cursor = con.cursor()
    try:
        cursor.execute('DELETE FROM receita WHERE id_receita = ?', (id,))
        con.commit()
        flash("Receita excluída com sucesso!", "success")
    except Exception as e:
        con.rollback()
        flash('Erro ao excluir receita.', 'error')
    finally:
        cursor.close()
    return redirect(url_for('listaReceita'))

@app.route('/cria_usuario', methods=['GET'])
def cria_usuario():
    return render_template('cadastro.html')

def validar_senha(senha):
    # Expressão regular para validar a senha
    padrao = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'

# Verifica se a senha atende ao padrão
    if re.fullmatch(padrao, senha):
        return True
    else:
        return False

@app.route('/adiciona_usuario', methods=['POST'])
def adiciona_usuario():
    data = request.form
    nome = data['nome']
    email = data['email']
    senha = data['senha']

    if not validar_senha(senha):
        flash('A sua senha precisa ter pelo menos 8 caracteres, uma letra maiúscula, uma letra minúscula e um número.')
        return redirect(url_for('cria_usuario'))

    cursor = con.cursor()
    try:
        cursor.execute('SELECT FIRST 1 id_usuario FROM USUARIO WHERE EMAIL = ?', (email,))
        if cursor.fetchone() is not None:
            flash('Este email já está sendo usado!')
            return redirect(url_for('cria_usuario'))

        cursor.execute("INSERT INTO Usuario (nome, email, senha) VALUES (?, ?, ?)",
                           (nome, email, senha))
        con.commit()
    finally:
        cursor.close()
        flash('Usuário adicionado com sucesso!')
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        cursor = con.cursor()
        try:
            cursor.execute("SELECT id_usuario,nome FROM Usuario WHERE email = ? AND senha = ?", (email, senha,))
            usuario = cursor.fetchone()

        except Exception as e:
            flash(f'Erro ao acessar o banco de dados: {e}')
            return redirect(url_for('login.html'))
        finally:
            cursor.close()

        if usuario:
            session['id_usuario'] = usuario[0]
            session['nome'] = usuario[1]
            return redirect(url_for('inicial'))
        else:
            flash('Email ou senha incorretos!')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('id_usuario', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
