import requests
import json


def busca_em_dou(termo: str):
    query = f"https://www.in.gov.br/consulta/-/buscar/dou?q={termo}&s=todos&exactDate=all&sortType=0"
    response = requests.get(query)

    json_response = seleciona_trecho_resultado(response)

    exibe_chaves(json_response["jsonArray"][0])

    exibe_titulos(json_response["jsonArray"])

    json_response = proxima_pagina(query, 1, 2)

    exibe_titulos(json_response["jsonArray"])

    breakpoint()


def seleciona_trecho_resultado(response) -> dict:
    inicio: int = response.text.find('{"jsonArray":')
    final: int = response.text[inicio:].find("</") + inicio

    json_response = json.loads(response.text[inicio:final])

    return json_response


def proxima_pagina(query: str, current_page: int, new_page: int) -> dict:
    new_query = (
        query
        + f"delta=20&currentPage={current_page}&newPage={new_page}&score=0&id=597386647&displayDate=1732244400000"
    )

    response = requests.get(new_query)
    json_response = seleciona_trecho_resultado(response)

    return json_response


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


def exibe_chaves(json_response: dict):
    print("\n### KEYS ###")
    for index, key in enumerate(json_response.keys()):
        print(f"{index + 1}- {key}")

    input("Pressione ENTER para continuar...")


busca_em_dou("processo judicial")
"delta=20&currentPage=1&newPage=2&score=0&id=597386647&displayDate=1732244400000"
"delta=20&currentPage=2&newPage=3&score=0&id=597384529&displayDate=1732244400000"
"delta=20&currentPage=2&newPage=3&score=0&id=597386647&displayDate=1732244400000"
"delta=20&currentPage=3&newPage=4&score=0&id=597384529&displayDate=1732244400000"

# with open("response.py", "w") as file:
#     file.write(f"x = {response.text[inicio:final]}")

textos = response.text[inicio:final]
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
