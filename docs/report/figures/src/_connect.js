// Ve duong noi giua cac phan tu HTML trong #fig (tinh tu vi tri that sau khi trang dung xong).
// connect("a", "b", {dash: true, color: "#..", arrow: true, label: "...", from: "bottom", to: "top"})
function connect(a, b, o = {}) {
  const fig = document.getElementById("fig");
  let svg = document.getElementById("wires");
  if (!svg) {
    svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.id = "wires";
    svg.style.cssText = "position:absolute;left:0;top:0;pointer-events:none;overflow:visible";
    svg.innerHTML = '<defs><marker id="ah" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">' +
      '<path d="M0,0 L9,4.5 L0,9 z" fill="context-stroke"/></marker></defs>';
    fig.style.position = "relative";
    fig.appendChild(svg);
  }
  svg.setAttribute("width", fig.scrollWidth); svg.setAttribute("height", fig.scrollHeight);
  const f = fig.getBoundingClientRect(), A = document.getElementById(a).getBoundingClientRect(),
        B = document.getElementById(b).getBoundingClientRect();
  const pt = (r, side) => ({
    top: [r.left + r.width / 2, r.top], bottom: [r.left + r.width / 2, r.bottom],
    left: [r.left, r.top + r.height / 2], right: [r.right, r.top + r.height / 2],
  })[side].map((v, i) => v - (i ? f.top : f.left));
  // align: "x" -> duong doc thang tai hoanh do tam cua dich; "y" -> duong ngang thang tai tung do tam cua dich
  if (o.align) {
    const R = o.ref ? document.getElementById(o.ref).getBoundingClientRect() : B;  // lay tam theo phan tu khac
    const r = [R.left + R.width / 2 - f.left, R.top + R.height / 2 - f.top];
    const [x1, y1, x2, y2] = o.align === "x"
      ? (B.top > A.bottom ? [r[0], A.bottom - f.top, r[0], B.top - f.top] : [r[0], A.top - f.top, r[0], B.bottom - f.top])
      : (B.left > A.right ? [A.right - f.left, r[1], B.left - f.left, r[1]] : [A.left - f.left, r[1], B.right - f.left, r[1]]);
    return line(svg, `M${x1},${y1} L${x2},${y2}`, o, x1, y1, x2, y2);
  }
  let fs = o.from, ts = o.to;
  if (!fs) {  // tu chon canh gan nhat
    const dx = (B.left + B.width / 2) - (A.left + A.width / 2), dy = (B.top + B.height / 2) - (A.top + A.height / 2);
    if (Math.abs(dx) > Math.abs(dy)) { fs = dx > 0 ? "right" : "left"; ts = dx > 0 ? "left" : "right"; }
    else { fs = dy > 0 ? "bottom" : "top"; ts = dy > 0 ? "top" : "bottom"; }
  }
  const [x1, y1] = pt(A, fs), [x2, y2] = pt(B, ts);
  const vertical = fs === "top" || fs === "bottom";
  const d = o.straight ? `M${x1},${y1} L${x2},${y2}` :
    (vertical ? `M${x1},${y1} C${x1},${(y1 + y2) / 2} ${x2},${(y1 + y2) / 2} ${x2},${y2}`
              : `M${x1},${y1} C${(x1 + x2) / 2},${y1} ${(x1 + x2) / 2},${y2} ${x2},${y2}`);
  line(svg, d, o, x1, y1, x2, y2);
}

function line(svg, d, o, x1, y1, x2, y2) {
  const p = document.createElementNS("http://www.w3.org/2000/svg", "path");
  p.setAttribute("d", d);
  p.setAttribute("fill", "none");
  p.setAttribute("stroke", o.color || "#7a869a");
  p.setAttribute("stroke-width", o.width || 1.6);
  if (o.dash) p.setAttribute("stroke-dasharray", "6 4");
  if (o.arrow !== false) p.setAttribute("marker-end", "url(#ah)");
  svg.appendChild(p);
  if (o.label) {
    const t = document.createElementNS("http://www.w3.org/2000/svg", "text");
    t.setAttribute("x", (x1 + x2) / 2 + (o.dx || 6)); t.setAttribute("y", (y1 + y2) / 2 + (o.dy || 4));
    t.setAttribute("font-size", o.size || 12); t.setAttribute("fill", o.labelColor || "#52606d");
    t.setAttribute("font-family", "Segoe UI, Arial"); t.textContent = o.label;
    svg.appendChild(t);
  }
}
