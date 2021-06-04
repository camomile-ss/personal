# coding: utf-8
'''
整備前のファイルと駅構成が同じかどうかチェック
'''
import argparse

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument('infname')
    parser.add_argument('orgfname')
    parser.add_argument('chkfname')

    args = parser.parse_args()

    infname = args.infname
    orgfname = args.orgfname
    chkfname = args.chkfname

    # 読込み
    with open(infname, 'r', encoding='utf-8') as inf:
        in_data = [line.strip().split('\t') for line in inf.readlines()]        
    with open(orgfname, 'r', encoding='utf-8') as orgf:
        org_data = [line.strip().split('\t') for line in orgf.readlines()]        
    
    # 路線リスト
    in_routes = [x[3] for x in in_data]
    in_routes = sorted(set(in_routes), key=lambda x: in_routes.index(x))
    org_routes = [x[3] for x in org_data]
    org_routes = sorted(set(org_routes), key=lambda x: org_routes.index(x))

    # 路線ごとの駅構成（緯度経度は要らない, orgは駅間データ要らない）
    in_data = {route: [x[2] for x in in_data if x[3]==route] for route in in_routes}    
    org_data = {route: [x[2] for x in org_data if x[3]==route and x[2]!='-'] for route in in_routes}

    # 比較
    outdata = []
    with open(chkfname, 'w', encoding='utf-8') as chkf:
        for r in in_routes:
            # 最初・最後が駅間でないか
            if in_data[r][0] == '-' or in_data[r][-1] == '-':
                print(r, ': start or end "-" ')
            # 駅構成がorgと同じか
            in_data[r] = [x for x in in_data[r] if x!='-']
            if in_data[r] != org_data[r]:
                print(r, ' ne original data.')
                chkf.write(r + '\n')
                chkf.write('orginal\t' + '\t'.join(org_data[r]) + '\n')
                chkf.write('modified\t' + '\t'.join(in_data[r]) + '\n')
