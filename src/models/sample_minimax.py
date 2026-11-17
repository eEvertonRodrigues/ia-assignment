arvore = {
    'A':['B', 'C'],
    'B':['D', 'E'],
    'C':['F', 'G'],
    'D':[],
    'E':[],
    'F':[],
    'G':[]
}

utilidades = {
    'D': 3,
    'E':5,
    'F':2,
    'G':9
}

def expandir(estado):
  return arvore[estado]

def eh_terminal(estado):
  return len(expandir(estado)) == 0

def avaliar(estado):
  return utilidades[estado]

def minimax(estado, maximizar):
  #caso base: chegamos em uma folha
  if eh_terminal(estado):
    return avaliar(estado)

  if maximizar:
    melhor_valor = float('-inf')
    for filho in expandir(estado):
      #JOGAR NO MAX DEPOIS EU VOU NO MIN
      valor = minimax(filho, False)
      melhor_valor = max(melhor_valor, valor)
  else:
    melhor_valor = float('inf')
    for filho in expandir(estado):
      #JOGAR NO MIN DEPOIS EU VOU NO MAX
      valor = minimax(filho, True)
      melhor_valor = min(melhor_valor, valor)
  print(f'Estado {estado}: valor = {melhor_valor}')
  return melhor_valor

resultado = minimax('A', True)
print(f'Resultado: {resultado}')

def escolher_jogada(estado):
  melhor_jogada = None
  melhor_valor = float('-inf')

  for filho in expandir(estado):
    #Após a jogada de Max, será a vez de uma de MIN.
    valor = minimax(filho, False)
    if valor > melhor_valor:
      melhor_valor = valor
      melhor_jogada = filho

  return melhor_jogada, melhor_valor
