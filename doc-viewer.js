// Lightweight PDF preview lightbox. PPTX/other files fall through to their
// normal <a href target="_blank"> behavior (browser download), since browsers
// can't render PowerPoint files natively.

function openDocLightbox(url, label) {
  var overlay = document.createElement('div');
  overlay.className = 'doc-lightbox';
  overlay.innerHTML =
    '<div class="doc-lightbox-bar">' +
      '<span>' + label + '</span>' +
      '<div class="doc-lightbox-actions">' +
        '<a href="' + url + '" target="_blank" rel="noopener">Open in new tab &rarr;</a>' +
        '<button class="doc-lightbox-close" aria-label="Close preview" type="button">&times;</button>' +
      '</div>' +
    '</div>' +
    '<iframe src="' + url + '" title="' + label + '"></iframe>';
  document.body.appendChild(overlay);
  document.body.style.overflow = 'hidden';

  function close() {
    overlay.remove();
    document.body.style.overflow = '';
    document.removeEventListener('keydown', onKey);
  }
  function onKey(e) {
    if (e.key === 'Escape') close();
  }
  overlay.querySelector('.doc-lightbox-close').addEventListener('click', close);
  overlay.addEventListener('click', function (e) {
    if (e.target === overlay) close();
  });
  document.addEventListener('keydown', onKey);
}

// Called from inline onclick on PDF doc-cards. Returns false (and prevents
// the default navigation) so the card opens the in-page lightbox instead of
// navigating away; returns true for anything else so normal link behavior
// (download/open) proceeds unhindered.
function handleDocClick(event, url, ext, label) {
  if (ext === 'pdf') {
    event.preventDefault();
    openDocLightbox(url, label);
    return false;
  }
  return true;
}
