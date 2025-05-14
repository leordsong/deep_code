from typing import *
try:
    from xbot.app.logging import trace as print
except:
    from xbot import print


def scrape_clothing_info(browser, target_area):
    """
    title: 抓取衣服产品信息
    description: 在%target_area%中抓取所有衣服的详细信息，包括商品标题、品牌、价格、颜色选项等
    inputs: 
        - browser (WebBrowser): 目标网页
        - target_area (Selector): 商品列表区域，uuid: sm78tzkj
    outputs: 
        - products (list): 包含所有抓取到的产品信息的列表
    """

    # 1. 查找目标区域并确保能正确获取
    print("1. 查找目标区域")
    product_container = browser.find_all_by_xpath(target_area, timeout=3)[0]
    
    # 2. 滚动页面确保所有产品加载完成
    print("2. 滚动页面确保所有产品加载完成")
    product_container.scroll_to(location="bottom")
    browser.wait_load_completed(timeout=5)
    
    # 3. 查找所有产品项
    print("3. 查找所有产品项")
    product_items = product_container.find_all_by_xpath(".//div[contains(@class, 'boost-sd__product-item')]", timeout=3)
    
    products = []
    print(f"   找到 {len(product_items)} 个产品项")
    
    # 4. 遍历每个产品并提取信息
    for i, item in enumerate(product_items):
        print(f"4.{i+1} 正在抓取产品 {i+1}/{len(product_items)}")
        
        product_info = {}
        
        try:
            # 提取产品ID
            product_info['id'] = item.get_attribute('data-product-id')
            
            # 提取产品标题
            title_element = item.find_all_by_xpath(".//div[contains(@class, 'boost-sd__product-title')]", timeout=3)
            if title_element:
                product_info['title'] = title_element[0].get_text()
            else:
                product_info['title'] = "未找到标题"
            
            # 提取品牌/制造商
            vendor_element = item.find_all_by_xpath(".//div[contains(@class, 'boost-sd__product-vendor')]", timeout=3)
            if vendor_element:
                product_info['vendor'] = vendor_element[0].get_text()
            else:
                product_info['vendor'] = "未找到品牌"
            
            # 提取价格
            price_element = item.find_all_by_xpath(".//span[contains(@class, 'boost-sd__format-currency')]//span", timeout=3)
            if price_element:
                product_info['price'] = price_element[0].get_text().strip()
            else:
                product_info['price'] = "未找到价格"
            
            # 提取产品链接
            link_element = item.find_all_by_xpath(".//a[contains(@class, 'boost-sd__product-link')]", timeout=3)
            if link_element and link_element[0].get_attribute('href'):
                product_info['link'] = link_element[0].get_attribute('href')
            else:
                product_info['link'] = "未找到链接"
            
            # 提取颜色选项
            color_options = []
            color_elements = item.find_all_by_xpath(".//label[contains(@class, 'boost-sd__radio-label')]", timeout=3)
            for color_el in color_elements:
                color = color_el.get_text()
                if color:
                    color_options.append(color)
            
            product_info['colors'] = color_options if color_options else []
            
            # 提取产品标签(如NEW)
            badge_element = item.find_all_by_xpath(".//p[contains(@class, 'boost-sd__product-badges')]", timeout=3)
            if badge_element:
                product_info['badge'] = badge_element[0].get_text()
            else:
                product_info['badge'] = ""
            
            # 提取功能特性
            features = []
            feature_elements = item.find_all_by_xpath(".//li[contains(@class, 'c_product-card__detail')]//span", timeout=3)
            for feature_el in feature_elements:
                feature = feature_el.get_text()
                if feature:
                    features.append(feature)
            
            product_info['features'] = features if features else []
            
            # 提取图片URL
            img_elements = item.find_all_by_xpath(".//img[contains(@class, 'boost-sd__product-image-img--main')]", timeout=3)
            if img_elements:
                product_info['image_url'] = img_elements[0].get_attribute('src')
            else:
                product_info['image_url'] = "未找到图片"
            
            products.append(product_info)
            
        except Exception as e:
            print(f"    抓取产品 {i+1} 时出错: {str(e)}")
    
    print(f"5. 总计抓取了 {len(products)} 个产品信息")
    return products

products = [
    {'id': '9605214732590', 'title': 'ミラノリブパールスリーブニット', 'vendor': 'NANO universe', 'price': '¥5,104\n(税込)', 'link': '/products/6734222338', 'colors': ['グレー', 'アイボリー', 'D.ネイビー'], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/WzLuvyguerpktjLawQXlpMKvXlb9rxiLyCszmBomhgu9uwt8eRURmc8tn7-XpYhPOmopAj5D3iL72Henbsg9l45Ibq60L8MAA-fAfCclYg_s1600.jpg?v=1727910579'},
    {'id': None, 'title': '未找到标题', 'vendor': '未找到品牌', 'price': '未找到价格', 'link': '/products/6734222338', 'colors': [], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/WzLuvyguerpktjLawQXlpMKvXlb9rxiLyCszmBomhgu9uwt8eRURmc8tn7-XpYhPOmopAj5D3iL72Henbsg9l45Ibq60L8MAA-fAfCclYg_s1600.jpg?v=1727910579'},
    {'id': '9728379027758', 'title': 'ロゴプリントTシャツ', 'vendor': 'NANO universe', 'price': '¥3,300\n(税込)', 'link': '/products/6735124308', 'colors': ['ブラック', 'チャコール', 'ベージュ', 'グレージュ', 'ブルー'], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/P9Z7R1iKVp0qhk9nTrfFOFGviGYhfGKYtFSoqCxkVkAigibI7d2CwbVp3fHOtKtHCF9Yqt62w5M4-ywvkN6fbWQkYUhHfm8Rx9cElaHnUow_s1600.jpg?v=1739793624'},
    {'id': None, 'title': '未找到标题', 'vendor': '未找到品牌', 'price': '未找到价格', 'link': '/products/6735124308', 'colors': [], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/P9Z7R1iKVp0qhk9nTrfFOFGviGYhfGKYtFSoqCxkVkAigibI7d2CwbVp3fHOtKtHCF9Yqt62w5M4-ywvkN6fbWQkYUhHfm8Rx9cElaHnUow_s1600.jpg?v=1739793624'},
    {'id': '9734612549934', 'title': '洗濯機洗い可UVカット接触冷感半袖ニット', 'vendor': 'NANO universe', 'price': '¥4,840\n(税込)', 'link': '/products/6735122318', 'colors': ['ブラック', 'ホワイト', 'ブルー'], 'badge': '', 'features': ['ウォッシャブル加工', '接触冷感', 'UVカット'], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/nxXPEazdC518Z43WZ6sromsO_yigNfYIHd_tw0CaSAHS0ZiZiNoBaFE2G2KjeL9pgvnqVgkxgwAdJKBJaSEL1ZFE83tZaQe6bcd4mCLung_s1600.jpg?v=1740511821'},
    {'id': None, 'title': '未找到标题', 'vendor': '未找到品牌', 'price': '未找到价格', 'link': '/products/6735122318', 'colors': [], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/nxXPEazdC518Z43WZ6sromsO_yigNfYIHd_tw0CaSAHS0ZiZiNoBaFE2G2KjeL9pgvnqVgkxgwAdJKBJaSEL1ZFE83tZaQe6bcd4mCLung_s1600.jpg?v=1740511821'},
    {'id': '9576435253550', 'title': '静電気防止 ボタンスリーブタートルリブニット', 'vendor': 'NANO universe', 'price': '¥3,520\n(税込)', 'link': '/products/6734222331', 'colors': ['L.グレー', 'D.グレー', 'ボルドー'], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/pF-KJtIE4_j2F1nlv_bTiwg17TLATGAJyBz1KlHPVT5UyiGZrSPIxcHvGv03dvnf2rvv5lenIah5yALe4-N_yCD40MXnSyNUZQ5b-t9T_s1600.jpg?v=1725933336'},
    {'id': None, 'title': '未找到标题', 'vendor': '未找到品牌', 'price': '未找到价格', 'link': '/products/6734222331', 'colors': [], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/pF-KJtIE4_j2F1nlv_bTiwg17TLATGAJyBz1KlHPVT5UyiGZrSPIxcHvGv03dvnf2rvv5lenIah5yALe4-N_yCD40MXnSyNUZQ5b-t9T_s1600.jpg?v=1725933336'},
    {'id': '9575069483310', 'title': '洗濯機洗い可 軽量ツイード調ニットカーディガン', 'vendor': 'NANO universe', 'price': '¥4,092\n(税込)', 'link': '/products/6734222337', 'colors': ['ブラック', 'アイボリー', 'パターン１'], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/e6prjFBRivaeeorasorJE7iQUHhHtqm0ng_m87ZN5Zvdg-Bp433vmq4_0Sp1xH8tQ6SUs4xtQ_qrf4703cVSUruxNAllWJ01zyIm56oYYw_s1600.jpg?v=1725851058'},
    {'id': None, 'title': '未找到标题', 'vendor': '未找到品牌', 'price': '未找到价格', 'link': '/products/6734222337', 'colors': [], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/e6prjFBRivaeeorasorJE7iQUHhHtqm0ng_m87ZN5Zvdg-Bp433vmq4_0Sp1xH8tQ6SUs4xtQ_qrf4703cVSUruxNAllWJ01zyIm56oYYw_s1600.jpg?v=1725851058'},
    {'id': '9568169394478', 'title': '「西川ダウン(R)」サージロングダウン', 'vendor': 'NANO universe', 'price': '¥63,800\n(税込)', 'link': '/products/6694214300', 'colors': ['ブラック', 'チャコール', 'グレージュ'], 'badge': '', 'features': ['撥水/防水加工'], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/6694214300_010_B1.jpg?v=1730887113'},
    {'id': None, 'title': '未找到标题', 'vendor': '未找到品牌', 'price': '未找到价格', 'link': '/products/6694214300', 'colors': [], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/6694214300_010_B1.jpg?v=1730887113'},
    {'id': '9527987241262', 'title': 'Anti Soaked(R) 汗染み防止 クルーネックTシャツ', 'vendor': 'NANO universe', 'price': '¥5,280\n(税込)', 'link': '/products/6694124302', 'colors': ['ブラック', 'チャコール', 'ホワイト', 'グレージュ'], 'badge': '', 'features': ['汗染み防止', 'ニオイ軽減 (防臭)', 'UVカット', '抗菌'], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/JrD8Y9A2ZXEPkia1MUt5BcQn54kKxwg2v_Qs3H-UvnT0OEK-cSUN9oxmXIGzlH5vlTZe7s7QDNZpPFkSD3MPxCvGwRDIMzVlo1HA4aFxK6U_s1600.jpg?v=1722679434'},
    {'id': None, 'title': '未找到标题', 'vendor': '未找到品牌', 'price': '未找到价格', 'link': '/products/6694124302', 'colors': [], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/JrD8Y9A2ZXEPkia1MUt5BcQn54kKxwg2v_Qs3H-UvnT0OEK-cSUN9oxmXIGzlH5vlTZe7s7QDNZpPFkSD3MPxCvGwRDIMzVlo1HA4aFxK6U_s1600.jpg?v=1722679434'},
    {'id': '9542676447534', 'title': '撥水加工ライトダウン リバーシブルノーカラージャケット', 'vendor': 'NANO universe', 'price': '¥9,240\n(税込)', 'link': '/products/6734214301', 'colors': ['ブラック', 'アイボリー', 'オリーブ'], 'badge': '', 'features': ['撥水/防水加工'], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/epDMlUkvxfbZXQEgZ6ak_YmLuHSD2TdtMC8ha0Yn4BuhwwWEiaI77BEl2HU1YQicQ8TPB1jP0G6_N1w1sm94ztvFrWHz-ZNuYqiYHIAZ_s1600.jpg?v=1723775215'},
    {'id': None, 'title': '未找到标题', 'vendor': '未找到品牌', 'price': '未找到价格', 'link': '/products/6734214301', 'colors': [], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/epDMlUkvxfbZXQEgZ6ak_YmLuHSD2TdtMC8ha0Yn4BuhwwWEiaI77BEl2HU1YQicQ8TPB1jP0G6_N1w1sm94ztvFrWHz-ZNuYqiYHIAZ_s1600.jpg?v=1723775215'},
    {'id': '9759041487150', 'title': 'Anti Soaked(R) 汗染み防止クルーネックリブTシャツ', 'vendor': 'NANO universe', 'price': '¥6,600\n(税込)', 'link': '/products/6695124304', 'colors': ['ブラック', 'チャコール', 'アイボリー', 'カーキ'], 'badge': 'NEW', 'features': ['抗菌', 'UVカット', '汗染み防止', 'ニオイ軽減 (防臭)'], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/RQ6-fJIQcFktpbQDlaogt7a1k2h8wKaJRCZU21v8GlTDiw8VYQftfN4BM8NkaYs6sa8GnTwoz0DQyFoditKoKFhRjV1M4nEvFd4z_UlcOPY_s1600.jpg?v=1741894227'},
    {'id': None, 'title': '未找到标题', 'vendor': '未找到品牌', 'price': '未找到价格', 'link': '/products/6695124304', 'colors': [], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/RQ6-fJIQcFktpbQDlaogt7a1k2h8wKaJRCZU21v8GlTDiw8VYQftfN4BM8NkaYs6sa8GnTwoz0DQyFoditKoKFhRjV1M4nEvFd4z_UlcOPY_s1600.jpg?v=1741894227'},
    {'id': '9710711243054', 'title': 'ダブルブレストジャケット', 'vendor': 'NANO universe', 'price': '¥11,880\n(税込)', 'link': '/products/6735116301', 'colors': ['チャコール', 'ベージュ', 'ネイビー'], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/DwSjogpeabuGEbtAn4hiu_rc37YiLAanpTvuMwC0u2hFN71wh9u94fSkFFC8SXTm921YCgAUzZY_tUs-UpgzkGDpkUhB4LeQ2-GhbaH2_w_s1600.jpg?v=1737673291'},
    {'id': None, 'title': '未找到标题', 'vendor': '未找到品牌', 'price': '未找到价格', 'link': '/products/6735116301', 'colors': [], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/DwSjogpeabuGEbtAn4hiu_rc37YiLAanpTvuMwC0u2hFN71wh9u94fSkFFC8SXTm921YCgAUzZY_tUs-UpgzkGDpkUhB4LeQ2-GhbaH2_w_s1600.jpg?v=1737673291'}, {'id': '9544910537006', 'title': 'クロップドニットセットワンピース', 'vendor': 'NANO universe', 'price': '¥5,346\n(税込)', 'link': '/products/6734219312', 'colors': ['チャコール', 'アイボリー', 'カーキ'], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/2ZP2YJh751h1pOYh2GGtoujV3CGD7_iNcx-K0XM83OVsMg0rEbaH1bLuz_L8kHlsWW5jlt0kzi-eNWRQxvxgpJUcVTbDsjg7DfJxpcNeEg_s1600.jpg?v=1724007998'}, {'id': None, 'title': '未找到标题', 'vendor': '未找到品牌', 'price': '未找到价格', 'link': '/products/6734219312', 'colors': [], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/2ZP2YJh751h1pOYh2GGtoujV3CGD7_iNcx-K0XM83OVsMg0rEbaH1bLuz_L8kHlsWW5jlt0kzi-eNWRQxvxgpJUcVTbDsjg7DfJxpcNeEg_s1600.jpg?v=1724007998'}, {'id': '9568169951534', 'title': '「西川ダウン(R)」ソロテックスAラインダウン', 'vendor': 'NANO universe', 'price': '¥60,500\n(税込)', 'link': '/products/6694214301', 'colors': ['ブラック', 'チャコール', 'オフホワイト'], 'badge': '', 'features': ['撥水/防水加工'], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/nZHmw-hMDgd3mF1fTGvxfDTOOuI58s9pVgMC7nz22SC9myymkesNXua_eC6XzLUVhrLm1-bUBlnY3XOrQULE2cRTxtMa3ctz_e1dOpJoFQ_s1600.jpg?v=1732604205'}, {'id': None, 'title': '未找到标题', 'vendor': '未找到品牌', 'price': '未找到价格', 'link': '/products/6694214301', 'colors': [], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/nZHmw-hMDgd3mF1fTGvxfDTOOuI58s9pVgMC7nz22SC9myymkesNXua_eC6XzLUVhrLm1-bUBlnY3XOrQULE2cRTxtMa3ctz_e1dOpJoFQ_s1600.jpg?v=1732604205'}, {'id': '9584679256366', 'title': 'シャドーストライプニットプルオーバー', 'vendor': 'NANO universe', 'price': '¥3,850\n(税込)', 'link': '/products/6734222310', 'colors': ['ブラック', 'ホワイト', 'ブルー'], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/KeclehNouDLMIem-qhOGsM7Lq-QUTeavNo6JhikQNyd9BdvHLQ8iw63N5yBlLsCq0HQiS4riaGpdZaAqmCBv61dTgpzYOj4bzsF8eavRZW4_s1600.jpg?v=1726531624'}, {'id': None, 'title': '未找到标题', 'vendor': '未找到品牌', 'price': '未找到价格', 'link': '/products/6734222310', 'colors': [], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/KeclehNouDLMIem-qhOGsM7Lq-QUTeavNo6JhikQNyd9BdvHLQ8iw63N5yBlLsCq0HQiS4riaGpdZaAqmCBv61dTgpzYOj4bzsF8eavRZW4_s1600.jpg?v=1726531624'}, {'id': '9774411055406', 'title': 'リネンタッチタックデザインボリュームブラウス', 'vendor': 'NANO universe', 'price': '¥5,940\n(税込)', 'link': '/products/6735121307', 'colors': ['チャコール', 'ホワイト', 'グリーン'], 'badge': 'NEW', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/4RUzaMCrdQgosGVqdCCJOM_36LI5eLbp1wNigh4f9B3n6Y42XeOzvLBrO-PoKLZ3ASjw7o6Vm6kQRUHbQwbeECIkNXm_uCJMzpFVRELoDQc_s1600.jpg?v=1743161434'}, {'id': None, 'title': '未找到标题', 'vendor': '未找到品牌', 'price': '未找到价格', 'link': '/products/6735121307', 'colors': [], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/4RUzaMCrdQgosGVqdCCJOM_36LI5eLbp1wNigh4f9B3n6Y42XeOzvLBrO-PoKLZ3ASjw7o6Vm6kQRUHbQwbeECIkNXm_uCJMzpFVRELoDQc_s1600.jpg?v=1743161434'}, {'id': '9544910471470', 'title': 'モチッと毛玉抑制ニットプルオーバー（セットアップ可）', 'vendor': 'NANO universe', 'price': '¥4,389\n(税込)', 'link': '/products/6734222319', 'colors': ['ブラック', 'グレー', 'ベージュ'], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/YrTXqIiqrSMDlybiZYgixzQmlUXtgcRROue8zE3BPHPvnxLIerE49etqVVSxHdrBuxDYrQa9PfB0vJOKf2KyhtMqS4K11ZXXfsACBRtB_s1600.jpg?v=1724007996'}, {'id': None, 'title': '未找到标题', 'vendor': '未找到品牌', 'price': '未找到价格', 'link': '/products/6734222319', 'colors': [], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/YrTXqIiqrSMDlybiZYgixzQmlUXtgcRROue8zE3BPHPvnxLIerE49etqVVSxHdrBuxDYrQa9PfB0vJOKf2KyhtMqS4K11ZXXfsACBRtB_s1600.jpg?v=1724007996'}, {'id': '9759041552686', 'title': 'Anti Soaked(R) 汗染み防止ボートネックTシャツ', 'vendor': 'NANO universe', 'price': '¥5,500\n(税込)', 'link': '/products/6695124303', 'colors': ['ブラック', 'チャコール', 'ホワイト', 'カーキ'], 'badge': 'NEW', 'features': ['抗菌', 'UVカット', '汗染み防止', 'ニオイ軽減 (防臭)'], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/O32zaCaDnQI0Gqrh2DM_SGWRj8HxjfbmNYI7qtFRAIaQbUBwEzC9njD6WGjaXYe0kdl_1wvVNrpgL1yh6MPvjV1CIewrPPqt6byPCYVcAmk_s1600.jpg?v=1741894229'}, {'id': None, 'title': '未找到标题', 'vendor': '未找到品牌', 'price': '未找到价格', 'link': '/products/6695124303', 'colors': [], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/O32zaCaDnQI0Gqrh2DM_SGWRj8HxjfbmNYI7qtFRAIaQbUBwEzC9njD6WGjaXYe0kdl_1wvVNrpgL1yh6MPvjV1CIewrPPqt6byPCYVcAmk_s1600.jpg?v=1741894229'}, {'id': '9624368513326', 'title': 'バスケットモールニットクルーワイドトップス', 'vendor': 'NANO universe', 'price': '¥4,466\n(税込)', 'link': '/products/6734222301', 'colors': ['ブラック', 'ホワイト', 'ボルドー'], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/6734222301_10.jpg?v=1732869710'}, {'id': None, 'title': '未找到标题', 'vendor': '未找到品牌', 'price': '未找到价格', 'link': '/products/6734222301', 'colors': [], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/6734222301_10.jpg?v=1732869710'}, {'id': '9651849330990', 'title': '洗濯機洗い可バイカラーニットジャケットカーディガン', 'vendor': 'NANO universe', 'price': '¥6,820\n(税込)', 'link': '/products/6735122303', 'colors': ['ブラック', 'アイボリー', 'Ｌ．ブルー'], 'badge': '', 'features': ['ウォッシャブル加工'], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/b7SP77gRpM7oS3-honLSgDGCk5E_vFtWo1Aw_rEWVkDerw0Fk-FnIX6EafLJcBDcbuSYs64FTiSCWuvCpQR-i3W9FnbCYWyoZaN0wXWi1Q_s1600.jpg?v=1731627353'}, {'id': None, 'title': '未找到标题', 'vendor': '未找到品牌', 'price': '未找到价格', 'link': '/products/6735122303', 'colors': [], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/b7SP77gRpM7oS3-honLSgDGCk5E_vFtWo1Aw_rEWVkDerw0Fk-FnIX6EafLJcBDcbuSYs64FTiSCWuvCpQR-i3W9FnbCYWyoZaN0wXWi1Q_s1600.jpg?v=1731627353'}, {'id': '9758039736622', 'title': 'PENNEYS別注TheFOXクルーネックサマーニット', 'vendor': 'NANO universe', 'price': '¥4,950\n(税込)', 'link': '/products/6735122324', 'colors': ['グレー', 'チャコール', 'ホワイト'], 'badge': 'NEW', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/zqo67SPAmvjzJpW4_C72LZzDfPh8hzpw8SjFRETskG8tyYoImbUBtKG9T1oYO0g5AAJ3PO-w4RQpMudhoMNmCY4EkWi0gu7vxIwgPo1t_s1600.jpg?v=1741865444'}, {'id': None, 'title': '未找到标题', 'vendor': '未找到品牌', 'price': '未找到价格', 'link': '/products/6735122324', 'colors': [], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/zqo67SPAmvjzJpW4_C72LZzDfPh8hzpw8SjFRETskG8tyYoImbUBtKG9T1oYO0g5AAJ3PO-w4RQpMudhoMNmCY4EkWi0gu7vxIwgPo1t_s1600.jpg?v=1741865444'}, {'id': '9528172577070', 'title': 'ドライウェザーストレッチ ダブルジャケット(セットアップ可)', 'vendor': 'NANO universe', 'price': '¥13,860\n(税込)', 'link': '/products/6694216303', 'colors': ['グレー', 'ベージュ', 'ネイビー'], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/6694216303_020_B.jpg?v=1727417457'}, {'id': None, 'title': '未找到标题', 'vendor': '未找到品牌', 'price': '未找到价格', 'link': '/products/6694216303', 'colors': [], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/6694216303_020_B.jpg?v=1727417457'}, {'id': '9560693670190', 'title': 'チュールフリルスリーブブラウス', 'vendor': 'NANO universe', 'price': '¥4,774\n(税込)', 'link': '/products/6734220315', 'colors': ['ブラック', 'オフホワイト', 'ベージュ'], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/umqyTYuo8rIhciH82TjbFwyPnLMrL_UvilZRneG55McC2ih_7MOaaPQLKewVcblrPZwtxbeqQ2zRE1nfq3dqI7bTxUOsH45k7kMMGhV2cg_s1600.jpg?v=1724897354'}, {'id': None, 'title': '未找到标题', 'vendor': '未找到品牌', 'price': '未找到价格', 'link': '/products/6734220315', 'colors': [], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/umqyTYuo8rIhciH82TjbFwyPnLMrL_UvilZRneG55McC2ih_7MOaaPQLKewVcblrPZwtxbeqQ2zRE1nfq3dqI7bTxUOsH45k7kMMGhV2cg_s1600.jpg?v=1724897354'}, {'id': '9768087716142', 'title': '前後2Wayゴールド釦クロップドワイドシャツ', 'vendor': 'NANO universe', 'price': '¥4,950\n(税込)', 'link': '/products/6735120314', 'colors': ['ブラック', 'アイボリー', 'ライムグリーン'], 'badge': 'NEW', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/7DZvM0UDkOj8BpQ8L9qsIlHKJm_ODgB0OPusanaZSfsXfXt8SPURZ82BOybQ_eVJi7zm00jtqfbWQoM2I3l7U3njLiwDbYjbsWAXI8-P_s1600.jpg?v=1742297419'}, {'id': None, 'title': '未找到标题', 'vendor': '未找到品牌', 'price': '未找到价格', 'link': '/products/6735120314', 'colors': [], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/7DZvM0UDkOj8BpQ8L9qsIlHKJm_ODgB0OPusanaZSfsXfXt8SPURZ82BOybQ_eVJi7zm00jtqfbWQoM2I3l7U3njLiwDbYjbsWAXI8-P_s1600.jpg?v=1742297419'}, {'id': '9654237331758', 'title': 'フクレジャガードカットトップス(セットアップ可)', 'vendor': 'NANO universe', 'price': '¥4,081\n(税込)', 'link': '/products/6735123301', 'colors': ['ブラック', 'アイボリー', 'グリーン'], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/AZclrJqMPfhc-hrD-eGrpFVHT9uk6Bzl23lsRdIOf4J0FVhGHhpZtx_5S44TvNMDtI6VBlC5FRW0LpJ9jtV3nOqZDCHSBCfXDUB8lJ07qA_s1600.jpg?v=1732847130'}, {'id': None, 'title': '未找到标题', 'vendor': '未找到品牌', 'price': '未找到价格', 'link': '/products/6735123301', 'colors': [], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/AZclrJqMPfhc-hrD-eGrpFVHT9uk6Bzl23lsRdIOf4J0FVhGHhpZtx_5S44TvNMDtI6VBlC5FRW0LpJ9jtV3nOqZDCHSBCfXDUB8lJ07qA_s1600.jpg?v=1732847130'}, {'id': '9528163139886', 'title': 'PURE LAMBS リバーミドルコート', 'vendor': 'NANO universe', 'price': '¥26,180\n(税込)', 'link': '/products/6694211300', 'colors': ['グレージュ', 'イエロー', 'Ｄ．ネイビー'], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/ZG2NFgExqS-rxzP-9Ye4b1euOLOTFi8XhEYKw1033xreyLBu0fe27XYqz0EjyI01Yyuq3Rn4uuIgwHBoqnU8yfq2tHIDcHDyRXj9oVRz_s1600.jpg?v=1732847785'}, {'id': None, 'title': '未找到标题', 'vendor': '未找到品牌', 'price': '未找到价格', 'link': '/products/6694211300', 'colors': [], 'badge': '', 'features': [], 'image_url': 'https://cdn.shopify.com/s/files/1/0802/1206/6606/files/ZG2NFgExqS-rxzP-9Ye4b1euOLOTFi8XhEYKw1033xreyLBu0fe27XYqz0EjyI01Yyuq3Rn4uuIgwHBoqnU8yfq2tHIDcHDyRXj9oVRz_s1600.jpg?v=1732847785'}]
