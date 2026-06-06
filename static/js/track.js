/**
 * beetle-finder アフィリエイト・エンゲージメント計測
 * GA4 カスタムイベント送信スクリプト
 */
(function () {
  'use strict';

  // ── アフィリエイトリンク クリック計測 ──────────────────────────
  // amazon.co.jp / af.moshimo.com(楽天・Yahoo) へのリンクを検知
  function getShop(href) {
    if (/amazon\.co\.jp/i.test(href)) return 'amazon';
    if (/moshimo\.com/i.test(href)) {
      if (/rakuten/i.test(href)) return 'rakuten';
      if (/yahoo/i.test(href)) return 'yahoo';
      return 'moshimo';
    }
    return 'other';
  }

  function getItemName(el) {
    // ボタンテキスト → 親行のテキスト → data-item 属性の順で取得
    if (el.dataset && el.dataset.item) return el.dataset.item;
    var row = el.closest('tr, .rec-row, .product-row, .kit-row, li');
    if (row) {
      var name = row.querySelector('td:first-child, .item-name, strong');
      if (name) return name.textContent.trim().slice(0, 60);
    }
    return el.textContent.trim().slice(0, 60) || '(unknown)';
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href]');
    if (!a) return;
    var href = a.href || '';
    if (!/amazon\.co\.jp|af\.moshimo\.com/i.test(href)) return;

    if (typeof gtag !== 'function') return;
    gtag('event', 'affiliate_click', {
      shop: getShop(href),
      item_name: getItemName(a),
      page_path: location.pathname,
      link_url: href.slice(0, 200)   // 長すぎるURLを切り捨て
    });
  }, true);  // capture phase: 子要素クリックも確実に拾う

  // ── スクロール深度計測（25 / 50 / 75 / 100%）─────────────────
  var scrollFired = {};
  var thresholds = [25, 50, 75, 100];

  function checkScroll() {
    var scrolled = window.scrollY + window.innerHeight;
    var total = document.documentElement.scrollHeight;
    if (total <= 0) return;
    var pct = Math.floor((scrolled / total) * 100);

    thresholds.forEach(function (t) {
      if (!scrollFired[t] && pct >= t) {
        scrollFired[t] = true;
        if (typeof gtag === 'function') {
          gtag('event', 'scroll_depth', {
            depth_percent: t,
            page_path: location.pathname
          });
        }
      }
    });
  }

  window.addEventListener('scroll', checkScroll, { passive: true });
  // ページロード直後に一度チェック（短いページ対応）
  window.addEventListener('load', checkScroll);

})();
