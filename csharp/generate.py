import json
import subprocess
import os
import sys
from os.path import join as pjoin
from distutils.dir_util import copy_tree, remove_tree


contracts = ["DUBI"]
namespace = "EthContracts"

# folder config
BIN_ROOT = "bin"
CONTRACTS_ROOT = pjoin("..", "build", "contracts")
GEN_OUTPUT = pjoin(".", "Generated")
gen_dll = pjoin(".", "Nethereum.Generator", "Nethereum.Generator.Console.dll")

for contract in contracts:
    # read contract json
    with open(pjoin(CONTRACTS_ROOT, f"{contract}.json")) as contract_file:
        contract_json = json.load(contract_file)
        abi = contract_json["abi"]
        bytecode = contract_json["bytecode"].lstrip("0x").rstrip("\n")

    # write .abi, .bin files
    os.makedirs(pjoin(BIN_ROOT, contract), exist_ok=True)
    abi_filename = pjoin(BIN_ROOT, contract, f"{contract}.abi")
    bin_filename = pjoin(BIN_ROOT, contract, f"{contract}.bin")

    with open(abi_filename, "w") as abi_file:
        json.dump(abi, abi_file)
    with open(bin_filename, "wb") as bin_file:
        bin_file.write(bytes(bytecode, "UTF-8"))

    # generate .cs files
    os.makedirs(GEN_OUTPUT, exist_ok=True)
    subprocess.call(
        f'dotnet {gen_dll} gen-fromabi -abi "{abi_filename}" -bin "{bin_filename}" -cn {contract} -ns {namespace} -o {GEN_OUTPUT}'
    )


# DUBIService.cs specific patches
def patch_DUBIService(code):
    code = "using Nethereum.Contracts.ContractHandlers;\n" + code
    return code


dubi_service = pjoin(GEN_OUTPUT, "DUBI", "Service", "DUBIService.cs")
with open(dubi_service, "r") as original:
    code = original.read()
with open(dubi_service, "w") as modified:
    modified.write(patch_DUBIService(code))


# copy to output folder, if provided
if len(sys.argv) == 2:
    output_folder = sys.argv[1]
    if os.path.exists(output_folder):
        copy_tree(GEN_OUTPUT, output_folder)
    else:
        print(f"output folder '{output_folder}' doesnt exist, not copying")
else:
    print(
        '(optional) provide path to copy output to. example: \'python generate.py "D:/UnityProject/Assets/Plugins"'
    )
