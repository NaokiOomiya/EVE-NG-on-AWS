# EVE-NG on AWS
EVE-NG on AWS環境を再現するためのリポジトリ。オンプレ上での構築も可能（なはず）。

### 前提条件
- Ubuntu 20.04
- Python 3.8.10

### Setup
1. 環境構築用パッケージを[SharePoint(アクセス制限あり)](https://nttdocomo.sharepoint.com/:u:/s/packetcore-dev/IQABKzPX0rEISZaSC5Fo1rrLAd_FOD5cgRTCwiw7KYuj9Uc?e=AxteQC)からダウンロードする。

2. 下記コマンドで本リポジトリをダウンロードする。
```
git clone https://github.com/NaokiOomiya/EVE-NG-on-AWS.git
cd EVE-NG-on-AWS
```

3. 下記コマンドで必要なパッケージをインストールする。
```
. ./setup.sh
```

4. （必要に応じて実施）実行環境とEVE-NGノードを接続したい場合、実行環境に仮想ネットワークインターフェースを設定する。
```
sudo ip addr add 192.168.10.10/24 dev pnet0
sudo ip route add 192.168.0.0/16 via 192.168.10.254
```

5. インストールした環境のIPアドレス宛にウェブブラウザからログインし、EVE-NGにログインする。
```
【デフォルト情報】
- ID: admin
- Pass: eve
```

### Files
- ansible.cfg: Playbook共通設定
- inventory.yml: Playbook共通変数
- migration_packages.tar.gz: 環境構築用パッケージ類
- setup.sh: 環境構築用シェルスクリプト
- playbook: Ansible playbook、pythonファイルとそのログ類

#### Playbook
- 0_BD: Build
    - 0_BD_BGRTs_topology.yml: 擬似BG-RT群生成トポロジーファイル
- 1_PC: Prior Confirmation
    - 1_PC_check_ssh.yml: ssh接続確認用
- 2_UT: Unit Test
    - 2_UT_collect_info.yml: 設定取得&ファイル化
- 3_IT: Integration Test
    - 3_IT_hsrp.yml: 特定IF閉塞によるHSRP切り替え確認
- 4
    - 4_bedrock.py: Bedrock連携による自動config修正
