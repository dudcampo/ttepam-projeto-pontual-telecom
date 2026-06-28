import sqlite3


NOME_BANCO = "estoque.db" # nome dado ao banco de dados da aplicacao

def conectar():  #esta funcao sera responsavel por criar uma conexao com o banco
        return sqlite3.connect(NOME_BANCO) # Ela esta presente em todas as demais funcoes

def criar_tabelas(): #cria as tabelas. caso ja estejam criadas, so ignora e segue
        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                       id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                       nome TEXT NOT NULL,
                       login TEXT NOT NULL UNIQUE,
                       senha_hash TEXT NOT NULL,
                       tipo_usuario TEXT NOT NULL CHECK (tipo_usuario IN ('admin', 'funcionario')),
                       data_cadastro TEXT DEFAULT (datetime('now'))
                       )
        """)
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS produtos (
                       id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
                       nome TEXT NOT NULL,
                       tipo TEXT,
                       tag TEXT,
                       quantidade INTEGER NOT NULL DEFAULT 0,
                       data_cadastro TEXT DEFAULT (datetime('now'))
                       )
        """)
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS movimentacoes (
                       id_movimentacao INTEGER PRIMARY KEY AUTOINCREMENT,
                       id_produto INTEGER NOT NULL,
                       id_usuario INTEGER NOT NULL,
                       tipo TEXT NOT NULL CHECK(tipo IN ('entrada', 'saida')),
                       quantidade INTEGER NOT NULL,
                       destino_finalidade TEXT,
                       data_hora TEXT DEFAULT (datetime('now')),
                       FOREIGN KEY (id_produto) REFERENCES produtos(id_produto),
                       FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
                        )
        """)
        conexao.commit()
        conexao.close()

#PARTE DE USUARIOS
def inserir_usuario(nome,login,senha_hash,tipo_usuario):
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("""
                INSERT INTO usuarios (nome,login,senha_hash,tipo_usuario)
                VALUES (?,?,?,?)""",
                (nome, login, senha_hash, tipo_usuario)        
        )
        conexao.commit()
        id_usuario = cursor.lastrowid
        conexao.close()
        return id_usuario

def autenticar_usuario(login, senha_hash):
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute(
                """SELECT id_usuario, nome, login, tipo_usuario
                FROM usuarios 
                WHERE login = ?
                AND senha_hash = ?""",
                (login,senha_hash)
        )
        usuario = cursor.fetchone()
        conexao.close()
        return usuario

def buscar_usuario_por_id(id_usuario):
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute(
                """SELECT id_usuario, nome, login, tipo_usuario
                FROM usuarios WHERE id_usuario = ?""",
                (id_usuario,)
        )
        usuario = cursor.fetchone()
        conexao.close()
        return usuario

#PARTE DE PRODUTOS
def inserir_produto(nome, tipo, tag, quantidade_inicial, id_usuario):
        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute(
                """INSERT INTO produtos (nome, tipo, tag, quantidade)
                VALUES (?, ?, ?, 0)""",
                (nome, tipo, tag)
        )
        id_produto = cursor.lastrowid
        conexao.commit()
        conexao.close()

        if quantidade_inicial and quantidade_inicial > 0:
                registrar_movimentacao(
                        id_produto=id_produto,
                        id_usuario=id_usuario,
                        tipo="entrada",
                        quantidade=quantidade_inicial
                )
        
        return id_produto

def buscar_produto(termo):

        conexao = conectar()
        cursor = conexao.cursor()
        termo_like = f"%{termo}%"
        cursor.execute(
                """SELECT id_produto, nome, tipo, tag, quantidade
                FROM produtos
                WHERE nome LIKE ? OR tag LIKE ? OR tipo LIKE ?""",
                (termo_like, termo_like, termo_like)
        )
        resultados = cursor.fetchall()
        conexao.close()
        return resultados

def listar_produtos():
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute(
                "SELECT id_produto, nome, tipo, tag, quantidade FROM produtos"
        )
        resultados = cursor.fetchall()
        conexao.close()
        return resultados

def excluir_produto(id_produto,usuario_logado):
        if usuario_logado["tipo_usuario"] != "admin":
                raise PermissionError("Apenas administradores podem excluir produtos")
        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute(
                "SELECT COUNT(*) FROM movimentacoes WHERE id_produto = ?",
        (id_produto,)
        )
        tem_movimentacao = cursor.fetchone()[0] > 0

        if tem_movimentacao:
                conexao.close()
                raise ValueError("Produto possui histórico de movimentação e não pode ser excluído")
        
        cursor.execute("DELETE FROM produtos WHERE id_produto = ?",(id_produto,))
        conexao.commit()
        conexao.close()

#MOVIMENTACOES DO SISTEMA
def registrar_movimentacao(id_produto, id_usuario, tipo, quantidade, destino_finalidade=None):
        if tipo not in ("entrada","saida"):
                raise ValueError("Tipo deve ser 'entrada' ou 'saida'.")
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute(
                """INSERT INTO movimentacoes
                (id_produto, id_usuario, tipo, quantidade, destino_finalidade)
                VALUES (?, ?, ?, ?, ?)""",
                (id_produto, id_usuario, tipo, quantidade, destino_finalidade)
        )        

        if tipo =="entrada":
                cursor.execute(
                        "UPDATE produtos SET quantidade = quantidade + ? WHERE id_produto = ?",
                        (quantidade, id_produto)
                )
        else: #saída
                cursor.execute(
                        "UPDATE produtos SET quantidade = quantidade - ? WHERE id_produto = ?",
                        (quantidade, id_produto)
                )
        conexao.commit()
        id_movimentacao = cursor.lastrowid
        conexao.close()
        return id_movimentacao

def listar_historico(id_produto=None, id_usuario=None):
        conexao = conectar()
        cursor = conexao.cursor()
        query = """
        SELECT m.id_movimentacao, p.nome AS produto, u.nome AS usuario,
        m.tipo, m.quantidade,m.destino_finalidade, m.data_hora
        FROM movimentacoes m
        JOIN produtos p ON m.id_produto = p.id_produto
        JOIN usuarios u ON m.id_usuario = u.id_usuario
        WHERE 1=1
        """
        parametros =[]
        if id_produto:
                query += " AND m.id_produto = ?"
                parametros.append(id_produto)
        if id_usuario:
                query += " AND m.id_usuario = ?"
                parametros.append(id_usuario)
        query+=" ORDER BY m.data_hora DESC"
        cursor.execute(query,parametros)
        resultados = cursor.fetchall()
        conexao.close()
        return resultados

                
