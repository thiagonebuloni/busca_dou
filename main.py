import requests
import json
from enum import Enum
from datetime import datetime


class ExactDate(Enum):
    QUALQUER = "all"
    DIA = "dia"
    SEMANA = "semana"
    MES = "mes"
    ANO = "ano"
    TODOS = "todos"
    PERSONALIZADO = "personalizado"


class OndePesquisar(Enum):
    TITULO = "title_pt_BR-"
    TEXTO = "ddm__text__21040__texto_pt_BR-"
    TUDO = ""


class Jornal(Enum):
    TODOS = "todos"
    SECAO1 = "do1"
    SECAO2 = "do2"
    SECAO3 = "do3"
    EDICAO_EXTRA = "doe"
    EDICAO_SUPLEMENTAR = "do1a"


dicionario: dict = {}


def menu() -> dict:
    dict_escolhas = {}
    termo: str = input("Termo de pesquisa: ")
    dict_escolhas["termo"] = termo

    while True:
        print("1- Pesquisa exata")
        print("2- Período")
        print("3- Ordenação")
        print("4- Escopo da pesquisa")
        print("5- Jornal específico")
        print("6- Fazer a pesquisa")

        escolha = input("Opção: ")
        match escolha:
            case "1":
                dict_escolhas["exact_match"] = True
            case "2":
                data_exata: ExactDate = menu_exact_match()
                dict_escolhas["exact_date"] = data_exata
                if data_exata == ExactDate.PERSONALIZADO:
                    exact_date_personalizado: list[str] = input(
                        "Digite a data de início e de fim (dd-mm-aaaa dd-mm-aaaa): "
                    ).split()
                    dict_escolhas["exact_date_personalizado"] = exact_date_personalizado
            case "3":
                dict_escolhas["sort_type"] = int(
                    input("Ordenar por data (0) ou relevância (1): ")
                )
            case "4":
                dict_escolhas["onde_pesquisar"] = menu_onde_pesquisar()
            case "5":
                dict_escolhas["jornal"] = menu_jornal()  # loop para varios jornais
            case "6":
                break

    return dict_escolhas


def menu_jornal() -> list[Jornal]:
    print("1- Todos")
    print("2- Seção 1")
    print("3- Seção 2")
    print("4- Seção 3")
    print("5- Edição Extra")
    print("6- Edição Suplementar")
    opcao: list[str] = input("Opção: ").split()

    jornal: list[Jornal] = []
    for o in opcao:
        match o:
            case "1":
                jornal.append(Jornal.TODOS)
            case "2":
                jornal.append(Jornal.SECAO1)
            case "3":
                jornal.append(Jornal.SECAO2)
            case "4":
                jornal.append(Jornal.SECAO3)
            case "5":
                jornal.append(Jornal.EDICAO_EXTRA)
            case "6":
                jornal.append(Jornal.EDICAO_SUPLEMENTAR)
            case _:
                print("Opção inválida.")
                return menu_jornal()
    return jornal


def menu_onde_pesquisar() -> OndePesquisar:
    print("1- Título")
    print("2- Texto")
    print("3- Tudo")
    opcao: str = input("Opção: ")

    match opcao:
        case "1":
            return OndePesquisar.TITULO
        case "2":
            return OndePesquisar.TEXTO
        case "3":
            return OndePesquisar.TUDO
        case _:
            print("Opção inválida.")
            return menu_onde_pesquisar()


def menu_exact_match() -> ExactDate:
    print("1- Qualquer período")
    print("2- Edição do Dia")
    print("3- Última semana")
    print("4- Último mês")
    print("5- Último ano")
    print("6- Personalizado")
    opcao: str = input("Opção: ")

    match opcao:
        case "1":
            return ExactDate.QUALQUER
        case "2":
            return ExactDate.DIA
        case "3":
            return ExactDate.SEMANA
        case "4":
            return ExactDate.MES
        case "5":
            return ExactDate.ANO
        case "6":
            return ExactDate.PERSONALIZADO
        case _:
            print("Opção inválida.")
            return menu_exact_match()


def busca_em_dou(
    termo: str,
    exact_match: bool = False,
    exact_date: ExactDate = ExactDate.QUALQUER,
    sort_type: int = 0,
    onde_pesquisar: OndePesquisar = OndePesquisar.TUDO,
    jornal: list[Jornal] = [Jornal.TODOS],
    exact_date_personalizado: list = [""],
) -> None:
    termo = termo.replace(" ", "+")

    if exact_match:
        termo = f"%22{termo}%22"

    if sort_type not in range(2):
        print("sort_type deve ser um valor entre 0 e 1.")
        sort_type = 0

    jornal_parsed: str = parse_jornal(jornal)

    if exact_date == ExactDate.PERSONALIZADO:
        exact_date_personalizado_parsed = parse_date_personalizado(
            exact_date_personalizado
        )
    else:
        exact_date_personalizado_parsed = ""

    query = f"https://www.in.gov.br/consulta/-/buscar/dou?q={onde_pesquisar.value}{termo}{jornal_parsed}&exactDate={exact_date.value}&sortType={sort_type}{exact_date_personalizado_parsed}"
    print(query)
    response = requests.get(query)

    json_response = seleciona_trecho_resultado(response)

    if json_response["jsonArray"] == []:
        print("Nenhum resultado encontrado.")
        return

    guarda_no_dicionario(json_response["jsonArray"])

    # exibe_chaves(json_response["jsonArray"][0])

    # exibe_titulos(json_response["jsonArray"])

    # pega_proxima_pagina(response)
    json_response = proxima_pagina(query, 1, 2, json_response["jsonArray"])
    # guarda_no_dicionario(json_response["jsonArray"])
    # exibe_titulos(json_response["jsonArray"])
    # json_response = proxima_pagina(query, 2, 3, json_response["jsonArray"])
    # guarda_no_dicionario(json_response["jsonArray"])
    # exibe_titulos(json_response["jsonArray"])


def parse_date_personalizado(exact_date_personalizado: list[str]) -> str:
    exact_date_personalizado_parsed: str = ""
    try:
        data_parsed = datetime.strptime(exact_date_personalizado[0], "%d-%m-%Y")

        exact_date_personalizado_parsed += (
            f"&publishFrom={data_parsed.strftime('%d-%m-%Y')}"
        )

        data_parsed = datetime.strptime(exact_date_personalizado[1], "%d-%m-%Y")

        exact_date_personalizado_parsed += (
            f"&publishTo={data_parsed.strftime('%d-%m-%Y')}"
        )

    except ValueError:
        print("Data inválida.")
        exit(1)
    print(exact_date_personalizado_parsed)
    print(data_parsed.strftime("%d-%m-%Y"))
    return exact_date_personalizado_parsed


def parse_jornal(jornal) -> str:
    jornal_parsed: str = ""

    if Jornal.TODOS in jornal:
        jornal_parsed = "&s=" + Jornal.TODOS.value
        return jornal_parsed

    for j in jornal:
        jornal_parsed += "&s=" + j.value

    return jornal_parsed


def seleciona_trecho_resultado(response) -> dict:
    inicio: int = response.text.find('{"jsonArray":')
    final: int = response.text[inicio:].find("</") + inicio

    json_response = json.loads(response.text[inicio:final])

    return json_response


def proxima_pagina(
    query: str, current_page: int, new_page: int, json_array: dict
) -> dict:
    pagination_id = json_array[-1]["classPK"]
    print(f"PAGINATION {pagination_id}")
    print(f"PAGINATION OUTRO {json_array[len(json_array)-1]['classPK']}")
    new_query = (
        query
        + f"delta=20&currentPage={current_page}&newPage={new_page}&score=0&id={pagination_id}&displayDate=1732244400000"
    )

    response = requests.get(new_query)
    json_response = seleciona_trecho_resultado(response)

    return json_response


def guarda_no_dicionario(json_response: dict):
    for i in range(len(json_response)):
        dicionario[json_response[i]["classPK"]] = json_response


def exibe_titulos(json_response: dict):
    print("\n### TITLES ###")
    for index, i in enumerate(range(len(json_response))):
        idx_title = json_response[i]["title"].find("<span")
        if idx_title == -1:
            idx_title = len(json_response[i]["title"])

        print(
            f"{index + 1}- {json_response[i]['title'][:idx_title]} || {json_response[i]['classPK']} "
        )

    input("Pressione ENTER para continuar...")


# def guarda_no_dicionario(json_response: dict) -> None:


def exibe_chaves(json_response: dict):
    print("\n### KEYS ###")
    for index, key in enumerate(json_response.keys()):
        print(f"{index + 1}- {key}")

    input("Pressione ENTER para continuar...")


def pega_proxima_pagina(response) -> None:
    print("\nRESPONSE\n")
    next_id = dicionario[-1]["classPK"]


lista_buttons = ["1btn", "2btn"]

dict_escolhas = menu()
busca_em_dou(**dict_escolhas)

inicio_pub: str = '{"pubName":'
pausa: str = "<span "
fim_pausa: str = "/span>"


def dados_gov():
    response = requests.get(
        "https://dados.gov.br/api/publico/conjuntos-dados/buscar?offset=0&tamanhoPagina=10&titulo=judicial"
    ).json()

    print(f"Keys: {response['registros'][0].keys()}")
    print(f"Length: {len(response['registros'])}")

    for registro in response["registros"]:
        print(f"{registro['title']},\n {registro['id']}")
    response.text.find('{"pubName":')
    response.text.find('"]},')
