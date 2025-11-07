(function() {
  function domainToBaseDN(host) {
    if (!host) return '';
    host = host.trim().toLowerCase();
    var parts = host.split('.').filter(Boolean);
    if (parts.length >= 2) {
      var domain = parts.slice(-2).join('.'); // dc.example.com -> example.com
      return 'DC=' + domain.split('.').join(',DC=');
    }
    return '';
  }

  function init() {
    var hostInput = document.getElementById('id_host');
    var baseDnInput = document.getElementById('id_base_dn');
    if (!hostInput || !baseDnInput) return;

    var update = function() {
      var suggested = domainToBaseDN(hostInput.value);
      if (!baseDnInput.value || baseDnInput.dataset.autofilled === '1') {
        baseDnInput.value = suggested;
        baseDnInput.dataset.autofilled = '1';
      }
    };

    hostInput.addEventListener('change', update);
    hostInput.addEventListener('blur', update);
    update();
  }

  if (document.readyState !== 'loading') init();
  else document.addEventListener('DOMContentLoaded', init);
})();
