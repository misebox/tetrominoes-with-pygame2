pygame2
https://www.pygame.org/docs/

参考:
https://www.pygame.org/docs/tut/ImportInit.html


ここからパクる
https://www.pygame.org/docs/tut/tom_games6.html#makegames-6-3


矩形
https://www.pygame.org/docs/ref/draw.html?highlight=draw%20rect#pygame.draw.rect


設計:


ミノの形は座標のコレクションで表現
(x, y), (x2, y2)...



- ミノ形を書く

[
  " # ",
  "###",
]

↓↓↓↓↓↓

points = set([(x1,y1), (x2, y2), ...])

# - 動かす ↓→←
# - 回転
# - 落ちる
# - 壁
#- 着地
#- 衝突検知
#- ミノ種類
