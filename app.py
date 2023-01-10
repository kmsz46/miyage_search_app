import streamlit as st
import glob
import pandas as pd
import json
import os
import logging

logger = logging.Logger("miyageapp")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    fmt='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
))
logger.addHandler(handler)

# あらかじめ必要なデータを読み込んでおく
@st.cache
def cached_data():
    # データの読み込み
    tdfk = pd.read_csv("tdfk.csv",encoding="utf-8")["tdfk"].values.tolist()
    review_data_file_path = []
    shop_file_path = []
    for t in tdfk:
        shop_file_path.append(glob.glob(os.path.join("data",t, "*", "shop_data.csv")))

    # 店舗のディレクトリ名を取得する
    dir_path = []
    for rdf in shop_file_path:
        dir_path.append([x.split("shop_data")[0] for x in rdf])

    # jsonデータの取得
    review_file_path = []
    for dp in dir_path:
        review_file_path.append([os.path.join(x, "miyage_review_relation.json") for x in dp])

    return tdfk,shop_file_path,review_file_path


def main():
    # 参考にしたサイトのURL：https://blog.amedama.jp/entry/streamlit-tutorial
    # 初めにデータを読み込んでおく
    tdfk, shop_file_path, review_file_path = cached_data()
    tdfk_dict = dict()
    for i in range(len(tdfk)):
        tdfk_dict[tdfk[i]] = i
    # タイトル
    st.title("お土産提示システム（仮）")
    # 入力フォーム
    select_tdfk = st.selectbox('都道府県を選択してください',tdfk)
    key = st.text_input(label="どのような味のお土産がほしいですか？")
    try:
        shop_df,miyage_df,review_df = sizzle_search(shop_file_path,review_file_path,key,tdfk_dict[select_tdfk])
        st.write(str(len(shop_df))+"件表示")
        # 結果を表示する
        for shop_name, shop_link, shop_place, miyage_name, review in zip(shop_df["shop_name"].to_list(),shop_df["link"].to_list(),shop_df["detail_place"].to_list(),miyage_df,review_df):
            st.subheader("店舗名："+str(shop_name))
            st.write("場所："+shop_place)
            for mn, r in zip(miyage_name,review):
                st.write("商品名:"+mn)
                st.caption("レビュー:"+r)

    except Exception as e:
        logger.error(e)
        st.write("該当するお土産が見つかりませんでした")

# シズルワードで検索するための関する
def sizzle_search(shop_file_path,review_file_path,key,select_tdfk):
    sfps = shop_file_path[select_tdfk]
    shop_tmp = []
    # 商品とレビューのデータを取得する
    miyage_df = []
    review_df = []
    rfps = review_file_path[select_tdfk]
    for id_,rfp in enumerate(rfps):
        with open(rfp) as f:
            review_data = json.load(f)
            tmp_miyage = []
            tmp_review = []
            flag = 0
            for miyage,review in zip(review_data.keys(),review_data.values()):
                for r in review:
                    if key in  r:
                        tmp_miyage.append(miyage)
                        tmp_review.append(r)
                        flag = 1
            if flag == 1:
                miyage_df.append(tmp_miyage)
                review_df.append(tmp_review)
                shop_tmp.append(pd.read_csv(sfps[id_]))
    shop_df = pd.concat(shop_tmp)

    return shop_df,miyage_df,review_df


if __name__ == "__main__":
    main()
