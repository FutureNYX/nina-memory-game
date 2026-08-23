# Adding the box-opening animation to memobyninasechko.tilda.ws

Tested by injecting the block into your live page at both phone and desktop
sizes. It sits between the video cover and the photo grid without touching
either of them.

You need a paid Tilda plan — Personal is enough. Free does not allow code blocks.

---

## 1. Add the block

1. Open the page in the Tilda editor.
2. **Библиотека блоков → Другое → T123 «HTML-код»**.
3. It lands at the bottom of the page. That's fine — you'll move it in step 2.
4. Click **Контент** on the new block.
5. Open `hero-block.html`, select all, copy, paste it into the box.
6. **Сохранить**.

## 2. Put it wherever you want

The animation is an ordinary Tilda block, so it goes anywhere any other block
goes, and it works in any position on the page.

To move it, hover over the block in the editor and use the control panel that
appears on its left:

- the **↑ / ↓ arrows** move it one position at a time, or
- **⠿ (drag handle)** — hold and drag it up the page, or
- the **gear icon → «Переместить»** if you prefer a menu.

To get what you described — cover, then animation, then the three photos —
you only need to move **one** block. Either drag the animation up so it sits
directly under the cover, or drag the photo block (the one with the three
product shots) down so it sits below the animation. Same result, one drag.

Then **Опубликовать**.

## 3. Check the background

The animation sits on a pale grey, `#ECEDF1`, sampled from the film's own
studio backdrop so the frames sit *on* the page rather than on top of it.

Your page uses white and `#F2F2F2` for its sections, so the grey reads as its
own section — which looks intentional and gives the animation room to breathe.

If you'd rather it matched the block above or below exactly, change one line
near the top of the pasted code:

```css
--ground:#ECEDF1;     /* try #FFFFFF or #F2F2F2 */
```

---

## Which file to paste

| File | What you get |
|---|---|
| `hero-block.html` | Animation **plus four short captions** that fade in and out as the box opens |
| `hero-block-plain.html` | Animation **only** — no text at all |

The captions are set in **TildaSans**, the font your site already uses, so they
match everything else and cost no extra loading time.

Note there is deliberately **no big heading** in the block — your cover block
already has «Авторская игра МЕМО» as the page's H1, and a second one would
confuse search engines. There's also no scroll arrow, since your cover already
has one.

---

## Yes, you can add and delete things

**Everything except the animation itself is optional.**

### Remove one caption
Find a chunk like this in the pasted code and delete it, from `<div` to `</div>`:

```html
<!-- caption 2 - as the box splits open -->
<div class="nsx__cap" data-from="0.28" data-to="0.44">
  <p class="nsx__eyebrow">Коробка</p>
  <p class="nsx__capText">Раскрывается сразу на четыре стороны.</p>
</div>
```

All four are independent. Delete one, three, or all of them.

### Change the wording
Type over the Russian between the `<p>` tags. Two styles are available:
`nsx__eyebrow` is the small grey uppercase label, `nsx__capText` is the sentence
under it.

### Change *when* a caption appears
`data-from` and `data-to` are positions in the scroll:

| value | what's on screen |
|---|---|
| `0.00` | box still closed |
| `0.30` | box splitting open |
| `0.60` | box lying open |
| `1.00` | cards fully burst out |

So `data-from="0.28" data-to="0.44"` means "fade in just over a quarter of the
way through, fade out before halfway".

### Make the animation quicker or slower to scroll through
Near the top of the code:

```css
.nsx__scrolly{
  height:350vh;
  height:350svh;
```

`350svh` is about three and a half screens of scrolling to open the box fully.
`250svh` is quicker, `500svh` is slower. There are two more values just below
for wide screens (`450svh`) and small phones (`320svh`) — change all three
together.

---

## It won't disturb the rest of the page

Every style in the block is name-spaced, so it cannot change how your other
blocks look, and nothing else on the page can change how it looks. Your cover,
photos, text, prices and the order button all keep working exactly as they do
now.

---

## One thing that can't be changed

The animation is 123 image files, and **Tilda cannot host them.** That's Tilda's
own rule rather than a limitation of this code — their help page on uploading
your own files says *«В данный момент загрузить файлы прямо на Tilda не
получится»* and tells you to link to an external service instead.

They're served from `https://futurenyx.github.io/nina-memory-game`, which is
free and fast. Nothing to set up — the block already points there. Just don't
delete that address from the code.
