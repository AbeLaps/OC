import numpy as np
import sys

#Aluno: Abel Andrade Prazeres dos Santos; matricula:22450083

#tamanho da ram, modificar a fim de testes mais simples
TAMRAM = 256

#dicionarios de instrucoes e registradores
instrucoesVirg = ['ADD', 'SHR','SHL', 'NOT', 'AND', 'OR', 'XOR', 'CMP',
 'LD', 'ST', 'DATA','MOVE']

instructor = {'ADD': '8', 'SHR': '9','SHL': 'a', 'NOT': 'b', 'AND':'c', 'OR': 'd', 'XOR': 'e', 'CMP': 'f',
'LD':'0', 'ST':'1', 'DATA':'2', 'JMPR':'3', 'JMP':'4', 'CLF':'6','IN':'7', 'OUT':'7','MOVE': 'e', 'HALT':'4','CLR': 'e'}

regs = {'R0': '00', 'R1': '01', 'R2': '10', 'R3': '11'}

#para checar comandos de 2 bytes
instrucoes = {'DATA', 'JMP', 'MOVE', 'HALT'}

labels = {}

#RAM
memory = [['0','0'] for _ in range(TAMRAM)]

#jcaez
caez = {'C': 8, 'A': 4, 'E': 2, 'Z': 1}


#pegar os arquivos a serem utilizados
if len(sys.argv) != 3:
    print("erro de compilacao, uso correto: python3 montador.py <entrada.asm> <saida.txt>")
    sys.exit(1)

arquivo_entrada = sys.argv[1]
arquivo_saida = sys.argv[2]

def escreverMemoriaEmArquivo(memoryList):   
    with open(arquivo_saida, 'w') as f:
        f.write('v3.0 hex words plain\n')
        for i in range(TAMRAM):
            f.write(memoryList[i][0].lower())
            f.write(memoryList[i][1].lower())
            f.write('\n')



with open(arquivo_entrada, 'r') as f:
    content = f.readlines()

#formatar a lista de instrucoes
content = [item.split(';')[0] for item in content] #tira comentarios
content = [x.strip().upper().split(' ') for x in content] #separa e tira espacos para modelo ['add', 'ra,rb']


#formata toda a lista para ficar cada argumento como um elemento--------
content1 = []
cont = 1

for sublista in content:
    cont += 1
    # remove itens vazios
    novaSublista = [item for item in sublista if  item != '']
    #print(novaSublista)
    if novaSublista:  # so adiciona se não ficar vazia
        if novaSublista[0] in instrucoesVirg:
            if not ',' in novaSublista[1]:
                print('erro: numero de argumentos invalidos linha:', cont)
                sys.exit(1)
        # divide elementos com vírgula
        sublista2 = []
        for item in novaSublista:
            sublista2.extend(item.split(','))
        content1.append(sublista2)

content1 = [[item for item in sublista if item != ''] for sublista in content1] #apenas para formatar r1,r2


#logica: para cada comando de 2 bytes adicionar um deslocamento para que possa preencher o primeiro numero corretamente

addrAt = 0

#1 passada
#percorre verificando os labels e colocando no dict
try:
    for i in range(len(content1)):
        if ':' in content1[i][0]:
            labels.update({content1[i][0][:-1] : (str(hex(addrAt))[2:]).zfill(2)})
            content1[i].pop(0)

        if content[i][0] in instrucoes:
            addrAt += 2

        else: 
            addrAt += 1

    print(content1)
    print(labels)
    #segunda passada
    #global para todas as intrucoes-------------

    desloc = 0
    addrAt = 0
    for i in range(len(content1)):
        k = i + desloc
        instAtual = content1[i][0]

        if len(content1[i]) > 3:
            print('erro: numero de argumentos invalido', instAtual, 'linha:',i)
            sys.exit(1)

        try: #jcaez
            if instAtual[0] == 'J' and instAtual[:2] != 'JM' : #intrucoes normais                                     
                memory[k][0] = '5' # 1 algarismo hex

            else: #normais
                memory[k][0] = instructor[instAtual] # 1 algarismo hex

        except:
            print('erro: instrucao invalida', instAtual)
            sys.exit(1)


        match instAtual:

            case 'DATA':
                desloc += 1
                addrAt += 2
                memory[k][1] = hex(int('00' + regs[content1[i][1]],2))[2:] # 1 algarismo hex

                #checar formato do valor
                if len(content1[i][2]) > 2 and content1[i][2][1] == 'X': #hexa
                    memory[k+1][0] = content1[i][2][2] #colocar o valor do data 
                    memory[k+1][1] = content1[i][2][3]

                elif len(content1[i][2]) > 2 and content1[i][2][1] == 'B': #binario
                    num = hex(int(content1[i][2],2))[2:].zfill(2) #colocar 2 digitos
                    memory[k+1][0] = num[0]
                    memory[k+1][1] = num[1]

                else: #decimal
                    num = int(content1[i][2])
                    if num > 127 or num < -128:
                        print('erro: numero fora do escopo', num)
                        sys.exit(1)

                    num = str(hex(int(np.binary_repr(num, width=8),2)))[2:].zfill(2) # complemento de 2 com 2 digitos
                    memory[k+1][0] = num[0]
                    memory[k+1][1] = num[1]


            case 'JMPR': #para jmpr
                addrAt += 1
                memory[k][1] = hex(int('00' + regs[content1[i][1]],2))[2:] 


            case 'JMP': #para jmp
                desloc += 1
                addrAt += 2
                print(content1[i][i])
                if content1[i][1] in labels:
                    memory[k+1][0] = labels[content1[i][1]][0]
                    memory[k+1][1] = labels[content1[i][1]][1]
                else:
                    if content1[i][1].lower().startswith(('0x')):
                        memory[k+1][0] = content1[i][1][2] #colocar o endereco do jmp sem label
                        memory[k+1][1] = content1[i][1][3]
                    else:
                        print('erro: label não encontrado')
                        sys.exit(1)


            case 'HALT':
                desloc += 1
                if addrAt < 16:
                    memory[k+1][0] = '0'
                    memory[k+1][1] = hex(addrAt)[2]
                else:
                    memory[k+1][0] = hex(addrAt)[2]
                    memory[k+1][1] = hex(addrAt)[3]
                addrAt += 2


            case 'CLF': #para CLF
               memory[k][1] = '0' 
               addrAt += 1


            case 'CLR':
                opcode = regs[content1[i][1]]
                memory[k][1] = hex(int(opcode + opcode,2))[2]
                addrAt += 1


            case 'MOVE':
                desloc += 1
                memory[k][1] = hex(int(regs[content1[i][1]] + regs[content1[i][2]],2))[2]
                memory[k+1][0] = 'e'
                memory[k+1][1] = hex(int(regs[content1[i][2]] + regs[content1[i][1]],2))[2]
                addrAt += 2


            case 'IN' | 'OUT': #para i/o
                opcode = ['0','0']
                if instAtual == 'OUT':
                    opcode[0] = '1'

                instAtual = content1[i][1]
                if instAtual == 'ADDR':
                    opcode[1] = '1'

                opcode = ''.join(opcode) 
                memory[k][1] = hex(int(opcode + regs[content1[i][2]],2))[2:]
                addrAt += 1


            case instru if instru[0] == 'J': #para jcaez
                desloc += 1
                acc = 0
                addrAt += 2
                for j in range(1, len(instAtual)):
                    acc += caez[instAtual[j]]
                memory[k][1] = hex(acc)[2]

                #checar formato do valor do addr

                if content1[i][1] in labels:
                    memory[k+1][0] = labels[content1[i][1]][0]
                    memory[k+1][1] = labels[content1[i][1]][1]

                elif content1[i][1][1] == 'X': #hexa
                    memory[k+1][0] = content1[i][1][2] #colocar o valor do addr
                    memory[k+1][1] = content1[i][1][3]

                elif len(content1[i][1]) > 2 and content1[i][1][1] == 'B': #binario
                    num = hex(int(content1[i][1],2)).zfill(2) #colocar 2 digitos
                    memory[k+1][0] = num[2]
                    memory[k+1][1] = num[3]

                else: #decimal
                    num = int(content1[i][1]) 
                    if num > 255 or num < 0:
                        print('erro: numero fora do escopo', num)
                        sys.exit(1)
                    num = str(hex(num))[2:].zfill(2) #colocar 2 digitos
                    memory[k+1][0] = num[0]
                    memory[k+1][1] = num[1]


            case _: #para instrucoes modelo ra,rb
                memory[k][1] = hex(int(regs[content1[i][1]] + regs[content1[i][2]],2))[2]
except:
    print(f'erro de leitura {instAtual} linha: {i}')
    sys.exit(1)
#---------------------------------------------------------------------------------------------------

#escrever a memoria no arquivo 
escreverMemoriaEmArquivo(memory)
print("compilado com sucesso")
