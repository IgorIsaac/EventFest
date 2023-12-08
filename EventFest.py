import sqlite3 
from datetime import datetime 
from abc import ABC, abstractmethod 
from enum import Enum

# Classe abstrata Evento
class Evento(ABC):
    @abstractmethod
    def esta_ativo(self):
        pass

    @abstractmethod
    def esta_proximo(self):
        pass

    @abstractmethod
    def ja_passou(self):
        pass

# Classe EventoConcreto que herda de Evento
class EventoConcreto(Evento):
    def __init__(self, nome, endereco, cep, preco, categoria, data, hora, descricao):
        # Inicializa as informações do evento
        self.nome = nome
        self.endereco = endereco
        self.cep = cep
        self.preco = float(preco)
        self.categoria = categoria
        self.data = datetime.strptime(data, "%d/%m/%Y")
        self.hora = hora
        self.descricao = descricao
        self.participantes = []

    def esta_ativo(self):
        # Verifica se o evento está ativo comparando a data/hora atual com a do evento
        data_hora_atual = datetime.now()
        data_hora_evento = datetime.combine(self.data, datetime.strptime(self.hora, "%H:%M").time())
        return data_hora_atual >= data_hora_evento

    def esta_proximo(self):
        # Verifica se o evento está próximo comparando a data/hora atual com a do evento
        data_hora_atual = datetime.now()
        data_hora_evento = datetime.combine(self.data, datetime.strptime(self.hora, "%H:%M").time())
        return data_hora_atual < data_hora_evento

    def ja_passou(self):
        # Verifica se o evento já passou comparando a data/hora atual com a do evento
        data_hora_atual = datetime.now()
        data_hora_evento = datetime.combine(self.data, datetime.strptime(self.hora, "%H:%M").time())
        return data_hora_atual > data_hora_evento

class Usuario:
    def __init__(self, nome, idade, sexo, telefone, endereco, cep):
        # Inicializa as informações do usuário
        self.nome = nome
        self.idade = int(idade)
        self.sexo = sexo
        self.telefone = telefone
        self.endereco = endereco
        self.cep = cep

class Participacoes:
    def __init__(self, id, evento_nome, participante):
        # Inicializa as informações da participação
        self.id = id
        self.evento_nome = evento_nome
        self.participante = participante

# Classe para manipulação de dados no banco SQLite
class ManipuladorDados:
    def __init__(self, nome_banco):
        # Inicializa o banco de dados
        self.nome_banco = nome_banco
        self.conexao = sqlite3.connect(self.nome_banco)
        self.criar_tabelas() # Chama o método para criar tabelas no banco

    def criar_tabelas(self):
        # Criação das tabelas se não existirem
        cursor = self.conexao.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                idade INTEGER,
                sexo TEXT,
                telefone TEXT,
                endereco TEXT,
                cep TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Eventos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                endereco TEXT,
                cep TEXT,
                preco REAL,
                categoria TEXT,
                data DATE,
                hora TEXT,
                descricao TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Participacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evento_nome TEXT,
                participante TEXT,
                FOREIGN KEY (evento_nome) REFERENCES Eventos (nome)
            )
        """)
        self.conexao.commit()

    def carregar_dados(self):
        # Carrega os dados do banco de dados
        cursor = self.conexao.cursor()
        cursor.execute("SELECT * FROM Usuarios")
        usuarios = cursor.fetchall()
        usuarios = [Usuario(*usuario[1:]) for usuario in usuarios]

        cursor.execute("SELECT * FROM Eventos")
        eventos = cursor.fetchall()
        eventos = [
            EventoConcreto(*evento[1:9]) for evento in eventos
        ]

        cursor.execute("SELECT * FROM Participacoes")
        participacoes = cursor.fetchall()
        finalParticipacoes = []
        for participacao in participacoes:
            finalParticipacoes.append(Participacoes(participacao[0], participacao[1], participacao[2]))
        
        participacoes = finalParticipacoes

        if not usuarios and not eventos:
            print("Não há usuários ou eventos registrados no sistema.")
        
        return {'usuarios': usuarios, 'eventos': eventos, 'participacoes': participacoes }

# Método para salvar dados no banco de dados
    def salvar_dados(self, dados, usuario, evento, usuario_participacao, evento_participacao, participacoes):
        cursor = self.conexao.cursor()
       
        if(usuario != None):
            cursor.execute("""
            INSERT INTO Usuarios (nome, idade, sexo, telefone, endereco, cep)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (usuario.nome, usuario.idade, usuario.sexo, usuario.telefone, usuario.endereco, usuario.cep))
       
        if(evento != None):
            cursor.execute("""
            INSERT INTO Eventos (nome, endereco, cep, preco, categoria, data, hora, descricao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (evento.nome, evento.endereco, evento.cep, evento.preco, evento.categoria, evento.data.strftime('%d/%m/%Y'), evento.hora, evento.descricao))

        if(evento_participacao != None and usuario_participacao != None):  
            cursor.execute("""
            INSERT INTO Participacoes (evento_nome, participante)
            VALUES (?, ?)
        """, (evento_participacao.nome, usuario_participacao.nome))
            

        if(participacoes != None):
            cursor.execute("DELETE FROM Participacoes")
            for participacao in participacoes:
                            cursor.execute("""
                INSERT INTO Participacoes (evento_nome, participante)
                VALUES (?, ?)
            """, (participacao.participante, participacao.evento_nome))

        self.conexao.commit()

# Método para buscar participantes
    def buscar_participantes(self):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT * FROM Participacoes")
        cursor.fetchall()
        self.conexao.commit()
        
# Método para apagar participação
    def apagar_participacao(self, evento, usuario):
        try:  
            conn = sqlite3.connect('dados.db')
            cursor = conn.cursor()
            consulta_sql = f"DELETE FROM Participacoes WHERE evento_nome = ? AND participante = ?"

            cursor.execute(consulta_sql, (evento.nome, usuario.nome))

            conn.commit()
            print("Registro excluído com sucesso.")
        except sqlite3.Error as e:
            print("Erro durante a exclusão:", e)

        finally:
            conn.close()

# Classe para gerenciar usuários
class GerenciadorUsuarios:
    def __init__(self, manipulador_dados):
        # Inicializa a classe GerenciadorUsuarios com um manipulador de dados fornecido
        self.manipulador_dados = manipulador_dados
        self.usuarios = []
        self.carregar_usuarios()

    def carregar_usuarios(self):
        # Carrega os dados de usuários usando o manipulador de dados
        dados = self.manipulador_dados.carregar_dados()
        if 'usuarios' in dados:
            # Se houver usuários, atualiza a lista de usuários com esses dados
            self.usuarios = dados['usuarios']

    def salvar_usuarios(self, usuario):
        # Cria um dicionário com informações de usuários e uma lista vazia para eventos
        dados = {'usuarios': self.usuarios, 'eventos': []}
        self.manipulador_dados.salvar_dados(dados, usuario, None, None, None, None)
        # Exibe uma mensagem de confirmação após salvar os usuários
        print("Usuários salvos com sucesso.")

    def cadastrar_usuario(self):
        # Método para cadastrar um novo usuário
        print("\n=== Cadastrar Novo Usuário ===")
        usuario = Usuario(input("Nome: "),
                     input("Idade: "),
                     input("Sexo (M/F): "),
                     input("Telefone: "),
                     input("Endereço: "),
                     input("CEP: "))
        self.usuarios.append(usuario)
        self.salvar_usuarios(usuario)

    def listar_usuarios(self):
        # Método para listar os usuários existentes
        print("\n=== Lista de Usuários ===")
        for usuario in self.usuarios:
            print(usuario.__dict__)

# Classe para gerenciar eventos
class GerenciadorEventos:
    def __init__(self, manipulador_dados, gerenciador_usuarios):
        # Inicialização da classe com manipulador de dados e gerenciador de usuários
        self.manipulador_dados = manipulador_dados
        self.gerenciador_usuarios = gerenciador_usuarios
        self.eventos = []
        self.participacoes = []
        self.carregar_eventos()
        self.carregar_participacoes()

    def carregar_eventos(self):
        # Método para carregar os eventos existentes
        dados = self.manipulador_dados.carregar_dados()
        if 'eventos' in dados: # Verifica se existem eventos salvos
            self.eventos = dados['eventos']

    def carregar_participacoes(self):
        # Método para carregar participações existentes nos eventos
        dados = self.manipulador_dados.carregar_dados()
        if 'participacoes' in dados: # Verifica se existem participações salvas
            self.participacoes = dados['participacoes']

    def salvar_eventos(self, evento):
        # Método para salvar os eventos
        dados = {'usuarios': [], 'eventos': self.eventos}
        self.manipulador_dados.salvar_dados(dados, None, evento, None, None, None)
        print("Eventos salvos com sucesso.")

    def salvar_participacao_evento(self, evento, usuario):
        # Método para salvar participação em um evento
            dados = {'usuarios': [], 'eventos': [], 'participacoes': self.participacoes}
            self.manipulador_dados.salvar_dados(dados, None, None, evento, usuario, None)

    def cancelar_participacao(self, evento, usuario):
         # Métodos para cancelar a participação de um usuário em um evento
        self.manipulador_dados.cancelar_participacao(evento, usuario);

    def cadastrar_evento(self):
        print("\n=== Cadastrar Novo Evento ===")
        id = 0
        while True:
            nome_evento = input("Nome do evento: ")
            endereco = input("Endereço: ")
            cep = input("CEP: ")
            preco = input("Preço: ")
            categoria = input("Categoria: ")
            data = input("Data (dd/mm/aaaa): ")
            hora = input("Hora (hh:mm): ")
            descricao = input("Descrição: ")

            try:
                datetime.strptime(data, "%d/%m/%Y")
                break
            except ValueError:
                print("Por favor, insira a data no formato dd/mm/aaaa.")

        evento = EventoConcreto(nome_evento, endereco, cep, preco, categoria, data, hora, descricao)
        self.eventos.append(evento)
        self.salvar_eventos(evento)

# Métodos para listar eventos próximos e passados
    def listar_eventos(self):
        print("\n=== Lista de Eventos ===")
        eventoNomes = []
        for evento in self.eventos:
            eventoNomes.append(evento.nome)

        dados = self.manipulador_dados.carregar_dados()
        participacoes = dados['participacoes']

        finalParticipacoes = []
        removeDuplicatas = []


        if(participacoes != []) :
            for evento in self.eventos:
                for participacao in participacoes:
                    if(participacao.participante == evento.nome):
                            finalParticipacoes.append(participacao.evento_nome)

                for final in finalParticipacoes:
                    if final not in removeDuplicatas:
                        removeDuplicatas.append(final)
                        if final not in evento.participantes:
                            evento.participantes.append(final)
                print(evento.__dict__)
                finalParticipacoes.clear()
                removeDuplicatas.clear()
        else :
            for evento in self.eventos:
                print(evento.__dict__)

    def listar_eventos_proximos(self):
        eventos_proximos = [evento for evento in self.eventos if evento.esta_proximo()]
        if eventos_proximos:
            print("\n=== Lista de Eventos Próximos ===")
            for evento in eventos_proximos:
                print(evento.__dict__)
        else:
            print("Não há eventos próximos.")

    def listar_eventos_passados(self):
        eventos_passados = [evento for evento in self.eventos if evento.ja_passou()]
        if eventos_passados:
            print("\n=== Lista de Eventos Passados ===")
            for evento in eventos_passados:
                print(evento.__dict__)
        else:
            print("Não há eventos passados.")

    def participar_evento(self):
        # Métodos para participar e cancelar participação em eventos
        print("\n=== Participar de Evento ===")
        nome_evento = input("Nome do evento: ").strip()
        usuario_nome = input("Nome do usuário: ")

        evento_encontrado = None
        for evento in self.eventos:
            if evento.nome.strip() == nome_evento:
                evento_encontrado = evento
                break

        if evento_encontrado:
            usuario_encontrado = None
            for usuario in self.gerenciador_usuarios.usuarios:
                if usuario.nome == usuario_nome:
                    usuario_encontrado = usuario
                    break

            if usuario_encontrado:
                print(f"{usuario_encontrado.nome} participou do evento {evento_encontrado.nome}.")
                self.salvar_participacao_evento(evento_encontrado, usuario_encontrado)
                print("Participação salva")

            else:
                print(f"Usuário {usuario_nome} não encontrado.")
        else:
            print(f"Evento {nome_evento} não encontrado.")
            
    def cancelar_participacao(self):
        # Método para cancelar participação
        print("\n=== Cancelar Participação em Evento ===")
        nome_evento = input("Nome do evento: ").strip()
        nome_usuario = input("Nome do usuário: ")

        evento_encontrado = None
        for evento in self.eventos:
            if evento.nome.strip() == nome_evento:
                evento_encontrado = evento
                break

        if evento_encontrado:
            usuario_encontrado = None
            for usuario in self.gerenciador_usuarios.usuarios:
                if usuario.nome == nome_usuario:
                    usuario_encontrado = usuario
                    break

            if usuario_encontrado:
                if usuario_encontrado.nome in evento_encontrado.participantes:
                    evento_encontrado.participantes.remove(usuario_encontrado.nome)
                    print(f"{usuario_encontrado.nome} cancelou a participação no evento {evento_encontrado.nome}.")
                    self.manipulador_dados.apagar_participacao(evento_encontrado, usuario_encontrado)
                    dados = self.manipulador_dados.carregar_dados()
                    participacoes = dados['participacoes']

                    for participacao in participacoes:
                        if participacao.evento_nome == usuario_encontrado.nome and participacao.participante == evento_encontrado.nome:
                            participacoes.remove(participacao)
    
                    self.manipulador_dados.salvar_dados(dados, None, None, evento, usuario, participacoes)
                else:
                    print(f"O usuário {usuario_encontrado.nome} não está participando do evento {evento_encontrado.nome}.")
            else:
                print(f"Usuário {nome_usuario} não encontrado.")
        else:
            print(f"Evento {nome_evento} não encontrado.")
            
    def listar_eventos_do_usuario(self):
        # Método para listar os eventos de um usuário específico
        nome_usuario = input("Digite o nome do usuário para listar os eventos: ")
        eventos_usuario = []
        final_eventos_usuario = []

        dados = self.manipulador_dados.carregar_dados()
        participacoes = dados['participacoes']

        for participacao in participacoes:
            if(participacao.evento_nome == nome_usuario):
                eventos_usuario.append(participacao.participante)

        # Filtra os eventos do usuário específico
        if eventos_usuario != []:
            for evento in self.eventos:
                if evento.nome in eventos_usuario:
                    final_eventos_usuario.append(evento.nome)

            print(f"\n=== Eventos do usuário {nome_usuario} ===")
            for evento in final_eventos_usuario:
                print(evento)
        else:
            print(f"Não há eventos para o usuário {nome_usuario}.")

# Classe Menu
class Menu:
    def __init__(self, gerenciador_usuarios, gerenciador_eventos):
        self.gerenciador_usuarios = gerenciador_usuarios
        self.gerenciador_eventos = gerenciador_eventos

    def exibir_menu(self):
        # Exibe as opções do menu
        print("\n===== MENU =====")
        print("1. Cadastrar evento")
        print("2. Cadastrar usuário")
        print("3. Listar usuários")
        print("4. Listar eventos")
        print("5. Listar eventos próximos")
        print("6. Listar eventos passados")
        print("7. Participar de evento")
        print("8. Cancelar participação de evento")
        print("9. Listar eventos do usuário")
        print("10. Sair")

    def executar(self):
        while True:
            self.exibir_menu() # Mostra o menu
            escolha = input("\nEscolha uma opção: ") # Solicita a escolha do usuário
            # Realiza a operação de acordo com a escolha do usuário
            if escolha == '1':
                self.gerenciador_eventos.cadastrar_evento()
            elif escolha == '2':
                self.gerenciador_usuarios.cadastrar_usuario()
            elif escolha == '3':
                self.gerenciador_usuarios.listar_usuarios()
            elif escolha == '4':
                self.gerenciador_eventos.listar_eventos()
            elif escolha == '5':
                self.gerenciador_eventos.listar_eventos_proximos()
            elif escolha == '6':
                self.gerenciador_eventos.listar_eventos_passados()
            elif escolha == '7':
                self.gerenciador_eventos.participar_evento()
            elif escolha == '8':
                self.gerenciador_eventos.cancelar_participacao()
            elif escolha == '9':
                self.gerenciador_eventos.listar_eventos_do_usuario()
            elif escolha == '10':
                print("\nPrograma encerrado. Obrigado por usar o sistema!")
                break
            else:
                print("\nOpção inválida. Por favor, escolha uma opção válida.")
                
# Inicialização das classes e execução do menu
nome_banco = "dados.db"
manipulador = ManipuladorDados(nome_banco)
gerenciador_usuarios = GerenciadorUsuarios(manipulador)
gerenciador_eventos = GerenciadorEventos(manipulador, gerenciador_usuarios)

menu = Menu(gerenciador_usuarios, gerenciador_eventos)
menu.executar()
