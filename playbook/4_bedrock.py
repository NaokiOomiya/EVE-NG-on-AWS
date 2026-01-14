import boto3
import json
import subprocess

# --- 設定情報 ---
# ルータのIPアドレスリスト

username = "cisco"
ssh_options = "-o KexAlgorithms=+diffie-hellman-group-exchange-sha1 -o HostKeyAlgorithms=+ssh-rsa"

def run_ssh_command(ip, command):
    """
    OSのsshコマンドを呼び出して実行結果を返す
    ※パスワード入力を省くため、公開鍵認証を設定済みであること
    """
    ssh_cmd = f"ssh {ssh_options} {username}@{ip} '{command}'"
    try:
        result = subprocess.check_output(ssh_cmd, shell=True, stderr=subprocess.STDOUT)
        return result.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output.decode('utf-8')}"

# 1. ログの収集
all_logs = ""
router_ips = ["192.168.10.252", "192.168.10.253"] # R_Agg, R_Agg_1
for i, ip in enumerate(router_ips):
    conf = run_ssh_command(ip, f"show run interface e0/{i+1}")
    state = run_ssh_command(ip, f"show standby brief")
    all_logs += f"\n--- Device: {ip} ---\n---show run interface:\n{conf}\n---show standby:\n{state}"
print(f"[DEBUG START]\n{all_logs}\n[DEBUG END]\n")

# 2. AWS Bedrockへのリクエスト（前述のコードと同様）
# logs には先ほど取得したテキストが代入されている想定
prompt = f"""
あなたはシニアネットワークエンジニアです。
以下のCiscoルータのログを分析し、HSRP(VIP: 192.168.10.254)が正しく冗長化（Preempt含む）動作をしない原因を特定してください。

{all_logs}

修正が必要なデバイスのIPアドレスをキーとしたオブジェクト（fixes）に、実行すべきコマンドのリストを格納してください。修正が不要なデバイスは含めないでください。
{{
  "analysis": "原因の簡潔な説明",
  "fixes": {{
    "192.168.10.253": ["修正コマンド1-1", "修正コマンド1-2"],
    "192.168.10.252": ["修正コマンド2-1", "修正コマンド2-2"]
  }}
}}

※注意: 
- 修正コマンドは 'conf t' で始まり 'end' で終わる形式にしてください。
- 修正が必要なインターフェース(Ethernet0/2)を必ず指定してください。
"""

# Bedrockクライアントの初期化
bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

def ask_bedrock(prompt):
    model_id = "anthropic.claude-3-haiku-20240307-v1:0" # Claude 3 Haiku
    # Price per 1,000 input tokens: $0.00025
    # Price per 1,000 output tokens: $0.00125
    # ref. https://aws.amazon.com/bedrock/pricing/
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": prompt}]
    })
    try:
        response = bedrock.invoke_model(modelId=model_id, body=body)
        response_body = json.loads(response.get('body').read())
        return json.loads(response_body['content'][0]['text'])
    except Exception as e:
        print(f"Error: {e}")
        return None

# 実行
result = ask_bedrock(prompt)
print(result)

def apply_fix_commands(ip, fix_commands):
    """
    AIが生成したコマンドリストをルータに投入する
    """
    # Ciscoルータで設定変更をするために 'conf t' から始まり 'end' で終わる文字列を作成
    # AIが既に含めている場合は調整が必要ですが、基本は改行で繋ぐだけです
    commands_str = "\n".join(fix_commands)
    ssh_cmd = f"ssh {ssh_options} {username}@{ip}"
    
    try:
        print(f"--- [{ip}] に設定を投入中... ---")
        subprocess.run(
            ssh_cmd, 
            shell=True, 
            input=commands_str.encode('utf-8'),
            check=True
        )
        print(f"--- [{ip}] 設定完了 ---")
    except subprocess.CalledProcessError as e:
        print(f"コマンド投入失敗: {e}")

if 'fixes' in result:
    print("\n" + "="*50)
    print("AIによる修正案が生成されました。内容を確認してください。")
    print("="*50)

    print(f"【AIの分析】\n{result['analysis']}")
    print(f"【修正案】\n{result['fixes']}")
    print("\n" + "="*50)
    
    # ユーザーに入力を求める
    confirmation = input("上記の設定変更を実行しますか？ (yes/no): ").strip().lower()
    
    if confirmation == 'yes':
        print("\n承認されました。実行を開始します...")
        for target_ip, commands in result['fixes'].items():
            apply_fix_commands(target_ip, commands)
        print("\nすべての修正が完了しました。")
    else:
        print("\n実行をキャンセルしました。設定は変更されていません。")