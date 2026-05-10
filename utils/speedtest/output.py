import json
import base64
import os
import time

meta_json = './meta.json'

sub_all_base64 = "./sub/sub_merge_base64.txt"
sub_all = "./sub/sub_merge.txt"
Eternity_file_base64 = "./Eternity"
Eternity_file = "./Eternity.txt"
Eternity_Base = "./EternityBase"

splitted_output = "./sub/splitted/"


def read_meta(file):
    while os.path.isfile(file) == False:
        print('Awaiting speedtest complete')
        time.sleep(30)
    with open(file, 'r', encoding='utf-8') as f:
        print('Reading meta.json')
        data = json.load(f)
        f.close()
    return data


def config_to_link(config_str):
    try:
        config = json.loads(config_str)
    except:
        return None

    protocol = config.get('type', '')
    tag = config.get('tag', '').split(' ')[0] if ' ' in config.get('tag', '') else config.get('tag', '')
    server = config.get('server', '')
    port = config.get('server_port', 0)

    if protocol == 'vmess':
        uuid = config.get('uuid', '')
        security = config.get('security', 'auto')
        transport = config.get('transport', {})
        network = transport.get('type', 'tcp') if isinstance(transport, dict) else 'tcp'

        path = ''
        host = ''
        if network == 'ws' and isinstance(transport, dict):
            path = transport.get('path', '')
            headers = transport.get('headers', {})
            host = headers.get('Host', '') if isinstance(headers, dict) else ''

        tls = config.get('tls', {})
        tls_enabled = tls.get('enabled', False) if isinstance(tls, dict) else False

        vmess_config = {
            "v": "2",
            "ps": tag,
            "add": server,
            "port": port,
            "id": uuid,
            "aid": 0,
            "net": network,
            "type": "none",
            "host": host,
            "path": path,
            "tls": 'tls' if tls_enabled else ''
        }
        link = "vmess://" + base64.b64encode(json.dumps(vmess_config, ensure_ascii=False).encode('utf-8')).decode('ascii')
        return link

    elif protocol == 'trojan':
        password = config.get('password', '')
        tls = config.get('tls', {})
        sni = ''
        if isinstance(tls, dict):
            sni = tls.get('serverName', '')
        return f"trojan://{password}@{server}:{port}?sni={sni}#{tag}"

    elif protocol == 'shadowsocks':
        method = config.get('method', 'aes-256-gcm')
        password = config.get('password', '')
        return f"ss://{base64.b64encode(f'{method}:{password}'.encode()).decode()}@{server}:{port}#{tag}"

    elif protocol == 'shadowsocksr':
        return None

    return None


def output(data, num):
    nodes = []
    for idx, item in enumerate(data):
        config_str = item.get('config', '')
        link = config_to_link(config_str)
        if link:
            ping = item.get('ping', 0)
            speed = item.get('speed', 0)
            avg_speed = item.get('avg_speed', speed)
            max_speed = item.get('max_speed', speed)
            nodes.append({
                'id': idx,
                'link': link,
                'ping': ping,
                'speed': speed,
                'avg_speed': avg_speed,
                'max_speed': max_speed,
                'remarks': item.get('tag', '').split(' ')[0] if ' ' in item.get('tag', '') else item.get('tag', ''),
                'protocol': item.get('type', '')
            })

    nodes = sorted(nodes, key=lambda x: (x['avg_speed'], x['ping']), reverse=True)

    print(f"Total nodes: {len(nodes)}")

    speed_only_nodes = [n for n in nodes if n['speed'] > 0 and n['ping'] == 0]
    ping_only_nodes = [n for n in nodes if n['ping'] > 0 and n['speed'] == 0]
    both_nodes = [n for n in nodes if n['speed'] > 0 and n['ping'] > 0]
    neither_nodes = [n for n in nodes if n['speed'] == 0 and n['ping'] == 0]

    print(f"  - speed > 0 only (no ping): {len(speed_only_nodes)}")
    print(f"  - ping > 0 only (no speed): {len(ping_only_nodes)}")
    print(f"  - both speed > 0 and ping > 0: {len(both_nodes)}")
    print(f"  - neither speed nor ping: {len(neither_nodes)}")

    working_nodes = [n for n in nodes if n['speed'] > 0 and n['ping'] > 0]
    print(f"Working nodes (speed > 0 AND ping > 0): {len(working_nodes)}")
    if working_nodes:
        print(f"Fastest: {working_nodes[0]['remarks']} - {working_nodes[0]['avg_speed']} KB/s")
        print(f"Slowest: {working_nodes[-1]['remarks']} - {working_nodes[-1]['avg_speed']} KB/s")

    output_list = []
    for item in nodes:
        output_list.append(item['link'])

    def arred(x, n):
        return x * (10 ** n) // 1 / (10 ** n)

    info_list = []
    for item in nodes:
        avg_speed_mb = arred(item['avg_speed'] * 0.00000095367432, 3)
        max_speed_mb = arred(item['max_speed'] * 0.00000095367432, 3)
        info = f"id: {item['id']} | remarks: {item['remarks']} | protocol: {item['protocol']} | ping: {item['ping']} MS | avg_speed: {avg_speed_mb} MB | max_speed: {max_speed_mb} MB | Link: {item['link']}\n"
        info_list.append(info)
    with open('./LogInfo.txt', 'w', encoding='utf-8') as f1:
        f1.writelines(info_list)
        f1.close()
        print('Write Log Success!')

    content = '\n'.join(output_list)
    content_base64 = base64.b64encode('\n'.join(output_list).encode('utf-8')).decode('ascii')
    content_base64_part = base64.b64encode('\n'.join(output_list[0:num]).encode('utf-8')).decode('ascii')

    os.makedirs(splitted_output, exist_ok=True)
    vmess_outputs = []
    trojan_outputs = []
    ssr_outputs = []
    ss_outputs = []
    vless_outputs = []

    for output_item in output_list:
        if str(output_item).startswith("vmess://"):
            vmess_outputs.append(output_item)
        if str(output_item).startswith("trojan://"):
            trojan_outputs.append(output_item)
        if str(output_item).startswith("ssr://"):
            ssr_outputs.append(output_item)
        if str(output_item).startswith("ss://"):
            ss_outputs.append(output_item)
        if str(output_item).startswith("vless://"):
            vless_outputs.append(output_item)

    with open(splitted_output.__add__("vmess.txt"), 'w', encoding='utf-8') as f:
        f.write("\n".join(vmess_outputs))
        print('Write vmess splitted Success!')
        f.close()

    with open(splitted_output.__add__("trojan.txt"), 'w', encoding='utf-8') as f:
        f.write("\n".join(trojan_outputs))
        print('Write trojan splitted Success!')
        f.close()

    with open(splitted_output.__add__("ssr.txt"), 'w', encoding='utf-8') as f:
        f.write("\n".join(ssr_outputs))
        print('Write ssr splitted Success!')
        f.close()

    with open(splitted_output.__add__("ss.txt"), 'w', encoding='utf-8') as f:
        f.write("\n".join(ss_outputs))
        print('Write ss splitted Success!')
        f.close()

    with open(splitted_output.__add__("vless.txt"), 'w', encoding='utf-8') as f:
        f.write("\n".join(vless_outputs))
        print('Write vless splitted Success!')
        f.close()

    with open(sub_all_base64, 'w+', encoding='utf-8') as f:
        f.write(content_base64)
        print('Write All Base64 Success!')
        f.close()
    with open(Eternity_file_base64, 'w+', encoding='utf-8') as f:
        f.write(content_base64_part)
        print('Write Part Base64 Success!')
        f.close()

    with open(sub_all, 'w', encoding='utf-8') as f:
        f.write(content)
        print('Write All Success!')
        f.close()
    with open(Eternity_Base, 'w', encoding='utf-8') as f:
        f.write(content)
        print('Write Base Success!')
        f.close()
    with open(Eternity_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_list[0:num]))
        print('Write Part Base Success!')
        f.close()
    return content


if __name__ == '__main__':
    num = 200
    value = read_meta(meta_json)
    value_len = len(value) if isinstance(value, list) else 0
    output(value, value_len if value_len <= num else num)
