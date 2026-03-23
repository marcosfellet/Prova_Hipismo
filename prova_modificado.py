import csv
from pathlib import Path
import os
from datetime import datetime
import json
import pandas as pd

class Aluno:
    def __init__(self, metragem, velocidade, nome, montaria, categoria):
        self._nome = nome
        self._montaria = montaria
        self._categoria = categoria          # grupo: chao, x, 40cm, 60cm, 80cm, 1m
        self._parametros = ParametrosProva(metragem, velocidade)

        self._tempo = None
        self._faltas = None
        self._obstaculos = None
        self._penalidade_tempo = None
        self._pontuacao = None
        self._avaliado = False

        self._tempo_concedido = self._parametros.tempo_concedido
        self._tempo_ideal = self._parametros.tempo_ideal
        self._tempo_limite = self._parametros.tempo_limite

    def avaliar(self):
        self._limpar_tela()
        print(f"\n{'='*60}")
        print(f" AVALIACAO DO COMPETIDOR".center(60))
        print(f"{'='*60}")
        print(f"\n Nome: {self._nome}")
        print(f" Montaria: {self._montaria}")
        print(f" Categoria: {self._categoria}")
        if self._categoria != '1m':
            print(f"\n Tempo concedido: {self._tempo_concedido}s")
            print(f" Tempo ideal: {self._tempo_ideal}s")
            print(f" Tempo limite: {self._tempo_limite}s")
        print(f"{'='*60}")

        # Coletar dados
        self._tempo = self._get_tempo()

        # Para categoria 1m, faltas e obstáculos não são usados na pontuação, mas ainda perguntamos para registro
        faltas_data = self._get_faltas()
        self._faltas = faltas_data[0]
        self._obstaculos = faltas_data[1]

        # Calcular penalidade de tempo (apenas para outras categorias)
        if self._categoria != '1m':
            self._penalidade_tempo = self._get_faltas_tempo()
        else:
            self._penalidade_tempo = 0

        self._pontuacao = self._get_pontuacao()
        self._avaliado = True

        print(f"\n{'='*60}")
        print(f" RESULTADO".center(60))
        print(f"{'='*60}")
        if self._categoria == '1m':
            print(f"\n Tempo: {self._pontuacao:.2f} segundos")
        else:
            print(f"\n Penalidade final: {self._pontuacao:.2f}")
            print(f" Penalidade por tempo: {self._penalidade_tempo}")
            print(f" Faltas: {self._faltas}")
            if self._obstaculos:
                print(f" Obstaculos com falta: {', '.join(self._obstaculos)}")
        print(f"\n{'='*60}")

        input("\nPressione Enter para continuar...")
        return self._pontuacao

    def _limpar_tela(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def _get_tempo(self):
        while True:
            try:
                tempo = float(input('\n Digite o tempo (s) - use PONTO como separador decimal: '))
                return tempo
            except ValueError:
                print(" Valor invalido! Digite um numero (ex: 45.6)")

    def _get_faltas(self):
        # Para 1m, faltas não são usadas, mas perguntamos por consistência
        while True:
            try:
                faltas = int(input('\n Digite o numero de faltas: '))
                break
            except ValueError:
                print(" Valor invalido! Digite um numero inteiro.")

        obstaculos_input = input(' Digite os obstaculos com falta (ex: 1,2,3 - Enter para nenhum): ').strip()
        if obstaculos_input == '':
            obstaculos = []
        else:
            obstaculos = [obs.strip() for obs in obstaculos_input.split(',') if obs.strip()]
        return [faltas, obstaculos]

    def _get_faltas_tempo(self):
        # Não usado para 1m
        diferenca_tempo = abs(self._tempo - self._tempo_concedido)
        diferenca_tempo_limite = abs(self._tempo - self._tempo_limite)

        if self._tempo == self._tempo_concedido:
            return 1
        elif self._tempo < self._tempo_limite or self._tempo >= self._tempo_concedido:
            if diferenca_tempo >= 0.01 and self._tempo_limite < self._tempo:
                penalidade = round(diferenca_tempo, 0)
                return 1 if penalidade == 0 else penalidade +1
            elif diferenca_tempo_limite >= 0.01 and self._tempo < self._tempo_concedido:
                penalidade = round(diferenca_tempo_limite, 0)
                return 1 if penalidade == 0 else penalidade
        return 0

    def _get_pontuacao(self):
        if self._categoria == '1m':
            # Pontuação = tempo (menor tempo melhor)
            return self._tempo
        else:
            return self._faltas * 4 + self._penalidade_tempo

    def to_dict(self):
        base = {
            'nome': self._nome,
            'montaria': self._montaria,
            'categoria': self._categoria,
            'tempo': self._tempo,
            'faltas': self._faltas,
            'obstaculos': ', '.join(self._obstaculos) if self._obstaculos else '',
            'avaliado': self._avaliado,
        }
        if self._categoria == '1m':
            base['pontuacao'] = self._pontuacao  # tempo
        else:
            base.update({
                'penalidade_tempo': self._penalidade_tempo,
                'pontuacao': self._pontuacao,
                'tempo_concedido': self._tempo_concedido,
                'tempo_ideal': self._tempo_ideal,
                'tempo_limite': self._tempo_limite
            })
        return base

    @property
    def nome(self):
        return self._nome

    @property
    def pontuacao(self):
        return self._pontuacao

    @property
    def avaliado(self):
        return self._avaliado

    @property
    def tempo_ideal(self):
        return self._tempo_ideal

    @property
    def tempo(self):
        return self._tempo


class ParametrosProva:
    def __init__(self, metragem=0, velocidade=0):
        self._metragem = float(metragem)
        self._velocidade = float(velocidade)
        self._tempo_concedido = self._calcula_TC()
        self._tempo_ideal = self._calcula_TI()
        self._tempo_limite = self._calcula_TL()

    def _calcula_TI(self) -> float:
        return round(self._tempo_concedido * 0.95, 0)

    def _calcula_TC(self) -> float:
        if self._velocidade <= 0:
            return 0
        return round((self._metragem * 60) / self._velocidade, 0)

    def _calcula_TL(self) -> float:
        return self._tempo_ideal - 3

    @property
    def tempo_concedido(self):
        return self._tempo_concedido

    @property
    def tempo_ideal(self):
        return self._tempo_ideal

    @property
    def tempo_limite(self):
        return self._tempo_limite


class GerenciadorProva:
    def __init__(self, parametros_grupos):
        self._parametros_grupos = parametros_grupos
        self._competidores_por_grupo = {
            'chao': {},
            'x': {},
            '40cm': {},
            '60cm': {},
            '80cm': {},
            '1m': {}
        }
        self._ordem_original = []
        self._grupos_concluidos = set()
        self._proximo_numero = {g: 1 for g in self._competidores_por_grupo}

    def _limpar_tela(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def _mapear_grupo(self, marcador):
        m = marcador.strip().lower()
        if m in ('chao', 'vara no chão'):
            return 'chao'
        if m == 'x':
            return 'x'
        if m == '40cm':
            return '40cm'
        if m == '60cm':
            return '60cm'
        if m == '80cm':
            return '80cm'
        if m == '1m':
            return '1m'
        return None

    def _obter_metragem_grupo(self, grupo):
        return self._parametros_grupos.get(grupo, (0.0, 10))[0]

    def _obter_velocidade_grupo(self, grupo):
        return self._parametros_grupos.get(grupo, (0.0, 10))[1]

    def carregar_lista_competidores(self, caminho_pasta='./Arquivo_Competidores'):
        self._limpar_tela()
        print("=" * 60)
        print(" CARREGANDO LISTA DE COMPETIDORES".center(60))
        print("=" * 60)

        caminho = Path(caminho_pasta)
        if not caminho.exists():
            print(f"\n Pasta nao encontrada: {caminho}")
            input("\nPressione Enter para continuar...")
            return False

        arquivos_csv = list(caminho.glob("*.csv"))
        if not arquivos_csv:
            print("\n Nenhum arquivo CSV encontrado")
            input("\nPressione Enter para continuar...")
            return False

        arquivo_usado = max(arquivos_csv, key=lambda f: f.stat().st_mtime)
        print(f"\n Arquivo carregado: {arquivo_usado.name}")

        with open(arquivo_usado, 'r', encoding='utf-8') as f:
            linhas = f.readlines()

        grupo_atual = None
        for g in self._proximo_numero:
            self._proximo_numero[g] = 1
        self._competidores_por_grupo = {g: {} for g in self._competidores_por_grupo}
        self._ordem_original = []

        for linha in linhas:
            linha = linha.strip()
            if not linha:
                continue

            if linha.endswith(',') or ',' not in linha:
                marcador = linha.rstrip(',').strip()
                grupo_atual = self._mapear_grupo(marcador)
                if grupo_atual:
                    print(f"  Grupo encontrado: {grupo_atual}")
                continue

            if grupo_atual:
                partes = linha.split(',')
                if len(partes) >= 2:
                    nome = partes[0].strip()
                    montaria = partes[1].strip()
                    if nome:
                        metragem = self._obter_metragem_grupo(grupo_atual)
                        velocidade = self._obter_velocidade_grupo(grupo_atual)
                        aluno = Aluno(metragem, velocidade, nome, montaria, grupo_atual)
                        numero = self._proximo_numero[grupo_atual]
                        self._proximo_numero[grupo_atual] += 1
                        self._competidores_por_grupo[grupo_atual][numero] = aluno
                        self._ordem_original.append((grupo_atual, numero, aluno))
                        print(f"    Competidor: {nome} - {montaria}")

        print(f"\n Total de competidores: {len(self._ordem_original)}")
        for grupo, competidores in self._competidores_por_grupo.items():
            if competidores:
                metragem, vel = self._parametros_grupos.get(grupo, (0, 0))
                print(f"   {grupo}: {len(competidores)} competidores (metragem: {metragem}m, velocidade: {vel}m/s)")

        input("\nPressione Enter para continuar...")
        return True

    def adicionar_competidor(self, grupo, nome, montaria):
        if grupo not in self._competidores_por_grupo:
            print(f"Grupo {grupo} invalido!")
            return False
        if grupo in self._grupos_concluidos:
            print(f"Grupo {grupo} ja foi premiado! Nao e possivel adicionar novos competidores.")
            return False

        metragem = self._obter_metragem_grupo(grupo)
        velocidade = self._obter_velocidade_grupo(grupo)
        aluno = Aluno(metragem, velocidade, nome, montaria, grupo)
        numero = self._proximo_numero[grupo]
        self._proximo_numero[grupo] += 1
        self._competidores_por_grupo[grupo][numero] = aluno
        self._ordem_original.append((grupo, numero, aluno))
        print(f"Competidor {nome} adicionado ao grupo {grupo} com numero {numero}.")
        return True

    # --- Ordenação com desempate (para grupos que usam pontuação tradicional) ---
    def _chave_ordenacao(self, aluno):
        if aluno._categoria == '1m':
            # Para 1m, ordena pelo tempo (pontuacao = tempo) e, se empatar, pelo número (ordem de entrada)
            return (aluno.pontuacao, aluno._tempo)  # tempo já é a pontuação
        else:
            if aluno.pontuacao == 0:
                return (0, abs(aluno.tempo - aluno.tempo_ideal))
            else:
                return (aluno.pontuacao, float('inf'))

    def _ordenar_avaliados(self, lista_alunos):
        return sorted(lista_alunos, key=lambda x: self._chave_ordenacao(x[1]))

    # --- Exportações ---
    def salvar_resultados_json(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo = f"resultados_completos_{timestamp}.json"
        dados_json = {
            'parametros_por_grupo': self._parametros_grupos,
            'data_exportacao': datetime.now().isoformat(),
            'grupos': {}
        }
        for grupo, competidores in self._competidores_por_grupo.items():
            if competidores:
                dados_json['grupos'][grupo] = {
                    'metragem': self._obter_metragem_grupo(grupo),
                    'velocidade': self._obter_velocidade_grupo(grupo),
                    'premiado': grupo in self._grupos_concluidos,
                    'competidores': {}
                }
                for numero, aluno in sorted(competidores.items()):
                    dados_json['grupos'][grupo]['competidores'][str(numero)] = aluno.to_dict()
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados_json, f, ensure_ascii=False, indent=2)
        print(f"\n JSON salvo em: {nome_arquivo}")
        return nome_arquivo

    def salvar_resultados_excel(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo = f"resultados_completos_{timestamp}.xlsx"

        with pd.ExcelWriter(nome_arquivo, engine='openpyxl') as writer:
            # Resumo geral
            resumo = []
            for grupo, competidores in self._competidores_por_grupo.items():
                if competidores:
                    total = len(competidores)
                    avaliados = sum(1 for a in competidores.values() if a.avaliado)
                    premiado = "Sim" if grupo in self._grupos_concluidos else "Nao"
                    resumo.append({
                        'Grupo': grupo,
                        'Metragem (m)': self._obter_metragem_grupo(grupo),
                        'Velocidade (m/s)': self._obter_velocidade_grupo(grupo),
                        'Total Competidores': total,
                        'Avaliados': avaliados,
                        'Pendentes': total - avaliados,
                        'Premiado': premiado
                    })
            pd.DataFrame(resumo).to_excel(writer, sheet_name='Resumo Geral', index=False)

            # Informações da prova
            pd.DataFrame([{
                'Data Exportacao': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'Total Competidores': len(self._ordem_original)
            }]).to_excel(writer, sheet_name='Informacoes Prova', index=False)

            # Cada grupo
            for grupo, competidores in self._competidores_por_grupo.items():
                if not competidores:
                    continue

                dados = []
                for num, aluno in sorted(competidores.items()):
                    base = {
                        'Nº no Grupo': num,
                        'Nome': aluno._nome,
                        'Montaria': aluno._montaria,
                        'Tempo (s)': aluno._tempo if aluno._tempo else '',
                        'Faltas': aluno._faltas if aluno._faltas else '',
                        'Obstaculos': ', '.join(aluno._obstaculos) if aluno._obstaculos else '',
                        'Status': 'Avaliado' if aluno._avaliado else 'Pendente'
                    }
                    if grupo == '1m':
                        base['Pontuacao (tempo)'] = aluno._pontuacao if aluno._pontuacao else ''
                    else:
                        base.update({
                            'Penalidade Tempo': aluno._penalidade_tempo if aluno._penalidade_tempo else '',
                            'Pontuacao': aluno._pontuacao if aluno._pontuacao else '',
                            'Tempo Concedido': aluno._tempo_concedido,
                            'Tempo Ideal': aluno._tempo_ideal,
                            'Tempo Limite': aluno._tempo_limite
                        })
                    dados.append(base)

                df = pd.DataFrame(dados)

                if any(a._avaliado for a in competidores.values()):
                    avaliados_list = [(n, a) for n, a in competidores.items() if a.avaliado]
                    ordenados = self._ordenar_avaliados(avaliados_list)
                    classif = []
                    for pos, (num, aluno) in enumerate(ordenados, 1):
                        linha = {
                            'Classificacao': pos,
                            'Nº no Grupo': num,
                            'Nome': aluno._nome,
                            'Montaria': aluno._montaria,
                            'Tempo (s)': aluno._tempo,
                            'Faltas': aluno._faltas,
                            'Obstaculos': ', '.join(aluno._obstaculos) if aluno._obstaculos else '',
                        }
                        if grupo == '1m':
                            linha['Pontuacao (tempo)'] = aluno._pontuacao
                        else:
                            linha.update({
                                'Penalidade Tempo': aluno._penalidade_tempo,
                                'Pontuacao': aluno._pontuacao,
                                '|tempo - tempo_ideal|': abs(aluno.tempo - aluno.tempo_ideal) if aluno.tempo else ''
                            })
                        classif.append(linha)
                    pd.DataFrame(classif).to_excel(writer, sheet_name=f'Grupo_{grupo}_Classificados', index=False)

                    pendentes = df[df['Status'] == 'Pendente']
                    if not pendentes.empty:
                        pendentes.to_excel(writer, sheet_name=f'Grupo_{grupo}_Pendentes', index=False)
                else:
                    df.to_excel(writer, sheet_name=f'Grupo_{grupo}', index=False)

            # Classificação geral (considerando que para 1m a pontuação é tempo, então misturar é problemático.
            # Melhor não misturar categorias com métricas diferentes. Vamos deixar só a classificação por categoria.
            # Mas podemos criar uma planilha de melhores tempos de 1m separadamente.
            # Para simplificar, não faremos classificação geral cruzando categorias.
        print(f"\n Excel salvo em: {nome_arquivo}")
        return nome_arquivo

    # --- Ranking no terminal ---
    def _mostrar_ranking_categorias(self):
        self._limpar_tela()
        print("=" * 80)
        print(" RANKING DAS CATEGORIAS".center(80))
        print("=" * 80)

        todas = {}
        for grupo, competidores in self._competidores_por_grupo.items():
            for num, aluno in competidores.items():
                if aluno._avaliado:
                    if grupo not in todas:
                        todas[grupo] = []
                    diff = abs(aluno.tempo - aluno.tempo_ideal) if aluno.tempo else 0
                    todas[grupo].append({
                        'numero': num,
                        'nome': aluno._nome,
                        'montaria': aluno._montaria,
                        'pontuacao': aluno._pontuacao,
                        'tempo': aluno._tempo,
                        'faltas': aluno._faltas,
                        'diferenca': diff,
                        'tempo_ideal': aluno._tempo_ideal
                    })

        if not todas:
            print("\n Nenhum competidor avaliado ainda!")
            input("\nPressione Enter para continuar...")
            return

        for cat in ['chao', 'x', '40cm', '60cm', '80cm', '1m']:
            if cat not in todas:
                continue

            comps = todas[cat]
            # Ordenar com a chave correta
            if cat == '1m':
                comps.sort(key=lambda x: (x['pontuacao'], x['numero']))  # pontuacao = tempo
            else:
                comps.sort(key=lambda x: (x['pontuacao'], x['diferenca']) if x['pontuacao'] == 0 else (x['pontuacao'], float('inf')))

            metragem = self._obter_metragem_grupo(cat)
            vel = self._obter_velocidade_grupo(cat)

            print(f"\n{'='*80}")
            print(f" CATEGORIA: {cat.upper()}".center(80))
            print(f" Altura: {metragem}m | Velocidade: {vel}m/s".center(80))
            if cat in self._grupos_concluidos:
                print(" GRUPO PREMIADO".center(80))
            print(f"{'='*80}")

            if cat == '1m':
                print(f"\n{'POS':<6} {'Nº':<4} {'NOME':<30} {'MONTARIA':<15} {'TEMPO (s)':<10} {'FALTAS':<6}")
                print("-" * 75)
                for pos, c in enumerate(comps, 1):
                    medalha = "1º" if pos == 1 else "2º" if pos == 2 else "3º" if pos == 3 else f"{pos:2d}º"
                    print(f"{medalha:<6} {c['numero']:<4} {c['nome'][:28]:<30} "
                          f"{c['montaria'][:13]:<15} {c['tempo']:<10.2f} {c['faltas']:<6}")
            else:
                print(f"\n{'POS':<6} {'Nº':<4} {'NOME':<30} {'MONTARIA':<15} {'PONT':<8} {'TEMPO':<8} {'FALTAS':<6} {'DIF':<8}")
                print("-" * 95)
                for pos, c in enumerate(comps, 1):
                    medalha = "1º" if pos == 1 else "2º" if pos == 2 else "3º" if pos == 3 else f"{pos:2d}º"
                    print(f"{medalha:<6} {c['numero']:<4} {c['nome'][:28]:<30} "
                          f"{c['montaria'][:13]:<15} {c['pontuacao']:<8.2f} "
                          f"{c['tempo']:<8.2f} {c['faltas']:<6} {c['diferenca']:<8.2f}")

            if comps:
                if cat == '1m':
                    tempos = [c['tempo'] for c in comps]
                    media = sum(tempos) / len(tempos)
                    print(f"\nESTATISTICAS DA CATEGORIA:")
                    print(f"   Total de competidores: {len(comps)}")
                    print(f"   Media dos tempos: {media:.2f}s")
                    print(f"   Melhor tempo: {min(tempos):.2f}s")
                    print(f"   Pior tempo: {max(tempos):.2f}s")
                else:
                    pont = [c['pontuacao'] for c in comps]
                    media = sum(pont) / len(pont)
                    print(f"\nESTATISTICAS DA CATEGORIA:")
                    print(f"   Total de competidores: {len(comps)}")
                    print(f"   Media de pontuacao: {media:.2f}")
                    print(f"   Melhor pontuacao: {min(pont):.2f}")
                    print(f"   Pior pontuacao: {max(pont):.2f}")
                    menor_tempo = min(comps, key=lambda x: x['tempo'])
                    print(f"   Menor tempo: {menor_tempo['tempo']:.2f}s ({menor_tempo['nome']})")

        input("\n\nPressione Enter para continuar...")

    # --- Métodos do menu (idênticos aos anteriores, apenas ajustes nos nomes) ---
    def menu_principal(self):
        while True:
            self._limpar_tela()
            print("=" * 60)
            print(" SISTEMA DE AVALIACAO DE PROVA".center(60))
            print("=" * 60)

            total = len(self._ordem_original)
            avaliados = sum(1 for _, _, a in self._ordem_original if a.avaliado)
            print(f"\n PROGRESSO: {avaliados}/{total} avaliados")

            print("\n STATUS DOS GRUPOS:")
            for g in ['chao', 'x', '40cm', '60cm', '80cm', '1m']:
                comps = self._competidores_por_grupo[g]
                if comps:
                    av = sum(1 for a in comps.values() if a.avaliado)
                    tot = len(comps)
                    status = "PREMIADO" if g in self._grupos_concluidos else f"{av}/{tot}"
                    met = self._obter_metragem_grupo(g)
                    vel = self._obter_velocidade_grupo(g)
                    print(f"   {g.upper()} (altura: {met}m, vel: {vel}m/s): {status}")

            print("\n" + "-" * 60)
            print("OPCOES:")
            print("   1 - Avaliar proximo grupo")
            print("   2 - Ver classificacao de um grupo")
            print("   3 - Mostrar resultados gerais")
            print("   4 - Ver RANKING das categorias")
            print("   5 - Adicionar novo competidor manualmente")
            print("   6 - SALVAR RESULTADOS (JSON + Excel)")
            print("   7 - Sair")
            print("-" * 60)

            op = input("\n Escolha uma opcao: ").strip()

            if op == '1':
                self._avaliar_por_grupo()
            elif op == '2':
                self._ver_classificacao_grupo()
            elif op == '3':
                self._mostrar_resultados_gerais()
            elif op == '4':
                self._mostrar_ranking_categorias()
            elif op == '5':
                self._adicionar_competidor_manual()
            elif op == '6':
                self._salvar_ambos_formatos()
            elif op == '7':
                if avaliados > 0:
                    print("\n Voce tem resultados nao salvos!")
                    salvar = input("Deseja salvar antes de sair? (s/n): ").lower()
                    if salvar == 's':
                        self._salvar_ambos_formatos()
                print("\n Encerrando programa...")
                break
            else:
                print("\n Opcao invalida!")
                input("Pressione Enter para continuar...")

    def _salvar_ambos_formatos(self):
        self._limpar_tela()
        print("=" * 60)
        print(" SALVANDO RESULTADOS".center(60))
        print("=" * 60)
        try:
            self.salvar_resultados_json()
            self.salvar_resultados_excel()
            print("\n Resultados salvos com sucesso!")
        except Exception as e:
            print(f"\n Erro ao salvar: {e}")
        input("\nPressione Enter para continuar...")

    def _adicionar_competidor_manual(self):
        self._limpar_tela()
        print("=" * 60)
        print(" ADICIONAR NOVO COMPETIDOR".center(60))
        print("=" * 60)

        grupos = ['chao', 'x', '40cm', '60cm', '80cm', '1m']
        for i, g in enumerate(grupos, 1):
            premiado = " (PREMIADO - NAO PODE ADICIONAR)" if g in self._grupos_concluidos else ""
            print(f"   {i}. {g}{premiado}")

        escolha = input("\n Digite o nome do grupo (ou numero): ").strip().lower()
        if escolha.isdigit():
            idx = int(escolha) - 1
            if 0 <= idx < len(grupos):
                grupo = grupos[idx]
            else:
                print("\n Numero invalido!")
                input("Pressione Enter para continuar...")
                return
        else:
            grupo = escolha

        if grupo not in self._competidores_por_grupo:
            print("\n Grupo invalido!")
            input("Pressione Enter para continuar...")
            return
        if grupo in self._grupos_concluidos:
            print("\n Esse grupo ja foi premiado. Nao e possivel adicionar novos competidores.")
            input("Pressione Enter para continuar...")
            return

        nome = input("\n Nome do competidor: ").strip()
        if not nome:
            print(" Nome nao pode ser vazio!")
            input("Pressione Enter para continuar...")
            return
        montaria = input(" Montaria do competidor: ").strip()
        if not montaria:
            montaria = "Sem montaria"

        self.adicionar_competidor(grupo, nome, montaria)
        input("\nPressione Enter para continuar...")

    def _avaliar_por_grupo(self):
        self._limpar_tela()
        print("=" * 60)
        print(" AVALIACAO POR GRUPO".center(60))
        print("=" * 60)

        disponiveis = []
        for g, comps in self._competidores_por_grupo.items():
            if g in self._grupos_concluidos:
                continue
            nao_avaliados = [n for n, a in comps.items() if not a.avaliado]
            if nao_avaliados:
                disponiveis.append(g)
                print(f"\n{g.upper()}: {len(nao_avaliados)} aguardando")
                for n in nao_avaliados[:3]:
                    aluno = comps[n]
                    print(f"   #{n}: {aluno.nome}")
                if len(nao_avaliados) > 3:
                    print(f"   ... e mais {len(nao_avaliados)-3}")

        if not disponiveis:
            print("\n Todos os grupos ja foram avaliados e premiados!")
            input("\nPressione Enter para continuar...")
            return

        print("\n" + "-" * 60)
        for i, g in enumerate(disponiveis, 1):
            print(f"   {i}. {g}")

        escolha = input("\n Digite o nome do grupo (ou numero): ").strip().lower()
        if escolha.isdigit():
            idx = int(escolha) - 1
            if 0 <= idx < len(disponiveis):
                escolha = disponiveis[idx]

        if escolha in self._competidores_por_grupo:
            self._avaliar_competidores_grupo(escolha)
        else:
            print("\n Grupo invalido!")
            input("Pressione Enter para continuar...")

    def _avaliar_competidores_grupo(self, grupo):
        comps = self._competidores_por_grupo[grupo]
        nao_avaliados = [(n, a) for n, a in comps.items() if not a.avaliado]
        if not nao_avaliados:
            return

        print(f"\n Grupo: {grupo.upper()} - {len(nao_avaliados)} competidores")
        print("=" * 50)

        for num, aluno in sorted(nao_avaliados):
            print(f"\n PROXIMO: #{num} - {aluno.nome}")
            input("\nPressione Enter para avaliar...")
            aluno.avaliar()

        self._premiar_grupo(grupo)
        self._grupos_concluidos.add(grupo)

        print("\n" + "-" * 50)
        salvar = input("Deseja salvar os resultados ate agora? (s/n): ").lower()
        if salvar == 's':
            self._salvar_ambos_formatos()

    def _premiar_grupo(self, grupo):
        self._limpar_tela()
        comps = self._competidores_por_grupo[grupo]
        avaliados = [(n, a) for n, a in comps.items() if a.avaliado]
        if not avaliados:
            return

        classificados = self._ordenar_avaliados(avaliados)

        print("\n" + "=" * 80)
        print(f"        PREMIACAO DO GRUPO: {grupo.upper()}        ".center(80))
        print("=" * 80)

        import time
        time.sleep(1)

        for pos, (num, aluno) in enumerate(classificados[:3], 1):
            if pos == 1:
                lugar = "PRIMEIRO LUGAR"
                medalha = "1º"
            elif pos == 2:
                lugar = "SEGUNDO LUGAR"
                medalha = "2º"
            else:
                lugar = "TERCEIRO LUGAR"
                medalha = "3º"

            print("\n" + "-" * 40)
            time.sleep(1)
            if pos == 1:
                print("E o GRANDE CAMPEAO e...")
                time.sleep(2)
                print(f"\n   {medalha} - {aluno.nome.upper()}!")
            else:
                print(f"Em {lugar.lower()}...")
                time.sleep(1)
                print(f"\n   {medalha} - {aluno.nome.upper()}!")
            if grupo == '1m':
                print(f"      Tempo: {aluno.pontuacao:.2f}s")
            else:
                print(f"      Penalidade: {aluno.pontuacao:.2f}")
            print("\nAplausos!")

        print("\n" + "=" * 50)
        print("PODIO FINAL DO GRUPO")
        print("=" * 50)
        for pos, (num, aluno) in enumerate(classificados[:5], 1):
            medalha = "1º" if pos == 1 else "2º" if pos == 2 else "3º" if pos == 3 else "4º" if pos == 4 else "5º"
            if grupo == '1m':
                print(f"{medalha} - {aluno.nome[:30]:<30} {aluno.pontuacao:<12.2f}s")
            else:
                print(f"{medalha} - {aluno.nome[:30]:<30} {aluno.pontuacao:<12.2f}")

        input("\n\nPressione Enter para continuar...")

    def _ver_classificacao_grupo(self):
        self._limpar_tela()
        print("=" * 60)
        print(" CLASSIFICACAO POR GRUPO".center(60))
        print("=" * 60)

        grupos = ['chao', 'x', '40cm', '60cm', '80cm', '1m']
        print("\nGrupos disponiveis:")
        for i, g in enumerate(grupos, 1):
            if self._competidores_por_grupo[g]:
                premiado = " (PREMIADO)" if g in self._grupos_concluidos else ""
                print(f"   {i}. {g}{premiado}")

        escolha = input("\n Digite o nome do grupo: ").strip().lower()
        if escolha.isdigit():
            idx = int(escolha) - 1
            if 0 <= idx < len(grupos):
                escolha = grupos[idx]

        if escolha in self._competidores_por_grupo:
            self._mostrar_classificacao_grupo(escolha)
        else:
            print("\n Grupo invalido!")
            input("Pressione Enter para continuar...")

    def _mostrar_classificacao_grupo(self, grupo):
        self._limpar_tela()
        comps = self._competidores_por_grupo[grupo]
        avaliados = [(n, a) for n, a in comps.items() if a.avaliado]
        if not avaliados:
            print(f"\n Nenhum competidor avaliado no grupo {grupo}")
            input("Pressione Enter para continuar...")
            return

        classificados = self._ordenar_avaliados(avaliados)

        met = self._obter_metragem_grupo(grupo)
        vel = self._obter_velocidade_grupo(grupo)
        print(f"\n{'='*60}")
        print(f" CLASSIFICACAO DO GRUPO: {grupo.upper()} (altura: {met}m, vel: {vel}m/s)".center(60))
        if grupo in self._grupos_concluidos:
            print(" GRUPO PREMIADO".center(60))
        print(f"{'='*60}")

        if grupo == '1m':
            print(f"\n{'POS':<4} {'NOME':<30} {'TEMPO (s)':<12} {'FALTAS':<8}")
            print("-" * 60)
            for pos, (num, aluno) in enumerate(classificados, 1):
                medalha = "1o" if pos == 1 else "2o" if pos == 2 else "3o" if pos == 3 else f"{pos:2d}"
                print(f"{medalha:>4} {aluno.nome[:30]:<30} {aluno.pontuacao:<12.2f} {aluno._faltas:<8}")
        else:
            print(f"\n{'POS':<4} {'NOME':<30} {'PONTUACAO':<12} {'DIFERENCA |t-t_ideal|':<20}")
            print("-" * 70)
            for pos, (num, aluno) in enumerate(classificados, 1):
                medalha = "1o" if pos == 1 else "2o" if pos == 2 else "3o" if pos == 3 else f"{pos:2d}"
                diff = abs(aluno.tempo - aluno.tempo_ideal) if aluno.tempo else 0
                print(f"{medalha:>4} {aluno.nome[:30]:<30} {aluno.pontuacao:<12.2f} {diff:<20.2f}")

        input("\n\nPressione Enter para continuar...")

    def _mostrar_resultados_gerais(self):
        self._limpar_tela()
        print("=" * 70)
        print(" RESULTADOS GERAIS".center(70))
        print("=" * 70)

        for g in ['chao', 'x', '40cm', '60cm', '80cm', '1m']:
            comps = self._competidores_por_grupo[g]
            av = {n: a for n, a in comps.items() if a.avaliado}
            if not av:
                continue

            met = self._obter_metragem_grupo(g)
            vel = self._obter_velocidade_grupo(g)
            print(f"\n GRUPO: {g.upper()} (altura: {met}m, vel: {vel}m/s) - {len(av)} avaliados")
            print("-" * 70)
            if g == '1m':
                print(f"{'Nº':<4} {'NOME':<30} {'TEMPO (s)':<12} {'FALTAS':<8}")
                print("-" * 70)
                for num in sorted(av.keys()):
                    aluno = av[num]
                    print(f"{num:<4} {aluno.nome[:30]:<30} {aluno.pontuacao:<12.2f} {aluno._faltas:<8}")
            else:
                print(f"{'Nº':<4} {'NOME':<30} {'PENALIDADE':<12} {'TEMPO':<10} {'FALTAS':<8}")
                print("-" * 70)
                for num in sorted(av.keys()):
                    aluno = av[num]
                    print(f"{num:<4} {aluno.nome[:30]:<30} {aluno.pontuacao:<12.2f} "
                          f"{aluno._tempo:<10.2f} {aluno._faltas:<8}")

        input("\n\nPressione Enter para continuar...")


# ================== PROGRAMA PRINCIPAL ==================
if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 60)
    print(" SISTEMA DE AVALIACAO DE PROVA".center(60))
    print("=" * 60)

    print("\n CONFIGURACAO DOS PARAMETROS POR GRUPO")
    print("-" * 40)

    parametros = {}

    # 40cm
    print("\n1. GRUPO 40cm")
    try:
        met = float(input("   Metragem (metros): "))
        vel = float(input("   Velocidade (m/s): "))
        parametros['40cm'] = (met, vel)
    except ValueError:
        print("   Valores invalidos! Usando padrao: 0.4m e 10m/s")
        parametros['40cm'] = (0.4, 10)

    # 60cm e 80cm (mesmos)
    print("\n2. GRUPOS 60cm e 80cm (parametros iguais)")
    try:
        met = float(input("   Metragem (metros): "))
        vel = float(input("   Velocidade (m/s): "))
        parametros['60cm'] = (met, vel)
        parametros['80cm'] = (met, vel)
    except ValueError:
        print("   Valores invalidos! Usando padrao: 0.6m e 10m/s")
        parametros['60cm'] = (0.6, 10)
        parametros['80cm'] = (0.6, 10)

    # 1m fixo (conforme solicitado: pontuação por tempo)
    parametros['1m'] = (0.0, 1.0)

    # Chao
    print("\n3. GRUPO CHAO")
    try:
        met = float(input("   Metragem (metros): "))
        vel = float(input("   Velocidade (m/s): "))
        parametros['chao'] = (met, vel)
    except ValueError:
        print("   Valores invalidos! Usando padrao: 0.0m e 10m/s")
        parametros['chao'] = (0.0, 10)

    # X
    print("\n4. GRUPO X")
    try:
        met = float(input("   Metragem (metros): "))
        vel = float(input("   Velocidade (m/s): "))
        parametros['x'] = (met, vel)
    except ValueError:
        print("   Valores invalidos! Usando padrao: 0.0m e 10m/s")
        parametros['x'] = (0.0, 10)

    prova = GerenciadorProva(parametros)

    if prova.carregar_lista_competidores():
        prova.menu_principal()
    else:
        print("\n Erro ao carregar lista de competidores. Encerrando.")