# -*- coding: utf-8 -*-
import requests, re

# CONSTANTES
URL_SRC_PARTS = "https://usher.ttvnw.net/vod/%s.m3u8?nauthsig=%s&nauth=%s&allow_source=true&player=twitchweb&allow_spectre=true&allow_audio_only=true"
URL_GET_TOKEN= "https://api.twitch.tv/api/vods/%s/access_token"
client_ID = "jzkbprff40iqj646a697cyrvl0zt2m6"

# FUNÇÕES
def gravar_arquivo(nome, conteudo, bin = False):
    arquivo = None
    if(bin):
        arquivo = open(nome, "wb+")
    else:
        arquivo = open(nome, "w+")
    arquivo.write(conteudo)
    arquivo.close()

def parse_m3u(data):
    regex_resolucao = re.compile(r"[0-9]+p[0-9]+")
    linhas = data.split("\n")
    i = 0
    retorno = {}
    while i < len(linhas):
        if(linhas[i][:17] == '#EXT-X-STREAM-INF'):
            dados = linhas[i].split(',')
            resolucao = dados[len(dados)-1][7:-1]
            if(regex_resolucao.match(resolucao)):
                retorno[resolucao] = linhas[i+1]
        i += 1
    return retorno

def extrair_partes(data, url):
    linhas = data.split("\n")
    url_splited = url.split('/')
    url = '/'.join(url_splited[:-1])+'/'
    i = 0
    retorno = []
    while i < len(linhas):
        if(linhas[i][:7] == '#EXTINF'):
            retorno.append( url+linhas[i+1] )
        i += 1
    return retorno

# PERGUNTANDO VOD AO USUÁRIO
vod_id = input("Informe o ID do VOD: ")

# OBTENDO TOKEN
print("\nOBTENDO TOKEN DE AUTORIZAÇÃO\n")

parsed_URL_Token = URL_GET_TOKEN % vod_id

r = requests.get(parsed_URL_Token, headers={"Client-ID": client_ID})

if(r.status_code != requests.codes.ok):
    print("Falha ao obter o token de autorização")
    exit()

auth = r.json()

# OBTENDO LISTA DE RESOLUÇÕES
print("BUSCANDO INFORMAÇÕES DO VOD\n")

parsed_URL_Lista = URL_SRC_PARTS % (vod_id, auth['sig'], auth['token'])

r = requests.get(parsed_URL_Lista, headers={"Client-ID": client_ID})

lista_resolucoes = parse_m3u(r.text)

#SOLICITANDO RESOLUÇÃO AO USUÁRIO

if(len(lista_resolucoes) <= 0):
    print('Não foi posível obter informações sobre este VOD')
    exit()

escolha = ''
url = ''
while not (escolha in lista_resolucoes.keys()):
    print("Escolha uma das seguintes resoluções:\n")
    for resolucao in lista_resolucoes:
        print('> '+resolucao)
    escolha = input("\nEscreva a sua escolha: ")

    try:
        url = lista_resolucoes[escolha]
    except KeyError:
        print("\nOpção inválida\n")

# BUSCANDO LISTA DE PARTES
print("\nBAIXANDO LISTA DE PARTES DO VOD\n")

r = requests.get(url)

partes = extrair_partes(r.text, url)

print(str(len(partes)) + ' partes.')

# INICIANDO DOWNLOAD
print("\nINICIANDO DOWNLOAD\n")

i = 0
while i < len(partes):
    print('{:.2f}'.format((i/len(partes))*100)+'% Concluido.', end="\r")
    r = requests.get(partes[i])
    gravar_arquivo(str(i)+'.ts', r.content, True)
    i += 1

# INICIANDO PROCESSAMENTO
print("\nPROCESSANDO VÍDEO\n")

#TODO
