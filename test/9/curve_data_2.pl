#!/bin/perl
# curve_data_2.txt 作成スクリプト

use strict;

sub mkhash {
    # railstation.txt から、路線コード辞書・駅コード辞書をつくる

    my $rsf = $_[0];  # railstation.txt
    my (%rt_hash, %st_hash, %no_hash);  # 路線コード辞書, 駅コード辞書, 駅番号辞書

    open FHr, "<$rsf" or die "$!";
    while (<FHr>){
	s/\r//;
	s/\n//;
	#chomp;
	my @strlist = split(/\t/);
	my $route = $strlist[1];  # 路線名

	# 路線名そのままで辞書に登録
	$rt_hash{$route} = substr($strlist[0], 0, 6);  # 路線コード あたま6ケタ
	$st_hash{$route}{$strlist[7]} = $strlist[5];  # 路線名=>駅名=>駅コード
	$no_hash{$route}{$strlist[7]} = $strlist[4];  # 路線名=>駅名=>駅コード

	# 路線名短縮対象なら短縮したものも登録（・から_の手前まで削除）[JRE]中央線・快速_0 -> [JRE]中央線_0
	if ($strlist[1] =~ /^(.+)・.+(_[01])$/){
	    $route = $1.$2;
	    $rt_hash{$route} = substr($strlist[0], 0, 6);  # 路線コード あたま6ケタ
	    $st_hash{$route}{$strlist[7]} = $strlist[5];  # 路線名=>駅名=>駅コード
	    $no_hash{$route}{$strlist[7]} = $strlist[4];  # 路線名=>駅名=>駅コード
	}
    }
    close FHr;

    return (\%rt_hash, \%st_hash, \%no_hash);
}

sub mkcurvedata2 {
    # 1行ずつ curve_data.txt 読んで curve_data_2.txt 書く

    my ($cuf, $outf, $rt_hash, $st_hash, $no_hash) = @_;
    open FHc, "<$cuf" or die "$!";
    open FHo, ">$outf" or die "$!";
    my $cnt = 0;
    my ($prev_rt, $rt_cd);
    while (<FHc>){
	s/\r//;
	s/\n//;
	#chomp;
	my ($lat, $long, $sta, $rt) = split(/\t/);
	if ($rt ne $prev_rt){
	    if (not exists($rt_hash->{$rt})){
		print "[route] $rt not in railstation.txt.\n";
	    }
	    $rt_cd = $rt_hash->{$rt};
	    $cnt = 0;
	    $prev_rt = $rt;
	}

	# 路線コード、路線名、連番
	my @outlist = ($rt_cd, $rt, $cnt);

	# 駅連番、駅コード、駅名
	if ($sta eq '-'){  # 中間点
	    push @outlist, ('-', '-', '-');
	}else{  # 駅
	    if (not exists($st_hash->{$rt}->{$sta})){
		print "[station] $rt $sta not in railstation.txt.\n";
	    }
	    push @outlist, ($no_hash->{$rt}->{$sta}, $st_hash->{$rt}->{$sta}, $sta);
	}
	
	# 緯度・経度
	push @outlist, ($lat, $long);

	# 書出し
	my $outline = join("\t", @outlist)."\n";
	print FHo $outline;

	$cnt ++;
    }
    close FHc;
    close FHo;
}

my $rsf = $ARGV[0];  # 入力 railstation.txt
my $cuf = $ARGV[1];  # 入力 curve_data.txt
my $outf = $ARGV[2];  # 出力 curve_data_2.txt

# railstation.txt から、路線コード辞書, 駅コード辞書, 駅番号辞書 作成
my ($rt_hash, $st_hash, $no_hash) = &mkhash($rsf);

# curve_data.txt から、curve_data_2.txt 作成
&mkcurvedata2($cuf, $outf, $rt_hash, $st_hash, $no_hash)
