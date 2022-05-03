import base64


with open('outfile.dump', 'r') as f:
    lines = f.readlines()

for index, line in enumerate(lines):
    stripped = line.strip('\n')
    try:
        data = base64.b64decode(stripped)
        with open(f'./data_out_{index}.xlsx', 'wb') as f:
            f.write(data)
    except Exception as e:
        print(f"Failed on index {index}, {e}")
        print(line)
        pass



