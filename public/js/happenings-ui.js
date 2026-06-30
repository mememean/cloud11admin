// ===== Happenings: shared UI components =====
// Card grid (desktop) / horizontal scroll (mobile), skeleton loading, render helpers.

function eventCardHTML(ev) {
  return (
    '<a class="ev-card" href="/happenings/event/' + ev.id + '">' +
      '<div class="ev-card-img"><img src="' + ev.image + '" alt="" loading="lazy"></div>' +
      '<div class="ev-card-body">' +
        '<div class="ev-card-title">' + ev.title + '</div>' +
        '<div class="ev-card-meta"><span class="ev-icon">&#128205;</span>' + ev.venue + '</div>' +
        '<div class="ev-card-meta"><span class="ev-icon">&#128197;</span>' + ev.date_range + '</div>' +
      '</div>' +
      '<div class="ev-card-arrow">&#8594;</div>' +
    '</a>'
  );
}

function skeletonCardHTML() {
  return '<div class="ev-card ev-skeleton"><div class="ev-card-img"></div><div class="ev-card-body">' +
    '<div class="sk-line sk-w70"></div><div class="sk-line sk-w50"></div><div class="sk-line sk-w50"></div>' +
    '</div></div>';
}

function renderEventGrid(containerEl, events) {
  containerEl.innerHTML = events.map(eventCardHTML).join('');
}

function renderSkeletons(containerEl, count) {
  var html = '';
  for (var i = 0; i < count; i++) html += skeletonCardHTML();
  containerEl.innerHTML = html;
}

function renderErrorState(containerEl, message) {
  containerEl.innerHTML = '<div class="ev-error">' + (message || 'Failed to load events.') + '</div>';
}

var HAPPENINGS_UI_CSS = '\
.ev-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}\
.ev-card{position:relative;display:block;border-radius:16px;overflow:hidden;background:var(--color-bg-soft,#f0f5ff);text-decoration:none;color:inherit;box-shadow:0 4px 18px rgba(15,23,42,.08);transition:transform .2s}\
.ev-card:hover{transform:translateY(-4px)}\
.ev-card-img{aspect-ratio:3/4;overflow:hidden;background:#dbe7fb}\
.ev-card-img img{width:100%;height:100%;object-fit:cover}\
.ev-card-body{padding:16px;background:linear-gradient(180deg,var(--color-primary-light,#6AABF8),var(--color-primary,#007ff7));color:#fff}\
.ev-card-title{font-weight:700;font-size:15px;margin-bottom:8px;line-height:1.3}\
.ev-card-meta{display:flex;align-items:center;gap:6px;font-size:12.5px;opacity:.9;margin-bottom:4px}\
.ev-card-arrow{position:absolute;right:16px;bottom:16px;color:#fff;font-size:16px}\
.ev-skeleton .ev-card-img{background:#e2e8f0;animation:ev-pulse 1.2s ease-in-out infinite}\
.ev-skeleton .ev-card-body{background:#f1f5f9}\
.sk-line{height:10px;border-radius:6px;background:#e2e8f0;margin-bottom:8px;animation:ev-pulse 1.2s ease-in-out infinite}\
.sk-w70{width:70%}.sk-w50{width:50%}\
@keyframes ev-pulse{0%,100%{opacity:1}50%{opacity:.5}}\
.ev-error{padding:32px;text-align:center;color:var(--color-muted,#64748b)}\
@media(max-width:768px){\
  .ev-grid{grid-template-columns:repeat(2,1fr);gap:14px}\
}\
@media(max-width:480px){\
  .ev-grid{display:flex;grid-template-columns:none;overflow-x:auto;gap:14px;padding-bottom:8px;scroll-snap-type:x mandatory;-webkit-overflow-scrolling:touch}\
  .ev-grid .ev-card{flex:0 0 72%;scroll-snap-align:start}\
}\
';

(function injectHappeningsCSS() {
  var s = document.createElement('style');
  s.textContent = HAPPENINGS_UI_CSS;
  document.head.appendChild(s);
})();
