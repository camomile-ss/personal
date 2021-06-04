# coding: utf-8
''' 共通 osより '''
import os
import sys
import zipfile

def zip_and_delete(filename):
    ''' ファイルzip  ・同じ場所にzip
                     ・ファイル名は拡張子だけzipに
                     ・元ファイルは消す
        e.g.) ./path/aaaa.ext -> ./path/aaaa.zip
    '''
    p, _ = os.path.splitext(filename)
    del_zipfn = p + '.zip'
    with zipfile.ZipFile(del_zipfn, 'w', compression=zipfile.ZIP_DEFLATED) as dzipf:
        dzipf.write(filename, arcname=os.path.basename(filename))
    os.remove(filename)

def ext1zipfile(fname, outdir=None):
    ''' 1zipファイル解凍
        outdir省略->同じ場所に解凍
    '''

    indir, basename = os.path.split(fname)

    if not outdir:
        outdir = indir

    with zipfile.ZipFile(fname) as zipf:
        zipf.extractall(outdir)

def ext1dir(indir, outdir=None):
    ''' dir内の複数zipファイルを解凍
        outdir省略->同じ場所に解凍
    '''

    zipfns = [x for x in os.listdir(indir) if x[-4:]=='.zip']
    for zipfn in zipfns:
        ext1zipfile(os.path.join(indir, zipfn), outdir)

def rmdir_recursively_noconfirm(dirn):
    ''' ディレクトリを中身ごと削除  ### 確認なし ###
            shutil.rmtree がうまくいかない（親ディレクトリだけ残り Text File busy になる）のでその代わり
            #### これでやっても同じ。エラーになったりならなかったりする。
            #### コマンド rm -r でやっても「テキストファイルがビジー状態」になることがある
            #### 仮想で共有ディレだと起きるみたい
            #### rm -r は何度かやるとOKのようなので、os.rmdir を10回までやってみる
    '''
    for x in os.listdir(dirn):
        x_ = os.path.join(dirn, x)
        if os.path.isfile(x_):  # ファイルは消す
            os.remove(x_)
        elif os.path.isdir(x_):  # ディレは
            rmdir_recursively(x_)  # 再帰
    # os.rmdir はエラーになったりならなかったりするので10回までやってみる
    ok, cnt = False, 0
    while not ok and cnt < 10:
        cnt += 1
        try:
            os.rmdir(dirn)
            ok = True
        except:
            continue
    if ok:
        print('rmdir ok. dir: {0}, count: {1}'.format(dirn, cnt))
    else:
        print('rmdir error. dir: {}'.format(dirn))
        sys.exit()

def rmdir_recursively(dirn):
    ''' ディレクトリを中身ごと削除
            shutil.rmtree がうまくいかない（親ディレクトリだけ残り Text File busy になる）のでその代わり
            #### これでやっても同じ。エラーになったりならなかったりする。
            #### コマンド rm -r でやっても「テキストファイルがビジー状態」になることがある
            #### 仮想で共有ディレだと起きるみたい
            #### rm -r は何度かやるとOKのようなので、os.rmdir を10回までやってみる
        return OK or else
    '''
    ans = input('### remove directory: {}, ### OK? ### >>'.format(dirn))
    if ans == 'OK':
        rmdir_recursively_noconfirm(dirn)
        print('[{}] removed.'.format(dirn))
    else:
        print('[{}] not removed.'.format(dirn))
    return ans

if __name__ == '__main__':

    rmdir_recursively(sys.argv[1])
