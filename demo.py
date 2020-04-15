"""
See the demo notebook for details / explanations.
"""

import qiskit, random, time

numBits= 10
numCompare= 4


def getRandomBases(numBits):
    b= []
    for i in range(numBits):
        if random.random() > 0.5: b.append("x")
        else: b.append("+")
    return b


simulator= qiskit.Aer.get_backend('qasm_simulator')
def sim(circ):
    job= qiskit.execute(circ, simulator, shots=1)

    result= job.result().get_counts(circ)

    key= list(result.keys())[0]
    key= "".join(list(reversed(key)))

    return key

def applyBases(circ, bases):
    circ.barrier()
    for i,bse in enumerate(bases):
        if bse=="x": circ.h(i)
    return circ

def genA():
    basesA= getRandomBases(numBits)
    circA= qiskit.QuantumCircuit(numBits, numBits*2)

    keyA= random.randint(0, 2**numBits)
    keyA= str(bin(keyA))[2:].zfill(numBits)

    for i,bit in enumerate(keyA):
        if bit=="1": circA.x(i)
    circA= applyBases(circA, basesA)

    return circA, basesA, keyA


def genB():
    basesB= getRandomBases(numBits)
    circB= qiskit.QuantumCircuit(numBits, numBits*2)
    circB= applyBases(circB, basesB)

    circB.barrier()
    circB.measure(range(numBits), range(numBits))

    return circB, basesB

def genE():
    basesE= getRandomBases(numBits)
    circE= qiskit.QuantumCircuit(numBits, numBits*2)
    circE= applyBases(circE, basesE)

    circE.barrier()
    circE.measure(range(numBits), range(numBits, numBits*2))

    circE.barrier()
    circE= applyBases(circE, basesE)

    return circE, basesE


# Return (is_acceptable_trial, is_detected)
def calc():
    circA, basesA, keyA= genA()
    circB, basesB= genB()
    circE, basesE= genE()

    k= sim(circA + circE + circB)
    keyB= k[:numBits]
    keyE= k[numBits:]

    matches= [i for i in range(len(basesA)) if basesA[i] == basesB[i]]
    siftA= [keyA[i] for i in matches]
    siftB= [keyB[i] for i in matches]

    if len(siftA) < numCompare: return 0,0 # disregard trial -- not enough sifted key bits
    elif siftA[:numCompare] != siftB[:numCompare]: return 1,1  # Eve detected
    else: return 1,0 # failed detection


counts= 0
total= 0
shots= 200

start= time.time()
for i in range(shots):
    accept,detect = calc()
    total+= accept
    counts+= detect
runtime= time.time() - start

print(f"Simulating {shots} trials with {numBits} qubits and {numCompare} key-sharing bits.")

print()
print("Expected detection rate:\t",f"{int((1 - 0.75**numCompare)*100)}%")
print(f"Simulated detection rate:\t", f"{int((counts / total)*100)}%")

print()
print("Runtime:", str(round(runtime,2)) + "s with",total,"accepted trials.")