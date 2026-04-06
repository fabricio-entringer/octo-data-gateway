/* Octo Data Gateway — Admin JS */

function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebar-overlay");
  sidebar.classList.toggle("open");
  overlay.classList.toggle("hidden");
}

function copyToClipboard(text, btnEl) {
  navigator.clipboard.writeText(text).then(function () {
    if (btnEl) {
      var original = btnEl.textContent;
      btnEl.textContent = "Copied!";
      setTimeout(function () { btnEl.textContent = original; }, 1500);
    }
  });
}

/* Close modals after successful HTMX swap */
document.body.addEventListener("htmx:afterSwap", function (evt) {
  var modal = document.getElementById("user-form-modal");
  if (modal && evt.detail.target && evt.detail.target.id === "user-table-body") {
    modal.remove();
  }
  /* Hide renew modals */
  document.querySelectorAll("[id^='renew-modal-']").forEach(function (el) {
    el.classList.add("hidden");
  });
});
