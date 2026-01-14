# EVE-NG on AWS

### Setup
Set up env (and virtual network interface if necessary).
```
. ./setup.sh
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