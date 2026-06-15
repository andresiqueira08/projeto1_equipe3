"""
EV Charging App — Simulação Interativa via Terminal
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Requisitos atendidos:
  [✔] CRUD completo de Usuários e Pontos de Recarga
  [✔] Estruturas de dados: dicionário, lista (vetor), tupla, matriz
  [✔] Manipulação de arquivos: dados persistidos em JSON (usuarios.json,
      pontos.json, historico.json)
"""

import json
import os
import random
import time

# ══════════════════════════════════════════════════════
# ARQUIVOS DE PERSISTÊNCIA
# ══════════════════════════════════════════════════════

ARQUIVO_USUARIOS  = "usuarios.json"
ARQUIVO_DONOS     = "donos.json"
ARQUIVO_PONTOS    = "pontos.json"
ARQUIVO_HISTORICO = "historico.json"

# ══════════════════════════════════════════════════════
# ESTRUTURAS DE DADOS (requisito explícito)
# ══════════════════════════════════════════════════════

# VETOR — lista de tipos de veículo disponíveis
VEHICLE_TYPES = ["Carro elétrico", "Moto elétrica", "Patinete elétrico"]

# VETOR — tipos de tomada suportados
PLUG_TYPES = ["Tipo 2", "CCS", "CHAdeMO", "Tesla"]

# TUPLA — campos obrigatórios de um ponto (imutável por definição)
CAMPOS_OBRIGATORIOS_PONTO = (
    "nome", "endereco", "tipo_tomada", "horario",
    "seguranca", "preco_kwh", "chave_pix", "responsavel"
)

# MATRIZ — tabela de compatibilidade veículo × tomada (vetor de vetores)
# Linhas = veículos, Colunas = tomadas (Tipo2, CCS, CHAdeMO, Tesla)
MATRIZ_COMPATIBILIDADE = [
    # Tipo2  CCS    CHAdeMO Tesla
    [True,  True,  True,  True ],   # Carro elétrico
    [True,  False, True,  False],   # Moto elétrica
    [True,  False, False, False],   # Patinete elétrico
]

# DICIONÁRIO — dados iniciais (seed) carregados caso os arquivos não existam
SEED_USUARIOS = {
    "ana@email.com": {
        "senha": "1234", "nome": "Ana Silva", "veiculo": None, "usar_gps": None
    },
    "bob@email.com": {
        "senha": "abcd", "nome": "Bob Souza", "veiculo": "Carro elétrico", "usar_gps": True
    },
}

SEED_DONOS = {
    "carlos@email.com": {
        "senha": "carlos123", "nome": "Carlos Lima",
        "cpf_cnpj": "123.456.789-00", "telefone": "(11) 99999-0001",
        "chave_pix": "carlos@pix.com", "banco": "Nubank",
    },
    "diana@email.com": {
        "senha": "diana123", "nome": "Diana Rocha",
        "cpf_cnpj": "987.654.321-00", "telefone": "(11) 99999-0002",
        "chave_pix": "diana@pix.com", "banco": "Itaú",
    },
}

SEED_PONTOS = [
    # ── Carros elétricos (Tipo 2 e CCS — maior potência) ──
    {
        "id": 1, "nome": "Ponto Centro",
        "endereco": "Rua das Flores, 100", "tipo_tomada": "Tipo 2",
        "horario": "06:00-23:00", "preco_kwh": 1.50, "disponivel": True,
        "avaliacao": 4.8, "seguranca": "Câmera 24h",
        "acessibilidade": "Rampa", "regras": "Qualquer veículo",
        "chave_pix": "carlos@pix.com", "responsavel": "Carlos Lima",
        "dono_email": "carlos@email.com",
    },
    {
        "id": 2, "nome": "Ponto Shopping Paulista",
        "endereco": "Av. Paulista, 500", "tipo_tomada": "CCS",
        "horario": "08:00-22:00", "preco_kwh": 2.00, "disponivel": False,
        "avaliacao": 4.2, "seguranca": "Portaria",
        "acessibilidade": "Elevador", "regras": "Apenas carros",
        "chave_pix": "diana@pix.com", "responsavel": "Diana Rocha",
        "dono_email": "diana@email.com",
    },
    {
        "id": 3, "nome": "Ponto Garagem Faria Lima",
        "endereco": "Av. Faria Lima, 1500", "tipo_tomada": "Tipo 2",
        "horario": "00:00-23:59", "preco_kwh": 1.80, "disponivel": True,
        "avaliacao": 4.6, "seguranca": "Circuito interno", "acessibilidade": "Elevador",
        "regras": "Apenas assinantes", "chave_pix": "faria@pix.com",
        "responsavel": "Faria Lima Park", "dono_email": "faria@email.com",
    },
    {
        "id": 4, "nome": "EletroCharge Aeroporto",
        "endereco": "Rod. dos Imigrantes, km 0", "tipo_tomada": "CCS",
        "horario": "00:00-23:59", "preco_kwh": 2.50, "disponivel": True,
        "avaliacao": 4.9, "seguranca": "Segurança 24h", "acessibilidade": "Amplo",
        "regras": "Qualquer carro elétrico", "chave_pix": "aero@pix.com",
        "responsavel": "AeroCharge", "dono_email": "aero@email.com",
    },
    {
        "id": 5, "nome": "Ponto Tesla Supercharger",
        "endereco": "Shopping Morumbi, piso B2", "tipo_tomada": "Tesla",
        "horario": "07:00-23:00", "preco_kwh": 2.20, "disponivel": True,
        "avaliacao": 4.7, "seguranca": "Câmera + segurança", "acessibilidade": "Rampa",
        "regras": "Veículos Tesla", "chave_pix": "tesla@pix.com",
        "responsavel": "Tesla Brasil", "dono_email": "tesla@email.com",
    },
    # ── Motos elétricas (Tipo 2 e CHAdeMO — menor potência) ──
    {
        "id": 6, "nome": "MotoCharge Brás",
        "endereco": "Rua Oriente, 300", "tipo_tomada": "Tipo 2",
        "horario": "07:00-20:00", "preco_kwh": 0.90, "disponivel": True,
        "avaliacao": 4.3, "seguranca": "Câmera", "acessibilidade": "Calçada plana",
        "regras": "Motos e patinetes", "chave_pix": "bras@pix.com",
        "responsavel": "João Oriente", "dono_email": "bras@email.com",
    },
    {
        "id": 7, "nome": "Ponto Residencial Vila Madalena",
        "endereco": "Rua Harmonia, 40", "tipo_tomada": "CHAdeMO",
        "horario": "08:00-22:00", "preco_kwh": 1.00, "disponivel": True,
        "avaliacao": 4.5, "seguranca": "Portão", "acessibilidade": "Sem degraus",
        "regras": "Motos e carros pequenos", "chave_pix": "vmad@pix.com",
        "responsavel": "Renata Lima", "dono_email": "vmad@email.com",
    },
    {
        "id": 8, "nome": "MotoStop Lapa",
        "endereco": "Rua Cayowaá, 55", "tipo_tomada": "Tipo 2",
        "horario": "06:00-21:00", "preco_kwh": 0.85, "disponivel": False,
        "avaliacao": 4.0, "seguranca": "Interfone", "acessibilidade": "Rampa lateral",
        "regras": "Motos apenas", "chave_pix": "lapa@pix.com",
        "responsavel": "Lapa Park Motos", "dono_email": "lapa@email.com",
    },
    # ── Patinetes elétricos (Tipo 2 — baixa potência, tomada simples) ──
    {
        "id": 9, "nome": "PatiCharge Ibirapuera",
        "endereco": "Portão 10 Parque Ibirapuera", "tipo_tomada": "Tipo 2",
        "horario": "06:00-22:00", "preco_kwh": 0.50, "disponivel": True,
        "avaliacao": 4.6, "seguranca": "Guarda parque", "acessibilidade": "Área aberta",
        "regras": "Patinetes e bikes", "chave_pix": "ibira@pix.com",
        "responsavel": "Prefeitura SP", "dono_email": "ibira@email.com",
    },
    {
        "id": 10, "nome": "PatiCharge Ciclovias Pinheiros",
        "endereco": "Av. Rebouças, 1200", "tipo_tomada": "Tipo 2",
        "horario": "00:00-23:59", "preco_kwh": 0.55, "disponivel": True,
        "avaliacao": 4.4, "seguranca": "Câmera municipal", "acessibilidade": "Ciclovia",
        "regras": "Patinetes e bikes elétricas", "chave_pix": "pinhe@pix.com",
        "responsavel": "CicloCharge", "dono_email": "pinhe@email.com",
    },
    {
        "id": 11, "nome": "Hub Mobilidade Consolação",
        "endereco": "Rua da Consolação, 800", "tipo_tomada": "Tipo 2",
        "horario": "07:00-21:00", "preco_kwh": 0.60, "disponivel": False,
        "avaliacao": 4.1, "seguranca": "Câmera", "acessibilidade": "Rampa",
        "regras": "Qualquer micromobilidade", "chave_pix": "conso@pix.com",
        "responsavel": "MobiHub", "dono_email": "conso@email.com",
    },
    # ── Multi-veículo (Tipo 2 — compatível com todos) ──
    {
        "id": 12, "nome": "Ponto Residencial Pinheiros",
        "endereco": "Rua Verde, 22", "tipo_tomada": "Tipo 2",
        "horario": "08:00-20:00", "preco_kwh": 1.20, "disponivel": True,
        "avaliacao": 4.5, "seguranca": "Interfone", "acessibilidade": "Sem degraus",
        "regras": "Qualquer veículo elétrico", "chave_pix": "eduardo@pix.com",
        "responsavel": "Eduardo Melo", "dono_email": "eduardo@email.com",
    },
]

# ══════════════════════════════════════════════════════
# MANIPULAÇÃO DE ARQUIVOS
# ══════════════════════════════════════════════════════

def carregar_json(caminho: str, padrao):
    """Lê arquivo JSON; cria o arquivo com `padrao` se não existir."""
    if not os.path.exists(caminho):
        print(f"  📄 Arquivo '{caminho}' não encontrado — criando com dados iniciais...")
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(padrao, f, ensure_ascii=False, indent=2)
        return padrao
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_json(caminho: str, dados) -> None:
    """Grava dados em arquivo JSON com indentação."""
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def carregar_dados():
    """Carrega todos os dados dos arquivos, criando-os caso não existam."""
    usuarios  = carregar_json(ARQUIVO_USUARIOS,  SEED_USUARIOS)
    donos     = carregar_json(ARQUIVO_DONOS,     SEED_DONOS)
    pontos    = carregar_json(ARQUIVO_PONTOS,    SEED_PONTOS)
    historico = carregar_json(ARQUIVO_HISTORICO, [])
    return usuarios, donos, pontos, historico


def salvar_dados(usuarios: dict, donos: dict, pontos: list, historico: list) -> None:
    """Persiste todos os dados nos arquivos."""
    salvar_json(ARQUIVO_USUARIOS,  usuarios)
    salvar_json(ARQUIVO_DONOS,     donos)
    salvar_json(ARQUIVO_PONTOS,    pontos)
    salvar_json(ARQUIVO_HISTORICO, historico)


# ══════════════════════════════════════════════════════
# CRUD — USUÁRIOS
# ══════════════════════════════════════════════════════

def crud_criar_usuario(usuarios: dict, email: str, nome: str, senha: str) -> dict:
    """CREATE — adiciona novo usuário."""
    usuario = {"senha": senha, "nome": nome, "veiculo": None, "usar_gps": None}
    usuarios[email] = usuario
    return usuario


def crud_ler_usuario(usuarios: dict, email: str) -> dict | None:
    """READ — retorna usuário pelo e-mail."""
    return usuarios.get(email)


def crud_atualizar_usuario(usuarios: dict, email: str, campo: str, valor) -> bool:
    """UPDATE — altera ou cria um campo do usuário (upsert)."""
    if email in usuarios:
        usuarios[email][campo] = valor
        return True
    return False


def crud_deletar_usuario(usuarios: dict, email: str) -> bool:
    """DELETE — remove usuário."""
    if email in usuarios:
        del usuarios[email]
        return True
    return False


# ══════════════════════════════════════════════════════
# CRUD — DONOS
# ══════════════════════════════════════════════════════

def crud_criar_dono(donos: dict, email: str, nome: str, senha: str,
                    cpf_cnpj: str, telefone: str, chave_pix: str, banco: str) -> dict:
    """CREATE — cadastra novo dono."""
    dono = {
        "senha": senha, "nome": nome, "cpf_cnpj": cpf_cnpj,
        "telefone": telefone, "chave_pix": chave_pix, "banco": banco,
    }
    donos[email] = dono
    return dono


def crud_ler_dono(donos: dict, email: str) -> dict | None:
    """READ — retorna dono pelo e-mail."""
    return donos.get(email)


def crud_atualizar_dono(donos: dict, email: str, campo: str, valor) -> bool:
    """UPDATE — altera ou cria campo do dono (upsert)."""
    if email in donos:
        donos[email][campo] = valor
        return True
    return False


def crud_deletar_dono(donos: dict, email: str) -> bool:
    """DELETE — remove dono."""
    if email in donos:
        del donos[email]
        return True
    return False


# ══════════════════════════════════════════════════════
# CRUD — PONTOS DE RECARGA
# ══════════════════════════════════════════════════════

def _proximo_id(pontos: list) -> int:
    return max((p["id"] for p in pontos), default=0) + 1


def crud_criar_ponto(pontos: list, dados: dict) -> dict:
    """CREATE — cadastra novo ponto de recarga."""
    ponto = {
        "id":            _proximo_id(pontos),
        "nome":          dados["nome"],
        "endereco":      dados["endereco"],
        "tipo_tomada":   dados["tipo_tomada"],
        "horario":       dados["horario"],
        "preco_kwh":     dados["preco_kwh"],
        "disponivel":    True,
        "avaliacao":     5.0,
        "seguranca":     dados["seguranca"],
        "acessibilidade":dados.get("acessibilidade", ""),
        "regras":        dados.get("regras", ""),
        "chave_pix":     dados["chave_pix"],
        "responsavel":   dados["responsavel"],
        "dono_email":    dados.get("dono_email", ""),
    }
    pontos.append(ponto)
    return ponto


def crud_ler_ponto(pontos: list, ponto_id: int) -> dict | None:
    """READ — retorna ponto pelo ID."""
    return next((p for p in pontos if p["id"] == ponto_id), None)


def crud_listar_pontos(pontos: list, apenas_disponiveis: bool = False) -> list:
    """READ — lista todos os pontos (com filtro opcional)."""
    if apenas_disponiveis:
        return [p for p in pontos if p["disponivel"]]
    return list(pontos)


def crud_atualizar_ponto(pontos: list, ponto_id: int, campo: str, valor) -> bool:
    """UPDATE — altera um campo do ponto."""
    ponto = crud_ler_ponto(pontos, ponto_id)
    if ponto and campo in ponto:
        ponto[campo] = valor
        return True
    return False


def crud_deletar_ponto(pontos: list, ponto_id: int) -> bool:
    """DELETE — remove ponto da lista."""
    for i, p in enumerate(pontos):
        if p["id"] == ponto_id:
            pontos.pop(i)
            return True
    return False


# ══════════════════════════════════════════════════════
# CRUD — HISTÓRICO DE USO
# ══════════════════════════════════════════════════════

def crud_criar_historico(historico: list, email: str, ponto: dict,
                          kwh: float, total: float) -> dict:
    """CREATE — registra uma sessão de uso."""
    registro = {
        "id":          len(historico) + 1,
        "usuario":     email,
        "ponto_nome":  ponto["nome"],
        "ponto_id":    ponto["id"],
        "kwh":         kwh,
        "total_reais": total,
        "data":        time.strftime("%Y-%m-%d %H:%M"),
    }
    historico.append(registro)
    return registro


def crud_ler_historico(historico: list, email: str) -> list:
    """READ — retorna registros de uso de um usuário."""
    return [r for r in historico if r["usuario"] == email]


# ══════════════════════════════════════════════════════
# COMPATIBILIDADE (uso da matriz)
# ══════════════════════════════════════════════════════

def veiculo_compativel(veiculo: str, tipo_tomada: str) -> bool:
    """Consulta a MATRIZ_COMPATIBILIDADE para checar se o veículo suporta a tomada."""
    if veiculo not in VEHICLE_TYPES or tipo_tomada not in PLUG_TYPES:
        return True  # desconhecido → não bloqueia
    i = VEHICLE_TYPES.index(veiculo)
    j = PLUG_TYPES.index(tipo_tomada)
    return MATRIZ_COMPATIBILIDADE[i][j]


# ══════════════════════════════════════════════════════
# UI HELPERS
# ══════════════════════════════════════════════════════

def sep(title=""):
    width = 60
    if title:
        side = max(2, width - len(title) - 4)
        print(f"\n{'─' * 3} {title} {'─' * side}")
    else:
        print("─" * width)


def pause(msg="Processando", seconds=0.5):
    print(f"  ⏳ {msg}...", end="", flush=True)
    time.sleep(seconds)
    print(" ✓")


def ask(prompt: str) -> str:
    while True:
        val = input(f"  ➤ {prompt}: ").strip()
        if val:
            return val
        print("    ⚠️  Campo obrigatório. Tente novamente.")


def ask_opcional(prompt: str, padrao: str = "") -> str:
    val = input(f"  ➤ {prompt} [{padrao}]: ").strip()
    return val if val else padrao


def ask_yn(prompt: str) -> bool:
    while True:
        val = input(f"  ➤ {prompt} [s/n]: ").strip().lower()
        if val in ("s", "sim", "y", "yes"):
            return True
        if val in ("n", "nao", "não", "no"):
            return False
        print("    ⚠️  Digite 's' para sim ou 'n' para não.")


def choose(prompt: str, options: list) -> str:
    print(f"\n  {prompt}")
    for i, opt in enumerate(options, 1):
        print(f"    {i}. {opt}")
    while True:
        raw = input("  ➤ Número: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print(f"    ⚠️  Digite um número entre 1 e {len(options)}.")


def choose_point(pontos: list) -> dict | None:
    if not pontos:
        print("  ⚠️  Nenhum ponto disponível.")
        return None
    print()
    for p in pontos:
        status = "🟢 Disponível" if p["disponivel"] else "🔴 Ocupado"
        print(f"    [{p['id']}] {p['nome']} — {p['endereco']} | {status} | ⭐ {p['avaliacao']}")
    ids = [str(p["id"]) for p in pontos]
    while True:
        raw = input("  ➤ ID do ponto: ").strip()
        if raw in ids:
            return next(p for p in pontos if str(p["id"]) == raw)
        print(f"    ⚠️  ID inválido. Opções: {', '.join(ids)}")


def ask_float(prompt: str, min_val: float = 0.0) -> float:
    while True:
        raw = input(f"  ➤ {prompt}: ").strip().replace(",", ".")
        try:
            val = float(raw)
            if val >= min_val:
                return val
            print(f"    ⚠️  Valor mínimo: {min_val}.")
        except ValueError:
            print("    ⚠️  Digite um número válido (ex: 1.50).")


def exibir_ponto(p: dict):
    sep("Detalhes do Ponto")
    print(f"  ID           : {p['id']}")
    print(f"  Nome         : {p['nome']}")
    print(f"  Endereço     : {p['endereco']}")
    print(f"  Tipo tomada  : {p['tipo_tomada']}")
    print(f"  Horário      : {p['horario']}")
    print(f"  Preço/kWh    : R$ {p['preco_kwh']:.2f}")
    print(f"  Segurança    : {p['seguranca']}")
    print(f"  Acessib.     : {p['acessibilidade']}")
    print(f"  Regras       : {p['regras']}")
    print(f"  Avaliação    : ⭐ {p['avaliacao']}")
    print(f"  Disponível   : {'✅ Sim' if p['disponivel'] else '❌ Não'}")


# ══════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════

def fazer_login(usuarios: dict, email_preenchido: str = None) -> tuple:
    sep("Login")
    for tentativa in range(3):
            if email_preenchido and tentativa == 0:
                email = email_preenchido
                print(f"  ➤ E-mail: {email}  (preenchido automaticamente)")
            else:
                email = ask("E-mail").lower().strip()
            senha = ask("Senha")
            u = crud_ler_usuario(usuarios, email)
            if u and u["senha"] == senha:
                pause("Realizando login")
                print(f"  ✅ Bem-vindo(a), {u['nome']}!")
                return email, u
            email_preenchido = None
            restantes = 2 - tentativa
            if restantes > 0:
                print(f"  ❌ Credenciais inválidas. {restantes} tentativa(s) restante(s).")
            else:
                print("  ❌ Tentativas esgotadas.")

            acao = choose("O que deseja fazer?", [
                "🔄 Tentar novamente",
                "📝 Criar uma nova conta",
                "🚪 Voltar ao menu principal",
            ])
            if "nova conta" in acao:
                return fazer_cadastro(usuarios)
            elif "Voltar" in acao:
                return None, None
            # "Tentar novamente" → continua o for (próxima tentativa)


def fazer_cadastro(usuarios: dict) -> tuple:
    sep("Cadastro de Novo Usuário")
    nome  = ask("Seu nome completo")
    while True:
        email = ask("E-mail").lower().strip()
        if email in usuarios:
            print(f"    ⚠️  O e-mail '{email}' já está cadastrado.")
            acao = choose("O que deseja fazer?", [
                "Fazer login com este e-mail",
                "Usar um e-mail diferente",
            ])
            if "login" in acao:
                return fazer_login(usuarios, email_preenchido=email)
            # "Usar e-mail diferente" → volta ao topo do while
        else:
            break
    senha = ask("Senha")
    pause("Criando cadastro")
    usuario = crud_criar_usuario(usuarios, email, nome, senha)
    print(f"  ✅ Usuário '{nome}' cadastrado com sucesso!")
    return email, usuario


def auth_flow_usuario(usuarios: dict) -> tuple:
    sep("Acesso — Área do Usuário")
    if ask_yn("Você já possui cadastro como usuário?"):
        return fazer_login(usuarios)
    return fazer_cadastro(usuarios)


def fazer_cadastro_dono(donos: dict) -> tuple:
    sep("Cadastro de Novo Proprietário")
    nome      = ask("Nome completo")
    while True:
        email = ask("E-mail").lower().strip()
        if email in donos:
            print(f"    ⚠️  E-mail \'{email}\' já cadastrado como proprietário.")
            acao = choose("O que deseja fazer?", [
                "Fazer login com este e-mail",
                "Usar um e-mail diferente",
            ])
            if "login" in acao:
                return fazer_login(donos, email_preenchido=email)
        else:
            break
    senha     = ask("Senha")
    cpf_cnpj  = ask("CPF ou CNPJ")
    telefone  = ask("Telefone de contato")
    chave_pix = ask("Chave PIX para recebimentos")
    banco     = ask("Banco")
    pause("Criando cadastro")
    dono = crud_criar_dono(donos, email, nome, senha, cpf_cnpj, telefone, chave_pix, banco)
    print(f"  ✅ Proprietário \'{nome}\' cadastrado com sucesso!")
    return email, dono


def auth_flow_dono(donos: dict) -> tuple:
    sep("Acesso — Área do Proprietário")
    if ask_yn("Você já possui cadastro como proprietário?"):
        return fazer_login(donos)
    return fazer_cadastro_dono(donos)


# ══════════════════════════════════════════════════════
# MENU CRUD — ADMIN DE PONTOS (para o dono)
# ══════════════════════════════════════════════════════

def menu_conta_dono(donos: dict, email_logado: str) -> bool:
    """Menu do proprietário para gerenciar seus dados. Retorna True se excluiu a conta."""
    while True:
        d = crud_ler_dono(donos, email_logado)
        sep("Gerenciar Minha Conta — Proprietário")
        acao = choose("O que deseja fazer?", [
            "👁  Ver meus dados       (READ)",
            "✏️  Alterar nome          (UPDATE)",
            "✏️  Alterar senha         (UPDATE)",
            "✏️  Alterar telefone      (UPDATE)",
            "✏️  Alterar chave PIX     (UPDATE)",
            "✏️  Alterar banco         (UPDATE)",
            "🗑️  Excluir minha conta   (DELETE)",
            "🔙 Voltar",
        ])

        if "Ver" in acao:
            sep("Meus Dados — Proprietário")
            print(f"  Nome       : {d['nome']}")
            print(f"  E-mail     : {email_logado}")
            print(f"  CPF/CNPJ   : {d.get('cpf_cnpj', 'Não informado')}")
            print(f"  Telefone   : {d.get('telefone', 'Não informado')}")
            print(f"  Chave PIX  : {d.get('chave_pix', 'Não informada')}")
            print(f"  Banco      : {d.get('banco', 'Não informado')}")
        elif "nome" in acao:
            crud_atualizar_dono(donos, email_logado, "nome", ask("Novo nome"))
            salvar_json(ARQUIVO_DONOS, donos)
            print("  ✅ Nome atualizado!")
        elif "senha" in acao:
            crud_atualizar_dono(donos, email_logado, "senha", ask("Nova senha"))
            salvar_json(ARQUIVO_DONOS, donos)
            print("  ✅ Senha atualizada!")
        elif "telefone" in acao:
            crud_atualizar_dono(donos, email_logado, "telefone", ask("Novo telefone"))
            salvar_json(ARQUIVO_DONOS, donos)
            print("  ✅ Telefone atualizado!")
        elif "PIX" in acao:
            crud_atualizar_dono(donos, email_logado, "chave_pix", ask("Nova chave PIX"))
            salvar_json(ARQUIVO_DONOS, donos)
            print("  ✅ Chave PIX atualizada!")
        elif "banco" in acao:
            crud_atualizar_dono(donos, email_logado, "banco", ask("Novo banco"))
            salvar_json(ARQUIVO_DONOS, donos)
            print("  ✅ Banco atualizado!")
        elif "Excluir" in acao:
            if ask_yn("⚠️  Tem certeza? Esta ação é irreversível."):
                crud_deletar_dono(donos, email_logado)
                salvar_json(ARQUIVO_DONOS, donos)
                print("  ✅ Conta de proprietário excluída. Até logo!")
                return True
        else:
            break
    return False


def menu_crud_pontos(email: str, pontos: list, donos: dict, historico: list):
    """Menu interativo de CRUD para pontos do proprietário logado."""
    while True:
        sep("Gerenciar Meus Pontos de Recarga")
        acao = choose("O que deseja fazer?", [
            "➕ Cadastrar novo ponto  (CREATE)",
            "📋 Ver meus pontos       (READ)",
            "✏️  Editar ponto          (UPDATE)",
            "🗑️  Remover ponto         (DELETE)",
            "💰 Ver ganhos",
            "🔙 Voltar",
        ])

        # ── CREATE ──────────────────────────────────────────
        if "CREATE" in acao:
            sep("Novo Ponto — Preenchimento")
            dados = {
                "nome":           ask("Nome do ponto"),
                "endereco":       ask("Endereço completo"),
                "tipo_tomada":    choose("Tipo de tomada", PLUG_TYPES),
                "horario":        ask("Horário de funcionamento (ex: 08:00-22:00)"),
                "seguranca":      ask("Segurança disponível"),
                "acessibilidade": ask_opcional("Acessibilidade", "Não informada"),
                "regras":         ask_opcional("Regras de uso", "Sem restrições"),
                "preco_kwh":      ask_float("Preço por kWh (R$)", min_val=0.01),
                "chave_pix":      ask("Chave PIX ou conta bancária"),
                "responsavel":    ask("Nome do responsável"),
                "dono_email":     email,
            }
            # Verificar campos obrigatórios via tupla CAMPOS_OBRIGATORIOS_PONTO
            faltando = [c for c in CAMPOS_OBRIGATORIOS_PONTO if not dados.get(c)]
            if faltando:
                print(f"  ⚠️  Campos obrigatórios faltando: {faltando}")
                continue
            sep("Termos da Plataforma")
            print("  📄 Ao publicar, você concorda com os termos de uso da plataforma.")
            if not ask_yn("Aceita os termos?"):
                print("  ❌ Cancelado.")
                continue
            ponto = crud_criar_ponto(pontos, dados)
            salvar_json(ARQUIVO_PONTOS, pontos)
            print(f"  ✅ Ponto '{ponto['nome']}' cadastrado com ID {ponto['id']}!")

        # ── READ ────────────────────────────────────────────
        elif "READ" in acao:
            meus = [p for p in pontos if p.get("dono_email") == email]
            if not meus:
                print("  ℹ️  Você ainda não possui pontos cadastrados.")
            else:
                for p in meus:
                    exibir_ponto(p)

        # ── UPDATE ──────────────────────────────────────────
        elif "UPDATE" in acao:
            meus = [p for p in pontos if p.get("dono_email") == email]
            if not meus:
                print("  ℹ️  Nenhum ponto para editar.")
                continue
            print("  Escolha o ponto que deseja editar:")
            ponto = choose_point(meus)
            if not ponto:
                continue
            campos_editaveis = [
                "nome", "endereco", "tipo_tomada", "horario",
                "seguranca", "acessibilidade", "regras", "preco_kwh",
                "chave_pix", "responsavel", "disponivel",
            ]
            campo = choose("Campo a alterar:", campos_editaveis)
            if campo == "preco_kwh":
                novo = ask_float("Novo preço por kWh")
            elif campo == "disponivel":
                novo = ask_yn("Disponível?")
            else:
                novo = ask(f"Novo valor para '{campo}'")
            if crud_atualizar_ponto(pontos, ponto["id"], campo, novo):
                salvar_json(ARQUIVO_PONTOS, pontos)
                print(f"  ✅ Campo '{campo}' atualizado!")
            else:
                print("  ❌ Falha na atualização.")

        # ── DELETE ──────────────────────────────────────────
        elif "DELETE" in acao:
            meus = [p for p in pontos if p.get("dono_email") == email]
            if not meus:
                print("  ℹ️  Nenhum ponto para remover.")
                continue
            sep("Remover Ponto")
            opcoes = [f"[{p['id']}] {p['nome']} — {p['endereco']}" for p in meus]
            opcoes.append("🔙 Voltar ao menu anterior")
            escolha = choose("Escolha o ponto que deseja remover:", opcoes)
            if "Voltar" in escolha:
                continue
            ponto = meus[opcoes.index(escolha)]
            if ask_yn(f"Confirmar remoção de '{ponto['nome']}'?"):
                crud_deletar_ponto(pontos, ponto["id"])
                salvar_json(ARQUIVO_PONTOS, pontos)
                print("  ✅ Ponto removido.")
            else:
                print("  ↩️  Remoção cancelada.")

        # ── GANHOS ──────────────────────────────────────────
        elif "ganhos" in acao:
            meus_ids = {p["id"] for p in pontos if p.get("dono_email") == email}
            meus_usos = [r for r in historico if r.get("ponto_id") in meus_ids]
            sep("Histórico de Ganhos")
            if not meus_usos:
                print("  ℹ️  Nenhum uso registrado ainda.")
            else:
                total_ganho = 0.0
                for r in meus_usos:
                    print(f"  {r['data']} | {r['usuario']} | "
                          f"{r['kwh']} kWh | R$ {r['total_reais']:.2f}")
                    total_ganho += r["total_reais"]
                print(f"\n  💰 Total acumulado: R$ {total_ganho:.2f}")

        else:
            break


def menu_crud_usuarios(usuarios: dict, email_logado: str):
    """Menu para o próprio usuário gerenciar sua conta. Retorna (deletado, veiculo, usar_gps)."""
    while True:
        u = crud_ler_usuario(usuarios, email_logado)
        sep("Gerenciar Minha Conta")
        acao = choose("O que deseja fazer?", [
            "👁  Ver meus dados           (READ)",
            "✏️  Alterar nome              (UPDATE)",
            "✏️  Alterar senha             (UPDATE)",
            "✏️  Alterar veículo           (UPDATE)",
            "✏️  Alterar preferência GPS   (UPDATE)",
            "🗑️  Excluir minha conta       (DELETE)",
            "🔙 Voltar",
        ])

        if "Ver" in acao:
            sep("Meus Dados")
            gps_label = {True: "Sim (automático)", False: "Não (manual)", None: "Não definido"}
            print(f"  Nome         : {u['nome']}")
            print(f"  E-mail       : {email_logado}")
            print(f"  Veículo      : {u['veiculo'] or 'Não definido'}")
            print(f"  Usar GPS     : {gps_label.get(u.get('usar_gps'))}")

        elif "nome" in acao:
            novo = ask("Novo nome")
            crud_atualizar_usuario(usuarios, email_logado, "nome", novo)
            salvar_json(ARQUIVO_USUARIOS, usuarios)
            print("  ✅ Nome atualizado!")

        elif "senha" in acao:
            nova = ask("Nova senha")
            crud_atualizar_usuario(usuarios, email_logado, "senha", nova)
            salvar_json(ARQUIVO_USUARIOS, usuarios)
            print("  ✅ Senha atualizada!")

        elif "veículo" in acao:
            novo_v = choose("Selecione o novo veículo", VEHICLE_TYPES)
            crud_atualizar_usuario(usuarios, email_logado, "veiculo", novo_v)
            salvar_json(ARQUIVO_USUARIOS, usuarios)
            print(f"  ✅ Veículo atualizado para: {novo_v}")

        elif "GPS" in acao:
            novo_gps = ask_yn("Usar GPS automático para localização?")
            crud_atualizar_usuario(usuarios, email_logado, "usar_gps", novo_gps)
            salvar_json(ARQUIVO_USUARIOS, usuarios)
            print(f"  ✅ Preferência GPS atualizada: {'Sim' if novo_gps else 'Não'}")

        elif "Excluir" in acao:
            if ask_yn("⚠️  Tem certeza? Esta ação é irreversível."):
                crud_deletar_usuario(usuarios, email_logado)
                salvar_json(ARQUIVO_USUARIOS, usuarios)
                print("  ✅ Conta excluída. Até logo!")
                return True, None, None   # deletado

        else:
            break

    u = crud_ler_usuario(usuarios, email_logado)
    return False, u.get("veiculo"), u.get("usar_gps")


# ══════════════════════════════════════════════════════
# FLUXO DO USUÁRIO (usar ponto de recarga)
# ══════════════════════════════════════════════════════

def _menu_buscar_ponto(email: str, veiculo: str, usar_gps: bool,
                       usuarios: dict, pontos: list, historico: list):
    """Menu pós-login: busca, seleciona e usa um ponto. Retorna False se conta excluída."""

    # Localização — GPS salvo no perfil OU digitar endereço específico
    sep("Localização")
    modo = choose("Como deseja localizar pontos?", [
        f"📡 Usar minha localização {'(GPS — padrão do perfil)' if usar_gps else '(GPS)'}",
        "📝 Digitar um endereço ou bairro específico",
    ])
    if "GPS" in modo:
        pause("Obtendo localização via GPS")
        print("  📍 Localização: Av. Brasil, 200 — São Paulo (mock GPS)")
    else:
        loc = ask("Digite o endereço, bairro ou região")
        print(f"  📍 Buscando pontos perto de: {loc}")

    # Busca e exibição dos pontos compatíveis
    pause("Buscando pontos compatíveis")
    disponiveis = crud_listar_pontos(pontos, apenas_disponiveis=False)

    # Filtra pela compatibilidade usando a MATRIZ
    compativeis = [
        p for p in disponiveis
        if veiculo_compativel(veiculo, p["tipo_tomada"])
    ]
    print(f"  🗺  {len(compativeis)} ponto(s) compatível(is) encontrado(s).")

    if ask_yn("Filtrar apenas pontos disponíveis agora?"):
        compativeis = [p for p in compativeis if p["disponivel"]]
        print(f"  🔍 {len(compativeis)} ponto(s) após filtro.")

    if not compativeis:
        print("  ❌ Nenhum ponto encontrado. Encerrando.")
        return True  # não foi excluído, apenas sem pontos

    sep("Mapa de Pontos")
    for p in compativeis:
        status = "🟢 Disponível" if p["disponivel"] else "🔴 Ocupado"
        print(f"  [{p['id']}] {p['nome']} — {p['endereco']}")
        print(f"       {status} | {p['tipo_tomada']} | R$ {p['preco_kwh']:.2f}/kWh | ⭐ {p['avaliacao']}")

    sep("Escolha um Ponto")
    escolhido = choose_point(compativeis)
    if not escolhido:
        return True

    exibir_ponto(escolhido)

    if not escolhido["disponivel"]:
        print("  ⚠️  Este ponto está ocupado. Escolha outro.")
        return True

    # Reserva
    reserva = None
    if ask_yn("Deseja fazer uma reserva antecipada?"):
        kwh_est = 30.0
        valor   = round(kwh_est * escolhido["preco_kwh"], 2)
        print(f"\n  💳 Estimativa: R$ {valor:.2f} ({kwh_est} kWh)")
        pause(f"Processando pagamento de R$ {valor:.2f}")
        aprovado = random.random() < 0.80
        if aprovado:
            print("  ✅ Pagamento aprovado! Reserva confirmada.")
            reserva = {"id": random.randint(1000, 9999), "status": "confirmada"}
        else:
            print("  ❌ Pagamento recusado. Reserva cancelada.")
            return True
    else:
        print("  🚗 Indo direto ao ponto sem reserva.")

    # Navegação
    pause("Calculando rota")
    print(f"  🧭 Navegando até: {escolhido['endereco']}")
    input("  ➤ [Pressione ENTER quando chegar ao ponto] ")

    # Chegada
    pause("Verificando disponibilidade ao chegar")
    ainda_disponivel = random.random() < 0.85
    escolhido["disponivel"] = ainda_disponivel
    crud_atualizar_ponto(pontos, escolhido["id"], "disponivel", ainda_disponivel)

    if not ainda_disponivel:
        print("  ⚠️  Ponto ocupado ao chegar! Procurando alternativa...")
        outros = [p for p in compativeis if p["id"] != escolhido["id"] and p["disponivel"]]
        if outros:
            escolhido = choose_point(outros)
            pause("Calculando nova rota")
            print(f"  🧭 Navegando até: {escolhido['endereco']}")
            input("  ➤ [Pressione ENTER quando chegar] ")
        else:
            print("  ❌ Sem alternativas. Encerrando.")
            return True
    else:
        print("  ✅ Ponto disponível!")

    # Recarga
    pause("Iniciando recarga")
    kwh = round(random.uniform(10, 50), 2)
    print(f"  ⚡ Recarga em andamento... {kwh} kWh")
    input("  ➤ [Pressione ENTER para finalizar a recarga] ")
    total = round(kwh * escolhido["preco_kwh"], 2)
    pause("Finalizando recarga")
    print(f"  ✅ Recarga concluída: {kwh} kWh — Total: R$ {total:.2f}")

    # Registra uso (CREATE no histórico) e persiste
    registro = crud_criar_historico(historico, email, escolhido, kwh, total)
    salvar_json(ARQUIVO_HISTORICO, historico)
    pause("Registrando uso no sistema")
    print(f"  📝 Registro #{registro['id']} salvo em '{ARQUIVO_HISTORICO}'.")

    # Libera ponto
    crud_atualizar_ponto(pontos, escolhido["id"], "disponivel", True)
    salvar_json(ARQUIVO_PONTOS, pontos)
    pause("Atualizando status do ponto")

    # Avaliação
    sep("Avaliação")
    nota_str = choose("Qual nota você dá a este ponto?",
                      ["1 ⭐", "2 ⭐⭐", "3 ⭐⭐⭐", "4 ⭐⭐⭐⭐", "5 ⭐⭐⭐⭐⭐"])
    nota = int(nota_str[0])
    nova_av = round((escolhido["avaliacao"] + nota) / 2, 1)
    crud_atualizar_ponto(pontos, escolhido["id"], "avaliacao", nova_av)
    salvar_json(ARQUIVO_PONTOS, pontos)
    print(f"  ✅ Avaliação registrada: {nota}/5  (nova média: {nova_av})")

    # Histórico do usuário
    sep("Seu Histórico de Uso")
    meu_historico = crud_ler_historico(historico, email)
    if meu_historico:
        for r in meu_historico:
            print(f"  {r['data']} | {r['ponto_nome']} | {r['kwh']} kWh | R$ {r['total_reais']:.2f}")
    else:
        print("  ℹ️  Nenhum uso anterior.")

    return True  # conta ainda existe


def run_user_flow(usuarios: dict, pontos: list, historico: list):
    sep("FLUXO: USUÁRIO — Usar Ponto de Recarga")

    email, usuario = auth_flow_usuario(usuarios)
    if not usuario:
        return

    # Veículo — só pergunta se não estiver salvo no perfil
    veiculo = usuario.get("veiculo")
    if not veiculo:
        veiculo = choose("Selecione seu tipo de veículo", VEHICLE_TYPES)
        crud_atualizar_usuario(usuarios, email, "veiculo", veiculo)
        salvar_json(ARQUIVO_USUARIOS, usuarios)
    else:
        print(f"  🚗 Veículo do perfil: {veiculo}")

    # GPS — pergunta apenas uma vez; depois só muda pelo perfil
    usar_gps = usuario.get("usar_gps")
    if usar_gps is None:
        print("  ℹ️  Preferência de localização não definida.")
        usar_gps = ask_yn("Deseja usar GPS automático por padrão?")
        crud_atualizar_usuario(usuarios, email, "usar_gps", usar_gps)
        salvar_json(ARQUIVO_USUARIOS, usuarios)
        print(f"  ✅ Preferência salva: {'GPS automático' if usar_gps else 'endereço manual'}")
        print("     (Para mudar, acesse Gerenciar minha conta → Alterar preferência GPS)")

    # ── Menu principal do usuário logado ──────────────────────────────────────
    while True:
        u = crud_ler_usuario(usuarios, email)
        sep(f"Olá, {u['nome']}!")
        print(f"  🚗 Veículo : {veiculo}   |   📍 GPS: {'automático' if usar_gps else 'manual'}")
        acao = choose("O que deseja fazer?", [
            "🔍 Buscar um ponto de recarga",
            "👤 Gerenciar minha conta",
            "🚪 Sair",
        ])

        if "Buscar" in acao:
            conta_existe = _menu_buscar_ponto(email, veiculo, usar_gps, usuarios, pontos, historico)
            if not conta_existe:
                break  # conta excluída dentro do submenu

        elif "Gerenciar" in acao:
            deletado, novo_veiculo, novo_gps = menu_crud_usuarios(usuarios, email)
            if deletado:
                break
            if novo_veiculo:
                veiculo = novo_veiculo
            if novo_gps is not None:
                usar_gps = novo_gps

        else:
            sep("FIM DO FLUXO DE USUÁRIO")
            break


# ══════════════════════════════════════════════════════
# FLUXO DO DONO (gerenciar pontos)
# ══════════════════════════════════════════════════════

def run_owner_flow(donos: dict, pontos: list, historico: list):
    sep("FLUXO: PROPRIETÁRIO — Gerenciar Pontos de Recarga")

    email, dono = auth_flow_dono(donos)
    if not dono:
        return

    while True:
        sep(f"Olá, {dono['nome']}! — Área do Proprietário")
        acao = choose("O que deseja fazer?", [
            "🏠 Gerenciar meus pontos de recarga",
            "👤 Gerenciar minha conta",
            "🚪 Sair",
        ])
        if "pontos" in acao:
            menu_crud_pontos(email, pontos, donos, historico)
        elif "conta" in acao:
            excluido = menu_conta_dono(donos, email)
            if excluido:
                break
            dono = crud_ler_dono(donos, email)
        else:
            sep("FIM DO FLUXO DO PROPRIETÁRIO")
            break


# ══════════════════════════════════════════════════════
# MENU PRINCIPAL
# ══════════════════════════════════════════════════════

def main():
    print("\n" + "=" * 60)
    print("   ⚡ EV CHARGING APP — Simulação Interativa")
    print("=" * 60)

    # Carrega dados dos arquivos (ou seed inicial)
    usuarios, donos, pontos, historico = carregar_dados()
    print(f"  📂 Dados carregados: {len(usuarios)} usuário(s), "
          f"{len(donos)} proprietário(s), {len(pontos)} ponto(s), {len(historico)} uso(s).")

    while True:
        sep("Menu Principal")
        escolha = choose(
            "Como você quer usar o aplicativo?",
            [
                "Sou usuário       — quero usar um ponto de recarga",
                "Sou proprietário  — quero gerenciar meus pontos",
                "Sair",
            ],
        )

        if "usuário" in escolha:
            run_user_flow(usuarios, pontos, historico)
        elif "proprietário" in escolha:
            run_owner_flow(donos, pontos, historico)
        else:
            salvar_dados(usuarios, donos, pontos, historico)
            print(f"\n  💾 Dados salvos em '{ARQUIVO_USUARIOS}', '{ARQUIVO_DONOS}', "
                  f"'{ARQUIVO_PONTOS}' e '{ARQUIVO_HISTORICO}'.")
            print("  👋 Até logo!\n")
            break


if __name__ == "__main__":
    main()
