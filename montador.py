import numpy as np
import sys

#tamanho da ram, modificar a fim de testes mais simples
TAMRAM = 256

#pegar os arquivos a serem utilizados
if len(sys.argv) != 3:
    print("erro de compilacao, uso correto: python3 montador.py <entrada.asm> <saida.txt>")
    sys.exit(1)

arquivo_entrada = sys.argv[1]
arquivo_saida = sys.argv[2]

with open(arquivo_entrada, 'r') as f:
    content = f.readlines()

content = [item.split(';')[0] for item in content] #tira comentarios
content = [x.strip().upper().split(' ') for x in content] #separa e tira espacos para modelo ['add', 'ra,rb']

#formata toda a lista para ficar cada argumento como um elemento--------
content1 = []

for sublista in content:
    # remove itens vazios
    nova_sublista = [item for item in sublista if  item != '']
    if nova_sublista:  # só adiciona se não ficar vazia
        # divide elementos com vírgula
        sublista_expandida = []
        for item in nova_sublista:
            sublista_expandida.extend(item.split(','))
        content1.append(sublista_expandida)

content1 = [[item for item in sublista if item != ''] for sublista in content1] #apenas para corrigir r1,,r2


 


#dicionarios de instrucoes e registradores
instructor = {'ADD': '8', 'SHR': '9','SHL': 'a', 'NOT': 'b', 'AND':'c', 'OR': 'd', 'XOR': 'e', 'CMP': 'f',
'LD':'0', 'ST':'1', 'DATA':'2', 'JMPR':'3', 'JMP':'4', 'CLF':'6','IN':'7', 'OUT':'7'}

regs = {'R0': '00', 'R1': '01', 'R2': '10', 'R3': '11'}

#para checar comandos de 2 bytes
instrucoes = ['DATA', 'JMP']

#RAM
memory = [['0','0'] for _ in range(TAMRAM)]

#jcaez
caez = {'C': 8, 'A': 4, 'E': 2, 'Z': 1}

#logica: para cada comando de 2 bytes adicionar um deslocamento para que possa preencher o primeiro numero corretamente


desloc = 0
#global para todas as intrucoes-------------
for i in range(len(content1)):
    try:
        if content1[i][0][0] == 'J' and content1[i][0][:2] != 'JM' : #intrucoes normais
            memory[i+desloc][0] = '5'
            desloc += 1
            
        else: #jcaez
            memory[i+desloc][0] = instructor[content1[i][0]]
            if content1[i][0] in instrucoes:
                desloc += 1
    except:
        print('erro: instrucao invalida', content1[i][0])
        quit()


#checar segundo numero--------------------------------------------------------
desloc = 0

for i in range(len(content1)):

    k = i + desloc

    instAtual = content1[i][0]
    if instAtual == 'DATA':
        desloc += 1
        memory[k][1] = hex(int('00' + regs[content1[i][1]],2))[2:] 
        #checar formato do valor
        if len(content1[i][2]) > 2 and content1[i][2][1] == 'X': #hexa
            memory[k+1][0] = content1[i][2][2] #colocar o valor do data 
            memory[k+1][1] = content1[i][2][3]


        

        elif len(content1[i][2]) > 2 and content1[i][2][1] == 'B': #binario
            content1[i][1] = content1[i][2][2:] #retirar 0b
            num = int(content1[i][1],2)

            if num < 16 : #menor que 0xf -> so tem 1 digito
                memory[k+1][0] = '0'
                memory[k+1][1] = str(hex(num))[2]

            else: #maior que 0xf -> 2 digitos pode manipular normalmente
                memory[k+1][0] = str(hex(num))[2]
                memory[k+1][1] = str(hex(num))[3]

        else: #decimal
            num = int(content1[i][2])
            if num > 127 or num < -128:
                print('erro: numero fora do escopo', num)
                quit()

            num = int(np.binary_repr(num, width=8),2) # complemento de 2

            if num < 16 : #menor que 0xf -> so tem 1 digito
                memory[k+1][0] = '0'
                memory[k+1][1] = str(hex(num))[2]

            else: #maior que 0xf -> 2 digitos pode manipular normalmente
                memory[k+1][0] = str(hex(num))[2]
                memory[k+1][1] = str(hex(num))[3]


    elif instAtual == 'JMPR': #para jmpr
        memory[k][1] = hex(int('00' + regs[content1[i][1]],2))[2:] 


    elif instAtual == 'JMP': #para jmp
        desloc += 1
        memory[k+1][0] = content1[i][1][2] #colocar o endereco do jmp 
        memory[k+1][1] = content1[i][1][3]


    elif instAtual == 'CLF': #para CLF
       memory[k][1] = '0' 


    elif instAtual == 'IN' or instAtual == 'OUT': #para i/o
        opcode = ['0','0']
        if instAtual == 'OUT':
            opcode[0] = '1'

        instAtual = content1[i][1]
        if instAtual == 'ADDR':
            opcode[1] = '1'

        opcode = ''.join(opcode) 
        memory[k][1] = hex(int(opcode + regs[content1[i][2]],2))[2:]


    elif instAtual[0] == 'J': #para jcaez
        desloc += 1
        acc = 0
        for j in range(1, len(instAtual)):
            acc += caez[instAtual[j]]
        memory[k][1] = str(hex(acc)[2:])

        #checar formato do valor do addr
        if  content1[i][1][1] == 'X': #hexa
            memory[k+1][0] = content1[i][1][2] #colocar o valor do addr
            memory[k+1][1] = content1[i][1][3]

        elif len(content1[i][1]) > 2 and content1[i][1][1] == 'B': #binario
            content1[i][1] = content1[i][1][2:] #retirar 0b
            num = int(content1[i][1],2)

            if num < 16 : #menor que 0xf -> so tem 1 digito
                memory[k+1][0] = '0'
                memory[k+1][1] = str(hex(num))[2]

            else: #maior que 0xf -> 2 digitos pode manipular normalmente
                print(str(hex(num))[2])
                memory[k+1][0] = str(hex(num))[2]
                memory[k+1][1] = str(hex(num))[3]
        else:
            num = int(content1[i][1])
            if num > 255 or num < 0:
                print('erro: numero fora do escopo', num)
                quit()
            print(str(hex(num)))
            if num < 16 : #menor que 0xf -> so tem 1 digito
                memory[k+1][0] = '0'
                memory[k+1][1] = str(hex(num))[2]

            else: #maior que 0xf -> 2 digitos pode manipular normalmente
                memory[k+1][0] = str(hex(num))[2]
                memory[k+1][1] = str(hex(num))[3]


    else:
        memory[k][1] = hex(int(regs[content1[i][1]] + regs[content1[i][2]],2))[2:] #para instrucoes modelo ra,rb
#---------------------------------------------------------------------------------------------------



#escrever a memoria no arquivo    
with open(arquivo_saida, 'w') as f:
    f.write('v3.0 hex words plain\n')
    for i in range(TAMRAM):
        f.write(memory[i][0].lower())
        f.write(memory[i][1].lower())
        f.write('\n')

print("compilado com sucesso")
