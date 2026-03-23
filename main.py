from prova import Aluno

metragem = input('Digite a metragem da pista, por favor (m): ')
velocidade = input('Digite a velocidade, por favor (m/min): ')

aluno = Aluno(metragem, velocidade)

print('\n ************************* PARAMETROS DA PROVA ************************* \n')

print(f'tempo ideal: {parametros._tempo_ideal} segundos')
print(f'tempo concedido: {parametros._tempo_concedido} segundos')
print(f'tempo limite: {parametros._tempo_limite} segundos')

print('\n *********************************************************************** \n')