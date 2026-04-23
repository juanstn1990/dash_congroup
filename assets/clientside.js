if (!window.dash_clientside) {
    window.dash_clientside = {};
}

window.dash_clientside.sidebar = {
    toggle: function(n_clicks) {
        if (!n_clicks) return window.dash_clientside.no_update;

        var sidebar = document.getElementById('sidebar-wrapper');
        var mainContent = document.getElementById('main-content');
        var toggleBtn = document.getElementById('sidebar-toggle');

        if (!sidebar) return window.dash_clientside.no_update;

        var isCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
        var newState = !isCollapsed;
        localStorage.setItem('sidebar-collapsed', newState);

        if (newState) {
            sidebar.style.width = '0px';
            sidebar.style.padding = '0px';
            sidebar.style.overflow = 'hidden';
            if (mainContent) mainContent.style.marginLeft = '0px';
            if (toggleBtn) {
                toggleBtn.style.left = '10px';
                toggleBtn.innerHTML = '→';
            }
        } else {
            sidebar.style.width = '250px';
            sidebar.style.padding = '1rem';
            sidebar.style.overflowY = 'auto';
            if (mainContent) mainContent.style.marginLeft = '270px';
            if (toggleBtn) {
                toggleBtn.style.left = '260px';
                toggleBtn.innerHTML = '☰';
            }
        }

        return window.dash_clientside.no_update;
    },

    restore: function(pathname) {
        var sidebar = document.getElementById('sidebar-wrapper');
        var mainContent = document.getElementById('main-content');
        var toggleBtn = document.getElementById('sidebar-toggle');

        if (toggleBtn) {
            if (!sidebar) {
                toggleBtn.style.display = 'none';
                return window.dash_clientside.no_update;
            }
            toggleBtn.style.display = 'block';
            toggleBtn.style.transition = 'left 0.3s ease';
        }

        if (!sidebar) return window.dash_clientside.no_update;

        var isCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';

        if (isCollapsed) {
            sidebar.style.width = '0px';
            sidebar.style.padding = '0px';
            sidebar.style.overflow = 'hidden';
            if (mainContent) mainContent.style.marginLeft = '0px';
            if (toggleBtn) {
                toggleBtn.style.left = '10px';
                toggleBtn.innerHTML = '→';
            }
        } else {
            sidebar.style.width = '250px';
            sidebar.style.padding = '1rem';
            sidebar.style.overflowY = 'auto';
            if (mainContent) mainContent.style.marginLeft = '270px';
            if (toggleBtn) {
                toggleBtn.style.left = '260px';
                toggleBtn.innerHTML = '☰';
            }
        }

        return window.dash_clientside.no_update;
    }
};
