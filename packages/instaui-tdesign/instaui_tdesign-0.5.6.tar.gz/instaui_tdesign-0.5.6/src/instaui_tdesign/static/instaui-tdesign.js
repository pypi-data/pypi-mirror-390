import { defineComponent as j, useAttrs as H, useSlots as K, createBlock as L, openBlock as N, mergeProps as U, unref as l, createSlots as q, renderList as I, withCtx as $, renderSlot as V, normalizeProps as W, guardReactiveProps as X, computed as T, ref as mt, onMounted as Ae, reactive as we, watch as te, createElementVNode as Et, createVNode as Te, toDisplayString as ct, createTextVNode as Rt, resolveDynamicComponent as Oe } from "vue";
import * as D from "tdesign-vue-next";
import { DateRangePickerPanel as $e, useConfig as Ce, MessagePlugin as Se, NotifyPlugin as Pe } from "tdesign-vue-next";
import { useBindingGetter as xe } from "instaui";
function Ee(t) {
  const { container: e = ".insta-main" } = t;
  return e;
}
const Re = /* @__PURE__ */ j({
  inheritAttrs: !1,
  __name: "Affix",
  setup(t) {
    const e = H(), r = K(), n = Ee(e);
    return (o, i) => (N(), L(D.Affix, U(l(e), { container: l(n) }), q({ _: 2 }, [
      I(l(r), (a, f) => ({
        name: f,
        fn: $((s) => [
          V(o.$slots, f, W(X(s)))
        ])
      }))
    ]), 1040, ["container"]));
  }
});
function De(t) {
  const e = [], r = T(() => t.data ?? []), n = mt(0), o = T(() => {
    n.value;
    const f = r.value;
    return e.reduce((s, u) => u(s), f);
  }), i = (f) => {
    e.push(f);
  };
  function a() {
    n.value++;
  }
  return {
    tableData: o,
    orgData: r,
    registerRowsHandler: i,
    notifyTableDataChange: a
  };
}
function Fe(t) {
  const { tableData: e, attrs: r } = t, n = [], o = T(() => {
    const a = r.extraColumns ?? [];
    let u = [...!r.columns && e.value.length > 0 ? je(e.value) : r.columns ?? [], ...a];
    u = Me(u), u = u.map(Ie);
    for (const p of n)
      u = p(u);
    return u;
  });
  function i(a) {
    n.push(a);
  }
  return [o, i];
}
function je(t) {
  const e = t[0];
  return Object.keys(e).map((n) => ({
    colKey: n,
    title: n,
    sorter: !0
  }));
}
function Ie(t) {
  const e = t.name ?? t.colKey, r = `header-cell-${e}`, n = `body-cell-${e}`, o = t.label ?? t.colKey;
  return {
    ...t,
    name: e,
    label: o,
    title: r,
    cell: n
  };
}
function Me(t) {
  const e = [];
  for (const r of t) {
    const n = e.find((o) => o.colKey === r.colKey);
    n ? Object.assign(n, r) : e.push({ ...r });
  }
  return e;
}
function Le(t) {
  const { tableData: e, attrs: r } = t;
  return T(() => {
    const { pagination: n } = r;
    let o;
    if (typeof n == "boolean") {
      if (!n)
        return;
      o = {
        defaultPageSize: 10
      };
    }
    return typeof n == "number" && n > 0 && (o = {
      defaultPageSize: n
    }), typeof n == "object" && n !== null && (o = n), {
      defaultCurrent: 1,
      total: e.value.length,
      ...o
    };
  });
}
var ee = typeof global == "object" && global && global.Object === Object && global, Ne = typeof self == "object" && self && self.Object === Object && self, S = ee || Ne || Function("return this")(), F = S.Symbol, re = Object.prototype, ze = re.hasOwnProperty, Ge = re.toString, J = F ? F.toStringTag : void 0;
function Be(t) {
  var e = ze.call(t, J), r = t[J];
  try {
    t[J] = void 0;
    var n = !0;
  } catch {
  }
  var o = Ge.call(t);
  return n && (e ? t[J] = r : delete t[J]), o;
}
var He = Object.prototype, Ke = He.toString;
function Ue(t) {
  return Ke.call(t);
}
var qe = "[object Null]", Ve = "[object Undefined]", Dt = F ? F.toStringTag : void 0;
function Z(t) {
  return t == null ? t === void 0 ? Ve : qe : Dt && Dt in Object(t) ? Be(t) : Ue(t);
}
function B(t) {
  return t != null && typeof t == "object";
}
var We = "[object Symbol]";
function k(t) {
  return typeof t == "symbol" || B(t) && Z(t) == We;
}
function ot(t, e) {
  for (var r = -1, n = t == null ? 0 : t.length, o = Array(n); ++r < n; )
    o[r] = e(t[r], r, t);
  return o;
}
var w = Array.isArray, Ft = F ? F.prototype : void 0, jt = Ft ? Ft.toString : void 0;
function ne(t) {
  if (typeof t == "string")
    return t;
  if (w(t))
    return ot(t, ne) + "";
  if (k(t))
    return jt ? jt.call(t) : "";
  var e = t + "";
  return e == "0" && 1 / t == -1 / 0 ? "-0" : e;
}
function At(t) {
  var e = typeof t;
  return t != null && (e == "object" || e == "function");
}
function ie(t) {
  return t;
}
var Xe = "[object AsyncFunction]", Ze = "[object Function]", Ye = "[object GeneratorFunction]", Je = "[object Proxy]";
function oe(t) {
  if (!At(t))
    return !1;
  var e = Z(t);
  return e == Ze || e == Ye || e == Xe || e == Je;
}
var pt = S["__core-js_shared__"], It = function() {
  var t = /[^.]+$/.exec(pt && pt.keys && pt.keys.IE_PROTO || "");
  return t ? "Symbol(src)_1." + t : "";
}();
function Qe(t) {
  return !!It && It in t;
}
var ke = Function.prototype, tr = ke.toString;
function z(t) {
  if (t != null) {
    try {
      return tr.call(t);
    } catch {
    }
    try {
      return t + "";
    } catch {
    }
  }
  return "";
}
var er = /[\\^$.*+?()[\]{}|]/g, rr = /^\[object .+?Constructor\]$/, nr = Function.prototype, ir = Object.prototype, or = nr.toString, ar = ir.hasOwnProperty, sr = RegExp(
  "^" + or.call(ar).replace(er, "\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g, "$1.*?") + "$"
);
function ur(t) {
  if (!At(t) || Qe(t))
    return !1;
  var e = oe(t) ? sr : rr;
  return e.test(z(t));
}
function fr(t, e) {
  return t?.[e];
}
function Y(t, e) {
  var r = fr(t, e);
  return ur(r) ? r : void 0;
}
var _t = Y(S, "WeakMap");
function lr() {
}
function cr(t, e, r, n) {
  for (var o = t.length, i = r + -1; ++i < o; )
    if (e(t[i], i, t))
      return i;
  return -1;
}
function pr(t) {
  return t !== t;
}
function gr(t, e, r) {
  for (var n = r - 1, o = t.length; ++n < o; )
    if (t[n] === e)
      return n;
  return -1;
}
function dr(t, e, r) {
  return e === e ? gr(t, e, r) : cr(t, pr, r);
}
function hr(t, e) {
  var r = t == null ? 0 : t.length;
  return !!r && dr(t, e, 0) > -1;
}
var _r = 9007199254740991, yr = /^(?:0|[1-9]\d*)$/;
function ae(t, e) {
  var r = typeof t;
  return e = e ?? _r, !!e && (r == "number" || r != "symbol" && yr.test(t)) && t > -1 && t % 1 == 0 && t < e;
}
function se(t, e) {
  return t === e || t !== t && e !== e;
}
var vr = 9007199254740991;
function wt(t) {
  return typeof t == "number" && t > -1 && t % 1 == 0 && t <= vr;
}
function Tt(t) {
  return t != null && wt(t.length) && !oe(t);
}
var br = Object.prototype;
function mr(t) {
  var e = t && t.constructor, r = typeof e == "function" && e.prototype || br;
  return t === r;
}
function Ar(t, e) {
  for (var r = -1, n = Array(t); ++r < t; )
    n[r] = e(r);
  return n;
}
var wr = "[object Arguments]";
function Mt(t) {
  return B(t) && Z(t) == wr;
}
var ue = Object.prototype, Tr = ue.hasOwnProperty, Or = ue.propertyIsEnumerable, fe = Mt(/* @__PURE__ */ function() {
  return arguments;
}()) ? Mt : function(t) {
  return B(t) && Tr.call(t, "callee") && !Or.call(t, "callee");
};
function $r() {
  return !1;
}
var le = typeof exports == "object" && exports && !exports.nodeType && exports, Lt = le && typeof module == "object" && module && !module.nodeType && module, Cr = Lt && Lt.exports === le, Nt = Cr ? S.Buffer : void 0, Sr = Nt ? Nt.isBuffer : void 0, yt = Sr || $r, Pr = "[object Arguments]", xr = "[object Array]", Er = "[object Boolean]", Rr = "[object Date]", Dr = "[object Error]", Fr = "[object Function]", jr = "[object Map]", Ir = "[object Number]", Mr = "[object Object]", Lr = "[object RegExp]", Nr = "[object Set]", zr = "[object String]", Gr = "[object WeakMap]", Br = "[object ArrayBuffer]", Hr = "[object DataView]", Kr = "[object Float32Array]", Ur = "[object Float64Array]", qr = "[object Int8Array]", Vr = "[object Int16Array]", Wr = "[object Int32Array]", Xr = "[object Uint8Array]", Zr = "[object Uint8ClampedArray]", Yr = "[object Uint16Array]", Jr = "[object Uint32Array]", v = {};
v[Kr] = v[Ur] = v[qr] = v[Vr] = v[Wr] = v[Xr] = v[Zr] = v[Yr] = v[Jr] = !0;
v[Pr] = v[xr] = v[Br] = v[Er] = v[Hr] = v[Rr] = v[Dr] = v[Fr] = v[jr] = v[Ir] = v[Mr] = v[Lr] = v[Nr] = v[zr] = v[Gr] = !1;
function Qr(t) {
  return B(t) && wt(t.length) && !!v[Z(t)];
}
function ce(t) {
  return function(e) {
    return t(e);
  };
}
var pe = typeof exports == "object" && exports && !exports.nodeType && exports, Q = pe && typeof module == "object" && module && !module.nodeType && module, kr = Q && Q.exports === pe, gt = kr && ee.process, zt = function() {
  try {
    var t = Q && Q.require && Q.require("util").types;
    return t || gt && gt.binding && gt.binding("util");
  } catch {
  }
}(), Gt = zt && zt.isTypedArray, ge = Gt ? ce(Gt) : Qr, tn = Object.prototype, en = tn.hasOwnProperty;
function rn(t, e) {
  var r = w(t), n = !r && fe(t), o = !r && !n && yt(t), i = !r && !n && !o && ge(t), a = r || n || o || i, f = a ? Ar(t.length, String) : [], s = f.length;
  for (var u in t)
    en.call(t, u) && !(a && // Safari 9 has enumerable `arguments.length` in strict mode.
    (u == "length" || // Node.js 0.10 has enumerable non-index properties on buffers.
    o && (u == "offset" || u == "parent") || // PhantomJS 2 has enumerable non-index properties on typed arrays.
    i && (u == "buffer" || u == "byteLength" || u == "byteOffset") || // Skip index properties.
    ae(u, s))) && f.push(u);
  return f;
}
function nn(t, e) {
  return function(r) {
    return t(e(r));
  };
}
var on = nn(Object.keys, Object), an = Object.prototype, sn = an.hasOwnProperty;
function un(t) {
  if (!mr(t))
    return on(t);
  var e = [];
  for (var r in Object(t))
    sn.call(t, r) && r != "constructor" && e.push(r);
  return e;
}
function Ot(t) {
  return Tt(t) ? rn(t) : un(t);
}
var fn = /\.|\[(?:[^[\]]*|(["'])(?:(?!\1)[^\\]|\\.)*?\1)\]/, ln = /^\w*$/;
function $t(t, e) {
  if (w(t))
    return !1;
  var r = typeof t;
  return r == "number" || r == "symbol" || r == "boolean" || t == null || k(t) ? !0 : ln.test(t) || !fn.test(t) || e != null && t in Object(e);
}
var tt = Y(Object, "create");
function cn() {
  this.__data__ = tt ? tt(null) : {}, this.size = 0;
}
function pn(t) {
  var e = this.has(t) && delete this.__data__[t];
  return this.size -= e ? 1 : 0, e;
}
var gn = "__lodash_hash_undefined__", dn = Object.prototype, hn = dn.hasOwnProperty;
function _n(t) {
  var e = this.__data__;
  if (tt) {
    var r = e[t];
    return r === gn ? void 0 : r;
  }
  return hn.call(e, t) ? e[t] : void 0;
}
var yn = Object.prototype, vn = yn.hasOwnProperty;
function bn(t) {
  var e = this.__data__;
  return tt ? e[t] !== void 0 : vn.call(e, t);
}
var mn = "__lodash_hash_undefined__";
function An(t, e) {
  var r = this.__data__;
  return this.size += this.has(t) ? 0 : 1, r[t] = tt && e === void 0 ? mn : e, this;
}
function M(t) {
  var e = -1, r = t == null ? 0 : t.length;
  for (this.clear(); ++e < r; ) {
    var n = t[e];
    this.set(n[0], n[1]);
  }
}
M.prototype.clear = cn;
M.prototype.delete = pn;
M.prototype.get = _n;
M.prototype.has = bn;
M.prototype.set = An;
function wn() {
  this.__data__ = [], this.size = 0;
}
function at(t, e) {
  for (var r = t.length; r--; )
    if (se(t[r][0], e))
      return r;
  return -1;
}
var Tn = Array.prototype, On = Tn.splice;
function $n(t) {
  var e = this.__data__, r = at(e, t);
  if (r < 0)
    return !1;
  var n = e.length - 1;
  return r == n ? e.pop() : On.call(e, r, 1), --this.size, !0;
}
function Cn(t) {
  var e = this.__data__, r = at(e, t);
  return r < 0 ? void 0 : e[r][1];
}
function Sn(t) {
  return at(this.__data__, t) > -1;
}
function Pn(t, e) {
  var r = this.__data__, n = at(r, t);
  return n < 0 ? (++this.size, r.push([t, e])) : r[n][1] = e, this;
}
function P(t) {
  var e = -1, r = t == null ? 0 : t.length;
  for (this.clear(); ++e < r; ) {
    var n = t[e];
    this.set(n[0], n[1]);
  }
}
P.prototype.clear = wn;
P.prototype.delete = $n;
P.prototype.get = Cn;
P.prototype.has = Sn;
P.prototype.set = Pn;
var et = Y(S, "Map");
function xn() {
  this.size = 0, this.__data__ = {
    hash: new M(),
    map: new (et || P)(),
    string: new M()
  };
}
function En(t) {
  var e = typeof t;
  return e == "string" || e == "number" || e == "symbol" || e == "boolean" ? t !== "__proto__" : t === null;
}
function st(t, e) {
  var r = t.__data__;
  return En(e) ? r[typeof e == "string" ? "string" : "hash"] : r.map;
}
function Rn(t) {
  var e = st(this, t).delete(t);
  return this.size -= e ? 1 : 0, e;
}
function Dn(t) {
  return st(this, t).get(t);
}
function Fn(t) {
  return st(this, t).has(t);
}
function jn(t, e) {
  var r = st(this, t), n = r.size;
  return r.set(t, e), this.size += r.size == n ? 0 : 1, this;
}
function x(t) {
  var e = -1, r = t == null ? 0 : t.length;
  for (this.clear(); ++e < r; ) {
    var n = t[e];
    this.set(n[0], n[1]);
  }
}
x.prototype.clear = xn;
x.prototype.delete = Rn;
x.prototype.get = Dn;
x.prototype.has = Fn;
x.prototype.set = jn;
var In = "Expected a function";
function Ct(t, e) {
  if (typeof t != "function" || e != null && typeof e != "function")
    throw new TypeError(In);
  var r = function() {
    var n = arguments, o = e ? e.apply(this, n) : n[0], i = r.cache;
    if (i.has(o))
      return i.get(o);
    var a = t.apply(this, n);
    return r.cache = i.set(o, a) || i, a;
  };
  return r.cache = new (Ct.Cache || x)(), r;
}
Ct.Cache = x;
var Mn = 500;
function Ln(t) {
  var e = Ct(t, function(n) {
    return r.size === Mn && r.clear(), n;
  }), r = e.cache;
  return e;
}
var Nn = /[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(?:\.|\[\])(?:\.|\[\]|$))/g, zn = /\\(\\)?/g, Gn = Ln(function(t) {
  var e = [];
  return t.charCodeAt(0) === 46 && e.push(""), t.replace(Nn, function(r, n, o, i) {
    e.push(o ? i.replace(zn, "$1") : n || r);
  }), e;
});
function Bn(t) {
  return t == null ? "" : ne(t);
}
function de(t, e) {
  return w(t) ? t : $t(t, e) ? [t] : Gn(Bn(t));
}
function ut(t) {
  if (typeof t == "string" || k(t))
    return t;
  var e = t + "";
  return e == "0" && 1 / t == -1 / 0 ? "-0" : e;
}
function St(t, e) {
  e = de(e, t);
  for (var r = 0, n = e.length; t != null && r < n; )
    t = t[ut(e[r++])];
  return r && r == n ? t : void 0;
}
function Hn(t, e, r) {
  var n = t == null ? void 0 : St(t, e);
  return n === void 0 ? r : n;
}
function Kn(t, e) {
  for (var r = -1, n = e.length, o = t.length; ++r < n; )
    t[o + r] = e[r];
  return t;
}
function Un() {
  this.__data__ = new P(), this.size = 0;
}
function qn(t) {
  var e = this.__data__, r = e.delete(t);
  return this.size = e.size, r;
}
function Vn(t) {
  return this.__data__.get(t);
}
function Wn(t) {
  return this.__data__.has(t);
}
var Xn = 200;
function Zn(t, e) {
  var r = this.__data__;
  if (r instanceof P) {
    var n = r.__data__;
    if (!et || n.length < Xn - 1)
      return n.push([t, e]), this.size = ++r.size, this;
    r = this.__data__ = new x(n);
  }
  return r.set(t, e), this.size = r.size, this;
}
function C(t) {
  var e = this.__data__ = new P(t);
  this.size = e.size;
}
C.prototype.clear = Un;
C.prototype.delete = qn;
C.prototype.get = Vn;
C.prototype.has = Wn;
C.prototype.set = Zn;
function Yn(t, e) {
  for (var r = -1, n = t == null ? 0 : t.length, o = 0, i = []; ++r < n; ) {
    var a = t[r];
    e(a, r, t) && (i[o++] = a);
  }
  return i;
}
function Jn() {
  return [];
}
var Qn = Object.prototype, kn = Qn.propertyIsEnumerable, Bt = Object.getOwnPropertySymbols, ti = Bt ? function(t) {
  return t == null ? [] : (t = Object(t), Yn(Bt(t), function(e) {
    return kn.call(t, e);
  }));
} : Jn;
function ei(t, e, r) {
  var n = e(t);
  return w(t) ? n : Kn(n, r(t));
}
function Ht(t) {
  return ei(t, Ot, ti);
}
var vt = Y(S, "DataView"), bt = Y(S, "Promise"), G = Y(S, "Set"), Kt = "[object Map]", ri = "[object Object]", Ut = "[object Promise]", qt = "[object Set]", Vt = "[object WeakMap]", Wt = "[object DataView]", ni = z(vt), ii = z(et), oi = z(bt), ai = z(G), si = z(_t), R = Z;
(vt && R(new vt(new ArrayBuffer(1))) != Wt || et && R(new et()) != Kt || bt && R(bt.resolve()) != Ut || G && R(new G()) != qt || _t && R(new _t()) != Vt) && (R = function(t) {
  var e = Z(t), r = e == ri ? t.constructor : void 0, n = r ? z(r) : "";
  if (n)
    switch (n) {
      case ni:
        return Wt;
      case ii:
        return Kt;
      case oi:
        return Ut;
      case ai:
        return qt;
      case si:
        return Vt;
    }
  return e;
});
var Xt = S.Uint8Array, ui = "__lodash_hash_undefined__";
function fi(t) {
  return this.__data__.set(t, ui), this;
}
function li(t) {
  return this.__data__.has(t);
}
function rt(t) {
  var e = -1, r = t == null ? 0 : t.length;
  for (this.__data__ = new x(); ++e < r; )
    this.add(t[e]);
}
rt.prototype.add = rt.prototype.push = fi;
rt.prototype.has = li;
function ci(t, e) {
  for (var r = -1, n = t == null ? 0 : t.length; ++r < n; )
    if (e(t[r], r, t))
      return !0;
  return !1;
}
function he(t, e) {
  return t.has(e);
}
var pi = 1, gi = 2;
function _e(t, e, r, n, o, i) {
  var a = r & pi, f = t.length, s = e.length;
  if (f != s && !(a && s > f))
    return !1;
  var u = i.get(t), p = i.get(e);
  if (u && p)
    return u == e && p == t;
  var g = -1, d = !0, h = r & gi ? new rt() : void 0;
  for (i.set(t, e), i.set(e, t); ++g < f; ) {
    var b = t[g], c = e[g];
    if (n)
      var y = a ? n(c, b, g, e, t, i) : n(b, c, g, t, e, i);
    if (y !== void 0) {
      if (y)
        continue;
      d = !1;
      break;
    }
    if (h) {
      if (!ci(e, function(A, m) {
        if (!he(h, m) && (b === A || o(b, A, r, n, i)))
          return h.push(m);
      })) {
        d = !1;
        break;
      }
    } else if (!(b === c || o(b, c, r, n, i))) {
      d = !1;
      break;
    }
  }
  return i.delete(t), i.delete(e), d;
}
function di(t) {
  var e = -1, r = Array(t.size);
  return t.forEach(function(n, o) {
    r[++e] = [o, n];
  }), r;
}
function Pt(t) {
  var e = -1, r = Array(t.size);
  return t.forEach(function(n) {
    r[++e] = n;
  }), r;
}
var hi = 1, _i = 2, yi = "[object Boolean]", vi = "[object Date]", bi = "[object Error]", mi = "[object Map]", Ai = "[object Number]", wi = "[object RegExp]", Ti = "[object Set]", Oi = "[object String]", $i = "[object Symbol]", Ci = "[object ArrayBuffer]", Si = "[object DataView]", Zt = F ? F.prototype : void 0, dt = Zt ? Zt.valueOf : void 0;
function Pi(t, e, r, n, o, i, a) {
  switch (r) {
    case Si:
      if (t.byteLength != e.byteLength || t.byteOffset != e.byteOffset)
        return !1;
      t = t.buffer, e = e.buffer;
    case Ci:
      return !(t.byteLength != e.byteLength || !i(new Xt(t), new Xt(e)));
    case yi:
    case vi:
    case Ai:
      return se(+t, +e);
    case bi:
      return t.name == e.name && t.message == e.message;
    case wi:
    case Oi:
      return t == e + "";
    case mi:
      var f = di;
    case Ti:
      var s = n & hi;
      if (f || (f = Pt), t.size != e.size && !s)
        return !1;
      var u = a.get(t);
      if (u)
        return u == e;
      n |= _i, a.set(t, e);
      var p = _e(f(t), f(e), n, o, i, a);
      return a.delete(t), p;
    case $i:
      if (dt)
        return dt.call(t) == dt.call(e);
  }
  return !1;
}
var xi = 1, Ei = Object.prototype, Ri = Ei.hasOwnProperty;
function Di(t, e, r, n, o, i) {
  var a = r & xi, f = Ht(t), s = f.length, u = Ht(e), p = u.length;
  if (s != p && !a)
    return !1;
  for (var g = s; g--; ) {
    var d = f[g];
    if (!(a ? d in e : Ri.call(e, d)))
      return !1;
  }
  var h = i.get(t), b = i.get(e);
  if (h && b)
    return h == e && b == t;
  var c = !0;
  i.set(t, e), i.set(e, t);
  for (var y = a; ++g < s; ) {
    d = f[g];
    var A = t[d], m = e[d];
    if (n)
      var _ = a ? n(m, A, d, e, t, i) : n(A, m, d, t, e, i);
    if (!(_ === void 0 ? A === m || o(A, m, r, n, i) : _)) {
      c = !1;
      break;
    }
    y || (y = d == "constructor");
  }
  if (c && !y) {
    var O = t.constructor, E = e.constructor;
    O != E && "constructor" in t && "constructor" in e && !(typeof O == "function" && O instanceof O && typeof E == "function" && E instanceof E) && (c = !1);
  }
  return i.delete(t), i.delete(e), c;
}
var Fi = 1, Yt = "[object Arguments]", Jt = "[object Array]", it = "[object Object]", ji = Object.prototype, Qt = ji.hasOwnProperty;
function Ii(t, e, r, n, o, i) {
  var a = w(t), f = w(e), s = a ? Jt : R(t), u = f ? Jt : R(e);
  s = s == Yt ? it : s, u = u == Yt ? it : u;
  var p = s == it, g = u == it, d = s == u;
  if (d && yt(t)) {
    if (!yt(e))
      return !1;
    a = !0, p = !1;
  }
  if (d && !p)
    return i || (i = new C()), a || ge(t) ? _e(t, e, r, n, o, i) : Pi(t, e, s, r, n, o, i);
  if (!(r & Fi)) {
    var h = p && Qt.call(t, "__wrapped__"), b = g && Qt.call(e, "__wrapped__");
    if (h || b) {
      var c = h ? t.value() : t, y = b ? e.value() : e;
      return i || (i = new C()), o(c, y, r, n, i);
    }
  }
  return d ? (i || (i = new C()), Di(t, e, r, n, o, i)) : !1;
}
function xt(t, e, r, n, o) {
  return t === e ? !0 : t == null || e == null || !B(t) && !B(e) ? t !== t && e !== e : Ii(t, e, r, n, xt, o);
}
var Mi = 1, Li = 2;
function Ni(t, e, r, n) {
  var o = r.length, i = o;
  if (t == null)
    return !i;
  for (t = Object(t); o--; ) {
    var a = r[o];
    if (a[2] ? a[1] !== t[a[0]] : !(a[0] in t))
      return !1;
  }
  for (; ++o < i; ) {
    a = r[o];
    var f = a[0], s = t[f], u = a[1];
    if (a[2]) {
      if (s === void 0 && !(f in t))
        return !1;
    } else {
      var p = new C(), g;
      if (!(g === void 0 ? xt(u, s, Mi | Li, n, p) : g))
        return !1;
    }
  }
  return !0;
}
function ye(t) {
  return t === t && !At(t);
}
function zi(t) {
  for (var e = Ot(t), r = e.length; r--; ) {
    var n = e[r], o = t[n];
    e[r] = [n, o, ye(o)];
  }
  return e;
}
function ve(t, e) {
  return function(r) {
    return r == null ? !1 : r[t] === e && (e !== void 0 || t in Object(r));
  };
}
function Gi(t) {
  var e = zi(t);
  return e.length == 1 && e[0][2] ? ve(e[0][0], e[0][1]) : function(r) {
    return r === t || Ni(r, t, e);
  };
}
function Bi(t, e) {
  return t != null && e in Object(t);
}
function Hi(t, e, r) {
  e = de(e, t);
  for (var n = -1, o = e.length, i = !1; ++n < o; ) {
    var a = ut(e[n]);
    if (!(i = t != null && r(t, a)))
      break;
    t = t[a];
  }
  return i || ++n != o ? i : (o = t == null ? 0 : t.length, !!o && wt(o) && ae(a, o) && (w(t) || fe(t)));
}
function Ki(t, e) {
  return t != null && Hi(t, e, Bi);
}
var Ui = 1, qi = 2;
function Vi(t, e) {
  return $t(t) && ye(e) ? ve(ut(t), e) : function(r) {
    var n = Hn(r, t);
    return n === void 0 && n === e ? Ki(r, t) : xt(e, n, Ui | qi);
  };
}
function Wi(t) {
  return function(e) {
    return e?.[t];
  };
}
function Xi(t) {
  return function(e) {
    return St(e, t);
  };
}
function Zi(t) {
  return $t(t) ? Wi(ut(t)) : Xi(t);
}
function be(t) {
  return typeof t == "function" ? t : t == null ? ie : typeof t == "object" ? w(t) ? Vi(t[0], t[1]) : Gi(t) : Zi(t);
}
function Yi(t) {
  return function(e, r, n) {
    for (var o = -1, i = Object(e), a = n(e), f = a.length; f--; ) {
      var s = a[++o];
      if (r(i[s], s, i) === !1)
        break;
    }
    return e;
  };
}
var Ji = Yi();
function Qi(t, e) {
  return t && Ji(t, e, Ot);
}
function ki(t, e) {
  return function(r, n) {
    if (r == null)
      return r;
    if (!Tt(r))
      return t(r, n);
    for (var o = r.length, i = -1, a = Object(r); ++i < o && n(a[i], i, a) !== !1; )
      ;
    return r;
  };
}
var to = ki(Qi);
function eo(t, e) {
  var r = -1, n = Tt(t) ? Array(t.length) : [];
  return to(t, function(o, i, a) {
    n[++r] = e(o, i, a);
  }), n;
}
function ro(t, e) {
  var r = t.length;
  for (t.sort(e); r--; )
    t[r] = t[r].value;
  return t;
}
function no(t, e) {
  if (t !== e) {
    var r = t !== void 0, n = t === null, o = t === t, i = k(t), a = e !== void 0, f = e === null, s = e === e, u = k(e);
    if (!f && !u && !i && t > e || i && a && s && !f && !u || n && a && s || !r && s || !o)
      return 1;
    if (!n && !i && !u && t < e || u && r && o && !n && !i || f && r && o || !a && o || !s)
      return -1;
  }
  return 0;
}
function io(t, e, r) {
  for (var n = -1, o = t.criteria, i = e.criteria, a = o.length, f = r.length; ++n < a; ) {
    var s = no(o[n], i[n]);
    if (s) {
      if (n >= f)
        return s;
      var u = r[n];
      return s * (u == "desc" ? -1 : 1);
    }
  }
  return t.index - e.index;
}
function oo(t, e, r) {
  e.length ? e = ot(e, function(i) {
    return w(i) ? function(a) {
      return St(a, i.length === 1 ? i[0] : i);
    } : i;
  }) : e = [ie];
  var n = -1;
  e = ot(e, ce(be));
  var o = eo(t, function(i, a, f) {
    var s = ot(e, function(u) {
      return u(i);
    });
    return { criteria: s, index: ++n, value: i };
  });
  return ro(o, function(i, a) {
    return io(i, a, r);
  });
}
function ao(t, e, r, n) {
  return t == null ? [] : (w(e) || (e = e == null ? [] : [e]), r = r, w(r) || (r = r == null ? [] : [r]), oo(t, e, r));
}
var so = 1 / 0, uo = G && 1 / Pt(new G([, -0]))[1] == so ? function(t) {
  return new G(t);
} : lr, fo = 200;
function lo(t, e, r) {
  var n = -1, o = hr, i = t.length, a = !0, f = [], s = f;
  if (i >= fo) {
    var u = e ? null : uo(t);
    if (u)
      return Pt(u);
    a = !1, o = he, s = new rt();
  } else
    s = e ? [] : f;
  t:
    for (; ++n < i; ) {
      var p = t[n], g = e ? e(p) : p;
      if (p = p !== 0 ? p : 0, a && g === g) {
        for (var d = s.length; d--; )
          if (s[d] === g)
            continue t;
        e && s.push(g), f.push(p);
      } else o(s, g, r) || (s !== f && s.push(g), f.push(p));
    }
  return f;
}
function kt(t, e) {
  return t && t.length ? lo(t, be(e)) : [];
}
function co(t) {
  const { attrs: e, columns: r, registerRowsHandler: n } = t;
  let o = mt(e.sort);
  const i = T(() => r.value?.some((s) => s.sorter)), a = T(
    () => r.value.filter((s) => s.sorter).length > 1
  );
  return n((s) => {
    if (!o.value)
      return s;
    const u = Array.isArray(o.value) ? o.value : [o.value], p = u.map((d) => d.sortBy), g = u.map(
      (d) => d.descending ? "desc" : "asc"
    );
    return ao(s, p, g);
  }), {
    onSortChange: (s) => {
      i.value && (o.value = s);
    },
    multipleSort: a,
    sort: o
  };
}
function po(t) {
  return new Function("return " + t)();
}
const go = j(ho, {
  props: ["props"]
});
function ho(t) {
  const e = t.props;
  Ae(() => {
    console.log("mounted");
  });
  const r = we({
    value: ""
  });
  return te(
    () => r.value,
    (n) => {
      e.onChange(n);
    }
  ), () => e.fSlot(r);
}
function _o(t) {
  const {
    tableData: e,
    registerColumnsHandler: r,
    registerRowsHandler: n,
    columns: o,
    notifyTableDataChange: i,
    slots: a
  } = t, f = new Map(
    Object.entries(a).filter(([h]) => h.startsWith("filter-")).map(([h, b]) => [h.replace("filter-", ""), b])
  );
  r(
    (h) => h.map(
      (b) => yo(
        b,
        e,
        t.tdesignGlobalConfig,
        f
      )
    )
  );
  const s = mt(), u = new Map(o.value.map((h) => [h.colKey, h]));
  te(s, i), n((h) => {
    if (!s.value)
      return h;
    const b = Object.keys(s.value).map((c) => {
      const y = s.value[c], A = u.get(c).filter, m = A.type, _ = A.predicate ? po(A.predicate) : void 0, O = m ?? A._type;
      return {
        key: c,
        value: y,
        type: O,
        predicate: _
      };
    });
    return h.filter((c) => b.every((y) => {
      const A = y.type, m = y.predicate;
      if (A === "multiple") {
        const _ = y.value;
        return _.length === 0 ? !0 : m ? m(s, c) : _.includes(c[y.key]);
      }
      if (A === "single") {
        const _ = y.value;
        return _ ? m ? m(_, c) : c[y.key] === _ : !0;
      }
      if (A === "input") {
        const _ = y.value;
        return _ ? m ? m(_, c) : c[y.key].toString().includes(_) : !0;
      }
      if (A === "date") {
        const _ = y.value;
        if (!_ || _ === "") return !0;
        const [O, E] = _, nt = new Date(c[y.key]);
        return m ? m(_, c) : new Date(O) <= nt && nt <= new Date(E);
      }
      if (A === "custom") {
        const _ = y.value;
        return _ ? m ? m(_, c) : c[y.key].toString().includes(_) : !0;
      }
      throw new Error(`not support filter type ${A}`);
    }));
  });
  const p = (h, b) => {
    if (!b.col) {
      s.value = void 0;
      return;
    }
    s.value = {
      ...h
    };
  };
  function g() {
    s.value = void 0;
  }
  function d() {
    return s.value ? Object.keys(s.value).map((h) => {
      const b = u.get(h).label, c = s.value[h];
      return c.length === 0 ? "" : `${b}: ${JSON.stringify(c)}`;
    }).join("; ") : null;
  }
  return {
    onFilterChange: p,
    filterValue: s,
    resetFilters: g,
    filterResultText: d
  };
}
function yo(t, e, r, n) {
  if (n.has(t.colKey)) {
    if (t.filter) throw new Error("cannot set both slot and filter");
    t.filter = {
      type: "custom",
      component: n.get(t.colKey)
    };
  }
  if (!("filter" in t))
    return t;
  if (!("type" in t.filter)) throw new Error("filter type is required");
  const { colKey: i } = t, a = t.filter.type;
  if (a === "multiple") {
    const f = kt(e.value, i).map((u) => ({
      label: u[i],
      value: u[i]
    })), s = {
      resetValue: [],
      list: [
        { label: r.selectAllText, checkAll: !0 },
        ...f
      ],
      ...t.filter
    };
    return {
      ...t,
      filter: ht(s)
    };
  }
  if (a === "single") {
    const s = {
      resetValue: null,
      list: kt(e.value, i).map((u) => ({
        label: u[i],
        value: u[i]
      })),
      showConfirmAndReset: !0,
      ...t.filter
    };
    return {
      ...t,
      filter: ht(s)
    };
  }
  if (a === "input") {
    const f = {
      resetValue: "",
      confirmEvents: ["onEnter"],
      showConfirmAndReset: !0,
      ...t.filter,
      props: {
        ...t.filter?.props
      }
    };
    return {
      ...t,
      filter: ht(f)
    };
  }
  if (a === "date") {
    const f = {
      resetValue: "",
      showConfirmAndReset: !0,
      props: {
        firstDayOfWeek: 7,
        ...t.filter?.props
      },
      style: {
        fontSize: "14px"
      },
      classNames: "filter-date-range",
      attrs: {
        "data-type": "date-range-picker"
      },
      ...t.filter,
      component: $e,
      _type: "date"
    };
    return delete f.type, {
      ...t,
      filter: f
    };
  }
  if (a === "custom")
    return {
      ...t,
      filter: {
        _type: "custom",
        component: go,
        props: { fSlot: t.filter.component }
      }
    };
  throw new Error(`not support filter type ${a}`);
}
function ht(t) {
  const { stateProps: e, props: r = {}, bindValue: n } = t, { getRef: o } = xe();
  if (n) {
    let i = function(f) {
      a.value = f;
    };
    const a = o(n);
    r.onChange = i, r.value = a;
  }
  return e && e.forEach((i) => {
    i in r && (r[i] = o(r[i]));
  }), t;
}
const vo = {
  hover: !0,
  bordered: !0,
  tableLayout: "auto",
  showSortColumnBgColor: !0
};
function bo(t) {
  const { attrs: e } = t;
  return T(() => ({
    ...vo,
    ...e
  }));
}
function mo(t, e) {
  return T(() => {
    const r = Object.keys(t).filter(
      (n) => n.startsWith("header-cell-")
    );
    return e.value.filter((n) => !r.includes(n.title)).map((n) => ({
      slotName: `header-cell-${n.name}`,
      content: n.label ?? n.colKey
    }));
  });
}
function Ao(t) {
  const e = new Set(t.value.map((r) => r.cell));
  return (r, n) => e.has(r) ? { ...n, currentValue: n.row[n.col.colKey] } : n;
}
const wo = /* @__PURE__ */ j({
  inheritAttrs: !1,
  __name: "Table",
  setup(t) {
    const e = H(), r = K(), { t: n, globalConfig: o } = Ce("table"), { tableData: i, orgData: a, registerRowsHandler: f, notifyTableDataChange: s } = De(e), [u, p] = Fe({
      tableData: i,
      attrs: e
    }), g = Le({ tableData: i, attrs: e }), { sort: d, onSortChange: h, multipleSort: b } = co({
      registerRowsHandler: f,
      attrs: e,
      columns: u
    }), { onFilterChange: c, filterValue: y, resetFilters: A, filterResultText: m } = _o({
      tableData: a,
      registerRowsHandler: f,
      registerColumnsHandler: p,
      columns: u,
      tdesignGlobalConfig: o.value,
      notifyTableDataChange: s,
      slots: r
    }), _ = bo({ attrs: e }), O = mo(r, u), E = Ao(u);
    return (nt, Ro) => (N(), L(D.Table, U(l(_), {
      pagination: l(g),
      sort: l(d),
      data: l(i),
      columns: l(u),
      "filter-value": l(y),
      onSortChange: l(h),
      onFilterChange: l(c),
      "multiple-sort": l(b)
    }), q({
      "filter-row": $(() => [
        Et("div", null, [
          Et("span", null, ct(l(n)(l(o).searchResultText, l(i).length, {
            result: l(m)(),
            count: l(i).length
          })), 1),
          Te(D.Button, {
            theme: "primary",
            variant: "text",
            onClick: l(A)
          }, {
            default: $(() => [
              Rt(ct(l(o).clearFilterResultButtonText), 1)
            ]),
            _: 1
          }, 8, ["onClick"])
        ])
      ]),
      _: 2
    }, [
      I(l(O), (ft) => ({
        name: ft.slotName,
        fn: $(() => [
          Rt(ct(ft.content), 1)
        ])
      })),
      I(l(r), (ft, lt) => ({
        name: lt,
        fn: $((me) => [
          V(nt.$slots, lt, W(X(l(E)(lt, me))))
        ])
      }))
    ]), 1040, ["pagination", "sort", "data", "columns", "filter-value", "onSortChange", "onFilterChange", "multiple-sort"]));
  }
});
function To(t) {
  const { affixProps: e = {} } = t;
  return {
    container: ".insta-main",
    ...e
  };
}
function Oo(t) {
  const { container: e = ".insta-main" } = t;
  return e;
}
const $o = /* @__PURE__ */ j({
  inheritAttrs: !1,
  __name: "Anchor",
  setup(t) {
    const e = H(), r = K(), n = To(e), o = Oo(e);
    return (i, a) => (N(), L(D.Anchor, U(l(e), {
      container: l(o),
      "affix-props": l(n)
    }), q({ _: 2 }, [
      I(l(r), (f, s) => ({
        name: s,
        fn: $((u) => [
          V(i.$slots, s, W(X(u)))
        ])
      }))
    ]), 1040, ["container", "affix-props"]));
  }
}), Co = /* @__PURE__ */ j({
  __name: "Icon",
  props: {
    name: {},
    size: {},
    color: {},
    prefix: {}
  },
  setup(t) {
    const e = t, r = T(() => {
      const [n, o] = e.name.split(":");
      return o ? e.name : `${e.prefix || "tdesign"}:${e.name}`;
    });
    return (n, o) => (N(), L(Oe("icon"), {
      class: "t-icon",
      icon: r.value,
      size: n.size,
      color: n.color
    }, null, 8, ["icon", "size", "color"]));
  }
}), So = /* @__PURE__ */ j({
  inheritAttrs: !1,
  __name: "Select",
  props: {
    options: {}
  },
  setup(t) {
    const e = t, r = H(), n = K(), o = T(() => {
      const i = e.options;
      if (i) {
        if (Array.isArray(i))
          return i.length === 0 ? void 0 : i.map(
            (a) => typeof a == "string" || typeof a == "number" ? { label: a, value: a } : a
          );
        throw new Error("options must be an array");
      }
    });
    return (i, a) => (N(), L(D.Select, U(l(r), { options: o.value }), q({ _: 2 }, [
      I(l(n), (f, s) => ({
        name: s,
        fn: $((u) => [
          V(i.$slots, s, W(X(u)))
        ])
      }))
    ]), 1040, ["options"]));
  }
}), Po = /* @__PURE__ */ j({
  inheritAttrs: !1,
  __name: "RadioGroup",
  props: {
    options: {}
  },
  setup(t) {
    const e = t, r = H(), n = K(), o = T(() => {
      const i = e.options;
      if (i) {
        if (Array.isArray(i))
          return i.length === 0 ? void 0 : i.map(
            (a) => typeof a == "string" || typeof a == "number" ? { label: a, value: a } : a
          );
        throw new Error("options must be an array");
      }
    });
    return (i, a) => (N(), L(D.RadioGroup, U(l(r), { options: o.value }), q({ _: 2 }, [
      I(l(n), (f, s) => ({
        name: s,
        fn: $((u) => [
          V(i.$slots, s, W(X(u)))
        ])
      }))
    ]), 1040, ["options"]));
  }
});
function xo(t) {
  return (e) => {
    if (e.length && e.length < 1)
      return e;
    const { multiple: r = !1 } = t;
    if (r) {
      if (e.length > 1) {
        const { file: n, ...o } = e;
        return o;
      }
      return { "file[0]": e.file };
    }
    return e;
  };
}
const Eo = /* @__PURE__ */ j({
  inheritAttrs: !1,
  __name: "Upload",
  setup(t) {
    const e = H(), r = K(), n = xo(e);
    return (o, i) => (N(), L(D.Upload, U(l(e), { formatRequest: l(n) }), q({ _: 2 }, [
      I(l(r), (a, f) => ({
        name: f,
        fn: $((s) => [
          V(o.$slots, f, W(X(s)))
        ])
      }))
    ]), 1040, ["formatRequest"]));
  }
});
function Io(t) {
  t.use(D), t.component("t-table", wo), t.component("t-affix", Re), t.component("t-anchor", $o), t.component("t-icon", Co), t.component("t-select", So), t.component("t-radio-group", Po), t.component("t-upload", Eo), window.$tdesign = {
    NotifyPlugin: Pe,
    MessagePlugin: Se
  };
}
export {
  Io as install
};
