const {
  SvelteComponent: p,
  assign: _,
  bubble: y,
  claim_element: k,
  compute_rest_props: m,
  detach: q,
  element: w,
  exclude_internal_props: C,
  get_spread_update: I,
  init: S,
  insert_hydration: E,
  listen: D,
  noop: d,
  safe_not_equal: G,
  set_attributes: g,
  src_url_equal: M,
  toggle_class: h
} = window.__gradio__svelte__internal;
function P(s) {
  let e, n, t, l, r = [
    { src: n = /*src*/
    s[0] },
    /*$$restProps*/
    s[1]
  ], a = {};
  for (let i = 0; i < r.length; i += 1)
    a = _(a, r[i]);
  return {
    c() {
      e = w("img"), this.h();
    },
    l(i) {
      e = k(i, "IMG", { src: !0 }), this.h();
    },
    h() {
      g(e, a), h(e, "svelte-kxeri3", !0);
    },
    m(i, c) {
      E(i, e, c), t || (l = D(
        e,
        "load",
        /*load_handler*/
        s[2]
      ), t = !0);
    },
    p(i, [c]) {
      g(e, a = I(r, [
        c & /*src*/
        1 && !M(e.src, n = /*src*/
        i[0]) && { src: n },
        c & /*$$restProps*/
        2 && /*$$restProps*/
        i[1]
      ])), h(e, "svelte-kxeri3", !0);
    },
    i: d,
    o: d,
    d(i) {
      i && q(e), t = !1, l();
    }
  };
}
function V(s, e, n) {
  const t = ["src"];
  let l = m(e, t), { src: r = void 0 } = e;
  function a(i) {
    y.call(this, s, i);
  }
  return s.$$set = (i) => {
    e = _(_({}, e), C(i)), n(1, l = m(e, t)), "src" in i && n(0, r = i.src);
  }, [r, l, a];
}
class j extends p {
  constructor(e) {
    super(), S(this, e, V, P, G, { src: 0 });
  }
}
const {
  SvelteComponent: z,
  attr: A,
  check_outros: B,
  children: F,
  claim_component: H,
  claim_element: J,
  create_component: K,
  destroy_component: L,
  detach: v,
  element: N,
  group_outros: O,
  init: Q,
  insert_hydration: R,
  mount_component: T,
  safe_not_equal: U,
  toggle_class: o,
  transition_in: u,
  transition_out: f
} = window.__gradio__svelte__internal;
function b(s) {
  let e, n;
  return e = new j({
    props: { src: (
      /*value*/
      s[0].url
    ), alt: "" }
  }), {
    c() {
      K(e.$$.fragment);
    },
    l(t) {
      H(e.$$.fragment, t);
    },
    m(t, l) {
      T(e, t, l), n = !0;
    },
    p(t, l) {
      const r = {};
      l & /*value*/
      1 && (r.src = /*value*/
      t[0].url), e.$set(r);
    },
    i(t) {
      n || (u(e.$$.fragment, t), n = !0);
    },
    o(t) {
      f(e.$$.fragment, t), n = !1;
    },
    d(t) {
      L(e, t);
    }
  };
}
function W(s) {
  let e, n, t = (
    /*value*/
    s[0] && b(s)
  );
  return {
    c() {
      e = N("div"), t && t.c(), this.h();
    },
    l(l) {
      e = J(l, "DIV", { class: !0 });
      var r = F(e);
      t && t.l(r), r.forEach(v), this.h();
    },
    h() {
      A(e, "class", "container svelte-1sgcyba"), o(
        e,
        "table",
        /*type*/
        s[1] === "table"
      ), o(
        e,
        "gallery",
        /*type*/
        s[1] === "gallery"
      ), o(
        e,
        "selected",
        /*selected*/
        s[2]
      ), o(
        e,
        "border",
        /*value*/
        s[0]
      );
    },
    m(l, r) {
      R(l, e, r), t && t.m(e, null), n = !0;
    },
    p(l, [r]) {
      /*value*/
      l[0] ? t ? (t.p(l, r), r & /*value*/
      1 && u(t, 1)) : (t = b(l), t.c(), u(t, 1), t.m(e, null)) : t && (O(), f(t, 1, 1, () => {
        t = null;
      }), B()), (!n || r & /*type*/
      2) && o(
        e,
        "table",
        /*type*/
        l[1] === "table"
      ), (!n || r & /*type*/
      2) && o(
        e,
        "gallery",
        /*type*/
        l[1] === "gallery"
      ), (!n || r & /*selected*/
      4) && o(
        e,
        "selected",
        /*selected*/
        l[2]
      ), (!n || r & /*value*/
      1) && o(
        e,
        "border",
        /*value*/
        l[0]
      );
    },
    i(l) {
      n || (u(t), n = !0);
    },
    o(l) {
      f(t), n = !1;
    },
    d(l) {
      l && v(e), t && t.d();
    }
  };
}
function X(s, e, n) {
  let { value: t } = e, { type: l } = e, { selected: r = !1 } = e;
  return s.$$set = (a) => {
    "value" in a && n(0, t = a.value), "type" in a && n(1, l = a.type), "selected" in a && n(2, r = a.selected);
  }, [t, l, r];
}
class Y extends z {
  constructor(e) {
    super(), Q(this, e, X, W, U, { value: 0, type: 1, selected: 2 });
  }
}
export {
  Y as default
};
