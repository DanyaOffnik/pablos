# -*- coding: utf-8 -*-
import io, py_compile, sys
P = r"C:\work\hunt2\modules\profiles.py"
s = io.open(P, encoding="utf-8-sig").read()
PAIRS = [
 ('''        "params": [("/", "searchword", "a"),
                   ("/index.php?option=com_content&view=article", "id", "1")],''',
  '''        "params": [("/", "searchword", "a"),
                   ("/index.php?option=com_content&view=article", "id", "1"),
                   ("/index.php?option=com_content&view=category", "id", "2"),
                   ("/index.php?option=com_content&view=category", "catid", "2"),
                   ("/index.php?option=com_finder&view=search", "q", "a"),
                   ("/index.php?option=com_tags&view=tag", "id", "1")],'''),
 ('''        "params": [("/index.php?do=search&subaction=search", "story", "a"),
                   ("/", "do", "search")],''',
  '''        "params": [("/index.php?do=search&subaction=search", "story", "a"),
                   ("/index.php?subaction=showfull", "id", "1"),
                   ("/index.php?do=stats", "id", "1"),
                   ("/index.php?do=feedback", "id", "1")],'''),
 ('''        "params": [("/search/", "q", "a"), ("/catalog/", "SECTION_ID", "1")],''',
  '''        "params": [("/search/", "q", "a"), ("/catalog/", "SECTION_ID", "1"),
                   ("/catalog/", "ELEMENT_ID", "1"), ("/catalog/", "PAGEN_1", "1"),
                   ("/bitrix/admin/sale_order.php", "ID", "1")],'''),
 ('''        "params": [("/", "s", "a"), ("/", "id_product", "1")],''',
  '''        "params": [("/", "s", "a"), ("/", "id_product", "1"),
                   ("/", "id_category", "2"), ("/", "orderby", "price"),
                   ("/", "id_lang", "1")],'''),
 ('''        "params": [("/index.php?route=product/product", "product_id", "1"),
                   ("/index.php?route=product/category", "path", "20"),
                   ("/index.php?route=product/search", "search", "a")],''',
  '''        "params": [("/index.php?route=product/product", "product_id", "1"),
                   ("/index.php?route=product/category", "path", "20"),
                   ("/index.php?route=product/search", "search", "a"),
                   ("/index.php?route=product/category", "sort", "p.price"),
                   ("/index.php?route=product/category", "order", "ASC"),
                   ("/index.php?route=product/category", "limit", "20"),
                   ("/index.php?route=product/category", "page", "2")],'''),
]
for i, (old, new) in enumerate(PAIRS, 1):
    if s.count(old) != 1:
        print("профиль %d: не найдено" % i); sys.exit(1)
    s = s.replace(old, new)
io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
py_compile.compile(P, doraise=True)
print("параметры: ок")
