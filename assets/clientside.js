if (!window.dash_clientside) {
    window.dash_clientside = {};
}

window.dash_clientside.sidebar = {
    toggle: function(n_clicks) {
        if (!n_clicks) return window.dash_clientside.no_update;

        var sidebar = document.getElementById('sidebar-wrapper');
        if (!sidebar) return window.dash_clientside.no_update;

        var isCollapsed = document.body.classList.contains('sidebar-collapsed');
        var newState = !isCollapsed;

        localStorage.setItem('sidebar-collapsed', newState ? 'true' : 'false');

        if (newState) {
            document.body.classList.add('sidebar-collapsed');
        } else {
            document.body.classList.remove('sidebar-collapsed');
        }

        var btn = document.getElementById('sidebar-toggle');
        if (btn) btn.textContent = newState ? '›' : '‹';

        return window.dash_clientside.no_update;
    },

    restore: function(pathname) {
        var btn = document.getElementById('sidebar-toggle');

        function applyState() {
            var sidebar = document.getElementById('sidebar-wrapper');
            if (!sidebar) {
                if (btn) btn.style.display = 'none';
                return false;
            }
            var isCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
            if (isCollapsed) {
                document.body.classList.add('sidebar-collapsed');
            } else {
                document.body.classList.remove('sidebar-collapsed');
            }
            if (btn) {
                btn.textContent = isCollapsed ? '›' : '‹';
                btn.style.display = 'flex';
            }
            return true;
        }

        // If sidebar isn't in the DOM yet (initial load race), wait for it
        if (!applyState()) {
            var observer = new MutationObserver(function(mutations, obs) {
                if (applyState()) {
                    obs.disconnect();
                }
            });
            var root = document.getElementById('page-content') || document.body;
            observer.observe(root, { childList: true, subtree: true });
        }

        return window.dash_clientside.no_update;
    }
};
