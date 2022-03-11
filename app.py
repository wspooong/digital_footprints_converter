# https://krvtz.net/posts/how-facebook-got-unicode-wrong.html

import json
import io
from pathlib import Path
import pandas as pd

class FacebookIO(io.FileIO):
    def read(self, size: int = -1) -> bytes:
        data: bytes = super(FacebookIO, self).readall()
        new_data: bytes = b''
        i: int = 0
        while i < len(data):
            # \u00c4\u0085
            # 0123456789ab
            if data[i:].startswith(b'\\u00'):
                u: int = 0
                new_char: bytes = b''
                while data[i+u:].startswith(b'\\u00'):
                    hex = int(bytes([data[i+u+4], data[i+u+5]]), 16)
                    new_char = b''.join([new_char, bytes([hex])])
                    u += 6

                char : str = new_char.decode('utf-8')
                new_chars: bytes = bytes(json.dumps(char).strip('"'), 'ascii')
                new_data += new_chars
                i += u
            else:
                new_data = b''.join([new_data, bytes([data[i]])])
                i += 1

        return new_data

def main():
    output_path = Path("output\\")
    rawdata_path = Path("rawdata\\")
    json_file_count = sum(1 for x in rawdata_path.rglob("*.json"))
    n = 1
    for p in rawdata_path.rglob("*.json"):
        print(f'''Processing: {n}/{json_file_count}, {'/'.join(p.parts[-2:])}''')
        n += 1
        if p.name == 'BrowserHistory.json':
            output_file_path = output_path.joinpath(*p.parts[1:]).with_suffix('.xlsx')
            output_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(p, 'r', encoding='UTF-8') as f:
                data = json.load(f)
            data = pd.json_normalize(data, 'Browser History')
            data.to_excel(output_file_path, index=False)
            continue
        if p.name == 'search-history.json':
            output_file_path = output_path.joinpath(*p.parts[1:]).with_suffix('.xlsx')
            output_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(p, 'r', encoding='UTF-8') as f:
                data = json.load(f)
            data = pd.json_normalize(data)
            data.to_excel(output_file_path, index=False)
            continue
        if p.name == 'watch-history.json':
            output_file_path = output_path.joinpath(*p.parts[1:]).with_suffix('.xlsx')
            output_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(p, 'r', encoding='UTF-8') as f:
                data = json.load(f)
            data = pd.json_normalize(data)
            data.to_excel(output_file_path, index=False)
            continue
        
        output_file_path = output_path.joinpath(*p.parts[1:])
        decoded_json = json.load(FacebookIO(p,'rb'))
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file_path, 'w', encoding='UTF-8') as f:
            json.dump(decoded_json, f, ensure_ascii=False, indent=4)

def check_folder_exists():
    if not Path("rawdata\\").is_dir():
        print(f'[ERROR] "rawdata" folder not exists, creating...')
        Path("rawdata\\").mkdir()
        print(f'[ERROR] Please put your digital footprints data in "rawdata" folder.')
        input(f'[ERROR] Press Enter to exit.')
        return False
    return True

if __name__ == '__main__':
    print(f'Digital Footprints Data Convert Tool.')
    print(f'Version: 0.1')
    print(f'----------------------------------------------')
    print(f'Supported Site: Facebook, Google Takeout')
    print(f'Facebook: fix encoding. Thanks to: https://krvtz.net/posts/how-facebook-got-unicode-wrong.html')
    print(f'Google: Convert JSON to EXCEL.')
    print(f'----------------------------------------------')
    print(f'Release Date: 2022/03/03')
    print(f'Author Site: wspooong.com')
    print(f'----------------------------------------------')
    input("Press Enter to continue or press Ctrl+C to exit.")
    if check_folder_exists():
        main()
        input("Done! Press Enter to exit.")

    
    
