import os


cwd = os.getcwd()
cases = os.listdir('./test_cases')

for each_case in cases:
    print(f'Running test: {each_case}')
    cur_path = f'{cwd}/test_cases/{each_case}'
    os.system(f'python3 NYU_RV32I_6913.py --iodir={cur_path}')
