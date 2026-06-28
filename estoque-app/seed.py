"""
Este script é feito para popular o banco como teste para um start padrão do programa
Ele adiciona:
- 1 usuário  admin padrão
- 4 produtos fictícios

"""

from database.database import criar_tabelas, inserir_usuario, inserir_produto, autenticar_usuario

def popular_dados_teste():
    criar_tabelas()

    admin_existente = autenticar_usuario("admin","admin123")
    if not admin_existente:
        id_admin_existente = inserir_usuario(
            nome="Administrador",
            login="admin",
            senha_hash="admin123",
            tipo_usuario="admin"
        )
        print(f"Usuário admin criado (id_unsuario ={id_admin}, login='admin', senha='admin123')")
    else:
        id_admin = id_admin_existente[0]
        print(f"Usuário admin já existia, pulando criação")

        produtos_teste= [
            ("Ureia",   "Fertilizante Nitrogenado", "nitrogenio", 500),
            ("MAP",     "Fertilizante Fosfatado",   "fosforo",    300),
            ("KCL",     "Fertilizante Potássico",   "potassio",   250),
            ("SSP",     "Fertilizante Fosfatado",   "fosforo",    150),
        ]

        for nome, tipo, tag, quantidade in produtos_teste:
            id_produto = inserir_produto(
                nome=nome,
                tipo=tipo,
                tag=tag,
                quantidade_inicial=quantidade,
                id_usuario=id_admin
            )
            print(f"Produto '{nome}' castrado (id_produto={id_produto}, quantidade inicial = {quantidade})")

        print("\nBanco populado com sucesso!")

if __name__== "__main__":
    popular_dados_teste()