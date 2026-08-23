# Adding the box-opening animation to your Tilda page

You need a paid Tilda plan (Personal is enough — Free does not allow code blocks).

---

## 1. Add the block

1. Open your page in the Tilda editor.
2. **Библиотека блоков → Другое → T123 «HTML-код»**.
3. Drag it to wherever you want the animation — normally right at the top,
   under the header.
4. Click **Контент** on the block.
5. Open **`hero-block.html`** (or `hero-block-plain.html`, see below), select
   everything, copy it, and paste it into the box.
6. **Сохранить** → **Опубликовать**.

That's it. One block, nothing else to install.

## 2. Set the page background

The animation was shot on a pale grey studio backdrop, so the page behind it
needs to be the same colour or you will see a seam where the block starts and
ends.

**Настройки сайта → Шрифты и цвета → Цвет фона → `#ECEDF1`**

(Or set just that one block's background to `#ECEDF1` if the rest of your page
is a different colour.)

---

## Which file to paste

| File | What you get |
|---|---|
| `hero-block.html` | The animation **plus four lines of text** that fade in and out as the box opens |
| `hero-block-plain.html` | The animation **only** — no text at all |

Use the plain one if you would rather write all the text in Tilda's own blocks.

---

## Yes, you can add and delete things

**Everything except the animation itself is optional and safe to delete.**

### Remove one line of text
In the pasted code, find a chunk that looks like this and delete the whole
thing, from `<div` to `</div>`:

```html
<!-- caption 2 - as the box splits open -->
<div class="nsx__cap" data-from="0.26" data-to="0.42">
  <p class="nsx__eyebrow">Коробка</p>
  <p class="nsx__capText">Собрана вручную и раскрывается сразу на четыре стороны.</p>
</div>
```

The four captions are independent. Delete one, three, or all of them — the
animation does not care.

### Change the wording
Just type over the Russian text between the `<p>` tags. Two styles are
available: `nsx__eyebrow` is the small grey uppercase label, `nsx__capText` is
the normal sentence underneath.

### Change *when* a line appears
`data-from` and `data-to` are positions in the scroll:

- `0.00` = box still closed
- `0.30` = box splitting open
- `0.60` = box lying open
- `1.00` = cards fully burst out

So `data-from="0.26" data-to="0.42"` means "fade in a quarter of the way
through, fade out just before halfway". Change the numbers to re-time it.

### Remove the "Листайте" hint
Delete the `<div class="nsx__hint">…</div>` block.

### Make the animation faster or slower to scroll through
Near the top of the code, find:

```css
.nsx__scrolly{
  height:400vh;
  height:400svh;
```

`400svh` means four screen-heights of scrolling to open the box fully. Lower it
to `250svh` for a quicker open, raise it to `600svh` for a slower one. There are
two more values further down for wide screens (`520svh`) and small phones
(`360svh`) — change all of them together.

---

## Everything else stays in Tilda

The animation block does not touch the rest of your page. Product description,
photos, specifications, the cart and the payment button are all normal Tilda
blocks, and they will work exactly as they always do. The code block is
completely self-contained — every style in it is name-spaced, so it cannot
change how your other blocks look.

---

## One thing that cannot be changed

The animation is 123 image files, and **Tilda cannot host them.** That is
Tilda's own rule, not a limitation of this code — their help page on uploading
your own files says: *«В данный момент загрузить файлы прямо на Tilda не
получится»*, and recommends linking to an external service.

They are served from `https://futurenyx.github.io/nina-memory-game`, which is
free and fast. Nothing to set up — the block already points at them. Just don't
delete that address from the code.
