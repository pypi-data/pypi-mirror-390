import { defineComponent as N, ref as b, computed as n, normalizeClass as i, watch as w, createElementBlock as T, openBlock as L, normalizeStyle as $, createElementVNode as u, unref as c, toDisplayString as x } from "vue";
import { useBindingGetter as z, useLanguage as D } from "instaui";
import { highlighterTask as H, getTransformers as S, readyCopyButton as E } from "@/shiki_code_logic";
function M(o) {
  return o.replace(/^[\r\n\u2028\u2029]+|[\r\n\u2028\u2029]+$/g, "");
}
const V = { class: "lang" }, G = ["innerHTML"], A = /* @__PURE__ */ N({
  __name: "Shiki_Code",
  props: {
    code: {},
    language: {},
    theme: {},
    themes: {},
    transformers: {},
    lineNumbers: { type: Boolean },
    useDark: { type: Boolean },
    decorations: {}
  },
  setup(o) {
    const e = o, {
      transformers: g = [],
      themes: f = {
        light: "vitesse-light",
        dark: "vitesse-dark"
      },
      useDark: h
    } = e, { getValue: p } = z(), m = b(""), s = n(() => e.language || "python"), a = n(
      () => e.theme || (p(h) ? "dark" : "light")
    ), v = n(() => e.lineNumbers ?? !0), y = n(() => i([
      `language-${s.value}`,
      `theme-${a.value}`,
      "shiki-code",
      { "line-numbers": v.value }
    ]));
    w(
      [() => e.code, a],
      async ([t, r]) => {
        if (!t)
          return;
        t = M(t);
        const l = await H, B = await S(g);
        m.value = await l.codeToHtml(t, {
          themes: f,
          lang: s.value,
          transformers: B,
          defaultColor: a.value,
          colorReplacements: {
            "#ffffff": "#f8f8f2"
          },
          decorations: e.decorations
        });
      },
      { immediate: !0 }
    );
    const { copyButtonClick: d, btnClasses: k } = E(e), C = D(), _ = n(() => `--shiki-code-copy-copied-text-content: '${C.value === "zh_CN" ? "已复制" : "Copied"}'`);
    return (t, r) => (L(), T("div", {
      class: i(y.value),
      style: $(_.value)
    }, [
      u("button", {
        class: i(c(k)),
        title: "Copy Code",
        onClick: r[0] || (r[0] = //@ts-ignore
        (...l) => c(d) && c(d)(...l))
      }, null, 2),
      u("span", V, x(s.value), 1),
      u("div", {
        innerHTML: m.value,
        style: { overflow: "hidden" }
      }, null, 8, G)
    ], 6));
  }
});
export {
  A as default
};
